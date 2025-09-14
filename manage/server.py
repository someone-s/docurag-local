from typing import Annotated
from fastapi import FastAPI
from pydantic import BaseModel, Field

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
conn.execute(f'CREATE TABLE IF NOT EXISTS chunks (id bigserial PRIMARY KEY, content text, embedding vector({vector_dimension}))')

app = FastAPI()

@app.post('/wipe')
def wipe():
    conn.execute('DROP TABLE IF EXISTS chunks')
    conn.execute(f'CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector({vector_dimension}))')



class AddRequestItem(BaseModel):
    chunk_content: str = Field(description="String representing the chunk text")
    embed: list[int] = Field(description="Array of int representing the embed vector")

@app.post('/add')
def add(item: AddRequestItem):
    embedding = np.array(item.embed)
    conn.execute('INSERT INTO chunks (content, embedding) VALUES (%s, %s)', (item.chunk_content, embedding,))

class FetchRequestItem(BaseModel):
    embed: list[int] = Field(description="Array of int representing the embed vector")

@app.post('/fetch')
def fetch(item: FetchRequestItem):
    embedding = np.array(item.embed)
    result = conn.execute('SELECT content FROM chunks ORDER BY embedding <-> %s LIMIT 5', (embedding,)).fetchall()
    return [row[0] for row in result]
