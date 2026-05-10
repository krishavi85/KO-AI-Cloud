from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Nexora AI"
    ADMIN_EMAIL: str = "krishanavinash@gmail.com"
    DATABASE_URL: str
    REDIS_URL: str
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    QDRANT_URL: str = "http://qdrant:6333"
    DEFAULT_CHAT_MODEL: str = "qwen2.5:7b"
    DEFAULT_EMBED_MODEL: str = "nomic-embed-text"
    DEFAULT_IMAGE_MODEL: str = "sdxl"
    JWT_SECRET: str
    API_KEY_PREFIX: str = "nexora_key"
    MAX_INPUT_CHARS: int = 12000
    MAX_OUTPUT_TOKENS: int = 2048
    UPLOAD_DIR: str = "/app/uploads"
    RAG_COLLECTION: str = "nexora_documents"
    ENABLE_GPU_ROUTER: bool = False
    GPU_WORKER_URLS: str = ""
    LIVEKIT_URL: str = ""
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    LIVEKIT_DEFAULT_ROOM: str = "nexora-voice"
    IMAGE_WORKER_URL: str = ""
    TTS_WORKER_URL: str = ""
    STT_WORKER_URL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
