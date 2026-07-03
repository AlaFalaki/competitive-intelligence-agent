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


import httpx
from bs4 import BeautifulSoup
from google.adk.tools import ToolContext

from app.db import get_db_connection


def save_company_profile(
    name: str,
    industry: str,
    description: str,
    headquarters: str,
    website: str,
    tool_context: ToolContext | None = None,
    additional_info: str | None = None,
) -> dict:
    """Saves the company profile information to the SQLite database.

    Args:
        name: The name of the company.
        industry: The industry the company operates in.
        description: A brief description of the company.
        headquarters: The headquarters location of the company.
        website: The company's official website URL.
        additional_info: Any other useful information for competitive analysis.

    Returns:
        A dict indicating success or error.
    """
    try:
        session_id = (
            tool_context.session.id
            if tool_context and tool_context.session
            else "test-session"
        )
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert or replace company profile
        cursor.execute(
            """
            INSERT OR REPLACE INTO company_profiles
            (name, industry, description, headquarters, website, additional_info, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                name,
                industry,
                description,
                headquarters,
                website,
                additional_info,
                session_id,
            ),
        )

        conn.commit()
        conn.close()
        return {
            "status": "success",
            "message": f"Successfully saved company profile for {name}.",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save profile: {e}"}


def get_company_profile(name: str) -> dict:
    """Retrieves the company profile information from the SQLite database.

    Args:
        name: The name of the company to query.

    Returns:
        A dict with the company profile or an error/not found message.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name, industry, description, headquarters, website, additional_info FROM company_profiles WHERE name = ?",
            (name,),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "status": "success",
                "profile": {
                    "name": row[0],
                    "industry": row[1],
                    "description": row[2],
                    "headquarters": row[3],
                    "website": row[4],
                    "additional_info": row[5],
                },
            }
        else:
            return {
                "status": "not_found",
                "message": f"No profile found for company {name}.",
            }
    except Exception as e:
        return {"status": "error", "message": f"Failed to query profile: {e}"}


def save_company_competitors(
    company_name: str,
    competitors: list[dict],
    tool_context: ToolContext | None = None,
) -> dict:
    """Saves the identified competitors to the SQLite database and session state.

    Args:
        company_name: The name of the company.
        competitors: A list of dicts, where each dict has keys 'competitor_name' and 'description' of the competitor.

    Returns:
        A dict indicating success or error.
    """
    try:
        session_id = (
            tool_context.session.id
            if tool_context and tool_context.session
            else "test-session"
        )
        conn = get_db_connection()
        cursor = conn.cursor()

        # Save to database
        for comp in competitors:
            comp_name = comp.get("competitor_name")
            desc = comp.get("description", "")
            cursor.execute(
                """
                INSERT OR REPLACE INTO competitors (company_name, competitor_name, description, session_id)
                VALUES (?, ?, ?, ?)
            """,
                (company_name, comp_name, desc, session_id),
            )

        conn.commit()
        conn.close()

        # Save to session state for the workflow
        if tool_context:
            tool_context.state["discovered_competitors"] = competitors

        return {
            "status": "success",
            "message": f"Successfully saved {len(competitors)} competitors for {company_name}.",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save competitors: {e}"}


def get_company_competitors(company_name: str) -> dict:
    """Retrieves the list of competitors for a company from the SQLite database.

    Args:
        company_name: The name of the company to query.

    Returns:
        A dict with the list of competitors or an error message.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT competitor_name, description FROM competitors WHERE company_name = ?
        """,
            (company_name,),
        )
        rows = cursor.fetchall()
        conn.close()

        competitors = [{"competitor_name": r[0], "description": r[1]} for r in rows]
        return {"status": "success", "competitors": competitors}
    except Exception as e:
        return {"status": "error", "message": f"Failed to query competitors: {e}"}


