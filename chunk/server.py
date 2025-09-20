from typing import Annotated
from fastapi import FastAPI

import os

from pydantic import BaseModel, Field
import semchunk
from transformers import AutoTokenizer, PreTrainedTokenizer

app = FastAPI()

model = os.environ['MODEL_ID']
max_size = int(os.environ['MAX_SIZE'])

tokenizer: PreTrainedTokenizer
if os.environ['PAD_LEFT'] == 'true':
    tokenizer = AutoTokenizer.from_pretrained(model, padding_side='left')
else:
    tokenizer = AutoTokenizer.from_pretrained(model)

default_chunker = semchunk.chunkerify(tokenizer, max_size)


class ChunkRequestItem(BaseModel):
    pretense: Annotated[str | None, Field(description="Optional string name of the document/group associated with the text")] = None
    text: Annotated[str, Field(description="String text to chunk")]

@app.post("/")
async def chunk(item: ChunkRequestItem):

    if item.pretense == None:
        chunks:list[str] = default_chunker(item.text, overlap=0.2)
        return chunks
    else:
        pretense_token_count = len(tokenizer.tokenize(item.pretense))
        offset_chunker = semchunk.chunkerify(tokenizer, max_size - pretense_token_count - 10) # 10 extra token for space between and margin of error
        chunks:list[str] = offset_chunker(item.text, overlap=0.2)
        return list(map(lambda text: f"{item.pretense} {text}", chunks))