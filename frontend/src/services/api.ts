import type { Conversation, SSEEvent } from '../types'
import { parseSSE } from './sse'

export interface ChatPayload {
  message: string
  conversation_id: number | null
  user_id: number | null
}

export async function login(username: string, password: string): Promise<{ user_id: number; username: string; role: string }> {
  const r = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  const data = await r.json()
  if (!r.ok) throw new Error(data.detail || '登录失败')
  return data
}

export async function register(username: string, password: string): Promise<{ user_id: number; username: string; role: string }> {
  const r = await fetch('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  const data = await r.json()
  if (!r.ok) throw new Error(data.detail || '注册失败')
  return data
}

export async function listConversations(userId: number | null): Promise<Conversation[]> {
  const q = userId ? `?user_id=${userId}` : ''
  const r = await fetch('/conversations' + q)
  if (!r.ok) return []
  return r.json()
}

export async function getConversation(id: number): Promise<{ role: string; content: string }[]> {
  const r = await fetch(`/conversations/${id}`)
  if (!r.ok) return []
  return r.json()
}

export async function listDocuments(): Promise<{ id: number; title: string; category: string }[]> {
  const r = await fetch('/admin/documents')
  if (!r.ok) return []
  return r.json()
}

export async function uploadDocument(file: File): Promise<void> {
  const fd = new FormData()
  fd.append('file', file)
  const r = await fetch('/admin/upload', { method: 'POST', body: fd })
  if (!r.ok) throw new Error('上传失败')
}

export async function deleteDocument(id: number): Promise<void> {
  await fetch(`/admin/documents/${id}`, { method: 'DELETE' })
}

export async function chatStream(payload: ChatPayload, onEvent: (e: SSEEvent) => void): Promise<void> {
  const resp = await fetch('/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!resp.ok) throw new Error(`请求失败 ${resp.status}`)
  for await (const ev of parseSSE(resp)) {
    onEvent(ev)
  }
}