def scrape_web_page(url: str) -> dict:
    """Fetches a web page URL and extracts the main text content.

    Args:
        url: The URL of the web page to fetch.

    Returns:
        A dict with the status and cleaned text content.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        # Follow redirects, timeout 10 seconds
        response = httpx.get(url, headers=headers, follow_redirects=True, timeout=10.0)

        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Failed to fetch page, HTTP status: {response.status_code}",
            }

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove navigation, headers, footers, scripts, styles to keep only core text
        for element in soup(["script", "style", "nav", "footer", "header", "iframe"]):
            element.decompose()

        # Extract text and clean up whitespace
        text = soup.get_text(separator="\n")
        cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(cleaned_lines)

        # Truncate text to avoid hitting context window limits
        if len(cleaned_text) > 12000:
            cleaned_text = cleaned_text[:12000] + "\n...[Content Truncated]..."

        return {"status": "success", "url": url, "content": cleaned_text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def save_pricing_info(
    company_name: str,
    pricing_page_url: str,
    raw_page_content: str,
    plans_json: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """Saves the extracted pricing information to the SQLite database and session state.

    Args:
        company_name: The name of the company.
        pricing_page_url: The URL of the pricing page.
        raw_page_content: The scraped text content of the page.
        plans_json: The JSON string representing the extracted plans and prices.

    Returns:
        A dict indicating success or error.
    """
    try:
        session_id = (
            tool_context.session.id
            if tool_context and tool_context.session
            else "test-session"
        )
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO pricing_information
            (company_name, pricing_page_url, raw_page_content, plans_json, session_id)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                company_name,
                pricing_page_url,
                raw_page_content,
                plans_json,
                session_id,
            ),
        )

        conn.commit()
        conn.close()

        # Store in shared session state
        if tool_context:
            pricing_data = tool_context.state.get("pricing_data", {})
            pricing_data[company_name] = plans_json
            tool_context.state["pricing_data"] = pricing_data

        return {
            "status": "success",
            "message": f"Successfully saved pricing for {company_name}.",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save pricing: {e}"}


def record_pricing_not_found(
    company_name: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """Records that pricing information was not found in the shared state and database.

    Args:
        company_name: The name of the company.

    Returns:
        A dict indicating success or error.
    """
    try:
        session_id = (
            tool_context.session.id
            if tool_context and tool_context.session
            else "test-session"
        )
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO pricing_information
            (company_name, pricing_page_url, raw_page_content, plans_json, session_id)
            VALUES (?, ?, ?, ?, ?)
        """,
            (company_name, "Not Found", "Not Found", "Not Found", session_id),
        )

        conn.commit()
        conn.close()

        # Store in shared session state
        if tool_context:
            pricing_data = tool_context.state.get("pricing_data", {})
            pricing_data[company_name] = "Not Found"
            tool_context.state["pricing_data"] = pricing_data

        return {
            "status": "success",
            "message": f"Recorded pricing as Not Found for {company_name}.",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to record not found status: {e}"}


def lookup_cik(company_name: str) -> str | None:
    """Helper to lookup a company CIK using the SEC tickers map."""
    headers = {"User-Agent": "ResearchAgent admin@competitive-intelligence-agent.local"}
    try:
        r = httpx.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=headers,
            timeout=10.0,
        )
        if r.status_code == 200:
            data = r.json()
            company_name_lower = company_name.lower()
            # Try exact ticker match first
            for item in data.values():
                if item.get("ticker", "").lower() == company_name_lower:
                    return str(item.get("cik_str")).zfill(10)
            # Try substring name match
            for item in data.values():
                if company_name_lower in item.get("title", "").lower():
                    return str(item.get("cik_str")).zfill(10)
    except Exception as e:
        print(f"SEC CIK lookup error: {e}")
    return None


