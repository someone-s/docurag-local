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

def database_create_if_not_exist():
    conn.execute((
        f'CREATE TABLE IF NOT EXISTS machine_categories ('
            f'machine_category text PRIMARY KEY'
        f')'
    ))
    conn.execute((
        f'CREATE TABLE IF NOT EXISTS machines ('
            f'machine_id bigserial PRIMARY KEY,'
            f'machine_make text,'
            f'machine_name text,'
            f'machine_category text REFERENCES machine_categories (machine_category),'
            f'machine_model text'
        f')'
    ))
    conn.execute((
        f'CREATE TABLE IF NOT EXISTS document_categories ('
            f'document_category text PRIMARY KEY'
        f')'
    ))
    conn.execute((
        f'CREATE TABLE IF NOT EXISTS documents ('
            f'document_id bigserial PRIMARY KEY,'
            f'document_category text REFERENCES document_categories (document_category),'
            f'document_data bytea,'
            f'machine_reference bigint REFERENCES machines (machine_id)'
        f')'
    ))
    conn.execute((
        f'CREATE TABLE IF NOT EXISTS chunks ('
            f'chunks_id bigserial PRIMARY KEY,'
            f'document_reference bigint REFERENCES documents (document_id),'
            f'section_name text,'
            f'section_text text,'
            f'section_start integer,'
            f'section_end integer,'
            f'segment_embed vector({vector_dimension})'
        f')'
    ))
            
def database_delete():
    conn.execute('DROP TABLE IF EXISTS chunks')
    conn.execute('DROP TABLE IF EXISTS documents')
    conn.execute('DROP TABLE IF EXISTS document_categories')
    conn.execute('DROP TABLE IF EXISTS machines')
    conn.execute('DROP TABLE IF EXISTS machine_categories')

def database_reset():
    database_delete()
    database_create_if_not_exist()


def database_machine_category_add(machine_category: str):
    database_create_if_not_exist()

    conn.execute((
        f'INSERT INTO machine_categories ('
            f'machine_category'
        f') VALUES ('
            '%s'
        f')'
    ), (machine_category,))

def database_machine_category_list() -> list[str]:
    database_create_if_not_exist()

    responses = conn.execute((
        f'SELECT machine_category '
        f'FROM machine_categories'
    )).fetchall()

    return [response[0] for response in responses]

def database_machine_category_delete(machine_category: str) -> bool:
    database_create_if_not_exist()

    usage_result = conn.execute((
        f'SELECT COUNT(*) FROM machines '
        f'WHERE machine_category = ''%s'
    ), (machine_category,)).fetchone()
    if usage_result[0] > 0:
        return False

    conn.execute((
        f'DELETE FROM machine_categories '
        f'WHERE machine_category = ''%s'
    ), (machine_category,))

    return True

def database_machine_category_exist(machine_category: str) -> bool:
    database_create_if_not_exist()

    count_result = conn.execute((
        f'SELECT COUNT(1) FROM machine_categories '
        f'WHERE machine_category = ''%s'
    ), (machine_category,)).fetchone()

    return True if count_result[0] == 1 else False



class Machine(BaseModel):
    make: Annotated[str, Field(description="String common name of machine")]
    name: Annotated[str, Field(description="String manufacturer of machine")]
    category: Annotated[str, Field(description="String category of machine")]
    model: Annotated[str, Field(description="String model serial of machine")]

def database_machine_add(machine: Machine) -> int|None:
    database_create_if_not_exist()

    if not database_machine_category_exist(machine.category):
        return None

    cursor = conn.execute((
        f'INSERT INTO machines ('
            f'machine_make,'
            f'machine_name,'
            f'machine_category,'
            f'machine_model'
        f') VALUES ('
            '%s,'
            '%s,'
            '%s,'
            '%s'
        f') RETURNING machine_id'
    ), (
        machine.make,
        machine.name,
        machine.category,
        machine.model,
    ))
    machine_id = cursor.fetchone()[0]
    return machine_id

def database_machine_list() -> list[int]:
    database_create_if_not_exist()

    responses = conn.execute((
        f'SELECT machine_id '
        f'FROM machines'
    )).fetchall()

    return [response[0] for response in responses]

def database_machine_fetch(machine_id: int) -> Machine|None:
    database_create_if_not_exist()

    response = conn.execute((
        f'SELECT '
            f'machine_make,' #0
            f'machine_name,' #1
            f'machine_category,' #2
            f'machine_model ' #3
        f'FROM machines '
        f'WHERE machine_id = ''%s'
    ), (machine_id,)).fetchone()

    if response == None:
        return None
    else:
        return Machine(
            make=response[0],
            name=response[1],
            category=response[2],
            model=response[3]
        )

def database_machine_delete(machine_id: int):
    database_create_if_not_exist()

    conn.execute((
        f'DELETE FROM machines '
        f'WHERE machine_id = ''%s'
    ), (machine_id,))

def database_machine_exist(machine_id: int) -> bool:
    database_create_if_not_exist()

    count_result = conn.execute((
        f'SELECT COUNT(1) FROM machines '
        f'WHERE machine_id = ''%s'
    ), (machine_id,)).fetchone()

    return True if count_result[0] == 1 else False
    

def database_document_category_add(document_category: str):
    database_create_if_not_exist()

    conn.execute((
        f'INSERT INTO document_categories ('
            f'document_category'
        f') VALUES ('
            '%s'
        f')'
    ), (document_category,))

def database_document_category_list() -> list[str]:
    database_create_if_not_exist()

    responses = conn.execute((
        f'SELECT document_category '
        f'FROM document_categories'
    )).fetchall()

    return [response[0] for response in responses]

