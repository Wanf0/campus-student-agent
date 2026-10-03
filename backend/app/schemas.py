from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: int | None = None
    intent: str | None = None


class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    user_id: int
    username: str
    role: str


class DocumentCreate(BaseModel):
    title: str
    category: str = "制度"
    source: str | None = None
    content: str


class DocumentResponse(BaseModel):
    id: int
    title: str
    category: str
    source: str | None = None
