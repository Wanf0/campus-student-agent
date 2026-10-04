<script setup lang="ts">
import type { ClarificationRequest } from '../types'

defineProps<{ clarification: ClarificationRequest }>()
const emit = defineEmits<{ (e: 'answer', value: string): void }>()

function quickFill(choice: string) {
  emit('answer', `查${choice}班的课表`)
}
</script>

<template>
  <div class="clarification">
    <div class="clarification-q">{{ clarification.question }}</div>
    <div v-if="clarification.missing.includes('student_group')" class="clarification-opts">
      <span class="clarification-hint">请选择班级：</span>
      <button class="opt-btn" @click="quickFill('A')">A 班</button>
      <button class="opt-btn" @click="quickFill('B')">B 班</button>
      <span class="clarification-hint">或直接在下方输入</span>
    </div>
  </div>
</template>
