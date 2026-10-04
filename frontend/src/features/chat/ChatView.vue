<script setup lang="ts">
import { computed, ref } from 'vue'
import { chatStore } from '../../stores/chat'
import MessageBubble from '../../components/MessageBubble.vue'
import EvidenceList from '../../components/EvidenceList.vue'
import ToolStatus from '../../components/ToolStatus.vue'
import ClarificationCard from '../../components/ClarificationCard.vue'
import TracePanel from '../../components/TracePanel.vue'
import ErrorState from '../../components/ErrorState.vue'

const store = chatStore
const msgBox = ref<HTMLElement | null>(null)

const messages = computed(() => store.state.messages)

function scrollBottom() {
  requestAnimationFrame(() => {
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
  })
}

function send() {
  store.send().then(scrollBottom)
}

function onClarificationAnswer(value: string) {
  store.state.draft = value
  store.send().then(scrollBottom)
}

function onRetry() {
  const lastUser = [...store.state.messages].reverse().find((m) => m.role === 'user')
  if (lastUser) {
    store.state.draft = lastUser.content
    store.send().then(scrollBottom)
  }
}
</script>

<template>
  <main class="chat-main">
    <div class="messages" ref="msgBox">
      <div v-for="m in messages" :key="m.id" class="msg" :class="m.role">
        <div class="avatar" :class="m.role">{{ m.role === 'user' ? '我' : 'AI' }}</div>
        <div class="msg-body">
          <MessageBubble :message="m" />

          <ToolStatus v-if="m.toolCalls?.length" :tools="m.toolCalls" />

          <ClarificationCard
            v-if="m.clarification && !m.streaming"
            :clarification="m.clarification"
            @answer="onClarificationAnswer"
          />

          <EvidenceList v-if="m.evidence?.length && !m.streaming" :evidence="m.evidence" :citations="m.citations ?? []" />

          <ErrorState v-if="m.error && !m.streaming" :message="m.error" :retryable="m.retryable ?? false" @retry="onRetry" />

          <TracePanel :message="m" />
        </div>
      </div>
      <div v-if="store.state.loading" class="msg assistant">
        <div class="avatar assistant">AI</div>
        <div class="msg-body"><div class="bubble typing">…</div></div>
      </div>
    </div>

    <div class="input-bar">
      <input
        v-model="store.state.draft"
        placeholder="输入你的问题，例如：查A班的课表"
        :disabled="store.state.loading"
        @keyup.enter="send"
      />
      <button :disabled="store.state.loading" @click="send">发送</button>
    </div>
  </main>
</template>
