<template>
  <div class="dashboard-root">
    <!-- Sidebar: Previous Sessions -->
    <aside class="sidebar glass-card">
      <div class="sidebar-header">
        <h3>Analysis History</h3>
        <button @click="loadSessions" class="refresh-btn" title="Refresh history">🔄</button>
      </div>
      <div class="sessions-list" v-if="sessions.length > 0">
        <div
          v-for="session in sessions"
          :key="session.session_id"
          class="session-card"
          :class="{ active: selectedSessionId === session.session_id }"
          @click="selectSession(session.session_id)"
        >
          <div class="session-info">
            <span class="session-company">{{ session.company_name }}</span>
            <span class="session-date">{{ formatDate(session.created_at) }}</span>
          </div>
          <span class="session-arrow">→</span>
        </div>
      </div>
      <div v-else class="sidebar-empty">
        No previous sessions found. Start an analysis to create one.
      </div>
    </aside>

    <!-- Main Container -->
    <div class="main-container">
      <header class="header">
        <div class="logo">
          <span class="pulse-dot"></span>
          <h1>Antigravity Intelligence</h1>
          <span class="badge">COMPETITIVE ANALYST</span>
          <NuxtLink to="/playground" class="badge" style="background: var(--accent-color); color: white; margin-left: 10px; text-decoration: none;">PLAYGROUND ↗</NuxtLink>
        </div>
        <div class="api-config" style="display: flex; align-items: center; gap: 8px; font-size: 13px;">
          <span style="color: var(--text-muted);">API Server:</span>
          <input
            v-model="apiBaseUrl"
            @change="saveApiUrl"
            style="background: var(--input-bg); border: 1px solid var(--border-color); color: var(--text-main); border-radius: 6px; padding: 4px 10px; width: 220px; font-size: 12px;"
            placeholder="http://localhost:8000"
          />
        </div>
      </header>

      <main class="main-content">
        <!-- Search & Control Panel -->
        <section class="control-panel glass-card">
          <div class="panel-header">
            <h2>Market Analysis Request</h2>
            <p>Provide a company name to execute the multi-agent profiling workflow.</p>
          </div>
          <form @submit.prevent="startAnalysis" class="search-form">
            <input
              v-model="targetCompany"
              type="text"
              placeholder="e.g. Apple Inc. or AAPL"
              required
              :disabled="analyzing"
              class="company-input"
            />
            <button type="submit" :disabled="analyzing" class="analyze-btn">
              <span v-if="analyzing" class="spinner"></span>
              <span>{{ analyzing ? 'Running Agents...' : 'Analyze Market' }}</span>
            </button>
          </form>
        </section>

        <!-- Live Stream Logs & Progress -->
        <section v-if="analyzing || logs.length > 0" class="logs-section glass-card">
          <div class="logs-header">
            <h3>Real-time Agent Activity Feed</h3>
            <span v-if="analyzing" class="status-indicator">
              <span class="dot blinking"></span>
              Agents Processing
            </span>
            <span v-else class="status-indicator success">
              <span class="dot"></span>
              Analysis Complete
            </span>
          </div>
          <div class="logs-container" ref="logsContainer">
            <div v-for="(log, idx) in logs" :key="idx" class="log-entry" :class="log.type">
              <div class="log-meta">
                <span class="log-time">{{ log.time }}</span>
                <span v-if="log.node" class="log-node">[{{ log.node }}]</span>
              </div>
              <div class="log-body">
                <span class="log-message">{{ log.message }}</span>
                
                <!-- Display tool calls if any -->
                <div v-if="log.tool_calls && log.tool_calls.length > 0" class="tool-calls-block">
                  <div v-for="call in log.tool_calls" :key="call.name" class="tool-call-badge">
                    <span class="tool-label">Executing Tool:</span>
                    <span class="tool-name">{{ call.name }}</span>
                    <pre class="tool-args" v-if="call.args && Object.keys(call.args).length > 0">{{ JSON.stringify(call.args, null, 2) }}</pre>
                  </div>
                </div>

                <!-- Display tool responses if any -->
                <div v-if="log.tool_responses && log.tool_responses.length > 0" class="tool-responses-block">
                  <div v-for="resp in log.tool_responses" :key="resp.name" class="tool-response-badge">
                    <span class="tool-label">Tool Return:</span>
                    <span class="tool-name">{{ resp.name }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Results Panel -->
        <section v-if="results" class="results-section">
          <nav class="tabs-nav glass-card">
            <button
              v-for="tab in ['overview', 'competitors', 'pricing', 'financials', 'news', 'report']"
              :key="tab"
              @click="activeTab = tab"
              :class="{ active: activeTab === tab }"
              class="tab-btn"
            >
              {{ tab === 'report' ? 'MASTER REPORT' : tab.toUpperCase() }}
            </button>
          </nav>

          <div class="tab-content glass-card">
            <!-- Overview Tab -->
            <div v-if="activeTab === 'overview'" class="tab-pane">
              <div v-if="results.profile" class="profile-layout">
                <div class="profile-header">
                  <h3>{{ results.company_name }}</h3>
                  <p class="industry">{{ results.profile.industry }}</p>
                </div>
                <div class="profile-grid">
                  <div class="info-card">
                    <span class="label">Headquarters</span>
                    <span class="value">{{ results.profile.headquarters }}</span>
                  </div>
                  <div class="info-card">
                    <span class="label">Website</span>
                    <a :href="results.profile.website" target="_blank" class="value link">
                      {{ results.profile.website }}
                    </a>
                  </div>
                </div>
                <div class="description-card">
                  <h4>Business Overview</h4>
                  <p>{{ results.profile.description }}</p>
                </div>
              </div>
              <div v-else class="empty-state">No profile information available.</div>
            </div>

            <!-- Competitors Tab -->
            <div v-if="activeTab === 'competitors'" class="tab-pane">
              <h3>Discovered Competitors</h3>
              <p class="subtitle">Identified peers for {{ results.company_name }} via competitive research.</p>
              <div v-if="results.competitors && results.competitors.length > 0" class="competitors-list">
                <div v-for="comp in results.competitors" :key="comp" class="competitor-item">
                  <span class="comp-icon">🏢</span>
                  <span class="comp-name">{{ comp }}</span>
                </div>
              </div>
              <div v-else class="empty-state">No competitors identified.</div>
            </div>

            <!-- Pricing Tab -->
            <div v-if="activeTab === 'pricing'" class="tab-pane">
              <h3>Subscription & Pricing Analysis</h3>
              <p class="subtitle">Extracted service tiers, prices, and feature comparisons.</p>
              <div class="pricing-grid">
                <div
                  v-for="(info, company) in results.pricing"
                  :key="company"
                  class="pricing-card"
                  :class="{ target: company === results.company_name }"
                >
                  <div class="card-badge" v-if="company === results.company_name">TARGET</div>
                  <h4>{{ company }}</h4>
                  <a :href="info.pricing_page_url" target="_blank" class="source-link">Pricing Page ↗</a>
                  <div v-if="getNormalizedPlans(info)" class="plans-list">
                    <div v-for="plan in getNormalizedPlans(info)" :key="plan.name" class="plan-item">
                      <div class="plan-header-info">
                        <span class="plan-name">{{ plan.name }}</span>
                        <span class="plan-price">{{ plan.price }}</span>
                      </div>
                      <ul class="features-list">
                        <li v-for="feat in plan.features" :key="feat">
                          <pre v-if="feat.startsWith('{') || feat.startsWith('[') || feat.startsWith('{\n')">{{ feat }}</pre>
                          <span v-else>✓ {{ feat }}</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                  <div v-else class="empty-state-card">
                    Pricing data not available for this company.
                  </div>
                </div>
              </div>
            </div>

            <!-- Financials Tab -->
            <div v-if="activeTab === 'financials'" class="tab-pane">
              <h3>Historical 10-K Financial Metrics</h3>
              <p class="subtitle">Comparing key financial statement items over the last two years.</p>
              <div class="financials-accordion">
                <div
                  v-for="(info, company) in results.financials"
                  :key="company"
                  class="financial-company-block"
                >
                  <h4>{{ company }} <span class="cik-badge">CIK: {{ info.cik }}</span></h4>
                  <div v-if="info.filing_data && info.filing_data.length > 0" class="table-container">
                    <table class="financial-table">
                      <thead>
                        <tr>
                          <th>Metric</th>
                          <th v-for="year in info.filing_data" :key="year.fiscal_year">
                            FY {{ year.fiscal_year }}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="m in financialMetricList" :key="m.key">
                          <td class="metric-label">{{ m.label }}</td>
                          <td v-for="year in info.filing_data" :key="year.fiscal_year">
                            {{ formatFinancialValue(year.metrics[m.key]) }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div v-else class="empty-state-card">
                    No structured financial data available.
                  </div>
                </div>
              </div>
            </div>

            <!-- News Tab -->
            <div v-if="activeTab === 'news'" class="tab-pane">
              <h3>Recent Announcements & News</h3>
              <p class="subtitle">Latest corporate announcements, mergers, funding, and controversies.</p>
              <div class="news-list">
                <div v-for="(summary, company) in results.news" :key="company" class="news-item-card">
                  <div class="news-company">{{ company }}</div>
                  <div class="news-summary-text" v-html="renderMarkdown(summary)"></div>
                </div>
              </div>
            </div>

            <!-- Master Report Tab -->
            <div v-if="activeTab === 'report'" class="tab-pane">
              <h3>Dynamic Master Analysis Report</h3>
              <p class="subtitle">AI-generated master strategy report with comparative charts, SWOT grids, and KPI decks.</p>
              
              <div v-if="results && results.master_report" class="report-layout-grid">
                <div v-for="(block, idx) in results.master_report.blocks" :key="idx" class="report-block-item">
                  <MarkdownBlock v-if="block.type === 'markdown'" :content="block.content" />
                  <ChartBlock v-else-if="block.type === 'chart'" v-bind="block" />
                  <SwotBlock v-else-if="block.type === 'swot'" v-bind="block" />
                  <ComparisonTableBlock v-else-if="block.type === 'comparison_table'" v-bind="block" />
                  <KpiCardsBlock v-else-if="block.type === 'kpi_cards'" v-bind="block" />
                  <FeatureComparisonBlock v-else-if="block.type === 'feature_comparison'" v-bind="block" />
                </div>
              </div>
              <div v-else class="empty-state">
                No report data available.
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import MarkdownBlock from '../../components/MarkdownBlock.vue'
import ChartBlock from '../../components/ChartBlock.vue'
import SwotBlock from '../../components/SwotBlock.vue'
import ComparisonTableBlock from '../../components/ComparisonTableBlock.vue'
import KpiCardsBlock from '../../components/KpiCardsBlock.vue'
import FeatureComparisonBlock from '../../components/FeatureComparisonBlock.vue'

const apiKey = ref('comp-intel-secret-key')
const apiBaseUrl = ref('http://localhost:8000')

const saveApiUrl = () => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('API_BASE_URL', apiBaseUrl.value)
  }
}

