<template>
  <div class="dashboard-root report-page">
    <!-- Sidebar: Previous Sessions (Collapsible) -->
    <aside class="sidebar glass-card" :class="{ collapsed: isSidebarCollapsed }">
      <div class="sidebar-header">
         <h3 v-if="!isSidebarCollapsed">Analysis History</h3>
         <button @click="isSidebarCollapsed = !isSidebarCollapsed" class="collapse-toggle-btn" :title="isSidebarCollapsed ? 'Expand history' : 'Collapse history'">
           {{ isSidebarCollapsed ? '➔' : '✕' }}
         </button>
         <button v-if="!isSidebarCollapsed" @click="loadSessions" class="refresh-btn" title="Refresh history">🔄</button>
      </div>
      <div v-if="!isSidebarCollapsed" style="display: flex; flex-direction: column; flex: 1; overflow: hidden;">
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
      </div>
    </aside>

    <!-- Main Container -->
    <div class="main-container">
      <header class="header">
        <div class="logo">
          <span class="pulse-dot"></span>
          <h1>Antigravity Intelligence</h1>
          <span class="badge">COMPETITIVE ANALYST</span>
          <NuxtLink to="/" class="badge" style="background: var(--accent-soft); color: var(--accent-color); margin-left: 10px; text-decoration: none;">HOME ↩</NuxtLink>
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
        <!-- Target Header Information -->
        <section class="session-header-card glass-card">
          <div class="session-meta">
            <h2>Competitive Profile: <span class="highlight-company">{{ companyName }}</span></h2>
            <p v-if="results && results.profile">
              Industry: <strong>{{ results.profile.industry }}</strong> | Headquarters: <strong>{{ results.profile.headquarters }}</strong>
            </p>
            <p v-else-if="analyzing">
              Running multi-agent workspace analysis to compile market profiles...
            </p>
          </div>
        </section>

        <!-- Progress Tracker Component -->
        <section v-if="analyzing" class="progress-section glass-card">
          <h3>Analysis Pipeline Progress</h3>
          <p class="subtitle" style="margin-bottom: 20px;">Tracking individual agent coordination and deep-dives in real time.</p>
          
          <div class="progress-stepper">
            <div v-for="step in steps" :key="step.id" class="step-item">
              <div class="step-icon" :class="step.status">
                <span v-if="step.status === 'completed'">✓</span>
                <span v-else-if="step.status === 'active'" class="spinner-small"></span>
                <span v-else>{{ step.id }}</span>
              </div>
              <div class="step-info">
                <div class="step-name" :class="step.status">{{ step.name }}</div>
                <div class="step-desc" v-if="step.status === 'active' && activeDetail">{{ activeDetail }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- Live Stream Logs Feed -->
        <section v-if="analyzing || (logs.length > 0 && !results)" class="logs-section glass-card">
          <div class="logs-header">
            <h3>Real-time Agent Activity Feed</h3>
            <span v-if="analyzing" class="status-indicator">
              <span class="dot blinking"></span>
              Agents Processing
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
                <div v-if="log.tool_calls && log.tool_calls.length > 0" class="tool-calls-block">
                  <div v-for="call in log.tool_calls" :key="call.name" class="tool-call-badge">
                    <span class="tool-label">Executing Tool:</span>
                    <span class="tool-name">{{ call.name }}</span>
                    <pre class="tool-args" v-if="call.args && Object.keys(call.args).length > 0">{{ JSON.stringify(call.args, null, 2) }}</pre>
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
              v-for="tab in ['report', 'overview', 'pricing', 'financials', 'news']"
              :key="tab"
              :class="{ active: activeTab === tab }"
              @click="activeTab = tab"
              class="tab-btn"
            >
              {{ tab.toUpperCase() }}
            </button>
          </nav>

          <div class="tab-content glass-card">
            <!-- Master Report Tab -->
            <div v-if="activeTab === 'report'" class="tab-pane">
              <h3>Dynamic Master Analysis Report</h3>
              <p class="subtitle">AI-generated master strategy report with comparative charts, SWOT grids, and KPI decks.</p>
              
              <div v-if="results.master_report" class="report-layout-grid">
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

            <!-- Profile / Overview Tab -->
            <div v-if="activeTab === 'overview'" class="tab-pane">
              <h3>Company Overview</h3>
              <div v-if="results.profile" class="profile-layout">
                <div class="profile-grid">
                  <div class="info-card">
                    <div class="label">Headquarters</div>
                    <div class="value">{{ results.profile.headquarters }}</div>
                  </div>
                  <div class="info-card">
                    <div class="label">Website</div>
                    <div class="value">
                      <a :href="results.profile.website" target="_blank" class="value link">{{ results.profile.website }}</a>
                    </div>
                  </div>
                </div>
                <div class="description-card">
                  <h4>Business Description</h4>
                  <p>{{ results.profile.description }}</p>
                </div>
              </div>
            </div>

            <!-- Pricing / Subscription Plans Tab -->
            <div v-if="activeTab === 'pricing'" class="tab-pane">
              <h3>Competitor Pricing Plans</h3>
              <p class="subtitle">Side-by-side comparison of subscription models and service structures.</p>
              <div class="pricing-grid">
                <div v-for="(info, company) in results.pricing" :key="company" class="pricing-card" :class="{ target: company === results.company_name }">
                  <div v-if="company === results.company_name" class="card-badge">TARGET</div>
                  <h4>{{ company }}</h4>
                  <a :href="info.pricing_page_url" target="_blank" class="source-link">Pricing Page ↗</a>
                  
                  <div v-if="getNormalizedPlans(info)" class="plans-list">
                    <div v-for="plan in getNormalizedPlans(info)" :key="plan.name" class="plan-item">
                      <div class="plan-header-info">
                        <span class="plan-name">{{ plan.name }}</span>
                        <span class="plan-price">{{ plan.price }}</span>
                      </div>
                      <ul class="features-list">
                        <li v-for="feat in plan.features" :key="feat">{{ feat }}</li>
                      </ul>
                    </div>
                  </div>
                  <div v-else class="empty-state-card">
                    No active subscription plans scraped.
                  </div>
                </div>
              </div>
            </div>

            <!-- Financials Tab -->
            <div v-if="activeTab === 'financials'" class="tab-pane">
              <h3>Financial Metrics Comparative</h3>
              <p class="subtitle">Latest reported numbers extracted from SEC 10-K and 10-Q filings.</p>
              
              <div class="table-container">
                <table class="financial-table">
                  <thead>
                    <tr>
                      <th>Financial Dimension</th>
                      <th>{{ results.company_name }}</th>
                      <th v-for="comp in results.competitors" :key="comp">{{ comp }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="metric in financialMetricList" :key="metric.key">
                      <td class="metric-label">{{ metric.label }}</td>
                      <td>{{ formatFinancialValue(getMetricValue(results.company_name, metric.key)) }}</td>
                      <td v-for="comp in results.competitors" :key="comp">
                        {{ formatFinancialValue(getMetricValue(comp, metric.key)) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
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
          </div>
        </section>
      </main>
    </div>

    <!-- Chat Sidebar Panel (Right Side) -->
    <aside class="chat-sidebar glass-card">
      <div class="chat-header">
        <h3>AI Market Copilot</h3>
        <button @click="clearChatHistory" class="clear-chat-btn" title="Clear chat history">🗑️ Clear</button>
      </div>
      
      <!-- Messages List -->
      <div class="chat-messages-container" ref="chatMessagesContainer">
        <div v-for="(msg, idx) in chatMessages" :key="idx" class="chat-message-bubble" :class="msg.role">
          <div class="message-meta">
            <strong>{{ msg.role === 'user' ? 'You' : 'Copilot' }}</strong>
          </div>
          <div class="message-body" v-html="renderMarkdown(msg.content)"></div>
        </div>
        
        <!-- Live Stream Tool Call Status -->
        <div v-if="chatSearchingStatus" class="chat-searching-indicator">
          <span class="spinner-small"></span>
          <span class="status-text">{{ chatSearchingStatus }}</span>
        </div>
      </div>
      
      <!-- Input Box -->
      <div class="chat-input-bar">
        <input
          v-model="chatInputText"
          @keyup.enter="sendChatMessage"
          placeholder="Ask about financials, competitors..."
          :disabled="chatLoading"
          class="chat-text-input"
        />
        <button @click="sendChatMessage" :disabled="chatLoading || !chatInputText.trim()" class="chat-send-btn">
          <span v-if="chatLoading" class="spinner-small"></span>
          <span v-else>Send</span>
        </button>
      </div>

      <!-- Warning Note -->
      <div class="chat-warning-note">
        ⚠️ Chat history is stored in-memory and will be cleared when the server restarts.
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import MarkdownBlock from '../../../components/MarkdownBlock.vue'
import ChartBlock from '../../../components/ChartBlock.vue'
import SwotBlock from '../../../components/SwotBlock.vue'
import ComparisonTableBlock from '../../../components/ComparisonTableBlock.vue'
import KpiCardsBlock from '../../../components/KpiCardsBlock.vue'
import FeatureComparisonBlock from '../../../components/FeatureComparisonBlock.vue'

const route = useRoute()
const companyName = ref(decodeURIComponent(route.params.id))
const selectedSessionId = ref(decodeURIComponent(route.params.id))

const apiKey = ref('comp-intel-secret-key')
const apiBaseUrl = ref('http://localhost:8000')

const saveApiUrl = () => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('API_BASE_URL', apiBaseUrl.value)
  }
}

const analyzing = ref(false)
const sessions = ref([])
const logs = ref([])
const logsContainer = ref(null)
const activeTab = ref('report')
const results = ref(null)
const activeDetail = ref('')

const isSidebarCollapsed = ref(true)
const chatMessages = ref([
  { role: 'model', content: 'Hi! I am your Competitive Intelligence Copilot. Ask me anything about ' + companyName.value + ' or its competitors. I can query the session database or search the live web!' }
])
const chatInputText = ref('')
const chatLoading = ref(false)
const chatSearchingStatus = ref('')
const chatMessagesContainer = ref(null)

const steps = ref([
  { id: 1, name: 'Routing & Planning', agent: 'Coordinator', status: 'pending' },
  { id: 2, name: 'Company Profiling', agent: 'CompanyProfileAgent', status: 'pending' },
  { id: 3, name: 'Competitor Discovery', agent: 'CompetitorDiscoveryAgent', status: 'pending' },
  { id: 4, name: 'Parallel Research Deep Dives', agents: ['PricingAnalysisAgent', 'SecFilingAgent', 'NewsResearchAgent'], status: 'pending' },
  { id: 5, name: 'Consolidating Datasets', agent: 'load_db_data_node', status: 'pending' },
  { id: 6, name: 'Generating Strategic Master Report', agent: 'MasterReportAgent', status: 'pending' },
  { id: 7, name: 'Finalizing & Saving Session', agent: 'save_master_report_node', status: 'pending' }
])

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

onMounted(async () => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('API_BASE_URL')
    if (saved) {
      apiBaseUrl.value = saved
    }
  }
  await loadSessions()
  await tryLoadExistingResults()
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

async function tryLoadExistingResults() {
  analyzing.value = true
  try {
    const res = await fetch(`${apiBaseUrl.value}/api/results/${encodeURIComponent(companyName.value)}`, {
      headers: { 'X-API-Key': apiKey.value }
    })
    if (res.status === 404) {
      // Results do not exist yet, trigger active workflow
      await startAnalysis()
    } else if (res.ok) {
      const data = await res.json()
      results.value = data
      activeTab.value = 'report' // Default to master report
      analyzing.value = false
    } else {
      throw new Error('Server returned unexpected status')
    }
  } catch (err) {
    console.error('Failed to load results:', err)
    await startAnalysis()
  }
}

async function startAnalysis() {
  analyzing.value = true
  logs.value = []
  results.value = null
  activeDetail.value = ''
  
  // Set all steps to pending initially
  steps.value.forEach(s => s.status = 'pending')

  const company = companyName.value
  const sseUrl = `${apiBaseUrl.value}/api/analyze?company_name=${encodeURIComponent(company)}&api_key=${encodeURIComponent(apiKey.value)}`
  
  const eventSource = new EventSource(sseUrl)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      const time = new Date().toLocaleTimeString()

      if (data.type === 'session_created') {
        selectedSessionId.value = data.session_id
        logs.value.push({
          time,
          type: 'status',
          message: `Created session ${data.session_id} for target: ${data.company_name}`
        })
      } else if (data.type === 'status' || data.type === 'done' || data.type === 'error') {
        logs.value.push({
          time,
          type: data.type,
          message: data.message
        })
        
        if (data.type === 'done') {
          eventSource.close()
          steps.value.forEach(s => s.status = 'completed')
          activeDetail.value = ''
          loadSessions() // Refresh sidebar list
          fetchResults(selectedSessionId.value)
        } else if (data.type === 'error') {
          eventSource.close()
          analyzing.value = false
        }
      } else if (data.type === 'log') {
        logs.value.push({
          time,
          type: 'log',
          node: data.node,
          message: data.text || 'Processing node...',
          tool_calls: data.tool_calls || [],
          tool_responses: data.tool_responses || []
        })
        
        activeDetail.value = data.text || ''
        updateProgress(data.node)
        
        nextTick(() => {
          if (logsContainer.value) {
            logsContainer.value.scrollTop = logsContainer.value.scrollHeight
          }
        })
      }
    } catch (err) {
      console.error('Failed to parse event:', err)
    }
  }

  eventSource.onerror = (err) => {
    console.error('EventSource failed:', err)
    logs.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'error',
      message: 'Connection to agent server lost or API key invalid.'
    })
    eventSource.close()
    analyzing.value = false
  }
}

