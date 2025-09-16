FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY frontend_chunk.py ./
COPY frontend_embed.py ./
COPY frontend_database.py ./
COPY frontend_query.py ./
COPY frontend_upload.py ./
COPY frontend_server.py ./

EXPOSE 8080

CMD [ "fastapi", "run", "./frontend_server.py", "--port", "8080" ]