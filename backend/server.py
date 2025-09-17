import asyncio
from typing import Annotated
from fastapi import FastAPI, File, HTTPException, Response, UploadFile, WebSocket, BackgroundTasks

from openai import AsyncOpenAI
import os

from pydantic import BaseModel, Field

from database import wipe_database, fetch_document_from_database, delete_document_and_embed_from_database, list_document_from_database, count_document_from_database
from upload import extract_information, store_information
from query import receive_parameters, retrive_relevant, generate_inference

from uuid import uuid4, UUID
from threading import Lock

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

app = FastAPI()

lock = Lock()
in_progress_upload: dict[UUID, str] = {}
def add_in_progress(file_name: str) -> UUID:
    new_id = uuid4()
    lock.acquire()
    in_progress_upload[new_id] = file_name
    lock.release()
    return new_id
def remove_in_progress(id: UUID):
    lock.acquire()
    in_progress_upload.pop(id, 'not found')
    lock.release()

@app.post('/wipe')
def wipe():
    wipe_database()

@app.post('/document/upload')
async def upload(file: Annotated[UploadFile, File(description="A PDF to convert to text")], background_task: BackgroundTasks):
    
    
    file_binary = await file.read()
    
    logger.info('upload file read complete')

    upload_id = add_in_progress(file.filename if file.filename != None else "Document")
    background_task.add_task(upload_continuation, upload_id, file_binary)

async def upload_continuation(upload_id: UUID, file_binary: bytes):

    async def on_progress():
        logger.info('upload extraction in-progress')
    
    extract_data = await extract_information(client, file_binary, on_progress)
    if extract_data == None:
        logger.warning('upload extraction failed nothing commited')
        return
    
    logger.info('upload extraction complete')

    store_information(file_binary, extract_data)

    logger.info('upload store complete')
    
    remove_in_progress(upload_id)


@app.websocket('/query')
async def query(websocket: WebSocket):

    await websocket.accept()

    machine_make, machine_name, machine_category, machine_model, query_text = await receive_parameters(fetch_input_hook=websocket.receive_json)
    

    relevant_texts = await retrive_relevant(machine_make, machine_name, machine_category, machine_model, query_text)
    for relevant_text in relevant_texts:

        await websocket.send_json({
            'type': 'document',
            'document_id': relevant_text.document_id,
            'machine_make': relevant_text.machine_make,
            'machine_name': relevant_text.machine_name,
            'machine_category': relevant_text.machine_category,
            'machine_model': relevant_text.machine_model,
            'document_category': relevant_text.document_category,
            'section_start': relevant_text.section_start,
            'section_end': relevant_text.section_end
        })
        await asyncio.sleep(0.00001)

    async def on_delta(delta: str):
        await websocket.send_json({'type': 'generate', 'delta': delta})
        await asyncio.sleep(0.0001)

    async def on_complete(text: str):
            await websocket.send_json({'type': 'complete', 'text': text})
            await asyncio.sleep(0.0001)
    
    await generate_inference(client, query_text, relevant_texts, on_delta=on_delta, on_complete=on_complete)

    await websocket.send_json({'type': 'log', 'message': "stream ended"})

    await websocket.close()


@app.get(
    '/document/fetch/{document_id}', 
    responses ={ 200: { "content": {'application/pdf': {}} } }, 
    response_class=Response
)
def get_document(document_id: int):
    binary_response = fetch_document_from_database(document_id)
    if binary_response == None:
        raise HTTPException(status_code=404, detail="document not found")
    return Response(content=binary_response, media_type='application/pdf')

@app.get('/document/list')
def get_document_subset(start_id: int = 0, limit: int|None = None):
    return { 'ids': list_document_from_database(start_id, limit) }


@app.get('/document/count')
def get_document_subset():
    return { 'count': count_document_from_database() }


class DeleteRequest(BaseModel):
    document_id: Annotated[int, Field("int id of the document to delete")]

@app.post('/document/delete')
def delete_document(request: DeleteRequest):
    delete_document_and_embed_from_database(request.document_id)