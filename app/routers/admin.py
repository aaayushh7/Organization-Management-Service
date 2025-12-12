
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.schemas import Token, AdminLogin
from app.services.org_service import authenticate_admin
from app.core.security import create_access_token
from app.core.database import get_database
from pymongo.database import Database

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/login", response_model=Token)
async def login_for_access_token(login_data: AdminLogin, db: Database = Depends(get_database)):
    user = await authenticate_admin(login_data, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create Token
    # We include org info in the token for convenience
    access_token = create_access_token(
        data={
            "sub": user["admin_email"],
            "org_id": str(user["_id"]), # Using Master Org ID as identifier
            "org_name": user["organization_name"]
        }
    )
    return {"access_token": access_token, "token_type": "bearer", "organization_id": str(user["_id"]), "organization_name": user["organization_name"]}