function updateProgress(currentNode) {
  if (!currentNode) return
  
  let activeIndex = -1
  if (currentNode === 'Coordinator') activeIndex = 0
  else if (currentNode === 'CompanyProfileAgent') activeIndex = 1
  else if (currentNode === 'CompetitorDiscoveryAgent') activeIndex = 2
  else if (['PricingAnalysisAgent', 'SecFilingAgent', 'NewsResearchAgent'].includes(currentNode)) activeIndex = 3
  else if (currentNode === 'load_db_data_node') activeIndex = 4
  else if (currentNode === 'MasterReportAgent') activeIndex = 5
  else if (currentNode === 'save_master_report_node') activeIndex = 6

  if (activeIndex !== -1) {
    for (let i = 0; i < steps.value.length; i++) {
      if (i < activeIndex) {
        steps.value[i].status = 'completed'
      } else if (i === activeIndex) {
        steps.value[i].status = 'active'
      } else {
        steps.value[i].status = 'pending'
      }
    }
  }
}

async function fetchResults(sessionId) {
  try {
    const res = await fetch(`${apiBaseUrl.value}/api/results/${encodeURIComponent(sessionId)}`, {
      headers: {
        'X-API-Key': apiKey.value
      }
    })
    if (!res.ok) throw new Error('Failed to retrieve results')
    const data = await res.json()
    results.value = data
    activeTab.value = 'report' // Default to master report tab when results are ready
  } catch (err) {
    console.error('Failed to fetch results:', err)
  } finally {
    analyzing.value = false
  }
}

