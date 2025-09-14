from typing import Annotated
from fastapi import FastAPI, File, UploadFile

from io import BufferedIOBase, BytesIO

from fastapi.responses import PlainTextResponse
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

app = FastAPI()

def pdf2text(readIO: BufferedIOBase, writeIO: BytesIO):

    laparams = LAParams()
    codec: str = "utf-8"
    caching: bool = True
    password: str = ""

    rsrcmgr = PDFResourceManager(caching=caching)
    device = TextConverter(rsrcmgr, writeIO, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    for page in PDFPage.get_pages(
        readIO,
        password=password,
        caching=caching,
    ):
        interpreter.process_page(page)

@app.post("/", response_class=PlainTextResponse)
async def convert(file: Annotated[UploadFile, File(description="A PDF to convert to text")]):

    with BytesIO(await file.read()) as input_buffer:
        with BytesIO() as output_buffer:
            pdf2text(input_buffer, output_buffer)
            return output_buffer.getvalue()