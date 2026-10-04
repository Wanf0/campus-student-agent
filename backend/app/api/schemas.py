from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None
    user_id: int | None = None


class Citation(BaseModel):
    title: str
    authority: str
    publish_date: str | None = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: int | None = None
    intent: str | None = None
    citations: list[Citation] = []


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
    source_authority: int = 1
    publish_date: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None
    version: str | None = None
    department: str | None = None
    doc_type: str = "其他"


class DocumentResponse(BaseModel):
    id: int
    title: str
    category: str
    source: str | None = None
