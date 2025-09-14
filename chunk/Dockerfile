FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY server.py ./

EXPOSE 8090

CMD [ "fastapi", "run", "./server.py", "--port", "8090" ]