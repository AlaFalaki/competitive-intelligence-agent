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

from typing import List, Literal, Union
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import types
from app.config import GEMINI_MODEL_LARGE


# 1. Pydantic Block Schemas matching Frontend Components
class KpiCard(BaseModel):
    label: str = Field(description="Uppercase indicator or name of the KPI (e.g. 'LIQUIDITY LEADER')")
    value: str = Field(description="Large highlighted value (e.g. '$97.5 Billion' or '12.1% of Rev')")
    subtitle: str = Field(description="Subtext context description (usually company name)")
    badge: str = Field("", description="Optional contextual small badge (e.g., 'Leader', 'Trending', '+2.4% YoY')")


class KpiCardsBlock(BaseModel):
    type: Literal["kpi_cards"] = "kpi_cards"
    cards: List[KpiCard] = Field(description="List of KPI highlight cards to display side-by-side")


class MarkdownBlock(BaseModel):
    type: Literal["markdown"] = "markdown"
    content: str = Field(description="Structured markdown narrative text comparing the companies")


class ChartDataset(BaseModel):
    label: str = Field(description="The name of the dataset series (usually the company name)")
    data: List[float] = Field(description="List of numeric float values in chronological order")


class ChartData(BaseModel):
    labels: List[str] = Field(description="Labels for the X-axis (e.g., ['FY 2024', 'FY 2025'])")
    datasets: List[ChartDataset] = Field(description="Array of dataset series")


class ChartBlock(BaseModel):
    type: Literal["chart"] = "chart"
    chart_type: Literal["bar", "line", "area", "pie", "doughnut"] = Field(description="The chart presentation format")
    title: str = Field(description="Title of the comparative chart")
    data: ChartData = Field(description="Chart datasets data structure")


class SwotBlock(BaseModel):
    type: Literal["swot"] = "swot"
    company: str = Field(description="The target company name")
    strengths: List[str] = Field(description="List of core strengths")
    weaknesses: List[str] = Field(description="List of core weaknesses")
    opportunities: List[str] = Field(description="List of core opportunities")
    threats: List[str] = Field(description="List of core threats")


class ComparisonTableBlock(BaseModel):
    type: Literal["comparison_table"] = "comparison_table"
    title: str = Field(description="Title of the financial comparison matrix")
    headers: List[str] = Field(description="Column headers (e.g. ['Metric', 'Apple', 'Google'])")
    rows: List[List[str]] = Field(description="Rows of the table, where each row is an array of cell values")


class FeatureCompany(BaseModel):
    name: str = Field(description="The company name")
    features_supported: List[bool] = Field(description="List of booleans showing support for each listed feature")


class FeatureComparisonBlock(BaseModel):
    type: Literal["feature_comparison"] = "feature_comparison"
    title: str = Field(description="Title of the feature matrix comparison")
    features: List[str] = Field(description="List of feature names compared")
    companies: List[FeatureCompany] = Field(description="Feature support indications per company")


# Unified Report block discriminator type
ReportBlock = Union[
    KpiCardsBlock,
    MarkdownBlock,
    ChartBlock,
    SwotBlock,
    ComparisonTableBlock,
    FeatureComparisonBlock,
]


class MasterReportOutput(BaseModel):
    blocks: List[ReportBlock] = Field(description="Chronological layout blocks comprising the final master report")


# Agent Instruction
master_report_instruction = """
You are a Master Report Agent. Your task is to analyze the consolidated database context of a company and its competitors, and generate a final strategic master analysis report.

You will receive all company profiles, financial statements, pricing plan details, and news summaries inside {session_data}.

You MUST incorporate recent news findings and announcements (from the news summaries of the target company and its competitors) in your analysis. Dedicate at least one Markdown Block specifically to comparing recent press releases, market rumors, product launches, or news momentum.

You MUST structure the report by weaving MULTIPLE (at least 4-5) separate, distinct Markdown Blocks in between other visual blocks (KPIs, Charts, SWOT, Tables, and checklist grids) to provide context and strategic commentary.

For example, your report structure should alternate between visual components and markdown context blocks:
1. A KPI Cards Block highlighting key quantitative metrics.
2. A Markdown Block: Executive summary and company positioning statement.
3. A Chart Block: Financial performance comparisons over the years.
4. A Markdown Block: Financial trajectory, growth drivers, and market opportunities analysis.
5. A Swot Block: 2x2 quadrant SWOT analysis dedicated to the target company.
6. A Markdown Block: Strategic implications of SWOT findings and core competitive risks.
7. A Comparison Table Block: Side-by-side margins, leverage, or cash flow ratios.
8. A Markdown Block: Operational efficiency assessment and competitor news insights (incorporating the scraped news details).
9. A Feature Comparison Block: Checklist matrix of product packages and service features.
10. A final Markdown Block: Synthesized conclusion, recent news momentum summary, and strategic recommendations.

Ensure your JSON outputs exactly match the specified schema formats. Do not use placeholders.
"""

master_report_agent = LlmAgent(
    name="MasterReportAgent",
    model=Gemini(
        model=GEMINI_MODEL_LARGE,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=master_report_instruction,
    output_schema=MasterReportOutput,
    output_key="master_report",
)
