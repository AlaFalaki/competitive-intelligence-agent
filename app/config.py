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

import logging
import os
from dotenv import load_dotenv
import google.auth

# Load .env from the agent project root directory (parent of app/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, ".env"))

# Load central model configurations
GEMINI_MODEL_SMALL = os.environ.get("GEMINI_MODEL_SAMLL", os.environ.get("GEMINI_MODEL_SMALL", "gemini-3.1-flash-lite"))
GEMINI_MODEL_LARGE = os.environ.get("GEMINI_MODEL_LARGE", "gemini-3.5-flash")

# Check if GOOGLE_API_KEY is provided (for Google AI Studio mode)
if os.environ.get("GOOGLE_API_KEY"):
    # Instruct the ADK GenAI client to use Google AI Studio
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
else:
    # Default to Google Cloud Vertex AI (which requires Application Default Credentials)
    try:
        _, project_id = google.auth.default()
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    except Exception:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "mock-project")
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

from app.db import run_migrations

# Run database migrations
run_migrations()

# Silence the harmless warning from the google-genai SDK about Automatic Function Calling (AFC) being
# disabled when combining built-in tools (like google_search) with custom Python callables.
# ADK implements and manages its own function execution loop independently.
logging.getLogger("google.genai").setLevel(logging.ERROR)


def load_instruction(filename: str) -> str:
    """Helper to load system instruction content from the instructions directory."""
    import pathlib

    path = pathlib.Path(__file__).parent / "instructions" / filename
    with open(path, encoding="utf-8") as f:
        return f.read()