async function selectSession(sessionId) {
  navigateTo(`/report/${encodeURIComponent(sessionId)}`)
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

function getMetricValue(company, key) {
  if (!results.value || !results.value.financials || !results.value.financials[company]) return null
  const filingData = results.value.financials[company].filing_data
  if (!filingData || filingData.length === 0) return null
  
  // Sort filings to find the latest
  const sorted = [...filingData].sort((a, b) => {
    const yearA = a.fiscal_year || a.year || 0
    const yearB = b.fiscal_year || b.year || 0
    return yearB - yearA
  })
  const latest = sorted[0]
  if (!latest) return null
  
  if (latest.metrics && latest.metrics[key] !== undefined) {
    return latest.metrics[key]
  }
  return latest[key]
}

function getNormalizedPlans(info) {
  if (!info || !info.plans) return null
  
  let rawPlans = info.plans
  if (typeof rawPlans === 'string') {
    try {
      rawPlans = JSON.parse(rawPlans)
    } catch {
      return null
    }
  }
  
  if (typeof rawPlans === 'object' && rawPlans !== null && !Array.isArray(rawPlans)) {
    if (Array.isArray(rawPlans.plans)) {
      rawPlans = rawPlans.plans
    }
  }
  
  if (Array.isArray(rawPlans)) {
    return rawPlans.map(plan => {
      const name = plan.name || plan.plan_name || 'Standard Plan'
      let price = plan.price || plan.pricing || 'Contact Sales'
      let features = plan.features || []
      
      if (typeof features === 'string') {
        features = [features]
      }
      return { name, price, features }
    })
  }
  
  if (typeof rawPlans === 'object' && rawPlans !== null) {
    const plansArray = []
    for (const [key, details] of Object.entries(rawPlans)) {
      if (key === 'currency' || key === 'licensing_model') continue
      let price = 'Contact Sales'
      let features = []
      let name = key
      
      if (typeof details === 'string') {
        price = details
      } else if (typeof details === 'object' && details !== null) {
        price = details.price || details.pricing || price
        features = details.features || details.included || features
        if (details.name) name = details.name
      }
      
      if (typeof features === 'string') {
        features = [features]
      }
      plansArray.push({ name, price, features })
    }
    return plansArray
  }
  
  return null
}

function renderMarkdown(md) {
  if (!md) return ''
  const cleaned = md.replace(/\\n/g, '\n')
  return marked.parse(cleaned, { breaks: true })
}

async function clearChatHistory() {
  try {
    await fetch(`${apiBaseUrl.value}/api/chat/clear`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey.value
      },
      body: JSON.stringify({
        session_id: companyName.value,
        message: ''
      })
    })
    chatMessages.value = [
      { role: 'model', content: 'Chat history cleared. Ask me anything about ' + companyName.value + '!' }
    ]
  } catch (err) {
    console.error('Failed to clear chat history:', err)
  }
}

