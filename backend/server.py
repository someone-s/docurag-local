from typing import Annotated
from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from openai import AsyncOpenAI
import os

from pydantic import BaseModel, Field

from databaseconnection import Machine, database_document_category_add, database_document_category_delete, database_document_category_exist, database_document_category_list, database_machine_add, database_machine_category_add, database_machine_category_delete, database_machine_category_exist, database_machine_category_list, database_machine_exist, database_machine_delete, database_machine_fetch, database_document_list_by_machine, database_machine_list, database_reset, database_document_fetch, database_document_delete, database_document_list, database_document_count
from uploadconnection import extract_information, store_document
from queryconnection import converse

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

origins = [
    os.environ['FRONTEND_ORIGIN'],
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/wipe')
def wipe():
    database_reset()




class MachineCategoryRequest(BaseModel):
    machine_category: Annotated[str, Field(description="String a category of machine")]

@app.post('/machine/category/add')
def machine_category_add(request: MachineCategoryRequest):
    database_machine_category_add(request.machine_category)

@app.get('/machine/category/list')
def machine_category_list():
    return { 'machine_categories': database_machine_category_list() }

@app.post('/machine/category/delete')
def machine_category_delete(request: MachineCategoryRequest):
    result = database_machine_category_delete(request.machine_category)
    if not result:
        raise HTTPException(422, "Machine category inuse")




@app.post('/machine/add')
def machine_add(machine: Machine):
    if not database_machine_category_exist(machine.category):
        raise HTTPException(422, "machine category does not exist")
    machine_id = database_machine_add(machine)
    if machine_id == None:
        raise HTTPException(500, "failed to add machine")
    return { 'machine_id': machine_id }

@app.get('/machine/list')
def machine_list():
    return { 'machine_ids': database_machine_list() }

@app.get('/machine/fetch/{machine_id}')
def machine_fetch(machine_id: int):
    machine = database_machine_fetch(machine_id)
    if machine == None:
        raise HTTPException(422, "Machine id does not exist")
    
    return machine

class MachineDeleteRequest(BaseModel):
    machine_id: Annotated[int, Field(description="Int id of machine")]

@app.post('/machine/delete')
def machine_delete(request: MachineDeleteRequest):
    database_machine_delete(request.machine_id)



class DocumentCategoryRequest(BaseModel):
    document_category: Annotated[str, Field(description="String a category of document")]

@app.post('/document/category/add')
def document_category_add(request: DocumentCategoryRequest):
    database_document_category_add(request.document_category)

@app.get('/document/category/list')
def document_category_list():
    return { 'document_categories': database_document_category_list() }

@app.post('/document/category/delete')
def document_category_delete(request: DocumentCategoryRequest):
    result = database_document_category_delete(request.document_category)
    if not result:
        raise HTTPException(422, "Machine category inuse")



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

@app.post('/document/upload')
async def document_upload(
    machine_ids_str: Annotated[str, Form(description="A comma separated list of int machine_ids this document is for, type is string due to framework limitation")],
    document_category: Annotated[str, Form()],
    file: Annotated[UploadFile, File(description="A PDF to convert to text")], 
    background_task: BackgroundTasks):

    machine_ids: list[int] = []

    for machine_id_str in machine_ids_str.split(','):
        machine_id: int
        try:
            machine_id = int(machine_id_str)
        except:
            raise HTTPException(422, f"machine_id {machine_id_str} is not an integer")
        
        if not database_machine_exist(machine_id):
            raise HTTPException(422, f"machine_id {machine_id} not valid")
        
        machine_ids.append(machine_id)

    logger.info(machine_ids)
    
    if not database_document_category_exist(document_category):
        raise HTTPException(422, "document_category not valid")

    file_binary = await file.read()
    
    logger.info('upload file read complete')

    upload_id = add_in_progress(file.filename if file.filename != None else "Document")
    background_task.add_task(document_upload_continuation, machine_ids, document_category, upload_id, file_binary)

async def document_upload_continuation(
        machine_ids: list[int],
        document_category: str,
        upload_id: UUID, 
        file_binary: bytes):

    async def on_progress():
        logger.info('upload extraction in-progress')
    
    extract_data = await extract_information(client, file_binary, on_progress)
    if extract_data == None:
        logger.warning('upload extraction failed nothing commited')
        return
    
    logger.info('upload extraction complete')

    # wont work if document category deleted
    is_success = store_document(machine_ids, document_category, file_binary, extract_data)

    logger.info('upload store complete')
    
    remove_in_progress(upload_id)

@app.get(
    '/document/fetch/{document_id}', 
    responses ={ 200: { "content": {'application/pdf': {}} } }, 
    response_class=Response
)
def document_fetch(document_id: int):
    binary_response = database_document_fetch(document_id)
    if binary_response == None:
        raise HTTPException(status_code=404, detail="document not found")
    return Response(content=binary_response, media_type='application/pdf')

@app.get('/document/list')
def document_list(start_id: int = 0, limit: int|None = None):
    return { 'document_ids': database_document_list(start_id, limit) }

@app.get('/document/list/machine/{machine_id}')
def document_list_machine(machine_id: int):
    return { 'document_ids': database_document_list_by_machine(machine_id) }

@app.get('/document/count')
def document_count():
    return { 'count': database_document_count() }

class DocumentDeleteRequest(BaseModel):
    document_id: Annotated[int, Field("int id of the document to delete")]

@app.post('/document/delete')
def document_delete(request: DocumentDeleteRequest):
    database_document_delete(request.document_id)



@app.websocket('/query')
async def query(websocket: WebSocket):

    try:
        await websocket.accept()

        await converse(client, websocket.receive_json, websocket.send_json)

        await websocket.close()
    except:
        logger.info("A websocket for query failed")
