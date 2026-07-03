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

import json
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.genai import types

from app.config import load_instruction, GEMINI_MODEL_SMALL
from app.db import get_db_connection

# Load Chat Copilot instruction markdown
chat_copilot_instruction = load_instruction("chat_copilot.md")


def get_database_session_data(session_id: str) -> str:
    """Retrieves all gathered competitive intelligence profiles, competitor lists, pricing,
    financial reports, and news for a specific target company session in the database.

    Args:
        session_id: The target company name / session ID to look up.

    Returns:
        A JSON string containing the compiled competitive report data.
    """
    from app.tools import get_session_data
    res = get_session_data(session_id=session_id)
    return json.dumps(res, indent=2)


def list_available_sessions() -> str:
    """Lists all target company profiles currently available in the database.

    Returns:
        A JSON string with a list of profiled companies.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT session_id FROM (
                SELECT session_id FROM company_profiles
                UNION ALL
                SELECT session_id FROM company_financials
                UNION ALL
                SELECT session_id FROM company_news
                UNION ALL
                SELECT session_id FROM pricing_information
            )
            WHERE session_id IS NOT NULL AND session_id != ''
            GROUP BY session_id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        sessions = [r[0] for r in rows]
        return json.dumps(sessions)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        conn.close()


chat_agent = LlmAgent(
    name="ChatCopilotAgent",
    model=Gemini(
        model=GEMINI_MODEL_SMALL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=chat_copilot_instruction,
    tools=[google_search, get_database_session_data, list_available_sessions],
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(include_server_side_tool_invocations=True)
    ),
)
