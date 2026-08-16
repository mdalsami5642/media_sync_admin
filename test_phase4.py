import json
from app import app

def test_flask_api():
    client = app.test_client()

    print("--- 1. Testing GET /api/status/smbd ---")
    res = client.get("/api/status/smbd")
    data = res.get_json()
    print(f"Status Code: {res.status_code} | Response: {data}")
    assert res.status_code == 200 and data.get("success") is True

    print("\n--- 2. Testing POST /api/service/smbd/restart ---")
    res = client.post("/api/service/smbd/restart")
    data = res.get_json()
    print(f"Status Code: {res.status_code} | Message: {data.get('message')}")
    assert res.status_code == 200 and data.get("success") is True

    print("\n--- 3. Testing GET /api/logs/smbd ---")
    res = client.get("/api/logs/smbd?lines=3")
    data = res.get_json()
    print(f"Status Code: {res.status_code} | Log Count: {len(data.get('logs', []))}")
    assert res.status_code == 200 and "logs" in data

    print("\n--- 4. Testing GET /api/config/smbd ---")
    res = client.get("/api/config/smbd")
    data = res.get_json()
    print(f"Status Code: {res.status_code} | Config Path: {data.get('path')}")
    assert res.status_code == 200 and data.get("path") == "/etc/samba/smb.conf"

    print("\n--- 5. Testing POST /api/shares ---")
    payload = {
        "share_name": "APITestShare",
        "folder_path": "~/APITestMedia",
        "read_only": False,
        "guest_ok": True
    }
    res = client.post(
        "/api/shares",
        data=json.dumps(payload),
        content_type="application/json"
    )
    data = res.get_json()
    print(f"Status Code: {res.status_code} | Message: {data.get('message')}")

    print("\n✅ PHASE 4 API TEST PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_flask_api()