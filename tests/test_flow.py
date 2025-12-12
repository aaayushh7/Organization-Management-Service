
import httpx
import time
import sys

BASE_URL = "http://127.0.0.1:8001"

def test_flow():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        print("1. Health Check")
        try:
            r = client.get("/")
            assert r.status_code == 200
            print("   -> OK")
        except Exception as e:
            print(f"   -> Failed: {e}")
            sys.exit(1)

        print("2. Create Organization 'TestCorp'")
        org_data = {
            "organization_name": "TestCorp",
            "email": "admin@testcorp.com",
            "password": "securepassword123"
        }
        r = client.post("/org/create", json=org_data)
        if r.status_code == 400 and "exists" in r.text:
            print("   -> Org already exists (Cleanup didn't happen?), proceeding...")
        else:
            assert r.status_code == 200, f"Failed: {r.text}"
            print("   -> OK")
            data = r.json()
            assert data["organization_collection"] == "org_testcorp"

        print("3. Admin Login")
        login_data = {
            "email": "admin@testcorp.com",
            "password": "securepassword123"
        }
        r = client.post("/admin/login", json=login_data)
        assert r.status_code == 200, f"Failed: {r.text}"
        token = r.json()["access_token"]
        print("   -> OK")
        
        headers = {"Authorization": f"Bearer {token}"}

        print("4. Get Organization 'TestCorp'")
        r = client.get("/org/get?organization_name=TestCorp")
        assert r.status_code == 200, f"Failed: {r.text}"
        print("   -> OK")

        print("5. Update Organization 'TestCorp' -> 'NewCorp'")
        update_data = {
            "organization_name": "NewCorp",
            "email": "admin@newcorp.com", # Updating email too
            "password": "securepassword123"
        }
        r = client.put("/org/update", json=update_data, headers=headers)
        assert r.status_code == 200, f"Failed: {r.text}"
        assert r.json()["organization_name"] == "NewCorp"
        assert r.json()["organization_collection"] == "org_newcorp"
        print("   -> OK")

        print("6. Verify Update (Get 'NewCorp')")
        r = client.get("/org/get?organization_name=NewCorp")
        assert r.status_code == 200
        print("   -> OK")

        print("7. Delete Organization 'NewCorp'")
        # Need to login again?
        # The token contains OLD org_name "TestCorp". 
        # The logic validates "current_user" against DB via "sub" (email).
        # But wait, my get_current_admin implementation:
        #   payload = jwt.decode(token)
        #   email = payload.get("sub")
        #   org_name = payload.get("org_name")
        #   find_one({"organization_name": org_name, "admin_email": email})
        #
        # If I updated the Org Name and Email in DB, the old Token (with old name/email) might NOT match the DB anymore!
        # This is a classic Auth issue.
        # If I update my email/orgname, my current token becomes invalid validation-wise if validation relies on DB lookup matching Token claims exactly.
        # Let's see. 
        # In `update_organization`, I update the DB.
        # My `get_current_admin` checks: `find_one({"organization_name": org_name, "admin_email": email})`.
        # The `org_name` and `email` come from the Token.
        # But the DB now has "NewCorp" and "admin@newcorp.com".
        # So the next request with the OLD token will FAIL (401).
        # So I need to Login *again* to get a new token? 
        # Yes, usually. Or the Update endpoint should return a new Token.
        # For this test, I will Login again with NEW credentials.
        
        print("   -> Logging in with New Credentials...")
        login_data_new = {
            "email": "admin@newcorp.com",
            "password": "securepassword123"
        }
        r = client.post("/admin/login", json=login_data_new)
        assert r.status_code == 200, f"Failed to login with new creds: {r.text}"
        new_token = r.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        
        print("   -> Deleting...")
        r = client.delete("/org/delete?organization_name=NewCorp", headers=new_headers)
        assert r.status_code == 200, f"Failed delete: {r.text}"
        print("   -> OK")
        
        print("SUCCESS: All flows passed.")

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2) 
    test_flow()
