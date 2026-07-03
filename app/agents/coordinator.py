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
from pydantic import BaseModel, Field

from app.config import GEMINI_MODEL_LARGE


class CoordinatorOutput(BaseModel):
    company_name: str = Field(description="The name of the company to profile.")


coordinator = LlmAgent(
    name="Coordinator",
    model=Gemini(
        model=GEMINI_MODEL_LARGE,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="Extract the name of the company that the user wants to profile from the query. Respond ONLY with the company name under the company_name schema field.",
    output_schema=CoordinatorOutput,
    output_key="company_name_state",
)
