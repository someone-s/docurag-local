import asyncio
from typing import Annotated
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket

import json
import sseclient
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
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
generate_serviceorip = os.environ['GENERATE_SERVICEORIP']
generate_port = os.environ['GENERATE_PORT']

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

app = FastAPI()
batch_size = int(os.environ['EMBED_BATCH_SIZE'])

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
    text: Annotated[str, Field(description="String representing the chunk text")]

@app.websocket('/query')
async def query(websocket: WebSocket):

    await websocket.accept()
    item = await websocket.receive_json()
    await websocket.send_json({'type': 'log', 'message': "Received messsage"})
    await asyncio.sleep(0.0001)

    query_text = item['text']

    chunk_req = requests.post(f'http://{chunk_serviceorip}:{chunk_port}/', json={'text': query_text})
    if chunk_req.status_code != 200:
        raise HTTPException(status_code=chunk_req.status_code, detail=chunk_req.reason)
    await websocket.send_json({'type': 'log', 'message': "Chunk complete"})
    await asyncio.sleep(0.0001)
    
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
        await websocket.send_json({'type': 'log', 'message': "One embed batch complete"})
        await asyncio.sleep(0.0001)

        for i in range(len(embed_output)):

            manage_input = { 'embed': embed_output[i] }
            manage_req = requests.post(f'http://{manage_serviceorip}:{manage_port}/fetch', json=manage_input)
            if manage_req.status_code != 200:
                raise HTTPException(status_code=manage_req.status_code, detail=manage_req.reason)
            maange_output = manage_req.json()
            await websocket.send_json({'type': 'log', 'message': "One embed fetch complete"})
            await asyncio.sleep(0.0001)
            
            for manage_item in maange_output:
                relevant_text[manage_item['id']] = manage_item['text']

    stream = await client.responses.create(
        model="gpt-5-nano",
        input=[
            {
            "role": "developer",
            "content": [
                {
                "type": "input_text",
                "text": "Answer the given Question using only the provided Facts."
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "input_text",
                "text": f"I need you the chatbot to answer my question: {query_text}, with the facts I'm listing below:\n{"\n\n".join([ f"Begin Fact {i}:\n{text}\nEnd Fact {i}" for i, text in enumerate(relevant_text.values())])}"
                }
            ]
            },
        ],
        text={
            "format": {
            "type": "text"
            },
            "verbosity": "medium"
        },
        reasoning={
            "effort": "medium"
        },
        tools=[],
        store=True,
        include=[
            "reasoning.encrypted_content",
            "web_search_call.action.sources"
        ],
        stream=True
    )
    async for event in stream:
        if isinstance(event, ResponseTextDeltaEvent):
            delta_event: ResponseTextDeltaEvent = event
            await websocket.send_text(delta_event.delta)
            await asyncio.sleep(0.0001)

    await websocket.send_json({'type': 'log', 'message': "Done"})