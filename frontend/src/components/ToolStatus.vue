<script setup lang="ts">
import type { ToolEvent } from '../types'
import { toolLabel } from '../types'

defineProps<{ tools: ToolEvent[] }>()
</script>

<template>
  <div v-if="tools.length" class="tool-status">
    <div v-for="(t, i) in tools" :key="i" class="tool-item" :class="t.status">
      <span class="tool-name">{{ toolLabel(t.tool) }}</span>
      <span class="tool-state">
        <template v-if="t.status === 'start'">进行中…</template>
        <template v-else-if="t.status === 'ok'">✓ 成功</template>
        <template v-else-if="t.status === 'error'">✗ 失败</template>
        <template v-else-if="t.status === 'missing_params'">需补充参数：{{ t.missing?.join('、') }}</template>
      </span>
    </div>
  </div>
</template>
