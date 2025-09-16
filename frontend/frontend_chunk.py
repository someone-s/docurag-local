from fastapi import HTTPException

import requests
import os

chunk_serviceorip = os.environ['CHUNK_SERVICEORIP']
chunk_port = os.environ['CHUNK_PORT']

batch_size = int(os.environ['EMBED_BATCH_SIZE'])

def get_chunk(text: str) -> list[str]:
    chunk_req = requests.post(f'http://{chunk_serviceorip}:{chunk_port}/', json={'text': text})
    if chunk_req.status_code != 200:
        raise HTTPException(status_code=chunk_req.status_code, detail=chunk_req.reason)
    
    return chunk_req.json()