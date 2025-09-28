## Setup
1. ### Create ```openai-key.env```
    - Create the file in the same directory as docker-compose-*.yml
    - Contents of the file should contain one line:  ```OPENAI_API_KEY=YoUrOpenAIApIKEy```
2. ### Create ```huggingface-key.env```
    - Create the file in the same directory as docker-compose-*.yml
    - Contents of the file should contain one line: ```HF_TOKEN=yoURhFTokeN```
3. ### Update ```docker-compose-dev-no-frontend.yml``` and ```docker-compose-prod.yml```
    - Install Nvidia Container Toolkit, following the link in [this hugging face guide.](https://huggingface.co/docs/text-embeddings-inference/en/supported_models#supported-hardware)
    - Ensure the current Docker context is the one with Nvidia container toolkit linked
      - If ```docker info | grep Runtimes``` does not contain ```nvidia```, you will need to either switch Docker context or check the Nvidia Toolkit was installed correctly
      - Switch Docker context by using commands under ```docker context --help```, verify that the context you chose is working with ```docker info | grep Runtimes```
    - Choose the correct Docker image for text-embedding-inference, based on your hardware. [See this hugging face page for details.](https://huggingface.co/docs/text-embeddings-inference/en/supported_models#supported-hardware)
      ```
        embed:  # internal port is 80
          image: ghcr.io/huggingface/text-embeddings-inference:turing-1.8
          container_name: embed
      ```

## Development Run
```
cd ROOT_OF_THE_REPO
docker compose up -f docker-compose-dev-no-frontend.yml
-> (or use vscode F1 -> Container: Compose Up)

cd ROOT_OF_THE_REPO/frontend
npm run dev
```
- Go to ```http://localhost:5173``` for frontend
- Go to ```http://localhost:8081/docs``` for fast api of backend
- Use ```psql postgres://POSTGRES_USER:POSTGRES_PASSWORD@localhost:5433/POSTGRES_DB``` with the values set in ```postgres-setting.env``` to access postgres directly

## Production Run
```
docker compose up -f docker-compose-prod.yml
-> (or use vscode F1 -> Container: Compose Up)
```
- Access frontend from ```http://localhost:80```
- Backend and Postgres are both inaccessible