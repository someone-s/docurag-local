FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY server.py ./

EXPOSE 8080

CMD [ "fastapi", "run", "./server.py", "--port", "8080" ]