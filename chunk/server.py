from fastapi import FastAPI

import os

from pydantic import BaseModel, Field
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


class ChunkRequestItem(BaseModel):
    name: str = Field(description="String name of the document/group associated with the text")
    text: str = Field(description="String text to chunk")

@app.post("/")
async def chunk(item: ChunkRequestItem):

    chunks:list[str] = chunker(item.text, overlap=0.5)
    return list(map(lambda text: 'part of ' + item.name + ': ' + text, chunks))