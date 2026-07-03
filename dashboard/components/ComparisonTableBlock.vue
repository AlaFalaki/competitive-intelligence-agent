<template>
  <div class="comparison-table-block glass-card">
    <h4 v-if="title" class="table-title">{{ title }}</h4>
    <div class="table-container">
      <table class="comparison-table">
        <thead>
          <tr>
            <th v-for="header in headers" :key="header">{{ header }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in rows" :key="idx">
            <td
              v-for="(cell, cellIdx) in row"
              :key="cellIdx"
              :class="{ 'metric-label': cellIdx === 0 }"
            >
              {{ cell }}
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
  headers: {
    type: Array,
    required: true,
  },
  rows: {
    type: Array,
    required: true,
  },
})
</script>

<style scoped>
.comparison-table-block {
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
.metric-label {
  font-weight: 500;
  color: var(--text-title);
}
</style>
