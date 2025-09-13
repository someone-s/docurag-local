import sys

from http.server import BaseHTTPRequestHandler, HTTPServer

from io import BufferedIOBase, BytesIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

def convert(readIO: BufferedIOBase, writeIO: BytesIO):

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


class Handler(BaseHTTPRequestHandler):

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!
    

    def do_POST(self):
    # curl http://<ServerIP>/index.html
        if self.path == "/":

            # Respond with the file contents.
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            with BytesIO(self.rfile.read(int(self.headers['content-length']))) as input_buffer:
                with BytesIO() as  outout_buffer:
                    convert(input_buffer, outout_buffer)
                    self.wfile.write(outout_buffer.getvalue())


        else:
            self.send_response(404)
        return

if __name__ == "__main__":
    hostName = sys.argv[1]
    serverPort = int(sys.argv[2])
    webServer = HTTPServer((hostName, serverPort), Handler)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")