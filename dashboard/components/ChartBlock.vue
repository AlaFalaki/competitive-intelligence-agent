<template>
  <div class="chart-block">
    <h4 v-if="title" class="chart-title">{{ title }}</h4>
    <div class="chart-container">
      <canvas ref="canvasRef"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  title: String,
  chart_type: {
    type: String,
    default: 'bar',
  },
  data: {
    type: Object,
    required: true,
  },
})

const canvasRef = ref(null)
let chartInstance = null

onMounted(() => {
  renderChart()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})

watch(
  () => props.data,
  () => {
    renderChart()
  },
  { deep: true }
)

function renderChart() {
  if (!canvasRef.value) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = canvasRef.value.getContext('2d')

  const colors = [
    { border: '#7c3aed', bg: 'rgba(124, 58, 237, 0.08)' },
    { border: '#2563eb', bg: 'rgba(37, 99, 235, 0.08)' },
    { border: '#10b981', bg: 'rgba(16, 185, 129, 0.08)' },
    { border: '#f59e0b', bg: 'rgba(245, 158, 11, 0.08)' },
  ]

  const datasets = props.data.datasets.map((dataset, idx) => {
    const activeColor = colors[idx % colors.length]

    return {
      label: dataset.label,
      data: dataset.data,
      borderColor: activeColor.border,
      backgroundColor:
        props.chart_type === 'pie' || props.chart_type === 'doughnut'
          ? colors.map((c) => c.border)
          : activeColor.bg,
      borderWidth: 2,
      tension: 0.35,
      fill: props.chart_type === 'area',
      pointBackgroundColor: activeColor.border,
      pointHoverRadius: 6,
    }
  })

  chartInstance = new Chart(ctx, {
    type: props.chart_type === 'area' ? 'line' : props.chart_type,
    data: {
      labels: props.data.labels,
      datasets: datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            font: { family: 'Outfit', size: 12, weight: '500' },
            color: '#334155',
          },
        },
      },
      scales:
        props.chart_type === 'pie' || props.chart_type === 'doughnut'
          ? {}
          : {
              x: {
                grid: { color: 'rgba(0, 0, 0, 0.03)' },
                ticks: { color: '#64748b', font: { family: 'Outfit', size: 11 } },
              },
              y: {
                grid: { color: 'rgba(0, 0, 0, 0.03)' },
                ticks: { color: '#64748b', font: { family: 'Outfit', size: 11 } },
              },
            },
    },
  })
}
</script>

<style scoped>
.chart-block {
  margin: 24px 0;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  border-radius: 16px;
  padding: 24px;
}
.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-title);
  margin-bottom: 16px;
}
.chart-container {
  position: relative;
  height: 320px;
  width: 100%;
}
</style>
