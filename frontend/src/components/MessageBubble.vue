<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '../types'
import { escapeHtml, renderMarkdown } from '../utils/markdown'

const props = defineProps<{ message: ChatMessage }>()

const html = computed(() => {
  if (props.message.role === 'user') return escapeHtml(props.message.content)
  if (props.message.streaming) return `<p>${escapeHtml(props.message.content)}</p>`
  return renderMarkdown(props.message.content)
})
</script>

<template>
  <div class="bubble md" :class="message.role" v-html="html"></div>
</template>
