import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from starlette.testclient import TestClient
from src.main import app

def test_websocket_chat_flow():
    client = TestClient(app)
    unique_email = f"ws_user_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"

    # 1. Register & get token
    reg_res = client.post("/api/v1/auth/register", json={"email": unique_email, "password": password})
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Chat Session
    session_res = client.post("/api/v1/chat/sessions", json={"title": "WebSocket Test"}, headers=headers)
    assert session_res.status_code == 201
    session_id = session_res.json()["id"]

    # 3. Test Unauthorized WebSocket (no token)
    with pytest.raises(Exception):
        with client.websocket_connect(f"/api/v1/ws/chat/{session_id}") as ws:
            pass

    # 4. Test Authenticated WebSocket Connection
    with client.websocket_connect(f"/api/v1/ws/chat/{session_id}?token={token}") as ws:
        # A. Connected frame
        conn_frame = ws.receive_json()
        assert conn_frame["type"] == "connected"
        assert conn_frame["session_id"] == session_id

        # B. Heartbeat ping
        ws.send_json({"type": "ping"})
        pong_frame = ws.receive_json()
        assert pong_frame["type"] == "pong"

        # C. Clear Context
        ws.send_json({"type": "clear_context"})
        clear_frame = ws.receive_json()
        assert clear_frame["type"] == "context_cleared"

        # D. Query Submission
        ws.send_json({
            "type": "query",
            "client_msg_id": "opt-test-123",
            "text": "What is the policy for vacation?"
        })

        # Receive frames until 'done'
        received_types = []
        tokens = []
        while True:
            frame = ws.receive_json()
            received_types.append(frame["type"])
            if frame["type"] == "token":
                tokens.append(frame["content"])
            elif frame["type"] == "done":
                assert frame["client_msg_id"] == "opt-test-123"
                assert "citations" in frame
                break

        assert "status" in received_types
        assert "done" in received_types
