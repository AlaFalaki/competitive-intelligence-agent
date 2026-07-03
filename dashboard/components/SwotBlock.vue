<template>
  <div class="swot-block glass-card">
    <h3 class="swot-title">{{ company }} SWOT Analysis</h3>
    <div class="swot-grid">
      <!-- Strengths -->
      <div class="swot-quadrant strengths">
        <div class="quadrant-header">
          <span class="quadrant-letter">S</span>
          <h4>Strengths</h4>
        </div>
        <ul class="quadrant-list">
          <li v-for="item in strengths" :key="item">{{ item }}</li>
        </ul>
      </div>

      <!-- Weaknesses -->
      <div class="swot-quadrant weaknesses">
        <div class="quadrant-header">
          <span class="quadrant-letter">W</span>
          <h4>Weaknesses</h4>
        </div>
        <ul class="quadrant-list">
          <li v-for="item in weaknesses" :key="item">{{ item }}</li>
        </ul>
      </div>

      <!-- Opportunities -->
      <div class="swot-quadrant opportunities">
        <div class="quadrant-header">
          <span class="quadrant-letter">O</span>
          <h4>Opportunities</h4>
        </div>
        <ul class="quadrant-list">
          <li v-for="item in opportunities" :key="item">{{ item }}</li>
        </ul>
      </div>

      <!-- Threats -->
      <div class="swot-quadrant threats">
        <div class="quadrant-header">
          <span class="quadrant-letter">T</span>
          <h4>Threats</h4>
        </div>
        <ul class="quadrant-list">
          <li v-for="item in threats" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  company: {
    type: String,
    required: true,
  },
  strengths: {
    type: Array,
    default: () => [],
  },
  weaknesses: {
    type: Array,
    default: () => [],
  },
  opportunities: {
    type: Array,
    default: () => [],
  },
  threats: {
    type: Array,
    default: () => [],
  },
})
</script>

<style scoped>
.swot-block {
  margin: 24px 0;
}
.swot-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-title);
  margin-bottom: 20px;
}
.swot-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}
@media (min-width: 768px) {
  .swot-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 16px;
  }
}
.swot-quadrant {
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}
.quadrant-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.quadrant-letter {
  font-size: 24px;
  font-weight: 800;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #fff;
}
.quadrant-header h4 {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-title);
}
.quadrant-list {
  list-style-type: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.quadrant-list li {
  font-size: 13px;
  color: var(--text-main);
  line-height: 1.4;
  padding-left: 12px;
  position: relative;
}
.quadrant-list li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: inherit;
}

/* Quadrant Specific Colors */
.strengths {
  background: rgba(16, 185, 129, 0.03);
  border-color: rgba(16, 185, 129, 0.1);
}
.strengths .quadrant-letter {
  background: #10b981;
}
.strengths li::before {
  color: #10b981;
}

.weaknesses {
  background: rgba(239, 68, 68, 0.03);
  border-color: rgba(239, 68, 68, 0.1);
}
.weaknesses .quadrant-letter {
  background: #ef4444;
}
.weaknesses li::before {
  color: #ef4444;
}

.opportunities {
  background: rgba(37, 99, 235, 0.03);
  border-color: rgba(37, 99, 235, 0.1);
}
.opportunities .quadrant-letter {
  background: #2563eb;
}
.opportunities li::before {
  color: #2563eb;
}

.threats {
  background: rgba(245, 158, 11, 0.03);
  border-color: rgba(245, 158, 11, 0.1);
}
.threats .quadrant-letter {
  background: #f59e0b;
}
.threats li::before {
  color: #f59e0b;
}
</style>
