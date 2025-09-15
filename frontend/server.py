import asyncio
from typing import Annotated
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket

from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
import requests
import os

from database import retreive_from_database, store_to_database

extract_serviceorip = os.environ['EXTRACT_SERVICEORIP']
extract_port = os.environ['EXTRACT_PORT']

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

app = FastAPI()

@app.post('/upload')
async def upload(\
    document_name: Annotated[str, File(description="Document name to associate with file")],\
    file: Annotated[UploadFile, File(description="A PDF to convert to text")]):
    
    extract_req = requests.post(f'http://{extract_serviceorip}:{extract_port}/', files=dict(file=await file.read()))
    if extract_req.status_code != 200:
        raise HTTPException(status_code=extract_req.status_code, detail=extract_req.reason)
    
    plain = extract_req.text

    store_to_database(document_name, plain)

@app.websocket('/query')
async def query(websocket: WebSocket):

    await websocket.accept()
    item = await websocket.receive_json()
    await websocket.send_json({'type': 'log', 'message': "Received messsage"})
    await asyncio.sleep(0.0001)

    query_text = item['text']

    relevant_text = await retreive_from_database(query_text)

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
