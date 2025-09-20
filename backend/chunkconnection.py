from fastapi import HTTPException

import requests
import os

chunk_serviceorip = os.environ['CHUNK_SERVICEORIP']
chunk_port = os.environ['CHUNK_PORT']

batch_size = int(os.environ['EMBED_BATCH_SIZE'])

def get_chunk(pretense: str|None, text: str) -> list[str]:

    chunK_input = { 'text': text }
    if pretense != None:
        chunK_input['pretense'] = pretense
    chunk_req = requests.post(f'http://{chunk_serviceorip}:{chunk_port}/', json=chunK_input)
    if chunk_req.status_code != 200:
        raise HTTPException(status_code=chunk_req.status_code, detail=chunk_req.reason)
    
    return chunk_req.json()