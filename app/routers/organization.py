
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.models.schemas import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.services.org_service import create_organization, MASTER_COLLECTION
from app.core.database import get_database
from app.core.security import settings, verify_password, get_password_hash
from pymongo.database import Database
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(
    prefix="/org",
    tags=["Organization"]
)

security = HTTPBearer()

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Database = Depends(get_database)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        org_name: str = payload.get("org_name")
        if email is None or org_name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await db[MASTER_COLLECTION].find_one({"organization_name": org_name, "admin_email": email})
    if user is None:
        raise credentials_exception
    return user

@router.post("/create", response_model=OrganizationResponse)
async def create_new_organization(org: OrganizationCreate, db: Database = Depends(get_database)):
    return await create_organization(org, db)

@router.get("/get", response_model=OrganizationResponse)
async def get_organization(organization_name: str, db: Database = Depends(get_database)):
    org = await db[MASTER_COLLECTION].find_one({"organization_name": organization_name})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return OrganizationResponse(
        organization_name=org["organization_name"],
        email=org["admin_email"],
        organization_collection=org["organization_collection"],
        admin_id=str(org["_id"]),
        created_at=org["created_at"]
    )

@router.put("/update", response_model=OrganizationResponse)
async def update_organization(
    org_update: OrganizationUpdate,
    current_user: dict = Depends(get_current_admin),
    db: Database = Depends(get_database)
):
    # Only allow updating OWN organization
    # "current_user" is from the token, so we know who they are.
    # The requirement says Input: organization_name, email, password
    # These are the NEW values.
    
    old_org_name = current_user["organization_name"]
    new_org_name = org_update.organization_name
    
    # 1. Update Metadata in Master
    # Check if new name exists (if changing name)
    if new_org_name != old_org_name:
        exists = await db[MASTER_COLLECTION].find_one({"organization_name": new_org_name})
        if exists:
            raise HTTPException(status_code=400, detail="Organization name already exists")
            
    new_collection_name = f"org_{new_org_name.lower().replace(' ', '_')}"
    old_collection_name = current_user["organization_collection"]
    
    # Update Fields
    updates = {
        "organization_name": new_org_name,
        "admin_email": org_update.email,
        "admin_password_hash": get_password_hash(org_update.password),
        "organization_collection": new_collection_name
    }
    
    await db[MASTER_COLLECTION].update_one({"_id": current_user["_id"]}, {"$set": updates})
    
    # 2. Sync Collection (Rename)
    if old_collection_name != new_collection_name:
        # Check if old collection exists
        col_list = await db.list_collection_names()
        if old_collection_name in col_list:
            await db[old_collection_name].rename(new_collection_name)
    
    # Fetch updated
    updated_org = await db[MASTER_COLLECTION].find_one({"_id": current_user["_id"]})
    return OrganizationResponse(
        organization_name=updated_org["organization_name"],
        email=updated_org["admin_email"],
        organization_collection=updated_org["organization_collection"],
        admin_id=str(updated_org["_id"]),
        created_at=updated_org["created_at"]
    )

@router.delete("/delete")
async def delete_organization(current_user: dict = Depends(get_current_admin), db: Database = Depends(get_database)):
    # Validate user is deleting their own org
    organization_name = current_user["organization_name"]
        
    # Drop Collection
    col_name = current_user["organization_collection"]
    await db[col_name].drop()
    
    # Remove from Master
    await db[MASTER_COLLECTION].delete_one({"_id": current_user["_id"]})
    
    return {"detail": f"Organization {organization_name} deleted successfully"}
