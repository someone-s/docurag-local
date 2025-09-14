from typing import Annotated
from fastapi import FastAPI, File

import os

import semchunk
from transformers import AutoTokenizer, PreTrainedTokenizer

app = FastAPI()

model = os.environ['MODEL']
max_size = int(os.environ['MAX_SIZE'])

tokenizer: PreTrainedTokenizer
if os.environ['PAD_LEFT'] == 'true':
    tokenizer = AutoTokenizer.from_pretrained(model, padding_side='left')
else:
    tokenizer = AutoTokenizer.from_pretrained(model)

chunker = semchunk.chunkerify(tokenizer, max_size - 50)

@app.post("/")
async def chunk(\
    name: Annotated[str, File(description="String name of the document/group associated with the text")], \
    text: Annotated[str, File(description="String text to chunk")]):

    chunks:list[str] = chunker(text, overlap=0.5)
    return list(map(lambda text: 'part of ' + name + ': ' + text, chunks))