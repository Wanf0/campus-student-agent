<script setup lang="ts">
import type { Citation, Evidence } from '../types'
import { authorityLabel } from '../types'
import { excerpt } from '../utils/markdown'

defineProps<{
  evidence: Evidence[]
  citations: Citation[]
}>()
</script>

<template>
  <div v-if="evidence.length" class="evidence-panel">
    <div class="evidence-title">依据（Evidence）</div>
    <div v-for="(e, i) in evidence" :key="i" class="evidence-card">
      <div class="evidence-meta">
        <span class="tag">{{ authorityLabel(e.source_authority) }}</span>
        <span class="src">{{ e.source_title }}</span>
        <span v-if="e.department" class="dept">{{ e.department }}</span>
      </div>
      <div class="evidence-dates" v-if="e.publish_date || e.effective_to || e.version">
        <span v-if="e.publish_date">发布 {{ e.publish_date }}</span>
        <span v-if="e.effective_to">有效期至 {{ e.effective_to }}</span>
        <span v-if="e.version">版本 {{ e.version }}</span>
      </div>
      <div class="evidence-excerpt">{{ excerpt(e.text) }}</div>
    </div>
  </div>
</template>
