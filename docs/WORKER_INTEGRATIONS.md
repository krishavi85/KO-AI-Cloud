# Nexora AI Worker Integrations

This document explains how to make the remaining advanced services real.

## 1. Speech-to-text worker

Environment variable:

```env
STT_WORKER_URL=http://your-stt-worker:9001
```

Expected endpoint:

```text
POST /transcribe
multipart/form-data file=<audio file>
```

Expected response:

```json
{
  "text": "transcribed text",
  "language": "en",
  "duration": 12.4
}
```

Recommended engines:

- faster-whisper
- whisper.cpp

## 2. Text-to-speech worker

Environment variable:

```env
TTS_WORKER_URL=http://your-tts-worker:9002
```

Expected endpoint:

```text
POST /tts
```

Request:

```json
{
  "text": "Hello from Nexora AI"
}
```

Recommended engine:

- Piper TTS

## 3. Image generation worker

Environment variable:

```env
IMAGE_WORKER_URL=http://your-image-worker:9003
```

Expected endpoint:

```text
POST /generate
```

Request:

```json
{
  "prompt": "futuristic AI dashboard",
  "model": "sdxl"
}
```

Recommended engines:

- ComfyUI
- Stable Diffusion WebUI
- custom SDXL FastAPI worker

## 4. Distributed GPU workers

Environment variables:

```env
ENABLE_GPU_ROUTER=true
GPU_WORKER_URLS=http://gpu-node-1:8000,http://gpu-node-2:8000
```

Expected endpoint on each worker:

```text
POST /v1/chat/completions
```

Recommended engines:

- vLLM
- Ollama on GPU nodes
- TGI

## Current status

These are now configurable integrations, not dead placeholders. If a worker URL is configured, Nexora AI forwards real requests to that worker. If not configured, the API returns a clear `worker_not_configured` status.