const targetCompany = ref('')
const analyzing = ref(false)
const sessions = ref([])
const selectedSessionId = ref('')
const logs = ref([])
const logsContainer = ref(null)
const activeTab = ref('overview')
const results = ref(null)

const financialMetricList = [
  { key: 'revenue', label: 'Revenue' },
  { key: 'gross_profit', label: 'Gross Profit' },
  { key: 'operating_income', label: 'Operating Income' },
  { key: 'net_income', label: 'Net Income' },
  { key: 'cash', label: 'Cash & Cash Equivalents' },
  { key: 'inventory', label: 'Inventory' },
  { key: 'accounts_receivable', label: 'Accounts Receivable' },
  { key: 'total_assets', label: 'Total Assets' },
  { key: 'total_debt', label: 'Total Debt' },
  { key: 'operating_cash_flow', label: 'Operating Cash Flow' },
  { key: 'capital_expenditures', label: 'Capital Expenditures (CapEx)' },
  { key: 'free_cash_flow', label: 'Free Cash Flow' },
  { key: 'r_and_d_expense', label: 'R&D Expense' },
  { key: 'shares_outstanding', label: 'Shares Outstanding' }
]

onMounted(() => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('API_BASE_URL')
    if (saved) {
      apiBaseUrl.value = saved
    }
  }
  loadSessions()
})

