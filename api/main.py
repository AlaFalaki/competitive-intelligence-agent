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

import asyncio
import json
import logging
import os
import sqlite3
import warnings
from collections.abc import AsyncGenerator

# Silence the harmless warning from the google-genai SDK about Automatic Function Calling (AFC) being
# disabled when combining built-in tools (like google_search) with custom Python callables.
# ADK implements and manages its own function execution loop independently.
logging.getLogger("google.genai").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*Automatic Function Calling.*")
warnings.filterwarnings("ignore", message=".*AFC.*")

from dotenv import load_dotenv  # noqa: E402

# Load .env from the agent project root directory (parent of api/)
agent_env_root = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".env",
    )
)
load_dotenv(dotenv_path=agent_env_root)

from fastapi import (  # noqa: E402
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Security,
    status,
)
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402
from fastapi.security import APIKeyHeader  # noqa: E402
from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402
from google.genai import types  # noqa: E402

# Import the workflow and shared DB_PATH from the agent project
from app.db import DB_PATH, run_migrations  # noqa: E402
from app.workflow import root_agent  # noqa: E402

# Ensure any unapplied database migrations (like master_reports table) are run on startup
run_migrations()

# Very naive authentication,
# TODO: replace with proper OAuth/JWT authentication in production
API_KEY_NAME = "X-API-Key"
API_KEY = "comp-intel-secret-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(title="Competitive Intelligence API Dashboard")

# Enable CORS for the NuxtJS frontend
# TODO: restrict allow_origins to specific domains in production deployment to prevent security vulnerabilities
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(
    api_key_h: str = Security(api_key_header),
    api_key_q: str = Query(None, alias="api_key"),
) -> str:
    """Verifies the request's API key header or query param."""
    api_key = api_key_h or api_key_q
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API credentials",
        )
    return api_key


def get_db_connection():
    return sqlite3.connect(DB_PATH)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/sessions", dependencies=[Depends(verify_api_key)])
def get_sessions():
    """Retrieves all previous unique analysis sessions across the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get unique session IDs and their earliest creation timestamps
        query = """
            SELECT session_id, MIN(created_at) as created_at FROM (
                SELECT session_id, created_at FROM company_profiles
                UNION ALL
                SELECT session_id, created_at FROM company_financials
                UNION ALL
                SELECT session_id, created_at FROM company_news
                UNION ALL
                SELECT session_id, created_at FROM pricing_information
            )
            WHERE session_id IS NOT NULL AND session_id != ''
            GROUP BY session_id
            ORDER BY created_at DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        sessions = [
            {
                "company_name": r[0],  # The session ID is the target company name
                "session_id": r[0],
                "created_at": r[1],
            }
            for r in rows
        ]
        return {"status": "success", "sessions": sessions}
    except Exception as e:
        return {"status": "error", "message": str(e), "sessions": []}
    finally:
        conn.close()


@app.get("/api/analyze")
async def analyze(
    company_name: str, api_key: str = Depends(verify_api_key)
) -> StreamingResponse:
    """Runs the multi-agent intelligence workflow and streams status updates as SSE."""

    async def event_generator() -> AsyncGenerator[str, None]:

        session_service = InMemorySessionService()
        # Set the session ID to exactly the target company name
        session_id = company_name.strip()
        await session_service.create_session(
            app_name="app", user_id="dashboard-user", session_id=session_id
        )

        runner = Runner(
            agent=root_agent,
            app_name="app",
            session_service=session_service,
        )

        try:
            # Yield initial status and unique session ID to the client
            yield f"data: {json.dumps({'type': 'session_created', 'session_id': session_id, 'company_name': company_name})}\n\n"
            yield f"data: {json.dumps({'type': 'status', 'message': f'Starting analysis session {session_id} for {company_name}...'})}\n\n"
            await asyncio.sleep(0.5)

            async for event in runner.run_async(
                user_id="dashboard-user",
                session_id=session_id,
                new_message=types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=company_name)],
                ),
            ):
                node_name = getattr(event, "node_path", None) or "Agent"

                # Extract and parse tool calls (function calls) and responses
                tool_calls = []
                tool_responses = []

                if hasattr(event, "content") and event.content:
                    parts = getattr(event.content, "parts", [])
                    for part in parts:
                        if getattr(part, "function_call", None):
                            f_call = part.function_call
                            tool_calls.append(
                                {
                                    "name": f_call.name,
                                    "args": getattr(f_call, "args", {}),
                                }
                            )
                        elif getattr(part, "function_response", None):
                            f_resp = part.function_response
                            tool_responses.append(
                                {
                                    "name": f_resp.name,
                                    "response": getattr(f_resp, "response", {}),
                                }
                            )

                text_content = ""
                if hasattr(event, "content") and event.content:
                    parts = getattr(event.content, "parts", [])
                    if parts and hasattr(parts[0], "text"):
                        text_content = parts[0].text

                # Stream the details including active tool execution
                log_data = {
                    "type": "log",
                    "node": node_name,
                    "text": text_content,
                    "tool_calls": tool_calls,
                    "tool_responses": tool_responses,
                }
                yield f"data: {json.dumps(log_data)}\n\n"
                await asyncio.sleep(0.1)

            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id, 'message': f'Analysis completed for {company_name}!'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Error occurred: {e}'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/results/{session_id}", dependencies=[Depends(verify_api_key)])
