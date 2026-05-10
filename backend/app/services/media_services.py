from pathlib import Path
from app.config import settings
from app.services.ollama_client import chat


def transcribe_audio_stub(path: str) -> dict:
    return {
        "status": "stub",
        "message": "Voice support scaffold is ready. Connect whisper.cpp or faster-whisper here.",
        "file": Path(path).name,
        "text": "",
    }


def text_to_speech_stub(text: str) -> dict:
    return {
        "status": "stub",
        "message": "TTS scaffold is ready. Connect Piper TTS here.",
        "text_preview": text[:120],
    }


def generate_image_stub(prompt: str) -> dict:
    return {
        "status": "stub",
        "message": "Image generation scaffold is ready. Connect Stable Diffusion WebUI, ComfyUI, or local SDXL worker here.",
        "model": settings.DEFAULT_IMAGE_MODEL,
        "prompt": prompt,
    }


def describe_image_prompt(prompt: str) -> str:
    return chat(
        settings.DEFAULT_CHAT_MODEL,
        [{"role": "user", "content": "Improve this image generation prompt: " + prompt}],
        400,
    )
