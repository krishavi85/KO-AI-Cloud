# K.O. AI Cloud v2 Upgrades

This document maps the requested next technically correct upgrades to the implemented codebase.

## 1. Streaming responses

Implemented with Server-Sent Events:

- `backend/app/routers/chat.py`
- Endpoint: `POST /v1/chat/stream`
- Frontend button: `Streaming Chat`

## 2. RAG memory using Qdrant

Implemented with Qdrant container and RAG service:

- `docker-compose.yml` includes `qdrant`
- `backend/app/services/rag.py`
- Collection: `ko_ai_documents`

## 3. File upload parsing

Implemented for TXT, Markdown, code files, CSV, JSON, PDF, and DOCX:

- `backend/app/routers/files.py`
- `backend/app/services/file_parser.py`
- Endpoint: `POST /files/upload`

## 4. Conversation persistence

Implemented with PostgreSQL tables:

- `Conversation`
- `Message`
- `UsageLog`

See:

- `backend/app/models.py`
- `backend/app/routers/chat.py`

## 5. Local embeddings

Implemented through Ollama embeddings:

- Default embedding model: `nomic-embed-text`
- Service: `backend/app/services/ollama_client.py`
- Function: `embed()`

Pull the model:

```bash
docker exec -it ko_ai_ollama ollama pull nomic-embed-text
```

## 6. Multi-model routing

Implemented with task classification:

- `backend/app/services/model_router.py`
- Endpoint: `GET /models/route?prompt=...`

Recommended models:

```bash
docker exec -it ko_ai_ollama ollama pull qwen2.5:7b
docker exec -it ko_ai_ollama ollama pull qwen2.5-coder:7b
docker exec -it ko_ai_ollama ollama pull llama3.1:8b
```

## 7. Admin analytics

Implemented with:

- `backend/app/routers/admin.py`
- Endpoint: `GET /admin/analytics`
- Frontend analytics card

## 8. Voice support

Scaffold implemented:

- `backend/app/routers/media.py`
- `backend/app/services/media_services.py`

Current state: safe stub.
Next real integration: `whisper.cpp`, `faster-whisper`, or `Piper`.

## 9. Image generation

Scaffold implemented:

- `POST /media/image/generate`
- Prompt improvement through local LLM

Current state: safe stub.
Next real integration: ComfyUI, Stable Diffusion WebUI, or local SDXL worker.

## 10. Distributed GPU serving

Scaffold implemented:

- `backend/app/services/gpu_router.py`
- Environment:
  - `ENABLE_GPU_ROUTER=true`
  - `GPU_WORKER_URLS=http://gpu-node-1:8000,http://gpu-node-2:8000`

Current state: router scaffold.
Next real integration: vLLM workers or dedicated Ollama GPU workers.

## Run

```bash
docker compose up --build
```

Pull required models:

```bash
docker exec -it ko_ai_ollama ollama pull qwen2.5:7b
docker exec -it ko_ai_ollama ollama pull nomic-embed-text
docker exec -it ko_ai_ollama ollama pull qwen2.5-coder:7b
```

Open:

```text
http://localhost:5173
```
