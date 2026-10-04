<script setup lang="ts">
import { ref } from 'vue'
import type { ChatMessage } from '../types'
import { intentLabel, toolLabel } from '../types'

defineProps<{ message: ChatMessage }>()
const open = ref(false)
</script>

<template>
  <div v-if="message.runId" class="trace">
    <button class="trace-toggle" @click="open = !open">详情（run trace）</button>
    <div v-if="open" class="trace-body">
      <div>run_id：{{ message.runId }}</div>
      <div v-if="message.intent">意图：{{ intentLabel(message.intent) }}</div>
      <div v-if="message.phase">阶段：{{ message.phase }}</div>
      <div v-if="message.toolCalls?.length">
        工具调用：
        <ul>
          <li v-for="(t, i) in message.toolCalls" :key="i">
            {{ toolLabel(t.tool) }} — {{ t.status }}
            <span v-if="t.missing?.length">（缺 {{ t.missing.join('、') }}）</span>
          </li>
        </ul>
      </div>
      <div v-if="message.evidence != null">检索证据：{{ message.evidence.length }} 条</div>
      <div v-if="message.latencyMs != null">耗时：{{ message.latencyMs }} ms</div>
    </div>
  </div>
</template>
