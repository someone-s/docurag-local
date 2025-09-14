from typing import Annotated
from fastapi import FastAPI, File, UploadFile

import os
import time

import numpy as np

from pgvector.psycopg import register_vector
import psycopg

vector_dimension = int(os.environ['VECTOR_DIM'])
db_resource = f'postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_SERVICEORIP']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}'
print(db_resource)

conn = None
while conn == None:
    try:
        conn = psycopg.connect(db_resource, autocommit=True)
    except:
        conn = None
        print('db not ready, retry in 1 second')
        time.sleep(1)

conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
register_vector(conn)

app = FastAPI()

@app.post('/wipe')
def wipe():
    conn.execute('DROP TABLE IF EXISTS chunks')
    conn.execute(f'CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector({vector_dimension}))')

@app.post('/add')
def add(\
        chunk_content: Annotated[str, File(description="String representing the chunk text")],
        embed: Annotated[list[int], File(description="Array of int representing the embed vector")]):
    embedding = np.array(embed)
    conn.execute('INSERT INTO chunks (content, embedding) VALUES (%s, %s)', (chunk_content, embedding,))

@app.post('/fetch')
def fetch(embed: Annotated[list[int], File(description="Array of int representing the embed vector")]):
    embedding = np.array(embed)
    result = conn.execute('SELECT content FROM chunks ORDER BY embedding <-> %s LIMIT 5', (embedding,)).fetchall()
    return [row[0] for row in result]
