# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

HEADERS = {
    "X-API-Key": "comp-intel-secret-key",
    "Content-Type": "application/json"
}


def test_chat_guardrails_blocked() -> None:
    """Verifies that messages containing curse words are blocked with 400 Bad Request."""
    payload = {
        "session_id": "test-session",
        "message": "This is absolute shit."
    }
    
    response = client.post("/api/chat", json=payload, headers=HEADERS)
    assert response.status_code == 400
    assert "Inappropriate language detected" in response.json()["detail"]


def test_chat_guardrails_allowed() -> None:
    """Verifies that clean messages are allowed and proceed to generate content."""
    payload = {
        "session_id": "test-session",
        "message": "Who is the CEO of Google?"
    }
    
    # We expect this request to succeed or start streaming, rather than being blocked by guardrails.
    # It might raise an error if LLM API is unavailable, but it should NOT return the inappropriate language 400 block.
    response = client.post("/api/chat", json=payload, headers=HEADERS)
    assert response.status_code != 400
