import { reactive } from 'vue'
import type { ChatMessage, Conversation, SSEEvent } from '../types'
import * as api from '../services/api'

let idCounter = 0
function genId(): string {
  return `m${++idCounter}`
}

export interface ChatState {
  loggedIn: boolean
  username: string
  password: string
  authError: string
  userId: number | null
  conversations: Conversation[]
  currentId: number | null
  messages: ChatMessage[]
  draft: string
  loading: boolean
  docs: { id: number; title: string; category: string }[]
}

export function useChatStore() {
  const state = reactive<ChatState>({
    loggedIn: false,
    username: '',
    password: '',
    authError: '',
    userId: null,
    conversations: [],
    currentId: null,
    messages: [],
    draft: '',
    loading: false,
    docs: [],
  })

  function applyEvent(msg: ChatMessage, ev: SSEEvent) {
    switch (ev.event) {
      case 'start':
        msg.intent = ev.intent
        msg.runId = ev.run_id
        if (ev.conversation_id != null) state.currentId = ev.conversation_id
        break
      case 'status':
        msg.phase = ev.phase
        break
      case 'evidence':
        msg.evidence = ev.items ?? []
        break
      case 'tool_call':
        msg.toolCalls = msg.toolCalls ?? []
        msg.toolCalls.push({ tool: ev.tool ?? '', status: ev.status ?? 'start', missing: ev.missing })
        break
      case 'clarification':
        msg.clarification = { missing: ev.missing ?? [], question: ev.question ?? '' }
        break
      case 'token':
        msg.content += ev.content ?? ''
        break
      case 'error':
        msg.error = ev.message
        msg.retryable = ev.retryable ?? false
        break
      case 'done':
        msg.citations = ev.citations ?? []
        if (ev.latency_ms != null) msg.latencyMs = ev.latency_ms
        if (ev.conversation_id != null) state.currentId = ev.conversation_id
        break
    }
  }

  async function authenticate(path: 'login' | 'register') {
    state.authError = ''
    try {
      const fn = path === 'login' ? api.login : api.register
      const data = await fn(state.username, state.password)
      state.userId = data.user_id
      state.loggedIn = true
      await loadConversations()
      newChat()
    } catch (e) {
      state.authError = (e as Error).message
    }
  }

  async function loadConversations() {
    state.conversations = await api.listConversations(state.userId)
  }

  function newChat() {
    state.currentId = null
    state.messages = []
    state.draft = ''
  }

  async function openConversation(id: number) {
    state.currentId = id
    const msgs = await api.getConversation(id)
    state.messages = msgs.map((m) => ({
      id: genId(),
      role: m.role as 'user' | 'assistant',
      content: m.content,
    }))
  }

  async function send() {
    const text = state.draft.trim()
    if (!text || state.loading) return
    state.messages.push({ id: genId(), role: 'user', content: text })
    state.draft = ''
    state.loading = true

    const msg: ChatMessage = {
      id: genId(),
      role: 'assistant',
      content: '',
      streaming: true,
      toolCalls: [],
      clarification: null,
    }
    state.messages.push(msg)

    try {
      await api.chatStream(
        { message: text, conversation_id: state.currentId, user_id: state.userId },
        (ev) => applyEvent(msg, ev),
      )
      msg.streaming = false
      await loadConversations()
    } catch (e) {
      msg.content = msg.content || `出错了：${(e as Error).message}`
      msg.streaming = false
      msg.error = (e as Error).message
      msg.retryable = true
    } finally {
      state.loading = false
    }
  }

  async function loadDocs() {
    state.docs = await api.listDocuments()
  }

  async function upload(file: File) {
    await api.uploadDocument(file)
    await loadDocs()
  }

  async function removeDoc(id: number) {
    await api.deleteDocument(id)
    await loadDocs()
  }

  function logout() {
    state.loggedIn = false
    state.conversations = []
    state.messages = []
    state.currentId = null
    state.docs = []
  }

  return {
    state,
    authenticate,
    loadConversations,
    newChat,
    openConversation,
    send,
    loadDocs,
    upload,
    removeDoc,
    logout,
    applyEvent,
  }
}

export type ChatStore = ReturnType<typeof useChatStore>

/** 应用级单例 store */
export const chatStore = useChatStore()
