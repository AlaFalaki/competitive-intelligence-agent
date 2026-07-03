<template>
  <div class="feature-comparison-block glass-card">
    <h4 v-if="title" class="table-title">{{ title }}</h4>
    <div class="table-container">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Feature / Capability</th>
            <th v-for="company in companies" :key="company.name" class="company-header">
              {{ company.name }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(feat, featIdx) in features" :key="feat">
            <td class="feature-label">{{ feat }}</td>
            <td v-for="company in companies" :key="company.name" class="checkmark-cell">
              <span v-if="company.features_supported[featIdx]" class="check-icon">✓</span>
              <span v-else class="cross-icon">✗</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  features: {
    type: Array,
    required: true,
  },
  companies: {
    type: Array,
    required: true,
  },
})
</script>

<style scoped>
.feature-comparison-block {
  margin: 24px 0;
}
.table-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-title);
  margin-bottom: 16px;
}
.table-container {
  overflow-x: auto;
  border: 1px solid var(--table-border);
  border-radius: 12px;
}
.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  text-align: left;
}
.comparison-table th {
  background-color: var(--table-header-bg);
  padding: 12px 16px;
  color: var(--text-muted);
  font-weight: 600;
  border-bottom: 1px solid var(--table-border);
}
.comparison-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--table-border);
  color: var(--text-main);
}
.comparison-table tr:hover td {
  background-color: var(--table-row-hover);
}
.feature-label {
  font-weight: 500;
  color: var(--text-title);
}
.company-header {
  text-align: center;
  width: 180px;
}
.checkmark-cell {
  text-align: center;
}
.check-icon {
  color: #10b981;
  font-weight: 700;
  font-size: 16px;
}
.cross-icon {
  color: #ef4444;
  font-weight: 700;
  font-size: 16px;
}
</style>
