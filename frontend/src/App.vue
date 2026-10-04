<script setup lang="ts">
import { ref } from 'vue'
import { chatStore } from './stores/chat'
import LoginView from './features/auth/LoginView.vue'
import ChatView from './features/chat/ChatView.vue'

const store = chatStore
const view = ref<'chat' | 'knowledge'>('chat')

async function onUpload(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    await store.upload(file)
  } catch {
    alert('上传失败')
  }
  input.value = ''
}
</script>

<template>
  <LoginView v-if="!store.state.loggedIn" />

  <div v-else class="chat-wrap">
    <aside class="sidebar">
      <div class="brand">🎓 校园学生智能体</div>
      <button class="new-chat" @click="store.newChat()">＋ 新建对话</button>
      <button class="new-chat kb" @click="view = 'knowledge'; store.loadDocs()">📚 知识库管理</button>
      <div class="conv-list">
        <div
          v-for="c in store.state.conversations"
          :key="c.id"
          class="conv-item"
          :class="{ active: c.id === store.state.currentId }"
          @click="view = 'chat'; store.openConversation(c.id)"
        >
          {{ c.title || '未命名对话' }}
        </div>
      </div>
      <div class="user-box">
        <span>{{ store.state.username }}</span>
        <button @click="store.logout()">退出</button>
      </div>
    </aside>

    <ChatView v-if="view === 'chat'" />

    <main v-else class="chat-main">
      <div class="kb-view">
        <div class="kb-head">
          <h2>知识库管理</h2>
          <label class="upload-btn">
            上传文档
            <input type="file" accept=".txt,.pdf" hidden @change="onUpload" />
          </label>
        </div>
        <p class="kb-hint">上传的文档将自动清洗、切分并向量化，供智能体检索使用。</p>
        <div class="kb-list">
          <div v-for="d in store.state.docs" :key="d.id" class="kb-item">
            <span class="kb-title">{{ d.title }}</span>
            <span class="kb-cat">{{ d.category }}</span>
            <button class="kb-del" @click="store.removeDoc(d.id)">删除</button>
          </div>
          <div v-if="!store.state.docs.length" class="kb-empty">暂无文档</div>
        </div>
      </div>
    </main>
  </div>
</template>
