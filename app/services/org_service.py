
from fastapi import HTTPException, status, Depends
from app.core.database import get_database, Database
from app.models.schemas import OrganizationCreate, OrganizationResponse, AdminLogin
from app.models.domain import MasterOrganization
from app.core.security import get_password_hash, verify_password, create_access_token
from pymongo.database import Database as MongoDatabase

MASTER_COLLECTION = "master_organizations"

async def create_organization(org_data: OrganizationCreate, db: MongoDatabase):
    # 1. Check if organization name exists
    existing_org = await db[MASTER_COLLECTION].find_one({"organization_name": org_data.organization_name})
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name already exists"
        )
    
    # 2. Create dynamic collection name
    collection_name = f"org_{org_data.organization_name.lower().replace(' ', '_')}"
    
    # 3. Hash password
    hashed_password = get_password_hash(org_data.password)
    
    # 4. Create Master Record
    new_org = MasterOrganization(
        organization_name=org_data.organization_name,
        organization_collection=collection_name,
        admin_email=org_data.email,
        admin_password_hash=hashed_password
    )
    
    result = await db[MASTER_COLLECTION].insert_one(new_org.dict())
    
    # 5. Create the dynamic collection (and maybe index or init data)
    # MongoDB creates collections lazily, but we can insert a dummy doc or explicit create
    # For now, we just ensure it's referenceable.
    # We could insert a config doc or similar.
    await db[collection_name].insert_one({"type": "init", "created_at": new_org.created_at})

    return OrganizationResponse(
        organization_name=new_org.organization_name,
        email=new_org.admin_email,
        organization_collection=new_org.organization_collection,
        admin_id=str(result.inserted_id),
        created_at=new_org.created_at
    )

async def authenticate_admin(login_data: AdminLogin, db: MongoDatabase):
    user = await db[MASTER_COLLECTION].find_one({"admin_email": login_data.email})
    if not user:
        return None
    if not verify_password(login_data.password, user["admin_password_hash"]):
        return None
    return user
