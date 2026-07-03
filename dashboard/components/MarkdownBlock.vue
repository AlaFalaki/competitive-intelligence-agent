<template>
  <div class="markdown-block" v-html="parsedContent"></div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  content: {
    type: String,
    required: true,
  },
})

const parsedContent = computed(() => {
  if (!props.content) return ''
  const cleaned = props.content.replace(/\\n/g, '\n')
  return marked.parse(cleaned, { breaks: true })
})
</script>

<style scoped>
.markdown-block {
  margin: 20px 0;
  line-height: 1.7;
  color: var(--text-main);
}
.markdown-block :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-title);
  margin-top: 28px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--card-border);
  padding-bottom: 8px;
}
.markdown-block :deep(h2) {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-title);
  margin-top: 24px;
  margin-bottom: 12px;
}
.markdown-block :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  color: var(--accent-color);
  margin-top: 18px;
  margin-bottom: 8px;
}
.markdown-block :deep(p) {
  margin-bottom: 12px;
}
.markdown-block :deep(ul), .markdown-block :deep(ol) {
  margin-left: 20px;
  margin-bottom: 16px;
}
.markdown-block :deep(li) {
  margin-bottom: 6px;
  list-style-type: disc;
}
.markdown-block :deep(strong) {
  color: var(--text-title);
}
.markdown-block :deep(blockquote) {
  border-left: 4px solid var(--accent-color);
  background: var(--accent-soft);
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 0 8px 8px 0;
}
</style>
