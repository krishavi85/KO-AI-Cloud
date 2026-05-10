from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "K.O. AI Cloud"
    DATABASE_URL: str
    REDIS_URL: str
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    QDRANT_URL: str = "http://qdrant:6333"
    DEFAULT_CHAT_MODEL: str = "qwen2.5:7b"
    DEFAULT_EMBED_MODEL: str = "nomic-embed-text"
    DEFAULT_IMAGE_MODEL: str = "sdxl"
    JWT_SECRET: str
    API_KEY_PREFIX: str = "koai_sk_live"
    MAX_INPUT_CHARS: int = 12000
    MAX_OUTPUT_TOKENS: int = 2048
    UPLOAD_DIR: str = "/app/uploads"
    RAG_COLLECTION: str = "ko_ai_documents"
    ENABLE_GPU_ROUTER: bool = False
    GPU_WORKER_URLS: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
