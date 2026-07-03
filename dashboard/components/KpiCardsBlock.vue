<template>
  <div class="kpi-cards-block">
    <div class="kpi-grid">
      <div v-for="(card, idx) in cards" :key="idx" class="kpi-card glass-card">
        <div class="kpi-header">
          <span class="kpi-label">{{ card.label }}</span>
          <span v-if="card.badge" class="kpi-badge">{{ card.badge }}</span>
        </div>
        <div class="kpi-value">{{ card.value }}</div>
        <div v-if="card.subtitle" class="kpi-subtitle">{{ card.subtitle }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  cards: {
    type: Array,
    required: true,
  },
})
</script>

<style scoped>
.kpi-cards-block {
  margin: 24px 0;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.kpi-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.kpi-label {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}
.kpi-badge {
  font-size: 10px;
  background-color: var(--badge-bg);
  color: var(--badge-text);
  border: 1px solid var(--badge-border);
  padding: 2px 8px;
  border-radius: 20px;
  font-weight: 600;
}
.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-title);
}
.kpi-subtitle {
  font-size: 12px;
  color: var(--text-muted);
}
</style>
