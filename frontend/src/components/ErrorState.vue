<script setup lang="ts">
defineProps<{ message: string; retryable: boolean }>()
const emit = defineEmits<{ (e: 'retry'): void }>()
</script>

<template>
  <div class="error-state">
    <div class="error-msg">{{ message || '出错了' }}</div>
    <button v-if="retryable" class="retry-btn" @click="emit('retry')">重试</button>
  </div>
</template>
