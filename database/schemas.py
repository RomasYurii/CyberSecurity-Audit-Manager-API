from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "player"

class TargetCreate(BaseModel):
    ip_address: str
    domain: str
    description: Optional[str] = None

class TargetResponse(BaseModel):
    id: int
    ip_address: str
    domain: str
    description: Optional[str] = None
    pentester_id: int

    class Config:
        from_attributes = True