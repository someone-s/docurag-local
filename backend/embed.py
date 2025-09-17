from fastapi import HTTPException

import requests
import math
import os

embed_serviceorip = os.environ['EMBED_SERVICEORIP']
embed_port = os.environ['EMBED_PORT']

batch_size = int(os.environ['EMBED_BATCH_SIZE'])

def get_embed(chunks: list[str]) -> list[list[float]]:
    batch_count = math.ceil(len(chunks) / batch_size)
    embed_outputs = []

    for batch in range(batch_count):
        actual_text = chunks[
                batch*batch_size:
                (batch+1)*batch_size
            ]

        embed_input = { 'inputs': actual_text }
        embed_req = requests.post(f'http://{embed_serviceorip}:{embed_port}/embed', json=embed_input)
        if embed_req.status_code != 200:
            raise HTTPException(status_code=embed_req.status_code, detail=embed_req.reason)
        embed_output = embed_req.json() # array of embed vectors (which are each array numbers)

        embed_outputs.extend(embed_output)
    
    return embed_outputs