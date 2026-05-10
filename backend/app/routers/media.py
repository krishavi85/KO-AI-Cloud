from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from app.deps import get_current_user
from app.models import User
from app.services.media_services import describe_image_prompt, generate_image_stub, text_to_speech_stub, transcribe_audio_stub

router = APIRouter(prefix="/media", tags=["media"])


class PromptPayload(BaseModel):
    prompt: str


class TextPayload(BaseModel):
    text: str


@router.post("/voice/transcribe")
def transcribe(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    path = f"/tmp/{user.id}_{file.filename}"
    with open(path, "wb") as out:
        out.write(file.file.read())
    return transcribe_audio_stub(path)


@router.post("/voice/tts")
def tts(payload: TextPayload, user: User = Depends(get_current_user)):
    return text_to_speech_stub(payload.text)


@router.post("/image/generate")
def image(payload: PromptPayload, user: User = Depends(get_current_user)):
    improved = describe_image_prompt(payload.prompt)
    data = generate_image_stub(improved or payload.prompt)
    data["improved_prompt"] = improved
    return data
