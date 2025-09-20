## Setup
1. create openai-key.env in the same directory as docker-compose.yml
    -   contents of the file should contain one line:  ```OPENAI_API_KEY=YoUrOpenAIApIKEy```
2. create huggingface-key.env in the same directory as docker-compose.yml
    -   contents of the file should contain one line: ```HF_TOKEN=yoURhFTokeN```

## Run
```
docker compose up
```