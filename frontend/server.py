import json
from typing import Annotated
from fastapi import FastAPI, File, HTTPException, UploadFile

from fastapi.responses import PlainTextResponse
import requests

import math

app = FastAPI()
batch_size = 32

@app.post('/upload')
async def upload(file: Annotated[UploadFile, File(description="A PDF to convert to text")]):
    
    extract_req = requests.post('http://0.0.0.0:8080/', files=dict(file=await file.read()))
    if extract_req.status_code != 200:
        raise HTTPException(status_code=extract_req.status_code, detail=extract_req.reason)
    
    plain = extract_req.text

    chunk_req = requests.post('http://0.0.0.0:8090/', json={'name': "Zanussi", 'text': plain})
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
        embed_req = requests.post('http://0.0.0.0:8095/embed', json=embed_input)
        if embed_req.status_code != 200:
            raise HTTPException(status_code=embed_req.status_code, detail=embed_req.reason)
        embed_output = embed_req.json() # array of embed vectors (which are each array numbers)

        print(len(actual_text))
        print(len(embed_output))

        for i in range(len(embed_output)):

            manage_input = {
                'chunk_content': actual_text[i],
                'embed': embed_output[i]
            }
            manage_req = requests.post('http://0.0.0.0:8085/add', json=manage_input)
            if manage_req.status_code != 200:
                raise HTTPException(status_code=manage_req.status_code, detail=manage_req.reason)

    return "1"

