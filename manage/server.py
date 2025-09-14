from fastapi import FastAPI
from pydantic import BaseModel, Field

import os
import time

import numpy as np

from pgvector.psycopg import register_vector
import psycopg


vector_dimension = int(os.environ['VECTOR_DIM'])
postgres_user = os.environ['POSTGRES_USER']
postgres_password = os.environ['POSTGRES_PASSWORD']
postgres_serviceorip = os.environ['POSTGRES_SERVICEORIP']
postgres_port = os.environ['POSTGRES_PORT']
postgres_db = os.environ['POSTGRES_DB']

db_resource = f'postgresql://{postgres_user}:{postgres_password}@{postgres_serviceorip}:{postgres_port}/{postgres_db}'
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
    embed: list[float] = Field(description="Array of int representing the embed vector")

@app.post('/add')
def add(item: AddRequestItem):
    embedding = np.array(item.embed)
    conn.execute('INSERT INTO chunks (content, embedding) VALUES (%s, %s)', (item.chunk_content, embedding,))

class FetchRequestItem(BaseModel):
    embed: list[float] = Field(description="Array of int representing the embed vector")

@app.post('/fetch')
def fetch(item: FetchRequestItem):
    embedding = np.array(item.embed)
    result = conn.execute('SELECT id, content FROM chunks ORDER BY embedding <-> %s LIMIT 5', (embedding,)).fetchall()
    return [{'id': row[0], 'text': row[1]} for row in result]