async function loadSessions() {
  try {
    const res = await fetch(`${apiBaseUrl.value}/api/sessions`, {
      headers: { 'X-API-Key': apiKey.value }
    })
    if (!res.ok) throw new Error('Failed to load sessions')
    const data = await res.json()
    if (data.status === 'success') {
      sessions.value = data.sessions
    }
  } catch (err) {
    console.error(err)
  }
}



function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatFinancialValue(val) {
  if (val === null || val === undefined) return 'N/A'
  if (typeof val === 'string') return val
  if (Math.abs(val) >= 1e9) {
    return '$' + (val / 1e9).toFixed(2) + ' B'
  }
  if (Math.abs(val) >= 1e6) {
    return '$' + (val / 1e6).toFixed(2) + ' M'
  }
  return '$' + val.toLocaleString()
}

async function startAnalysis() {
  const company = targetCompany.value.trim()
  if (!company) return
  navigateTo(`/report/${encodeURIComponent(company)}`)
}

async function selectSession(sessionId) {
  navigateTo(`/report/${encodeURIComponent(sessionId)}`)
}

function getNormalizedPlans(info) {
  if (!info || !info.plans) return null
  
  let rawPlans = info.plans
  
  if (typeof rawPlans === 'string') {
    try {
      rawPlans = JSON.parse(rawPlans)
    } catch (e) {
      return [{ name: 'Pricing Info', price: 'Scraped Text', features: [rawPlans] }]
    }
  }
  
  if (rawPlans && typeof rawPlans === 'object' && Array.isArray(rawPlans.plans)) {
    return rawPlans.plans.map(p => normalizePlan(p))
  }
  
  if (Array.isArray(rawPlans)) {
    return rawPlans.map(p => normalizePlan(p))
  }
  
  if (rawPlans && typeof rawPlans === 'object') {
    const keys = Object.keys(rawPlans)
    if (keys.length === 1 && Array.isArray(rawPlans[keys[0]])) {
      return rawPlans[keys[0]].map(p => normalizePlan(p))
    }
    
    const plansList = []
    for (const key of keys) {
      const val = rawPlans[key]
      if (val && typeof val === 'object') {
        plansList.push(normalizePlan({ name: key, ...val }))
      } else {
        plansList.push({ name: key, price: String(val), features: [] })
      }
    }
    if (plansList.length > 0) return plansList
  }
  
  return [{ name: 'Details', price: 'Parsed Data', features: [JSON.stringify(rawPlans, null, 2)] }]
}

function normalizePlan(plan) {
  if (!plan || typeof plan !== 'object') {
    return { name: 'Plan', price: String(plan), features: [] }
  }
  
  const name = plan.name || plan.tier || plan.plan || plan.title || 'Plan'
  const price = plan.price || plan.cost || plan.rate || plan.monthly_price || 'Contact Sales'
  
  let features = []
  const rawFeatures = plan.features || plan.features_list || plan.included || plan.benefits || []
  if (Array.isArray(rawFeatures)) {
    features = rawFeatures.map(f => String(f))
  } else if (typeof rawFeatures === 'object') {
    features = Object.entries(rawFeatures).map(([k, v]) => `${k}: ${v}`)
  } else if (rawFeatures) {
    features = [String(rawFeatures)]
  }
  
  return { name, price, features }
}

function renderMarkdown(md) {
  if (!md) return ''
  const cleaned = md.replace(/\\n/g, '\n')
  return marked.parse(cleaned, { breaks: true })
}
</script>