def database_document_category_delete(document_category: str) -> bool:
    database_create_if_not_exist()

    usage_result = conn.execute((
        f'SELECT COUNT(*) FROM documents '
        f'WHERE document_category = ''%s'
    ), (document_category,)).fetchone()
    if usage_result[0] > 0:
        return False
    
    conn.execute((
        f'DELETE FROM document_categories '
        f'WHERE document_category = ''%s'
    ), (document_category,))

    return True

def database_document_category_exist(document_category: str) -> bool:
    database_create_if_not_exist()

    count_result = conn.execute((
        f'SELECT COUNT(1) FROM document_categories '
        f'WHERE document_category = ''%s'
    ), (document_category,)).fetchone()

    return True if count_result[0] == 1 else False



class Segment(BaseModel):
    embed: Annotated[list[float], Field(description="Fixed length array of int representing the embed vector, length of array is set based on model")]

class Section(BaseModel):
    name: Annotated[str, Field(description="String section title or topic")]
    text: Annotated[str, Field(description="String section text")]
    start: Annotated[int, Field(description="Int page where section begin")]
    end: Annotated[int, Field(description="Int page where section end")]
    segments: Annotated[list[Segment], Field(description="One or more segment (each containing vector) representing this section")]

class Document(BaseModel):
    category: Annotated[str, Field(description="String category of document")]
    data: Annotated[bytes, Field(description="Bytes of the source pdf")]

def database_document_add(machine_id: int, document: Document, sections: list[Section]) -> bool:
    database_create_if_not_exist()

    if not database_document_category_exist(document.category):
        return False

    cursor = conn.execute((
        f'INSERT INTO documents ('
            f'document_category,'
            f'document_data,'
            f'machine_reference'
        f') VALUES ('
            '%s,'
            '%s,'
            '%s'
        f') RETURNING document_id'
    ), (
        document.category, 
        document.data,
        machine_id,
    ))
    document_id = cursor.fetchone()[0]

    for section in sections:
        for segment in section.segments:
            conn.execute((
                f'INSERT INTO chunks ('
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
                    '%s'
                f')'
            ), (
                document_id,
                section.name,
                section.text,
                section.start,
                section.end,
                np.array(segment.embed),
            ))

    return True


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

def database_document_query(request: FetchEmbedRequest) -> list[FetchEmbedResponse]:
    database_create_if_not_exist()

    filters: list[str] = []
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
        filter_query = f'WHERE {" AND ".join(filters)}'
    
    embed_results = conn.execute((
        f'SELECT '
            f'seld.machine_make,' #0
            f'seld.machine_name,' #1
            f'seld.machine_category,' #2
            f'seld.machine_model,' #3
            f'seld.document_id,' #4
            f'c.section_name,' #5
            f'c.section_text,' #6
            f'c.section_start,' #7
            f'c.section_end ' #8
        f'FROM chunks c '
        f'INNER JOIN ('
            f'SELECT '
                f'selm.machine_make,'
                f'selm.machine_name,'
                f'selm.machine_category,'
                f'selm.machine_model,'
                f'd.document_id '
            f'FROM documents d '
            f'INNER JOIN ('
                f'SELECT '
                    f'machine_id,'
                    f'machine_make,'
                    f'machine_name,'
                    f'machine_category,'
                    f'machine_model '
                f'FROM machines '
                f'{filter_query}'
            f') selm '
            f'ON selm.machine_id = d.machine_reference'
        f') seld '
        f'ON seld.document_id = c.document_reference '
        f'ORDER BY segment_embed <-> ''%s '
        f'LIMIT 3'
    ), (np.array(request.query_embed),)).fetchall()

    responses: list[FetchEmbedResponse] = []

    for embed_result in embed_results:

        document_result = conn.execute((
            f'SELECT '
                f'document_id,' #0
                f'document_category ' #1
            f'FROM documents '
            f'WHERE document_id = ''%s'' '
            f'LIMIT 1'
        ), (embed_result[4],)).fetchone()

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


def database_document_list(start_id: int = 0, limit: int|None = None) -> list[int]:
    database_create_if_not_exist()

    limiter = f'LIMIT {limit}' if limit != None else '' 

    document_results = conn.execute((
        f'SELECT '
            f'document_id ' #0
        f'FROM documents '
        f'WHERE document_id >= ''%s'' '
        f'{limiter}'
    ), (start_id,)).fetchall()

    return [document_result[0] for document_result in document_results] # list of document ids

def database_document_list_by_machine(machine_id: int) -> list[int]:
    database_create_if_not_exist()

    document_results = conn.execute((
        f'SELECT '
            f'document_id ' #0
        f'FROM documents '
        f'WHERE machine_reference = ''%s'
    ), (machine_id,)).fetchall()

    return [document_result[0] for document_result in document_results] # list of document ids

def database_document_count() -> int:
    database_create_if_not_exist()

    document_result = conn.execute((
        f'SELECT '
            f'COUNT(*) ' #0
        f'FROM documents'
    )).fetchone()

    return document_result[0]

def database_document_fetch(document_id: int) -> bytes|None:
    database_create_if_not_exist()

    document_result = conn.execute((
        f'SELECT '
            f'document_data ' #0
        f'FROM documents '
        f'WHERE document_id = ''%s'' '
        f'LIMIT 1'
    ), (document_id,)).fetchone()
    
    if document_result == None:
        return None
    
    return document_result[0]

def database_document_delete(document_id: int):
    database_create_if_not_exist()

    conn.execute((
        f'DELETE FROM chunks '
        f'WHERE document_reference = ''%s'
    ), (document_id,))

    conn.execute((
        f'DELETE FROM documents '
        f'WHERE document_id = ''%s'
    ), (document_id,))
