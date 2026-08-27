import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_auth_and_protected_routes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        password = "SecurePassword123!"

        # 1. Register
        reg_res = await ac.post("/api/v1/auth/register", json={"email": unique_email, "password": password})
        assert reg_res.status_code == 201, reg_res.text
        data = reg_res.json()
        assert "access_token" in data
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Login
        login_res = await ac.post("/api/v1/auth/login", json={"email": unique_email, "password": password})
        assert login_res.status_code == 200, login_res.text
        assert "access_token" in login_res.json()

        # 3. Get /me
        me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200, me_res.text
        assert me_res.json()["email"] == unique_email

        # 4. Upload document
        file_content = b"This is a test contract for DocuMind Q&A. Section 1 covers terms."
        files = {"file": ("test_contract.txt", file_content, "text/plain")}
        upload_res = await ac.post("/api/v1/documents", files=files, headers=headers)
        assert upload_res.status_code == 202, upload_res.text
        doc_data = upload_res.json()
        assert doc_data["filename"] == "test_contract.txt"
        doc_id = doc_data["id"]

        # 5. List documents
        list_res = await ac.get("/api/v1/documents", headers=headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1

        # 6. Get document by ID
        get_doc_res = await ac.get(f"/api/v1/documents/{doc_id}", headers=headers)
        assert get_doc_res.status_code == 200

        # 7. Create Chat Session
        session_res = await ac.post("/api/v1/chat/sessions", json={"title": "Contract Discussion"}, headers=headers)
        assert session_res.status_code == 201, session_res.text
        session_id = session_res.json()["id"]

        # 8. List Chat Sessions
        sessions_list_res = await ac.get("/api/v1/chat/sessions", headers=headers)
        assert sessions_list_res.status_code == 200
        assert len(sessions_list_res.json()) >= 1

        # 9. Get Chat Session Details
        session_detail_res = await ac.get(f"/api/v1/chat/sessions/{session_id}", headers=headers)
        assert session_detail_res.status_code == 200
        assert "messages" in session_detail_res.json()

        # 10. Update Chat Session Title
        rename_res = await ac.patch(f"/api/v1/chat/sessions/{session_id}", json={"title": "Updated Contract Discussion"}, headers=headers)
        assert rename_res.status_code == 200
        assert rename_res.json()["title"] == "Updated Contract Discussion"

        # 11. Delete Document
        del_doc_res = await ac.delete(f"/api/v1/documents/{doc_id}", headers=headers)
        assert del_doc_res.status_code == 204

        # 12. Delete Chat Session
        del_session_res = await ac.delete(f"/api/v1/chat/sessions/{session_id}", headers=headers)
        assert del_session_res.status_code == 204
