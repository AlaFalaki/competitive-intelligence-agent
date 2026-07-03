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
from google.genai import types

from app.config import load_instruction, GEMINI_MODEL_SMALL
from app.tools import fetch_sec_filings, save_company_financials

# Load the SEC Filing Agent instructions
sec_filing_instruction = load_instruction("sec_filing.md")

# SEC Filing Agent: Performs the SEC data gathering and analysis
sec_filing_agent = LlmAgent(
    name="SecFilingAgent",
    model=Gemini(
        model=GEMINI_MODEL_SMALL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=sec_filing_instruction
    + "\n\nAnalyze SEC filings for the company '{company_name}' and its competitors.",
    # Enable fetching and saving tools
    tools=[fetch_sec_filings, save_company_financials],
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(include_server_side_tool_invocations=True)
    ),
)
