
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class MasterOrganization(BaseModel):
    organization_name: str
    organization_collection: str
    admin_email: EmailStr
    admin_password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        # Pydantic V2 config if needed, or V1 style
        from_attributes = True

# We can add more domain models here as needed for dynamic collections
