from typing import Annotated
from fastapi import FastAPI, File

import semchunk
from transformers import AutoTokenizer, PreTrainedTokenizer

app = FastAPI()

# MXBAI max size is 512 but we'll not use the whole so that we can prepend file name
tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained('mixedbread-ai/mxbai-embed-large-v1')
chunker = semchunk.chunkerify(tokenizer, 512 - 50)

# # QWEN3 max size is 8192 but we'll not use the whole so that we can prepend file name
# tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-Embedding-0.6B', padding_side='left')
# chunker = semchunk.chunkerify(tokenizer, 8192 - 50)

@app.post("/")
async def chunk(\
    name: Annotated[str, File(description="String name of the document/group associated with the text")], \
    text: Annotated[str, File(description="String text to chunk")]):

    chunks:list[str] = chunker(text, overlap=0.5)
    return list(map(lambda text: 'part of ' + name + ': ' + text, chunks))