import json
from typing import Awaitable, Callable

from openai import AsyncOpenAI
from openai.types.responses import ResponseInProgressEvent, ResponseTextDoneEvent
import base64

from embedconnection import get_embed
from chunkconnection import get_chunk
from databaseconnection import add_document_with_embed_to_database, AddDocument, AddSection, AddSegment, Machine, fetch_machine_category_from_database, fetch_machine_make_from_database

def get_schema(
        known_make: list[str], 
        known_machine_category: list[str], 
        known_document_category: list[str]):
    extract_schema: dict[str,object] = {
        "type": "object",
        "properties": {
            "document": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The type and nature of the document, choose other if type does not match any other options",
                        "enum": known_document_category
                    }
                },
                "required": [
                    "category"
                ],
                "additionalProperties": False
            },
            "machine": {
                "type": "object",
                "properties": {

                    "make": {
                        "type": [
                            "string",
                            "null"
                        ],
                        "description": "The manufacturer of the machine, if not match any provided brand names, set this field to null and set the newMake field with the new make",
                        "enum": known_make
                    },
                    "newMake": {
                        "type": "string",
                        "description": "The name of a manufacturer in snake_case if the document does not mostly match the provided options in the make field, leave empty otherwise"
                    },

                    "name": {
                        "type": "string",
                        "description": "The common human readable name of the machine"
                    },

                    "category": {
                        "type": [
                            "string",
                            "null"
                        ],
                        "description": "The type of machine this document is for, if not match any provided category, set this field to null and set the newCategory field with the new type",
                        "enum": known_machine_category
                    },
                    "newCategory": {
                        "type": "string",
                        "description": "The category of the machine in snake_case if the document does not mostly match the provided options in the category field, leave empty otherwise"
                    },
                    
                    "model": {
                        "type": "string",
                        "description": "The serial number of the machine referenced in the document"
                    }
                },
                "required": [
                    "make",
                    "newMake",
                    "name",
                    "category",
                    "newCategory",
                    "model"
                ],
                "additionalProperties": False
            },
            "sections": {
            "type": "array",
            "description": "A detailed list of all sections presented in the document",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the section"
                    },
                    "text": {
                        "type": "string",
                        "description": "A verbose extract of the text from the document, combined with text desciption of images in the section, reformating is allowed"
                    },
                    "startPage": {
                        "type": "integer",
                        "description": "The first page where the section begins, ignoring appearance in any index page"
                    },
                    "endPage": {
                        "type": "integer",
                        "description": "The last page where the section appears, ignoring appearance in any index page"
                    }
                },
                "required": [
                    "name",
                    "text",
                    "startPage",
                    "endPage"
                ],
                "additionalProperties": False
            }
        }
        },
        "required": [
            "document",
            "machine",
            "sections"
        ],
        "additionalProperties": False
    }
    
    return extract_schema


async def extract_information(
        client: AsyncOpenAI,
        file_binary: bytes,
        on_progress: Callable[[], Awaitable[None]]) -> dict[str,object]|None:
    extract_input = base64.b64encode(file_binary).decode('ascii')

    known_make = fetch_machine_make_from_database()

    known_machine_category = fetch_machine_category_from_database()

    known_document_category = [
        "user_manual",
        "warranty_information",
        "other"
    ]

    extract_schema = get_schema(known_make, known_machine_category, known_document_category)

    output: str|None = None

    stream = await client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Given the document uploaded, populate the response json based on the description on each fields in the schema.\n\nNo further instructions or clarification will be provided."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "filename": "156817671_UserManual_0c696b41-4e62-4e21-a7ee-23a8b1a14aa4.pdf",
                        "file_data": f"data:application/pdf;base64,{extract_input}"
                    }
                ]
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "manual_extract",
                "strict": True,
                "schema": extract_schema
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
        ],
        stream=True
    )
    async for event in stream:
        if isinstance(event, ResponseInProgressEvent):
            await on_progress()
            
        if isinstance(event, ResponseTextDoneEvent):
            done_event: ResponseTextDoneEvent = event
            output = done_event.text
    
    if output == None:
        return None
    else:
        return json.loads(output)


def store_information(file_binary: bytes, extract_data: dict[str]): # type: ignore
    document_info = extract_data['document']
    document_category = document_info['category']

    machine_info = extract_data['machine']

    machine_make: str|None = machine_info['make']
    if machine_make == None:
        machine_make = machine_info['newMake']

    machine_name: str = machine_info['name']

    machine_category: str|None = machine_info['category']
    if machine_category == None:
        machine_category = machine_info['newCategory']

    machine_model: str = machine_info['model']

    addSections: list[AddSection] = []
    sections = extract_data['sections']
    for section in sections:
        section_text: str = section['text']

        addSegments: list[AddSegment] = []
        chunks = get_chunk(section_text)
        embeds = get_embed(chunks)
        for embed in embeds:
            addSegments.append(AddSegment(
                embed=embed
            ))
        
        addSections.append(AddSection(
            name=section['name'],
            text=section['text'],
            start=section['startPage'],
            end=section['endPage'],
            segments=addSegments
        ))


    add_document_with_embed_to_database(AddDocument(
        category=document_category,
        data=file_binary,
        machine=Machine(
            make=machine_make,
            name=machine_name,
            category=machine_category,
            model=machine_model
        ),
        sections=addSections
    ))