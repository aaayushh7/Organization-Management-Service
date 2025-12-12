
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import datetime

class OrganizationBase(BaseModel):
    organization_name: str
    email: EmailStr

class OrganizationCreate(OrganizationBase):
    password: str

class OrganizationUpdate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrganizationResponse(OrganizationBase):
    organization_collection: str
    admin_id: Optional[str] = None
    created_at: Optional[datetime] = None

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None

class TokenData(BaseModel):
    email: Optional[str] = None
