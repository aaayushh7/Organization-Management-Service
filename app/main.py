
from fastapi import FastAPI
from app.routers import admin, organization
from app.core.database import db

app = FastAPI(title="Organization Management Service")

@app.on_event("startup")
async def startup_event():
    db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    db.close()

app.include_router(admin.router)
app.include_router(organization.router)

@app.get("/")
async def root():
    return {"message": "Organization Management Service is running"}