async function sendChatMessage() {
  const query = chatInputText.value.trim()
  if (!query || chatLoading.value) return
  
  chatMessages.value.push({ role: 'user', content: query })
  chatInputText.value = ''
  chatLoading.value = true
  chatSearchingStatus.value = 'Preparing response...'
  
  nextTick(() => {
    scrollToChatBottom()
  })
  
  try {
    const response = await fetch(`${apiBaseUrl.value}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey.value
      },
      body: JSON.stringify({
        session_id: companyName.value,
        message: query
      })
    })
    
    if (!response.ok) throw new Error('Chat request failed')
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        const cleanLine = line.trim()
        if (cleanLine.startsWith('data: ')) {
          try {
            const data = JSON.parse(cleanLine.substring(6))
            if (data.type === 'log') {
              if (data.tool_calls && data.tool_calls.length > 0) {
                const call = data.tool_calls[0]
                if (call.name === 'google_search') {
                  chatSearchingStatus.value = `Searching Google for "${call.args.query || 'query'}"...`
                } else if (call.name === 'get_database_session_data') {
                  chatSearchingStatus.value = `Reading stored profiles & reports from database...`
                } else {
                  chatSearchingStatus.value = `Running ${call.name}...`
                }
                
                // Add inline tool log inside chat messages
                const toolMsgContent = `🔧 *Invoked tool: \`${call.name}\`*`
                const len = chatMessages.value.length
                const lastMsg = len > 0 ? chatMessages.value[len - 1] : null
                if (!lastMsg || lastMsg.content !== toolMsgContent) {
                  if (lastMsg && lastMsg.role === 'model' && lastMsg.content === '') {
                    lastMsg.content = toolMsgContent
                  } else {
                    chatMessages.value.push({ role: 'model', content: toolMsgContent })
                  }
                  chatMessages.value.push({ role: 'model', content: '' })
                }
              } else if (data.tool_responses && data.tool_responses.length > 0) {
                chatSearchingStatus.value = `Analyzing tool response...`
              } else {
                chatSearchingStatus.value = ''
              }
              
              if (data.text) {
                const len = chatMessages.value.length
                let modelMsg = len > 0 && chatMessages.value[len - 1].role === 'model' ? chatMessages.value[len - 1] : null
                if (!modelMsg) {
                  modelMsg = { role: 'model', content: data.text }
                  chatMessages.value.push(modelMsg)
                } else if (modelMsg.content.startsWith('🔧 *Invoked tool:')) {
                  chatMessages.value.push({ role: 'model', content: data.text })
                } else {
                  modelMsg.content += data.text
                }
                nextTick(() => scrollToChatBottom())
              }
            } else if (data.type === 'done') {
              chatSearchingStatus.value = ''
            } else if (data.type === 'error') {
              const len = chatMessages.value.length
              const modelMsg = len > 0 && chatMessages.value[len - 1].role === 'model' ? chatMessages.value[len - 1] : null
              if (modelMsg) {
                modelMsg.content += `\n\n*Error: ${data.message}*`
              } else {
                chatMessages.value.push({ role: 'model', content: `*Error: ${data.message}*` })
              }
              chatSearchingStatus.value = ''
            }
          } catch (e) {
            // Keep buffering
          }
        }
      }
    }
  } catch (err) {
    console.error(err)
    chatMessages.value.push({ role: 'model', content: 'Sorry, I encountered an error while retrieving the response.' })
    chatSearchingStatus.value = ''
  } finally {
    chatLoading.value = false
    nextTick(() => scrollToChatBottom())
  }
}

