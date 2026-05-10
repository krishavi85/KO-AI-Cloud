from pathlib import Path

import requests

from app.config import settings
from app.services.ollama_client import chat


def transcribe_audio(path: str) -> dict:
    if settings.STT_WORKER_URL:
        with open(path, "rb") as audio_file:
            response = requests.post(
                settings.STT_WORKER_URL.rstrip("/") + "/transcribe",
                files={"file": audio_file},
                timeout=300,
            )
        response.raise_for_status()
        return response.json()

    return {
        "status": "worker_not_configured",
        "message": "Configure STT_WORKER_URL to enable real transcription with Whisper or faster-whisper.",
        "file": Path(path).name,
        "text": "",
    }


def text_to_speech(text: str) -> dict:
    if settings.TTS_WORKER_URL:
        response = requests.post(
            settings.TTS_WORKER_URL.rstrip("/") + "/tts",
            json={"text": text},
            timeout=300,
        )
        response.raise_for_status()
        return response.json()

    return {
        "status": "worker_not_configured",
        "message": "Configure TTS_WORKER_URL to enable real speech synthesis with Piper or another local TTS worker.",
        "text_preview": text[:120],
    }


def generate_image(prompt: str) -> dict:
    if settings.IMAGE_WORKER_URL:
        response = requests.post(
            settings.IMAGE_WORKER_URL.rstrip("/") + "/generate",
            json={"prompt": prompt, "model": settings.DEFAULT_IMAGE_MODEL},
            timeout=600,
        )
        response.raise_for_status()
        return response.json()

    return {
        "status": "worker_not_configured",
        "message": "Configure IMAGE_WORKER_URL to enable ComfyUI, Stable Diffusion WebUI, or a local SDXL worker.",
        "model": settings.DEFAULT_IMAGE_MODEL,
        "prompt": prompt,
    }


def describe_image_prompt(prompt: str) -> str:
    return chat(
        settings.DEFAULT_CHAT_MODEL,
        [{"role": "user", "content": "Improve this image generation prompt: " + prompt}],
        400,
    )
