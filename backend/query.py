from typing import Awaitable, Callable

from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent, ResponseTextDoneEvent

from pydantic import BaseModel

from embed import get_embed
from chunk import get_chunk
from database import fetch_embed_from_database, FetchEmbedRequest

class RelevantText(BaseModel):
    document_id: int
    machine_make: str
    machine_name: str
    machine_category: str
    machine_model: str
    document_category: str
    section_text: str
    section_start: int
    section_end: int

async def retrive_relevant(
        machine_make: str|None, 
        machine_name: str|None, 
        machine_category: str|None, 
        machine_model: str|None, 
        query_text: str,
        ) -> list[RelevantText]:
    relevant_texts: list[RelevantText] = []
    query_chunks = get_chunk(query_text)
    query_embeds = get_embed(query_chunks)
    for query_embed in query_embeds:
        responses = fetch_embed_from_database(FetchEmbedRequest(
            query_embed=query_embed,
            machine_make=machine_make,
            machine_name=machine_name,
            machine_category=machine_category,
            machine_model=machine_model
        ))
        
        for response in responses:
            machine = response.machine
            document = response.document
            section = response.section

            relevant_texts.append(RelevantText(
                document_id=document.id,
                machine_make=machine.make,
                machine_name=machine.name,
                machine_category=machine.category,
                machine_model=machine.model,
                document_category=document.category,
                section_text=section.text,
                section_start=section.start,
                section_end=section.end
            ))
            
    return relevant_texts

async def receive_parameters(fetch_input_hook: Callable[[], Awaitable[str]]) -> tuple[str|None, str|None, str|None, str|None, str]:
    machine_make:str|None = None
    machine_name:str|None = None
    machine_category:str|None = None
    machine_model:str|None = None

    query_text: str
    while True:
        item = await fetch_input_hook()
        item_type = item['type']
        match item_type:
            case 'data':
                parameter = item['parameter']
                value = item['value']
                match parameter:
                    case 'machine_make':
                        machine_make = value
                    case 'machine_name':
                        machine_name = value
                    case 'machine_category':
                        machine_category = value
                    case 'machine_model':
                        machine_model = value
            case 'command':
                action = item['action']
                match action:
                    case 'begin':
                        query_text = item['query']
                        break
    return machine_make,machine_name,machine_category,machine_model,query_text

async def generate_inference(
        client: AsyncOpenAI, 
        query_text: str, 
        relevant_texts: list[RelevantText], 
        on_delta: Callable[[str], Awaitable[None]], 
        on_complete: Callable[[str], Awaitable[None]]):
    fact_texts = [(
        f'Treat this as a fact:\n'
        f'Source Document Id: {relevant_text.document_id}\n'
        f'Source Document Type: {relevant_text.document_category}\n'
        f'Source Document Pages: From page {relevant_text.section_start} to page {relevant_text.section_end}\n'
        f'Relevant machine: {relevant_text.machine_name} made by {relevant_text.machine_make} with model {relevant_text.machine_model}\n'
        f'Excerpt: {relevant_text.section_text}\n'
    ) for relevant_text in relevant_texts]

    input_entries: list[dict] = []
    input_entries.append({
        "role": "developer",
        "content": [
            {
            "type": "input_text",
            "text": "Answer the given Question using only provided Facts."
            }
        ]
    })
    for fact_text in fact_texts:
        input_entries.append({
            "role": "developer",
            "content": [
                {
                "type": "input_text",
                "text": fact_text
                }
            ]
        })
    input_entries.append({
        "role": "user",
        "content": [
            {
            "type": "input_text",
            "text": query_text
            }
        ]
    })


    stream = await client.responses.create(
        model="gpt-5-nano",
        input=input_entries,
        text={
            "format": {
            "type": "text"
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
            "web_search_call.action.sources"
        ],
        stream=True
    )
    async for event in stream:
        if isinstance(event, ResponseTextDeltaEvent):
            delta_event: ResponseTextDeltaEvent = event
            await on_delta(delta_event.delta)
            
        if isinstance(event, ResponseTextDoneEvent):
            done_event: ResponseTextDoneEvent = event
            await on_complete(done_event.text)