function scrollToChatBottom() {
  if (chatMessagesContainer.value) {
    chatMessagesContainer.value.scrollTop = chatMessagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.session-header-card {
  margin-bottom: 24px;
  background: var(--accent-soft);
  border-color: var(--accent-border);
}
.highlight-company {
  color: var(--accent-color);
  font-weight: 700;
}
.progress-section {
  margin-bottom: 24px;
}
.progress-stepper {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 600px;
}
.step-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}
.step-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  transition: all 0.3s ease;
  flex-shrink: 0;
}
.step-icon.pending {
  border: 2px solid var(--text-muted);
  color: var(--text-muted);
  background: transparent;
}
.step-icon.active {
  border: 2px solid var(--accent-color);
  color: var(--accent-color);
  background: var(--accent-soft);
  box-shadow: 0 0 10px rgba(79, 70, 229, 0.15);
}
.step-icon.completed {
  background: #10b981;
  color: #ffffff;
  border: 2px solid #10b981;
}
.step-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 4px;
}
.step-name {
  font-size: 14.5px;
  font-weight: 500;
  transition: all 0.3s ease;
}
.step-name.pending {
  color: var(--text-muted);
}
.step-name.active {
  color: var(--accent-color);
  font-weight: 600;
}
.step-name.completed {
  color: var(--text-main);
  font-weight: 500;
}
.step-desc {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.4;
  animation: fadeIn 0.4s ease forwards;
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(79, 70, 229, 0.2);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
