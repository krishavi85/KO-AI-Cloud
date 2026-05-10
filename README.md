# K.O. AI Cloud

Standalone private AI service platform with local model serving, API keys, RAG memory, file upload, and streaming chat.

## Stack
- FastAPI
- PostgreSQL
- Redis
- Ollama
- React/Vite
- Docker Compose
- Local RAG memory

## Features
- Local AI model serving
- ChatGPT-style chat UI
- API key generation
- Streaming responses
- Token Shield compression
- File uploads
- Retrieval-Augmented Generation (RAG)
- Conversation memory
- Usage tracking

## Start

```bash
docker compose up --build
```

Pull model:

```bash
docker exec -it ko_ai_ollama ollama pull qwen2.5:7b
```
