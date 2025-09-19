from typing import Any, Awaitable, Callable

from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent, ResponseTextDoneEvent, ResponseInputParam, ResponseCreatedEvent, ResponseOutputMessage, ResponseReasoningItem, ResponseOutputItemDoneEvent, ResponseFunctionToolCall

from pydantic import BaseModel

from embedconnection import get_embed
from chunkconnection import get_chunk
from databaseconnection import FetchEmbedRequest, database_document_query

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

class MachineState(BaseModel):
    make:str|None = None
    name:str|None = None
    category:str|None = None
    model:str|None = None

class ConverseState(BaseModel):
    query_text: str|None = None
    machine_state: MachineState = MachineState()
    relevant_texts: list[RelevantText] = []

async def converse(
        client: AsyncOpenAI,
        fetch_input_hook: Callable[[], Awaitable[dict[str, str]]],
        send_output_hook: Callable[[Any], Awaitable[None]]
):
    
    conversation_log = create_conversation_log()

    converse_state = ConverseState()

    while True:
        shouldContinue = await receive_input(fetch_input_hook, converse_state)
        if not shouldContinue:
            break

        retrieved_relevant_texts = await retrive_relevant(converse_state)
        for relevant_text in retrieved_relevant_texts:

            if relevant_text in converse_state.relevant_texts:
                continue

            converse_state.relevant_texts.append(relevant_text)

            await send_output_hook({
                'type': 'document',
                'document_id': relevant_text.document_id,
                'machine_make': relevant_text.machine_make,
                'machine_name': relevant_text.machine_name,
                'machine_category': relevant_text.machine_category,
                'machine_model': relevant_text.machine_model,
                'document_category': relevant_text.document_category,
                'section_start': relevant_text.section_start,
                'section_end': relevant_text.section_end
            })

        append_conversation_fact(conversation_log, retrieved_relevant_texts)
        append_conversation_query(conversation_log, converse_state.query_text)

        await generate_inference(client, conversation_log, send_output_hook)

    await send_output_hook({'type': 'log', 'message': "stream ended"})


async def receive_input(
        fetch_input_hook: Callable[[], Awaitable[dict[str, str]]],
        converse_state: ConverseState
) -> bool:
    
    has_new_info: bool = False
    new_info = ConverseState()

    while True:
        item = await fetch_input_hook()
        item_type = item['type']
        match item_type:

            case 'data':
                parameter = item['parameter']
                value = item['value']
                match parameter:
                    case 'machine_make':
                        has_new_info = True
                        new_info.machine_state.make = value
                    case 'machine_name':
                        has_new_info = True
                        new_info.machine_state.name = value
                    case 'machine_category':
                        has_new_info = True
                        new_info.machine_state.category = value
                    case 'machine_model':
                        has_new_info = True
                        new_info.machine_state.model = value
                    case _:
                        raise Exception('unkown parameter type')
                    

            case 'command':
                action = item['action']
                match action:
                    case 'generate':
                        converse_state.query_text = item['query']

                        if has_new_info:
                            converse_state.machine_state = new_info.machine_state

                        return True
                    case 'exit':
                        return False
                    case _:
                        raise Exception('unkown action type')
                    
            case _:
                raise Exception('unkown item type')

async def retrive_relevant(
        converse_state: ConverseState
) -> list[RelevantText]:
    if converse_state.query_text == None:
        raise Exception("Query text should not be None")

    relevant_texts: list[RelevantText] = []
    query_chunks = get_chunk(converse_state.query_text)
    query_embeds = get_embed(query_chunks)
    for query_embed in query_embeds:
        responses = database_document_query(FetchEmbedRequest(
            query_embed=query_embed,
            machine_make=converse_state.machine_state.make,
            machine_name=converse_state.machine_state.name,
            machine_category=converse_state.machine_state.category,
            machine_model=converse_state.machine_state.model
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


def create_conversation_log() -> ResponseInputParam:

    input_entries: ResponseInputParam = []
    input_entries.append({
        "role": "developer",
        "content": [
            {
                "type": "input_text",
                "text": f"Answer the given Question using only provided Facts."
            }
        ]
    })

    return input_entries

def append_conversation_fact(
        conversation_log: ResponseInputParam,
        relevant_texts: list[RelevantText]
):
    
    fact_texts = [(
        f'Provided is an excerpt from a {relevant_text.document_category} '
        f'for {relevant_text.machine_name} made by {relevant_text.machine_make} (model serial: {relevant_text.machine_model}).\n'
        f'\n'
        f'Use the following fields for to reference this excerpt in tool calling.'
        f'documentId: {relevant_text.document_id}\n'
        f'startPage: {relevant_text.section_start}\n'
        f'endPage: {relevant_text.section_end}\n'
        f'\n'
        f'Excerpt below:\n'
        f'{relevant_text.section_text}\n'
    ) for relevant_text in relevant_texts]

    for fact_text in fact_texts:
        conversation_log.append({
            "role": "developer",
            "content": [
                {
                    "type": "input_text",
                    "text": fact_text
                }
            ]
        })

def append_conversation_query(
        conversation_log: ResponseInputParam,
        query_text: str
):
    conversation_log.append({
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": query_text
            }
        ]
    })



response_schema: dict[str,object] = {
    "type": "object",
    "properties": {
        "segments": {
            "type": "array",
            "description": "A list of segments forming a cohesive response",
            "items": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "A sentence part of the whole response, referencing a fact. Remember use \n to format response"
                    },
                    "documentId": {
                        "type": "integer",
                        "description": "The documentId of the fact that this segment refers to"
                    },
                    "startPage": {
                        "type": "integer",
                        "description": "The startPage of the fact this segment refers to"
                    },
                    "endPage": {
                        "type": "integer",
                        "description": "The endPage of the fact this segment refers to"
                    }
                },
                "required": [
                    "text",
                    "documentId",
                    "startPage",
                    "endPage"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": [
        "segments"
    ],
    "additionalProperties": False
}

async def generate_inference(
        client: AsyncOpenAI, 
        conversation_log: ResponseInputParam,
        send_output_hook: Callable[[Any], Awaitable[None]]
):


    stream = await client.responses.create(
        model="gpt-5-nano",
        input=conversation_log,
        text={
            "format": {
                "type": "json_schema",
                "name": "render_output",
                "strict": True,
                "schema": response_schema
            },
            "verbosity": "medium"
        },
        reasoning={
            "effort": "medium"
        },
        store=True,
        include=['reasoning.encrypted_content',],
        stream=True
    )
    async for event in stream:
        if isinstance(event, ResponseTextDeltaEvent):
            delta_event: ResponseTextDeltaEvent = event
            await send_output_hook({'type': 'generate', 'delta': delta_event.delta})
            
        if isinstance(event, ResponseTextDoneEvent):
            done_event: ResponseTextDoneEvent = event
            await send_output_hook({'type': 'complete', 'text': done_event.text})

        if isinstance(event, ResponseCreatedEvent):
            created_event: ResponseCreatedEvent = event

            for output in created_event.response.output:
                if isinstance(output, ResponseOutputMessage):
                    message_output: ResponseOutputMessage = output
                    conversation_log.append(message_output)

                if isinstance(output, ResponseReasoningItem):
                    reasoning_output: ResponseReasoningItem = output
                    conversation_log.append(reasoning_output)