def get_results(session_id: str):
    """Retrieves all gathered profile, pricing, financials, competitors, and news for a specific session ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Fetch Profile
    cursor.execute(
        "SELECT name, industry, description, headquarters, website FROM company_profiles WHERE session_id = ?",
        (session_id,),
    )
    p_row = cursor.fetchone()
    if not p_row:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"No results found for session {session_id}",
        )

    company_name = p_row[0]
    profile = {
        "name": p_row[0],
        "industry": p_row[1],
        "description": p_row[2],
        "headquarters": p_row[3],
        "website": p_row[4],
    }

    # 2. Fetch Competitors
    cursor.execute(
        "SELECT competitor_name FROM competitors WHERE session_id = ?",
        (session_id,),
    )
    competitor_list = [row[0] for row in cursor.fetchall()]

    # 3. Fetch Pricing (for target + competitors)
    cursor.execute(
        "SELECT company_name, pricing_page_url, plans_json FROM pricing_information WHERE session_id = ?",
        (session_id,),
    )
    db_pricing = cursor.fetchall()
    db_pr_names = [row[0] for row in db_pricing]

    def find_matching_company(name, db_names):
        if not name or not db_names:
            return None
        n_clean = name.lower().replace(",", "").replace(".", "").replace("llc", "").replace("inc", "").replace("corp", "").replace("corporation", "").strip()
        for db_name in db_names:
            db_clean = db_name.lower().replace(",", "").replace(".", "").replace("llc", "").replace("inc", "").replace("corp", "").replace("corporation", "").strip()
            if db_clean in n_clean or n_clean in db_clean:
                return db_name
            w_n = [w for w in n_clean.split() if w not in ("(amd)", "(alphabet)", "(intel)", "google", "alphabet")]
            w_db = [w for w in db_clean.split() if w not in ("google", "alphabet")]
            if w_n and w_db and w_n[0] == w_db[0]:
                return db_name
        return None

    pricing = {}
    companies_to_query = [company_name, *competitor_list]
    for c in companies_to_query:
        match = find_matching_company(c, db_pr_names)
        if match:
            pr_row = [r for r in db_pricing if r[0] == match][0]
            try:
                plans = json.loads(pr_row[2])
            except Exception:
                plans = pr_row[2]
            pricing[c] = {"pricing_page_url": pr_row[1], "plans": plans}

    # 4. Fetch Financials (for target + competitors)
    cursor.execute(
        "SELECT company_name, cik, filing_data_json FROM company_financials WHERE session_id = ?",
        (session_id,),
    )
    db_financials = cursor.fetchall()
    db_fin_names = [row[0] for row in db_financials]

    financials = {}
    for c in companies_to_query:
        match = find_matching_company(c, db_fin_names)
        if match:
            f_row = [r for r in db_financials if r[0] == match][0]
            try:
                filing_data = json.loads(f_row[2])
            except Exception:
                filing_data = []
            financials[c] = {"cik": f_row[1], "filing_data": filing_data}

    # 5. Fetch News (for target + competitors)
    cursor.execute(
        "SELECT company_name, news_summary FROM company_news WHERE session_id = ?",
        (session_id,),
    )
    db_news = cursor.fetchall()
    db_news_names = [row[0] for row in db_news]

    news = {}
    for c in companies_to_query:
        match = find_matching_company(c, db_news_names)
        if match:
            n_row = [r for r in db_news if r[0] == match][0]
            news[c] = n_row[1]

    # 6. Fetch Master Report
    master_report = None
    cursor.execute(
        "SELECT report_json FROM master_reports WHERE session_id = ?",
        (session_id,),
    )
    m_row = cursor.fetchone()
    if m_row:
        try:
            master_report = json.loads(m_row[0])
        except Exception:
            master_report = None

    conn.close()

    return {
        "company_name": company_name,
        "session_id": session_id,
        "profile": profile,
        "competitors": competitor_list,
        "pricing": pricing,
        "financials": financials,
        "news": news,
        "master_report": master_report,
    }


from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    session_id: str
    message: str

# Global session service for Chat
CHAT_SESSION_SERVICE = InMemorySessionService()

# Import the chat_agent from the core agents module
from app.agents import chat_agent


@app.post("/api/chat", dependencies=[Depends(verify_api_key)])
async def chat_endpoint(request: ChatRequest) -> StreamingResponse:
    """Streams the chat response from the Copilot agent, including log events for tool calls."""
    
    # 1. Naive guardrail check for bad or curse words
    MOCK_CURSE_WORDS = {"fuck", "shit", "bitch", "asshole", "bastard", "crappy"}
    message_lower = request.message.lower()
    if any(word in message_lower for word in MOCK_CURSE_WORDS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inappropriate language detected in chat message."
        )

    # 2. LLM as a judge check using small model (commented out for now)
    # from google.genai import Client
    # from app.config import GEMINI_MODEL_SMALL
    # try:
    #     client = Client()
    #     judge_prompt = (
    #         "You are an enterprise content moderation judge. Analyze the following user query "
    #         "for profanity, toxicity, policy violations, or inappropriate content. "
    #         "Respond with ONLY 'SAFE' or 'UNSAFE'.\n\n"
    #         f"Query: {request.message}"
    #     )
    #     judge_resp = client.models.generate_content(
    #         model=GEMINI_MODEL_SMALL,
    #         contents=judge_prompt
    #     )
    #     if "UNSAFE" in judge_resp.text.upper():
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Message flagged as inappropriate by LLM moderator."
    #         )
    # except Exception as e:
    #     # Do not block execution if content moderation fails due to API issues
    #     pass

    async def chat_event_generator() -> AsyncGenerator[str, None]:
        session_id = f"{request.session_id}-chat"

        # Ensure session is created
        try:
            await CHAT_SESSION_SERVICE.create_session(
                app_name="app", user_id="dashboard-user", session_id=session_id
            )
        except Exception:
            pass # Already exists

        runner = Runner(
            agent=chat_agent,
            app_name="app",
            session_service=CHAT_SESSION_SERVICE,
        )

        try:
            async for event in runner.run_async(
                user_id="dashboard-user",
                session_id=session_id,
                new_message=types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=request.message)],
                ),
            ):
                node_name = getattr(event, "node_path", None) or "Copilot"

                tool_calls = []
                tool_responses = []

                if hasattr(event, "content") and event.content:
                    parts = getattr(event.content, "parts", [])
                    for part in parts:
                        if getattr(part, "function_call", None):
                            f_call = part.function_call
                            tool_calls.append({
                                "name": f_call.name,
                                "args": getattr(f_call, "args", {}),
                            })
                        elif getattr(part, "function_response", None):
                            f_resp = part.function_response
                            tool_responses.append({
                                "name": f_resp.name,
                                "response": getattr(f_resp, "response", {}),
                            })

                text_content = ""
                if hasattr(event, "content") and event.content:
                    parts = getattr(event.content, "parts", [])
                    for part in parts:
                        val = getattr(part, "text", None)
                        if val:
                            text_content += val

                # Yield stream log/content structure
                yield f"data: {json.dumps({
                    'type': 'log',
                    'node': node_name,
                    'text': text_content,
                    'tool_calls': tool_calls,
                    'tool_responses': tool_responses,
                })}\n\n"
                await asyncio.sleep(0.05)

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(chat_event_generator(), media_type="text/event-stream")


@app.post("/api/chat/clear", dependencies=[Depends(verify_api_key)])
async def clear_chat(request: ChatRequest):
    session_id = f"{request.session_id}-chat"
    try:
        await CHAT_SESSION_SERVICE.delete_session(
            app_name="app", user_id="dashboard-user", session_id=session_id
        )
        return {"status": "success", "message": "Chat history cleared"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
