<template>
  <div class="playground-root">
    <div class="playground-header glass-card">
      <div class="header-top">
        <h3>🖥️ Final Report Component Showcase & Playground</h3>
        <NuxtLink to="/" class="back-link">← Back to Dashboard</NuxtLink>
      </div>
      <p class="description">
        These are the pre-built frontend components used to render the final Strategic Master Report. Rather than forcing the LLM to write redundant HTML/CSS markup, the workflow gives the model structured access to these components. 
      </p>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-icon">⚡</span>
          <div>
            <strong>Token Optimization</strong>
            <p>Drastically reduces output token usage and generation latency by returning clean JSON data payloads instead of verbose raw markdown formatting.</p>
          </div>
        </div>
        <div class="info-item">
          <span class="info-icon">🎨</span>
          <div>
            <strong>Design Consistency</strong>
            <p>Only the required data attributes are sent to create charts, SWOT tables, and metrics, ensuring styling consistency and preventing model layout breakages.</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="tab-content glass-card">
      <div class="report-layout-grid">
        <div v-for="(block, idx) in sampleReport.blocks" :key="idx" class="report-block-item">
          <MarkdownBlock v-if="block.type === 'markdown'" :content="block.content" />
          <ChartBlock v-else-if="block.type === 'chart'" v-bind="block" />
          <SwotBlock v-else-if="block.type === 'swot'" v-bind="block" />
          <ComparisonTableBlock v-else-if="block.type === 'comparison_table'" v-bind="block" />
          <KpiCardsBlock v-else-if="block.type === 'kpi_cards'" v-bind="block" />
          <FeatureComparisonBlock v-else-if="block.type === 'feature_comparison'" v-bind="block" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MarkdownBlock from '../../components/MarkdownBlock.vue'
import ChartBlock from '../../components/ChartBlock.vue'
import SwotBlock from '../../components/SwotBlock.vue'
import ComparisonTableBlock from '../../components/ComparisonTableBlock.vue'
import KpiCardsBlock from '../../components/KpiCardsBlock.vue'
import FeatureComparisonBlock from '../../components/FeatureComparisonBlock.vue'

const sampleReport = ref({
  blocks: [
    {
      type: 'kpi_cards',
      cards: [
        { label: 'Liquidity Leader', value: '$97.5 Billion', subtitle: 'Apple Inc.', badge: 'Leader' },
        { label: 'Highest R&D Invested', value: '12.1% of Rev', subtitle: 'Google', badge: '+2.4% YoY' },
        { label: 'Fastest News Momentum', value: '15 Stories', subtitle: 'Samsung Electronics', badge: 'Trending' }
      ]
    },
    {
      type: 'markdown',
      content: `# Market Competitiveness Matrix & Insights\nWe performed a deep comparative analysis of **Apple Inc.** alongside its core peers **Samsung Electronics** and **Google**. Using gathered SEC data, pricing plans, and news, this report outlines structural performance differences.`
    },
    {
      type: 'markdown',
      content: `## 📊 Component Rendering Capabilities\nBelow is a showcase of how styled Markdown blocks render within the master report layout:\n\n*   **Bold & Emphasis**: Highlighting key segments like **$97.5B cash reserves**.\n*   **External Anchors**: Navigating to resources like [SEC Edgar Filings Database](https://www.sec.gov/edgar/searchedgar/companysearch).\n*   **Blockquote Callouts**:\n    > "Competitor pricing trends indicate a major shift towards on-device processing capabilities, driving up hardware capital expenditures across the industry."`
    },
    {
      type: 'chart',
      chart_type: 'bar',
      title: 'Operating Income Comparison (FY 2024 - FY 2025)',
      data: {
        labels: ['FY 2024', 'FY 2025'],
        datasets: [
          { label: 'Apple', data: [114301000000, 123000000000] },
          { label: 'Samsung Electronics', data: [45000000000, 48000000000] },
          { label: 'Google', data: [84293000000, 92000000000] }
        ]
      }
    },
    {
      type: 'markdown',
      content: `### Strategic Position & SWOT Highlight\nSamsung's higher focus on mobile displays and semiconductor manufacturing creates strong tailwinds in pricing efficiency, while Google continues to lead in pure margins via search and advertisement revenue channels.`
    },
    {
      type: 'swot',
      company: 'Apple Inc.',
      strengths: ['Vast premium ecosystem (iOS lock-in)', 'Massive free cash reserves ($97.5B)', 'High customer retention rates'],
      weaknesses: ['Dependence on iPhone product cycles', 'Slower release timeline for cloud LLM services'],
      opportunities: ['On-device AI integration (Apple Intelligence)', 'AR/VR wearable category expansion'],
      threats: ['Antitrust investigations in US and EU markets', 'Global hardware chip supply chain regulations']
    },
    {
      type: 'comparison_table',
      title: 'Gross Margin & Cash Flow Efficiency Matrix',
      headers: ['Financial Dimension', 'Apple', 'Samsung Electronics', 'Google'],
      rows: [
        ['Gross Margin (%)', '46.2%', '38.5%', '56.1%'],
        ['R&D Efficiency (% of Revenue)', '8.2%', '10.4%', '12.1%'],
        ['Cash-to-Debt Ratio', '0.92', '0.45', '1.10']
      ]
    },
    {
      type: 'markdown',
      content: `### AI Feature Support & Readiness\nA key differentiator for 2026 and beyond is model availability. While Google features robust APIs, Apple is targeting on-device processing to bypass latency and retain user privacy.`
    },
    {
      type: 'feature_comparison',
      title: 'Advanced AI Capability checklist',
      features: ['On-Device Processing', 'Multimodal APIs', 'Enterprise Fine-Tuning Support', 'End-to-End Encryption'],
      companies: [
        { name: 'Apple', features_supported: [true, false, false, true] },
        { name: 'Google', features_supported: [true, true, true, false] },
        { name: 'Samsung', features_supported: [true, true, false, false] }
      ]
    }
  ]
})
</script>

<style scoped>
.playground-root {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}
.back-link {
  display: inline-block;
  color: var(--accent-color);
  text-decoration: none;
  font-weight: 600;
  font-size: 13.5px;
  padding: 6px 14px;
  background: rgba(124, 58, 237, 0.08);
  border: 1px solid var(--accent-border);
  border-radius: 8px;
  transition: all 0.2s ease;
}
.back-link:hover {
  background: var(--accent-color);
  color: var(--text-inverse);
  text-decoration: none;
}
.playground-header {
  margin-bottom: 30px;
  background: var(--accent-soft);
  border: 1px solid var(--accent-border);
  padding: 24px 30px;
}
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 16px;
}
.playground-header h3 {
  color: var(--accent-color);
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}
.description {
  font-size: 14.5px;
  color: var(--text-main);
  line-height: 1.6;
  margin-bottom: 20px;
  max-width: 900px;
}
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  border-top: 1px solid rgba(124, 58, 237, 0.15);
  padding-top: 20px;
}
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
.info-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.info-icon {
  font-size: 20px;
  line-height: 1;
}
.info-item strong {
  display: block;
  font-size: 14px;
  color: var(--text-title);
  margin-bottom: 4px;
}
.info-item p {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0;
}
</style>
