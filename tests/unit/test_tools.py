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

import os
from unittest.mock import MagicMock, patch

import app.db
import app.tools
from app.db import get_db_connection, run_migrations
from app.tools import (
    fetch_sec_filings,
    get_company_competitors,
    get_company_financials,
    get_company_news,
    get_company_profile,
    record_pricing_not_found,
    save_company_competitors,
    save_company_financials,
    save_company_news,
    save_company_profile,
    save_pricing_info,
    scrape_web_page,
)


def test_sqlite_saving_and_retrieval(tmp_path) -> None:
    """Test SQLite database migrations, saving, and retrieval tools with a temporary database."""
    # Temporarily override DB_PATH in app.db to use a temporary DB for isolation
    original_db_path_db = app.db.DB_PATH

    temp_db = os.path.join(tmp_path, "test_comp_intel.db")
    app.db.DB_PATH = temp_db

    try:
        # Run database migrations to set up the schema in our temp database
        run_migrations()

        # Mock tool context for capturing session run ids
        mock_tool_context = MagicMock()
        mock_tool_context.session.id = "test-run-session-123"
        mock_tool_context.state = {}

        # 1. Test get_company_profile when not exists
        res = get_company_profile("Nonexistent LLC")
        assert res["status"] == "not_found"

        # 2. Test save_company_profile
        save_res = save_company_profile(
            name="Test Corp",
            industry="Software",
            description="Testing tools",
            headquarters="New York, NY",
            website="https://testcorp.com",
            tool_context=mock_tool_context,
            additional_info="Some extra details",
        )
        assert save_res["status"] == "success"

        # Verify session_id was saved to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT session_id FROM company_profiles WHERE name = 'Test Corp'"
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "test-run-session-123"
        conn.close()

        # 3. Test retrieval after save
        get_res = get_company_profile("Test Corp")
        assert get_res["status"] == "success"
        assert get_res["profile"]["name"] == "Test Corp"
        assert get_res["profile"]["industry"] == "Software"
        assert get_res["profile"]["description"] == "Testing tools"
        assert get_res["profile"]["headquarters"] == "New York, NY"
        assert get_res["profile"]["website"] == "https://testcorp.com"
        assert get_res["profile"]["additional_info"] == "Some extra details"

        # 4. Test save_company_competitors and verify state/DB save
        competitors_list = [
            {"competitor_name": "Comp A", "description": "Direct competitor"},
            {"competitor_name": "Comp B", "description": "Indirect competitor"},
        ]

        save_comp_res = save_company_competitors(
            company_name="Test Corp",
            competitors=competitors_list,
            tool_context=mock_tool_context,
        )
        assert save_comp_res["status"] == "success"

        # Verify state was updated
        assert mock_tool_context.state["discovered_competitors"] == competitors_list

        # Verify session_id was saved to DB for competitors
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT session_id FROM competitors WHERE company_name = 'Test Corp'"
        )
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "test-run-session-123"
        conn.close()

        # 5. Test retrieve competitors from database
        get_comp_res = get_company_competitors("Test Corp")
        assert get_comp_res["status"] == "success"
        assert len(get_comp_res["competitors"]) == 2
        assert get_comp_res["competitors"][0]["competitor_name"] == "Comp A"
        assert get_comp_res["competitors"][0]["description"] == "Direct competitor"
        assert get_comp_res["competitors"][1]["competitor_name"] == "Comp B"
        assert get_comp_res["competitors"][1]["description"] == "Indirect competitor"

        # 6. Test scrape_web_page (with mock HTTP response)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = (
            "<html><nav>Navbar</nav><body><h1>Pricing</h1><p>Pro: $10/mo</p>"
            "<script>alert(1)</script></body></html>"
        )

        with patch("httpx.get", return_value=mock_response):
            scrape_res = scrape_web_page("https://testcorp.com/pricing")
            assert scrape_res["status"] == "success"
            # It should extract clean text from the HTML, ignoring scripts and navs
            assert "Pricing" in scrape_res["content"]
            assert "Pro: $10/mo" in scrape_res["content"]
            assert "Navbar" not in scrape_res["content"]

        # 7. Test save_pricing_info
        plans_data = '{"plans": [{"tier": "Pro", "price": "$10/mo"}]}'
        save_price_res = save_pricing_info(
            company_name="Test Corp",
            pricing_page_url="https://testcorp.com/pricing",
            raw_page_content="Pricing: Pro: $10/mo",
            plans_json=plans_data,
            tool_context=mock_tool_context,
        )
        assert save_price_res["status"] == "success"

        # Verify database save & session ID
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pricing_page_url, plans_json, session_id FROM pricing_information WHERE company_name = 'Test Corp'"
        )
        price_row = cursor.fetchone()
        assert price_row is not None
        assert price_row[0] == "https://testcorp.com/pricing"
        assert price_row[1] == plans_data
        assert price_row[2] == "test-run-session-123"
        conn.close()

        # Verify tool_context state has pricing data
        assert mock_tool_context.state["pricing_data"]["Test Corp"] == plans_data

        # 8. Test record_pricing_not_found
        save_not_found = record_pricing_not_found(
            company_name="Comp A",
            tool_context=mock_tool_context,
        )
        assert save_not_found["status"] == "success"

        # Verify not found saved in state
        assert mock_tool_context.state["pricing_data"]["Comp A"] == "Not Found"

        # 9. Test SEC tools (with mock HTTP responses)
        def mock_sec_get(url, *args, **kwargs):
            m = MagicMock()
            m.status_code = 200
            if "company_tickers.json" in url:
                m.json.return_value = {
                    "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
                }
            elif "companyfacts" in url:
                m.json.return_value = {
                    "facts": {
                        "us-gaap": {
                            "Revenues": {
                                "units": {
                                    "USD": [
                                        {
                                            "form": "10-K",
                                            "val": 1000000,
                                            "fy": 2025,
                                            "fp": "FY",
                                            "end": "2025-12-31",
                                        }
                                    ]
                                }
                            },
                            "Assets": {
                                "units": {
                                    "USD": [
                                        {
                                            "form": "10-K",
                                            "val": 5000000,
                                            "fy": 2025,
                                            "fp": "FY",
                                            "end": "2025-12-31",
                                        }
                                    ]
                                }
                            },
                            "NetIncomeLoss": {
                                "units": {
                                    "USD": [
                                        {
                                            "form": "10-K",
                                            "val": 200000,
                                            "fy": 2025,
                                            "fp": "FY",
                                            "end": "2025-12-31",
                                        }
                                    ]
                                }
                            },
                        }
                    }
                }
            return m

        with patch("httpx.get", side_effect=mock_sec_get):
            sec_res = fetch_sec_filings("AAPL")
            assert sec_res["status"] == "success"
            assert sec_res["cik"] == "0000320193"
            assert len(sec_res["historical_metrics"]) == 1
            assert sec_res["historical_metrics"][0]["fiscal_year"] == 2025
            assert sec_res["historical_metrics"][0]["metrics"]["revenue"] == 1000000
            assert (
                sec_res["historical_metrics"][0]["metrics"]["total_assets"] == 5000000
            )
            assert sec_res["historical_metrics"][0]["metrics"]["net_income"] == 200000

        # 10. Test save_company_financials
        save_fin_res = save_company_financials(
            company_name="Apple Inc.",
            cik="0000320193",
            filing_data_json='[{"fiscal_year": 2025, "metrics": {"revenue": 1000000}}]',
            tool_context=mock_tool_context,
        )
        assert save_fin_res["status"] == "success"

        # Verify database save
        get_fin_res = get_company_financials("Apple Inc.")
        assert get_fin_res["status"] == "success"
        assert get_fin_res["financials"]["cik"] == "0000320193"
        assert (
            get_fin_res["financials"]["filing_data_json"]
            == '[{"fiscal_year": 2025, "metrics": {"revenue": 1000000}}]'
        )

        # Verify state save
        assert (
            mock_tool_context.state["company_financials"]["Apple Inc."]["cik"]
            == "0000320193"
        )
        assert (
            mock_tool_context.state["company_financials"]["Apple Inc."][
                "filing_data_json"
            ]
            == '[{"fiscal_year": 2025, "metrics": {"revenue": 1000000}}]'
        )

        # 11. Test save_company_news
        save_news_res = save_company_news(
            company_name="Apple Inc.",
            news_summary="Apple launched a new iPhone and acquired a startup.",
            tool_context=mock_tool_context,
        )
        assert save_news_res["status"] == "success"

        # Verify database save
        get_news_res = get_company_news("Apple Inc.")
        assert get_news_res["status"] == "success"
        assert (
            get_news_res["news_summary"]
            == "Apple launched a new iPhone and acquired a startup."
        )

        # Verify state save
        assert (
            mock_tool_context.state["company_news"]["Apple Inc."]
            == "Apple launched a new iPhone and acquired a startup."
        )

    finally:
        # Restore original DB_PATH
        app.db.DB_PATH = original_db_path_db
