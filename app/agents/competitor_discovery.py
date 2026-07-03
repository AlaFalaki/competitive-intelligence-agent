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
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.genai import types

from app.config import load_instruction, GEMINI_MODEL_LARGE
from app.tools import save_company_competitors

# Load the Competitor Discovery Agent instructions
competitor_discovery_instruction = load_instruction("competitor_discovery.md")

# Competitor Discovery Agent: Performs the discovery by invoking the instructions
competitor_discovery_agent = LlmAgent(
    name="CompetitorDiscoveryAgent",
    model=Gemini(
        model=GEMINI_MODEL_LARGE,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=competitor_discovery_instruction
    + "\n\nFind competitors for the company: {company_name}",
    # Enable google_search grounding and SQLite saving
    tools=[google_search, save_company_competitors],
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(include_server_side_tool_invocations=True)
    ),
)
