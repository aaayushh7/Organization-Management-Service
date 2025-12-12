
# Organization Management Service

A backend service built with FastAPI and MongoDB for managing organizations in a multi-tenant architecture.

## Architecture & Design

### High Level Diagram

![High Level Design](./diag.png)

### Design Choices
- **FastAPI**: Chosen for high performance and automatic validation/docs.
- **MongoDB**: Ideal for storing flexible/dynamic data per organization.
- **Multi-tenancy Strategy**: 
    - **Single Database, Dynamic Collections**: Each organization gets its own collection (`org_<name>`). 
    - **Master Collection**: Stores metadata (name, admin, collection reference) in `master_organizations`.
    - **Trade-offs**: 
        - *Pros*: Easy to implement, good isolation for small-medium scale.
        - *Cons*: If 10,000s of orgs, having 10,000s of collections might impact metadata performance on some Mongo configs. For very large scale, separate Databases per Org or Sharding key `org_id` in a single collection is preferred.
- **Authentication**: JWT based admin authentication.

## Getting Started

### Prerequisites
- Python 3.9+
- MongoDB running locally on port 27017

### Installation
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r organization_service/requirements.txt
   ```

### Running the Application
```bash
cd organization_service
uvicorn app.main:app --reload --port 8000
```
Access documentation at: `http://127.0.0.1:8000/docs`

### Running Tests
```bash
# Ensure server is running on port 8001 (or update test script)
# Or just run the script (it assumes port 8001 currently in config)
python organization_service/tests/test_flow.py
```
*Note: The test script currently targets port 8001.*

## API Endpoints
- `POST /org/create`: Create new organization.
- `POST /admin/login`: Login as Org Admin.
- `GET /org/get`: Get Org details.
- `PUT /org/update`: Update Org details (Syncs/Renames collection).
- `DELETE /org/delete`: Delete Org.

## Deployment

### Vercel Deployment
This project is configured for Vercel.

1.  **Fork/Push** this repository to GitHub.
2.  **Import** the project in Vercel.
3.  **Environment Variables**: You **MUST** set the following environment variable in Vercel Project Settings:
    -   `MONGODB_URL`: Your MongoDB Atlas Connection String (e.g., `mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority`)
4.  **Database**: Vercel does not host databases. You must use a cloud provider like **MongoDB Atlas** (Free Tier available).
    -   Create a Cluster on MongoDB Atlas.
    -   Get the connection string.
    -   Allow Access from Anywhere (0.0.0.0/0) or Vercel IPs in Network Access.
    -   Use that string for `MONGODB_URL`.

