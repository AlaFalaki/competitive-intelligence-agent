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

from app.config import load_instruction, GEMINI_MODEL_SMALL
from app.tools import record_pricing_not_found, save_pricing_info, scrape_web_page

# Load the Pricing Analysis Agent instructions
pricing_analysis_instruction = load_instruction("pricing_analysis.md")

# Pricing Analysis Agent: Performs the pricing research by invoking the instructions
pricing_analysis_agent = LlmAgent(
    name="PricingAnalysisAgent",
    model=Gemini(
        model=GEMINI_MODEL_SMALL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=pricing_analysis_instruction
    + "\n\nAnalyze pricing for the company '{company_name}' and its competitors.",
    # Enable google_search, web scraping, and SQLite saving/logging
    tools=[
        google_search,
        scrape_web_page,
        save_pricing_info,
        record_pricing_not_found,
    ],
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(include_server_side_tool_invocations=True)
    ),
)
