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

class VulnerabilityCreate(BaseModel):
    name_en: str
    name_uk: str
    description_en: str
    description_uk: str

class VulnerabilityResponse(VulnerabilityCreate):
    id: int

    class Config:
        from_attributes = True

class TargetVulnerabilityCreate(BaseModel):
    vulnerability_id: int
    severity: str

class TargetVulnerabilityResponse(BaseModel):
    vulnerability_id: int
    severity: str

    class Config:
        from_attributes = True

class TargetUpdate(BaseModel):
    ip_address: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None

class VulnerabilityUpdate(BaseModel):
    name_en: Optional[str] = None
    name_uk: Optional[str] = None
    description_en: Optional[str] = None
    description_uk: Optional[str] = None

class TargetVulnerabilityUpdate(BaseModel):
    severity: str