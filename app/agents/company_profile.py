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

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.genai import types

from app.config import load_instruction, GEMINI_MODEL_SMALL
from app.tools import save_company_profile

# Load the Company Profile Agent instructions
company_profile_instruction = load_instruction("company_profile.md")


# Callback to extract the company name from Coordinator's structured output
# and save it to the session state so it can be dynamically injected.
async def extract_company_name_callback(callback_context: CallbackContext) -> None:
    company_data = callback_context.state.get("company_name_state", {})
    if isinstance(company_data, dict):
        callback_context.state["company_name"] = company_data.get("company_name", "")
    else:
        callback_context.state["company_name"] = str(company_data)


# Company Profile Agent: Performs the profiling by invoking the instructions
company_profile_agent = LlmAgent(
    name="CompanyProfileAgent",
    model=Gemini(
        model=GEMINI_MODEL_SMALL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=company_profile_instruction + "\n\nProfile the company: {company_name}",
    # Enable google_search grounding and SQLite saving
    tools=[google_search, save_company_profile],
    before_agent_callback=extract_company_name_callback,
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(include_server_side_tool_invocations=True)
    ),
)
