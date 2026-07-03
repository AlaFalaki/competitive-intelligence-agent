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

"""Model Context Protocol (MCP) Server for Competitive Intelligence.

Exposes proprietary, non-public market intelligence reports and M&A rumors
to the agent via stdio JSON-RPC 2.0.
"""

import json
import sys

# Mock proprietary internal reports database
PROPRIETARY_REPORTS = {
    "google": (
        "PROPRIETARY RESEARCH - CONFIDENTIAL\n"
        "Target: Alphabet Inc. (Google)\n"
        "Internal Analysis Code: G-INT-99\n"
        "Key Insights:\n"
        "1. Project 'VibeFlow' is expected to enter beta in Q4 2026. This is a multi-agent "
        "autonomous workflow engine built specifically for Vertex AI enterprise clients.\n"
        "2. Rumor: Google is planning to expand its infrastructure capital expenditures by "
        "another 15% YoY, specifically targeting custom TPU v6 pods for agentic training.\n"
        "3. Margin Forecast: Core Search margins remain strong at 56%, but Cloud Agentic "
        "services are operating at a temporary gross margin deficit of -5% due to hardware scaling costs."
    ),
    "microsoft": (
        "PROPRIETARY RESEARCH - CONFIDENTIAL\n"
        "Target: Microsoft Corp.\n"
        "Internal Analysis Code: MS-INT-42\n"
        "Key Insights:\n"
        "1. Azure AI Agents are transitioning to a hybrid local/cloud orchestration model "
        "leveraging local NPUs on Copilot+ PCs to offload up to 30% of standard LLM tasks.\n"
        "2. M&A Rumor: Microsoft is actively evaluating the acquisition of an open-source "
        "MCP connector ecosystem company to solidify its position in agent communication protocol standards.\n"
        "3. Gross Margin projection for Azure Agentic Workflows: Expected to reach 65% by "
        "mid-2027 as hardware efficiency gains are realized."
    ),
    "apple": (
        "PROPRIETARY RESEARCH - CONFIDENTIAL\n"
        "Target: Apple Inc.\n"
        "Internal Analysis Code: AP-INT-07\n"
        "Key Insights:\n"
        "1. Apple Intelligence Server Side (PCC) is preparing for 'Agent-OS' release in iOS 20. "
        "This features full-action delegation tools that execute local shell commands sandboxed on-device.\n"
        "2. Supply Chain Insight: Silicon orders for 3nm chips have increased by 20%, showing "
        "Apple expects massive demand for agent-heavy devices.\n"
        "3. Services division margin is forecasted to hit a record 74.5% due to high adoption "
        "of agent-curated app marketplace subscriptions."
    ),
}


def log(msg: str):
    """Log helper to print debug logs to stderr (since stdout is used for JSON-RPC)."""
    sys.stderr.write(f"[MCP LOG] {msg}\n")
    sys.stderr.flush()


def main():
    log("Competitive Intelligence MCP Server started.")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            req_id = req.get("id")

            log(f"Received request: {method} (id: {req_id})")

            # Handle JSON-RPC Initialize
            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "comp-intel-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            # Handle Initialize Notification
            elif method == "notifications/initialized":
                # No response needed for notification
                continue
            # List Tools
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": "get_proprietary_market_insights",
                                "description": (
                                    "Retrieve internal, proprietary corporate intelligence research reports "
                                    "and M&A rumors for a specific target company. Use this to supplement "
                                    "public web searches."
                                ),
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "company_name": {
                                            "type": "string",
                                            "description": "The name of the company to query proprietary research for."
                                        }
                                    },
                                    "required": ["company_name"]
                                }
                            }
                        ]
                    }
                }
            # Call Tool
            elif method == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                company_name = arguments.get("company_name", "").lower()

                log(f"Calling tool: {tool_name} with args: {arguments}")

                if tool_name == "get_proprietary_market_insights":
                    # Simple fuzzy matching
                    matched_key = None
                    for key in PROPRIETARY_REPORTS.keys():
                        if key in company_name or company_name in key:
                            matched_key = key
                            break

                    if matched_key:
                        report_content = PROPRIETARY_REPORTS[matched_key]
                    else:
                        report_content = (
                            f"No internal proprietary research found for company: '{arguments.get('company_name')}'."
                        )

                    resp = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": report_content
                                }
                            ]
                        }
                    }
                else:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: tool {tool_name}"
                        }
                    }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

            # Write JSON-RPC response
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        except Exception as e:
            log(f"Error handling request: {e}")
            # Send standard JSON-RPC parse/internal error if possible
            try:
                err_resp = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {e}"
                    }
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
            except Exception:
                pass


if __name__ == "__main__":
    main()
