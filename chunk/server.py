from typing import Annotated
from fastapi import FastAPI, File

import semchunk
from transformers import AutoTokenizer, PreTrainedTokenizer

app = FastAPI()

tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-0.6B', padding_side='left')
# QWEN3 max size is 8192 but we'll not use the whole so that we can prepend file name
chunker = semchunk.chunkerify(tokenizer, 4096)

@app.post("/")
async def chunk(\
    name: Annotated[str, File(description="String name of the document/group associated with the text")], \
    text: Annotated[str, File(description="String text to chunk")]):

    chunks:list[str] = chunker(text, overlap=0.5)
    return list(map(lambda text: 'part of ' + name + ': ' + text, chunks))