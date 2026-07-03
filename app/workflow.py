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
from google.adk.workflow import JoinNode, Workflow
from google.adk.agents.context import Context

from app.agents import (
    company_profile_agent,
    competitor_discovery_agent,
    coordinator,
    news_research_agent,
    pricing_analysis_agent,
    sec_filing_agent,
    master_report_agent,
)
from app.tools import get_session_data, get_db_connection

# JoinNode to fan-in parallel branches
join_node = JoinNode(name="merge_analysis")


def load_db_data_node(ctx: Context, node_input: dict) -> str:
    """Loads all consolidated competitor data from the database and inserts it into the state."""
    data = get_session_data(session_id=ctx.session.id)
    ctx.state["session_data"] = json.dumps(data, indent=2)
    return "Consolidated session data loaded."


def save_master_report_node(ctx: Context, node_input: dict) -> str:
    """Saves the final generated pydantic master report JSON back to SQLite database."""
    session_id = ctx.session.id
    report_json = json.dumps(node_input)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO master_reports (session_id, report_json) VALUES (?, ?)",
        (session_id, report_json),
    )
    conn.commit()
    conn.close()

    return "Analysis and master report generation complete."


# Graph Workflow: Coordinator -> CompanyProfile -> CompetitorDiscovery
# Then fan-out to PricingAnalysis, SecFiling, and NewsResearch in parallel, join,
# load db data, generate master report, and save.
root_agent = Workflow(
    name="competitive_intelligence_workflow",
    edges=[
        ("START", coordinator),
        (coordinator, company_profile_agent),
        (company_profile_agent, competitor_discovery_agent),
        (
            competitor_discovery_agent,
            (pricing_analysis_agent, sec_filing_agent, news_research_agent),
        ),
        (
            (pricing_analysis_agent, sec_filing_agent, news_research_agent),
            join_node,
        ),
        (join_node, load_db_data_node),
        (load_db_data_node, master_report_agent),
        (master_report_agent, save_master_report_node),
    ],
)
