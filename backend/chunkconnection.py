
import os

import semchunk
from transformers import AutoTokenizer, PreTrainedTokenizer

model = os.environ['MODEL_ID']
max_size = int(os.environ['MAX_SIZE'])

tokenizer: PreTrainedTokenizer
if os.environ['PAD_LEFT'] == 'true':
    tokenizer = AutoTokenizer.from_pretrained(model, padding_side='left')
else:
    tokenizer = AutoTokenizer.from_pretrained(model)

default_chunker = semchunk.chunkerify(tokenizer, max_size)

def get_chunk(pretense: str|None, text: str) -> list[str]:

    if pretense == None:
        chunks:list[str] = default_chunker(text, overlap=0.2)
        return chunks
    else:
        pretense_token_count = len(tokenizer.tokenize(pretense))
        offset_chunker = semchunk.chunkerify(tokenizer, max_size - pretense_token_count - 10) # 10 extra token for space between and margin of error
        chunks:list[str] = offset_chunker(text, overlap=0.2)
        return list(map(lambda text: f"{pretense} {text}", chunks))