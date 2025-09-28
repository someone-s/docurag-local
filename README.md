# DocuRAG
A web application using a mixture of local model and OpenAI API to perform Retrieval Augmentated Generation. Include persistent document storage and management and integrated PDF viewer using PDFEmbed and linking to PDF document using custom prompting.

## Highlights
- Link to document source 🔗
    - Response from the system provide a reference to the source document, which the user can quick on to immediately open up the relevant page
- Query constraint 🔎
    - Users can optionally specify a specific machine, category and/or model relevant to their questions. With only relevant documents used in respond.
- Document management 📂
    - Documents and their embeddings are stored persistently in Postgres. Embeds are generated once per file and reused for any future query
- Expandable categories 📋
    - Categories and makes can be expanded to support new document and machine types directly from the frontend.

## Small things
- Processing status 🛎
    - While documents are being processed and added to the system, the frontend shows in-progress files in-sync with the backend (using websockets), letting the user know the progress of any file upload clearly.
- Light/Dark mode 🌤
    - Light mode darkmode support based upon Shadcn-Vue implementation
- Resizable windows 🪟
    - PDF viewer can be resized dynamically for optimal size based on user preference
- Pagination and infinite-scrolling 📜
    - Both the machine and document list loads entries in 50 item chunks, using Tanstack Query, Table and Virtualizer to achieve the functionality. (This is a bit overkill for the use case)

## Screenshots
Query | Machines | Documents
-----:|:-----:|:-----
![Query Page](/readme/QueryPage.png) | ![Machine Page](/readme/MachinePage.png) | ![Document Page](/readme/DocumentPage.png)

## Setup
1. Create ```openai-key.env```
    - Create the file in the same directory as docker-compose-*.yml
    - Contents of the file should contain one line:  ```OPENAI_API_KEY=YoUrOpenAIApIKEy```
2. Create ```huggingface-key.env```
    - Create the file in the same directory as docker-compose-*.yml
    - Contents of the file should contain one line: ```HF_TOKEN=yoURhFTokeN```
3. Update ```docker-compose-dev-no-frontend.yml``` and ```docker-compose-prod.yml```
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

## Extra Fluff
No AI code editor (i.e. Cursor) was used to make this, since I am actually trying to refresh my skills.