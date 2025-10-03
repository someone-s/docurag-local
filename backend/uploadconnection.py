import json
from typing import Awaitable, Callable

from openai import AsyncOpenAI
from openai.types.responses import ResponseInProgressEvent, ResponseTextDoneEvent
import base64

from embedconnection import get_embed
from chunkconnection import get_chunk
from databaseconnection import database_document_add, Document, Section, Segment, database_machine_fetch_multiple 

extract_schema: dict[str,object] = {
    "type": "object",
    "properties": {
        "sections": {
        "type": "array",
        "description": "ALWAYS INCLUDE ALL PAGES FROM THE DOCUMENT! A detailed list of all sections presented in the document",
        "items": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the section"
                },
                "text": {
                    "type": "string",
                    "description": "ALWAYS FILL WITH TEXT FROM THE DOCUMENT! Extract word for word all sentences from the section; additionally, add text description of images in the section."
                },
                "startPage": {
                    "type": "integer",
                    "description": "The first page where the section begins, ignoring appearance in any index page. This is unrelated to the section number."
                },
                "endPage": {
                    "type": "integer",
                    "description": "The last page where the section appears, ignoring appearance in any index page. This is unrelated to the section number"
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
        "sections"
    ],
    "additionalProperties": False
}


async def extract_information(
        client: AsyncOpenAI,
        file_binary: bytes,
        on_progress: Callable[[], Awaitable[None]]
) -> dict[str,object]|None:
    extract_input = base64.b64encode(file_binary).decode('ascii')

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
                        "filename": "document.pdf",
                        "file_data": f"data:application/pdf;base64,{extract_input}"
                    }
                ]
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "response",
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

def store_document(
        machine_ids: list[int],
        document_category: str,
        file_binary: bytes, 
        extract_data: dict[str]
): # type: ignore
    
    machines = database_machine_fetch_multiple(machine_ids)
    reference = f"{document_category} for \n" + "\n".join([f"{machine.make} {machine.name} {machine.category} {machine.model}" for machine in machines]) + "\n"

    sections: list[Section] = []
    for section in extract_data['sections']:
        section_text: str = section['text']

        addSegments: list[Segment] = []
        chunks = get_chunk(reference, section_text)
        embeds = get_embed(chunks)
        for embed in embeds:
            addSegments.append(Segment(
                embed=embed
            ))
        
        sections.append(Section(
            name=section['name'],
            text=section['text'],
            start=section['startPage'],
            end=section['endPage'],
            segments=addSegments
        ))


    database_document_add(
        machine_ids=machine_ids,
        document=Document(
            category=document_category,
            data=file_binary,
        ),
        sections=sections
    )