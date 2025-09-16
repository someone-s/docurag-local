import asyncio
from typing import Annotated
from fastapi import FastAPI, File, HTTPException, Response, UploadFile, WebSocket

from openai import AsyncOpenAI
import os

from pydantic import BaseModel, Field

from frontend_database import wipe_database, fetch_document_from_database, delete_document_and_embed_from_database

from frontend_upload import extract_information, store_information
from frontend_query import receive_parameters, retrive_relevant, generate_inference

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

app = FastAPI()

@app.post('/wipe')
def wipe():
    wipe_database()

@app.websocket('/upload')
async def upload(websocket: WebSocket):

    await websocket.accept()

    file_binary = await websocket.receive_bytes()

    async def on_progress():
        await websocket.send_json({'type': 'log', 'message': 'extraction in-progress'})
        await asyncio.sleep(0.0001)
    
    extract_data = await extract_information(client, file_binary, on_progress)
    if extract_data == None:
        await websocket.send_json({'type': 'error', 'message': 'extraction failed'})
        await websocket.close()
        return
    
    await websocket.send_json({'type': 'log', 'message': 'extraction complete'})
    await asyncio.sleep(0.0001)

    store_information(file_binary, extract_data)

    await websocket.send_json({'type': 'log', 'message': 'store complete'})
    await websocket.close()



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

class DeleteRequest(BaseModel):
    document_id: Annotated[int, Field("int id of the document to delete")]

@app.post('/document/delete')
def delete_document(request: DeleteRequest):
    delete_document_and_embed_from_database(request.document_id)