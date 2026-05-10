from pydantic import BaseModel, EmailStr
from typing import List, Literal, Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class APIKeyCreateRequest(BaseModel):
    name: str


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    session_id: Optional[str] = "default"
    max_tokens: Optional[int] = None
    use_rag: bool = True


class ChatCompletionResponse(BaseModel):
    model: str
    route: str
    response: str
    compressed: bool
    rag_chunks: int


class ModelRoute(BaseModel):
    task: str
    model: str
    route: str
