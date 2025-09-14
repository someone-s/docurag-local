from typing import Annotated
from fastapi import FastAPI, File, HTTPException, UploadFile

from pydantic import BaseModel, Field
import requests
import math
import os

extract_serviceorip = os.environ['EXTRACT_SERVICEORIP']
extract_port = os.environ['EXTRACT_PORT']
chunk_serviceorip = os.environ['CHUNK_SERVICEORIP']
chunk_port = os.environ['CHUNK_PORT']
embed_serviceorip = os.environ['EMBED_SERVICEORIP']
embed_port = os.environ['EMBED_PORT']
manage_serviceorip = os.environ['MANAGE_SERVICEORIP']
manage_port = os.environ['MANAGE_PORT']

app = FastAPI()
batch_size = 32

@app.post('/upload')
async def upload(\
    document_name: Annotated[str, File(description="Document name to associate with file")],\
    file: Annotated[UploadFile, File(description="A PDF to convert to text")]):
    
    extract_req = requests.post(f'http://{extract_serviceorip}:{extract_port}/', files=dict(file=await file.read()))
    if extract_req.status_code != 200:
        raise HTTPException(status_code=extract_req.status_code, detail=extract_req.reason)
    
    plain = extract_req.text

    chunk_req = requests.post(f'http://{chunk_serviceorip}:{chunk_port}/', json={'name': document_name, 'text': plain})
    if chunk_req.status_code != 200:
        raise HTTPException(status_code=chunk_req.status_code, detail=chunk_req.reason)
    
    chunks_array = chunk_req.json()
    batch_count = math.ceil(len(chunks_array) / batch_size)

    for batch in range(batch_count):

        actual_text = chunks_array[
                batch*batch_size:
                (batch+1)*batch_size
            ]

        embed_input = { 'inputs': actual_text }
        embed_req = requests.post(f'http://{embed_serviceorip}:{embed_port}/embed', json=embed_input)
        if embed_req.status_code != 200:
            raise HTTPException(status_code=embed_req.status_code, detail=embed_req.reason)
        embed_output = embed_req.json() # array of embed vectors (which are each array numbers)

        for i in range(len(embed_output)):

            manage_input = {
                'chunk_content': actual_text[i],
                'embed': embed_output[i]
            }
            manage_req = requests.post(f'http://{manage_serviceorip}:{manage_port}/add', json=manage_input)
            if manage_req.status_code != 200:
                raise HTTPException(status_code=manage_req.status_code, detail=manage_req.reason)


class QueryRequestItem(BaseModel):
    text: str = Field(description="String representing the chunk text")

@app.post('/query')
async def query(item: QueryRequestItem):

    chunk_req = requests.post(f'http://{chunk_serviceorip}:{chunk_port}/', json={'text': item.text})
    if chunk_req.status_code != 200:
        raise HTTPException(status_code=chunk_req.status_code, detail=chunk_req.reason)
    
    chunks_array = chunk_req.json()
    batch_count = math.ceil(len(chunks_array) / batch_size)

    relevant_text = {}

    for batch in range(batch_count):

        actual_text = chunks_array[
                batch*batch_size:
                (batch+1)*batch_size
            ]

        embed_input = { 'inputs': actual_text }
        embed_req = requests.post(f'http://{embed_serviceorip}:{embed_port}/embed', json=embed_input)
        if embed_req.status_code != 200:
            raise HTTPException(status_code=embed_req.status_code, detail=embed_req.reason)
        embed_output = embed_req.json() # array of embed vectors (which are each array numbers)

        for i in range(len(embed_output)):

            manage_input = { 'embed': embed_output[i] }
            manage_req = requests.post(f'http://{manage_serviceorip}:{manage_port}/fetch', json=manage_input)
            if manage_req.status_code != 200:
                raise HTTPException(status_code=manage_req.status_code, detail=manage_req.reason)
            maange_output = manage_req.json()
            
            for manage_item in maange_output:
                relevant_text[manage_item['id']] = manage_item['text']
    
    return relevant_text
            