def fetch_sec_filings(company_name: str) -> dict:
    """Fetches historical SEC EDGAR financial metrics for a company by lookup.

    Args:
        company_name: The ticker or name of the company.

    Returns:
        A dict with the CIK and the parsed historical metrics list.
    """
    cik = lookup_cik(company_name)
    if not cik:
        return {
            "status": "not_found",
            "message": f"Could not locate CIK for company {company_name}.",
        }

    headers = {"User-Agent": "ResearchAgent admin@competitive-intelligence-agent.local"}

    try:
        # Fetch company facts (XBRL data)
        facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        facts_r = httpx.get(facts_url, headers=headers, timeout=20.0)
        if facts_r.status_code != 200:
            return {
                "status": "error",
                "message": f"Failed to fetch company facts for CIK {cik} (status {facts_r.status_code}).",
            }
        facts = facts_r.json()

        # Define US-GAAP tags mapping for each metric
        concepts_map = {
            "revenue": [
                "Revenues",
                "SalesRevenueNet",
                "RevenueFromContractWithCustomerExcludingAssessedTax",
                "SalesRevenueGoodsNet",
            ],
            "gross_profit": ["GrossProfit"],
            "operating_income": ["OperatingIncomeLoss"],
            "net_income": [
                "NetIncomeLoss",
                "NetIncomeLossAvailableToCommonStockholdersBasic",
            ],
            "cash": ["CashAndCashEquivalentsAtCarryingValue"],
            "inventory": ["InventoryNet", "Inventories"],
            "accounts_receivable": [
                "AccountsReceivableNetCurrent",
                "AccountsReceivableNet",
            ],
            "total_assets": ["Assets"],
            "total_debt": [
                "LongTermDebt",
                "LongTermDebtNoncurrent",
                "DebtCurrent",
                "ShortTermBorrowings",
            ],
            "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
            "capital_expenditures": ["PaymentsToAcquirePropertyPlantAndEquipment"],
            "r_and_d_expense": ["ResearchAndDevelopmentExpense"],
            "shares_outstanding": [
                "EntityCommonStockSharesOutstanding",
                "WeightedAverageNumberOfSharesOutstandingBasic",
            ],
        }

        # Find the available fiscal years in the facts
        years = set()
        for concept in ["Assets", "NetIncomeLoss", "Revenues"]:
            if concept in facts.get("facts", {}).get("us-gaap", {}):
                concept_data = facts["facts"]["us-gaap"][concept]
                for unit in concept_data.get("units", {}).values():
                    for entry in unit:
                        if entry.get("form") == "10-K" and entry.get("fy"):
                            years.add(entry.get("fy"))

        sorted_years = sorted(years, reverse=True)
        if not sorted_years:
            return {
                "status": "not_found",
                "message": f"No fiscal years found in 10-K data for CIK {cik}.",
            }

        # Take the last two fiscal years
        target_years = sorted_years[:2]

        historical_metrics = []
        for fy in target_years:
            year_data = {"fiscal_year": fy, "metrics": {}}
            for metric_name, tags in concepts_map.items():
                best_val = None
                best_end = None
                for tag in tags:
                    if tag in facts.get("facts", {}).get("us-gaap", {}):
                        tag_data = facts["facts"]["us-gaap"][tag]
                        for unit in tag_data.get("units", {}).values():
                            for entry in unit:
                                if (
                                    entry.get("form") == "10-K"
                                    and entry.get("fy") == fy
                                ):
                                    if entry.get("fp") == "FY" or not entry.get("fp"):
                                        if (
                                            best_val is None
                                            or entry.get("end", "") > best_end
                                        ):
                                            best_val = entry.get("val")
                                            best_end = entry.get("end", "")
                year_data["metrics"][metric_name] = best_val
                if best_end and "end_date" not in year_data:
                    year_data["end_date"] = best_end

            # Calculate Free Cash Flow dynamically if OCF and Capex are available
            ocf = year_data["metrics"].get("operating_cash_flow")
            capex = year_data["metrics"].get("capital_expenditures")
            if ocf is not None and capex is not None:
                year_data["metrics"]["free_cash_flow"] = ocf - capex
            else:
                year_data["metrics"]["free_cash_flow"] = None

            historical_metrics.append(year_data)

        return {
            "status": "success",
            "cik": cik,
            "historical_metrics": historical_metrics,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def save_company_financials(
    company_name: str,
    cik: str,
    filing_data_json: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """Saves the extracted company financials to the SQLite database and session state.

    Args:
        company_name: The name of the company.
        cik: The Central Index Key (CIK) of the company.
        filing_data_json: The JSON string representing the extracted metrics list.

    Returns:
        A dict indicating success or error.
    """
    try:
        session_id = (
            tool_context.session.id
            if tool_context and tool_context.session
            else "test-session"
        )
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO company_financials
            (company_name, cik, filing_data_json, session_id)
            VALUES (?, ?, ?, ?)
        """,
            (company_name, cik, filing_data_json, session_id),
        )

        conn.commit()
        conn.close()

        # Save to session state for the workflow
        if tool_context:
            fin_data = tool_context.state.get("company_financials", {})
            fin_data[company_name] = {
                "cik": cik,
                "filing_data_json": filing_data_json,
            }
            tool_context.state["company_financials"] = fin_data

        return {
            "status": "success",
            "message": f"Successfully saved company financials for {company_name}.",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save company financials: {e}"}


def get_company_financials(company_name: str) -> dict:
    """Retrieves the company financials from the SQLite database.

    Args:
        company_name: The name of the company to query.

    Returns:
        A dict with the company financials or an error/not found message.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT cik, filing_data_json FROM company_financials WHERE company_name = ?
        """,
            (company_name,),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "status": "success",
                "financials": {
                    "cik": row[0],
                    "filing_data_json": row[1],
                },
            }
        else:
            return {
                "status": "not_found",
                "message": f"No financials found for company {company_name}.",
            }
    except Exception as e:
        return {"status": "error", "message": f"Failed to query financials: {e}"}


def save_company_news(
    company_name: str,
    news_summary: str,
    tool_context: ToolContext | None = None,
) -> dict:
    """Saves the compiled news summary to the SQLite database and session state.

    Args:
        company_name: The name of the company.
        news_summary: The compiled news summary content.

    Returns:
        A dict indicating success or error.
    """
    try:
        session_id = (
            tool_context.session.id
            if tool_context and tool_context.session
            else "test-session"
        )
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO company_news (company_name, news_summary, session_id)
            VALUES (?, ?, ?)
        """,
            (company_name, news_summary, session_id),
        )

        conn.commit()
        conn.close()

        # Save to session state for the workflow
        if tool_context:
            news_data = tool_context.state.get("company_news", {})
            news_data[company_name] = news_summary
            tool_context.state["company_news"] = news_data

        return {
            "status": "success",
            "message": f"Successfully saved news summary for {company_name}.",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save news: {e}"}


def get_company_news(company_name: str) -> dict:
    """Retrieves the news summary from the SQLite database.

    Args:
        company_name: The name of the company to query.

    Returns:
        A dict with the news summary or an error/not found message.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT news_summary FROM company_news WHERE company_name = ?
        """,
            (company_name,),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "status": "success",
                "news_summary": row[0],
            }
        else:
            return {
                "status": "not_found",
                "message": f"No news summary found for company {company_name}.",
            }
    except Exception as e:
        return {"status": "error", "message": f"Failed to query news: {e}"}


def get_session_data(session_id: str | None = None, tool_context: ToolContext | None = None) -> dict:
    """Retrieves all gathered profile, competitors, pricing, financials, and news data from the SQLite database for the current analysis session.

    Returns:
        A dictionary containing consolidated market intelligence data for the target company and its competitors.
    """
    import json
    try:
        if not session_id:
            session_id = (
                tool_context.session.id
                if tool_context and tool_context.session
                else "test-session"
            )
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Fetch Profile
        cursor.execute(
            "SELECT name, industry, description, headquarters, website, additional_info FROM company_profiles WHERE session_id = ?",
            (session_id,),
        )
        p_row = cursor.fetchone()
        if not p_row:
            conn.close()
            return {"status": "error", "message": f"No profile found for session {session_id}"}

        company_name = p_row[0]
        profile = {
            "name": p_row[0],
            "industry": p_row[1],
            "description": p_row[2],
            "headquarters": p_row[3],
            "website": p_row[4],
            "additional_info": p_row[5],
        }

        # 2. Fetch Competitors
        cursor.execute(
            "SELECT competitor_name FROM competitors WHERE session_id = ?",
            (session_id,),
        )
        competitor_list = [row[0] for row in cursor.fetchall()]

        # 3. Fetch Pricing
        cursor.execute(
            "SELECT company_name, pricing_page_url, plans_json FROM pricing_information WHERE session_id = ?",
            (session_id,),
        )
        db_pricing = cursor.fetchall()
        db_pr_names = [row[0] for row in db_pricing]
        
        def find_matching_company(name, db_names):
            if not name or not db_names:
                return None
            n_clean = name.lower().replace(",", "").replace(".", "").replace("llc", "").replace("inc", "").replace("corp", "").replace("corporation", "").strip()
            for db_name in db_names:
                db_clean = db_name.lower().replace(",", "").replace(".", "").replace("llc", "").replace("inc", "").replace("corp", "").replace("corporation", "").strip()
                if db_clean in n_clean or n_clean in db_clean:
                    return db_name
                w_n = [w for w in n_clean.split() if w not in ("(amd)", "(alphabet)", "(intel)", "google", "alphabet")]
                w_db = [w for w in db_clean.split() if w not in ("google", "alphabet")]
                if w_n and w_db and w_n[0] == w_db[0]:
                    return db_name
            return None

        pricing = {}
        companies_to_query = [company_name] + competitor_list
        for c in companies_to_query:
            match = find_matching_company(c, db_pr_names)
            if match:
                pr_row = [r for r in db_pricing if r[0] == match][0]
                try:
                    plans = json.loads(pr_row[2])
                except Exception:
                    plans = pr_row[2]
                pricing[c] = {"pricing_page_url": pr_row[1], "plans": plans}

        # 4. Fetch Financials
        cursor.execute(
            "SELECT company_name, cik, filing_data_json FROM company_financials WHERE session_id = ?",
            (session_id,),
        )
        db_financials = cursor.fetchall()
        db_fin_names = [row[0] for row in db_financials]
        
        financials = {}
        for c in companies_to_query:
            match = find_matching_company(c, db_fin_names)
            if match:
                f_row = [r for r in db_financials if r[0] == match][0]
                try:
                    filing_data = json.loads(f_row[2])
                except Exception:
                    filing_data = []
                financials[c] = {"cik": f_row[1], "filing_data": filing_data}

        # 5. Fetch News
        cursor.execute(
            "SELECT company_name, news_summary FROM company_news WHERE session_id = ?",
            (session_id,),
        )
        db_news = cursor.fetchall()
        db_news_names = [row[0] for row in db_news]
        
        news = {}
        for c in companies_to_query:
            match = find_matching_company(c, db_news_names)
            if match:
                n_row = [r for r in db_news if r[0] == match][0]
                news[c] = n_row[1]

        conn.close()
        return {
            "status": "success",
            "company_name": company_name,
            "session_id": session_id,
            "profile": profile,
            "competitors": competitor_list,
            "pricing": pricing,
            "financials": financials,
            "news": news,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

