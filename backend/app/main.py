from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routers import admin, api_keys, auth, chat, files, media, models

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(api_keys.router)
app.include_router(chat.router)
app.include_router(files.router)
app.include_router(admin.router)
app.include_router(media.router)
app.include_router(models.router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "mode": "standalone-local-ai-v2",
        "features": [
            "streaming-chat",
            "qdrant-rag",
            "file-upload-parsing",
            "conversation-persistence",
            "local-embeddings",
            "multi-model-routing",
            "admin-analytics",
            "voice-scaffold",
            "image-scaffold",
            "distributed-gpu-scaffold",
        ],
    }
