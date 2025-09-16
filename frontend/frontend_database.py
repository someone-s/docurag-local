from typing import Annotated
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

def create_if_not_exist_database():
    conn.execute((
        f'CREATE TABLE IF NOT EXISTS documents ('
            f'document_id bigserial PRIMARY KEY,'
            f'document_category text,'
            f'document_data bytea'
        f')'
    ))
    conn.execute((
        f'CREATE TABLE IF NOT EXISTS chunks ('
            f'chunks_id bigserial PRIMARY KEY,'
            f'machine_make text,'
            f'machine_name text,'
            f'machine_category text,'
            f'machine_model text,'
            f'document_reference bigint REFERENCES documents (document_id),'
            f'section_name text,'
            f'section_text text,'
            f'section_start integer,'
            f'section_end integer,'
            f'segment_embed vector({vector_dimension})'
        f')'
    ))
            
def delete_database():
    conn.execute('DROP TABLE IF EXISTS chunks')
    conn.execute('DROP TABLE IF EXISTS documents')

def wipe_database():
    delete_database()
    create_if_not_exist_database()


class Machine(BaseModel):
    make: Annotated[str, Field(description="String common name of machine")]
    name: Annotated[str, Field(description="String manufacturer of machine")]
    category: Annotated[str, Field(description="String category of machine")]
    model: Annotated[str, Field(description="String model serial of machine")]

class AddSegment(BaseModel):
    embed: Annotated[list[float], Field(description="Fixed length array of int representing the embed vector, length of array is set based on model")]

class AddSection(BaseModel):
    name: Annotated[str, Field(description="String section title or topic")]
    text: Annotated[str, Field(description="String section text")]
    start: Annotated[int, Field(description="Int page where section begin")]
    end: Annotated[int, Field(description="Int page where section end")]
    segments: Annotated[list[AddSegment], Field(description="One or more segment (each containing vector) representing this section")]

class AddDocument(BaseModel):
    category: Annotated[str, Field(description="String category of document")]
    data: Annotated[bytes, Field(description="Bytes of the source pdf")]
    machine: Annotated[Machine, Field(description="The machine associated with the document")]
    sections: Annotated[list[AddSection], Field(description="One or more section in the document")]

def add_document_with_embed_to_database(document: AddDocument):
    create_if_not_exist_database()

    machine = document.machine
    cursor = conn.execute((
        f'INSERT INTO documents ('
            f'document_category,'
            f'document_data'
        f') VALUES ('
            '%s,'
            '%s'
        f') RETURNING document_id'
    ), (document.category, document.data,))
    document_id = cursor.fetchone()[0]

    for section in document.sections:
        for segment in section.segments:
            conn.execute((
                f'INSERT INTO chunks ('
                    f'machine_make,'
                    f'machine_name,'
                    f'machine_category,'
                    f'machine_model,'
                    f'document_reference,'
                    f'section_name,'
                    f'section_text,'
                    f'section_start,'
                    f'section_end,'
                    f'segment_embed'
                f') VALUES ('
                    '%s,'
                    '%s,'
                    '%s,'
                    '%s,'
                    '%s,'
                    '%s,'
                    '%s,'
                    '%s,'
                    '%s,'
                    '%s'
                f')'
            ), (
                machine.make,
                machine.name,
                machine.category,
                machine.model,
                document_id,
                section.name,
                section.text,
                section.start,
                section.end,
                np.array(segment.embed),
            ))


class FetchEmbedRequest(BaseModel):
    query_embed: Annotated[list[float], Field(description="Array of int representing the embed vector")]
    machine_make: Annotated[str|None, Field(description="Optional string common name of machine")]
    machine_name: Annotated[str|None, Field(description="Optional string manufacturer of machine")]
    machine_category: Annotated[str|None, Field(description="Optional string category of machine")]
    machine_model: Annotated[str|None, Field(description="Optional model serial of machine")]

class FetchEmbedSection(BaseModel):
    name: Annotated[str, Field(description="String section title or topic")]
    text: Annotated[str, Field(description="String section text")]
    start: Annotated[int, Field(description="Int page where section begin")]
    end: Annotated[int, Field(description="Int page where section end")]

class FetchEmbedDocument(BaseModel):
    id: Annotated[int, Field(description="Int id of document")]
    category: Annotated[str, Field(description="String category of document")]

class FetchEmbedResponse(BaseModel):
    machine: Annotated[Machine, Field(description="The machine associated with the document")]
    document: Annotated[FetchEmbedDocument, Field(description="Document of the retrieved section")]
    section: Annotated[FetchEmbedSection, Field(description="The section in the document")]

def fetch_embed_from_database(request: FetchEmbedRequest) -> list[FetchEmbedResponse]:
    create_if_not_exist_database()

    filters = []
    if request.machine_make != None:
        filters.append(f'machine_make LIKE \'{request.machine_make}\'')
    if request.machine_name != None:
        filters.append(f'machine_name LIKE \'{request.machine_name}\'')
    if request.machine_category != None:
        filters.append(f'machine_category LIKE \'{request.machine_category}\'')
    if request.machine_model != None:
        filters.append(f'machine_model LIKE \'{request.machine_model}\'')

    filter_query: str = ''
    if len(filters) > 0: 
        filter_query = f'WHERE {' AND '.join(filters)}'

    embed_results = conn.execute((
        f'SELECT '
            f'machine_make,' #0
            f'machine_name,' #1
            f'machine_category,' #2
            f'machine_model,' #3
            f'document_reference,' #4
            f'section_name,' #5
            f'section_text,' #6
            f'section_start,' #7
            f'section_end ' #8
        f'FROM chunks '
        f'{filter_query} '
        f'ORDER BY segment_embed <-> '
        '%s '
        f'LIMIT 3'
    ), (np.array(request.query_embed),)).fetchall()

    responses: list[FetchEmbedResponse] = []

    for embed_result in embed_results:

        document_result = conn.execute((
            f'SELECT '
                f'document_id,' #0
                f'document_category ' #1
            f'FROM documents '
            f'WHERE document_id = {embed_result[4]} '
            f'LIMIT 1'
        )).fetchone()

        responses.append(FetchEmbedResponse(
            machine=Machine(
                make=embed_result[0],
                name=embed_result[1],
                category=embed_result[2],
                model=embed_result[3]
            ),
            document=FetchEmbedDocument(
                id=document_result[0],
                category=document_result[1],
            ),
            section=FetchEmbedSection(
                name=embed_result[5],
                text=embed_result[6],
                start=embed_result[7],
                end=embed_result[8]
            )
        ))
    
    return responses


def fetch_document_from_database(document_id: int) -> bytes|None:
    create_if_not_exist_database()

    document_result = conn.execute((
        f'SELECT '
            f'document_data ' #0
        f'FROM documents '
        f'WHERE document_id = {document_id} '
        f'LIMIT 1'
    )).fetchone()
    
    if document_result == None:
        return None
    
    return document_result[0]

def delete_document_and_embed_from_database(document_id: int):
    create_if_not_exist_database()

    conn.execute((
        f'DELETE FROM chunks '
        f'WHERE document_reference = {document_id}'
    ))

    conn.execute((
        f'DELETE FROM documents '
        f'WHERE document_id = {document_id}'
    ))