import { describe, it, expect } from 'vitest'
import { useChatStore } from './chat'
import type { ChatMessage } from '../types'

function newMsg(): ChatMessage {
  return { id: '1', role: 'assistant', content: '', streaming: true, toolCalls: [] }
}

describe('chat store applyEvent', () => {
  it('按事件顺序累积消息状态', () => {
    const store = useChatStore()
    const msg = newMsg()

    store.applyEvent(msg, { event: 'start', intent: 'qa', run_id: 'r1', conversation_id: 5 })
    expect(msg.intent).toBe('qa')
    expect(msg.runId).toBe('r1')
    expect(store.state.currentId).toBe(5)

    store.applyEvent(msg, { event: 'evidence', items: [{ text: 't', source_title: 's', source_authority: 1 }] })
    expect(msg.evidence).toHaveLength(1)

    store.applyEvent(msg, { event: 'tool_call', tool: 'query_score', status: 'ok' })
    expect(msg.toolCalls).toHaveLength(1)
    expect(msg.toolCalls![0].status).toBe('ok')

    store.applyEvent(msg, { event: 'clarification', missing: ['student_group'], question: 'q' })
    expect(msg.clarification?.missing).toEqual(['student_group'])

    store.applyEvent(msg, { event: 'token', content: '你好' })
    expect(msg.content).toBe('你好')

    store.applyEvent(msg, { event: 'done', citations: [{ title: 'x', authority: '校级' }] })
    expect(msg.citations).toHaveLength(1)
  })

  it('空证据赋值为空数组', () => {
    const store = useChatStore()
    const msg = newMsg()
    store.applyEvent(msg, { event: 'evidence', items: [] })
    expect(msg.evidence).toEqual([])
  })

  it('错误事件设置错误与可重试标记', () => {
    const store = useChatStore()
    const msg = newMsg()
    store.applyEvent(msg, { event: 'error', message: '查询失败', retryable: true })
    expect(msg.error).toBe('查询失败')
    expect(msg.retryable).toBe(true)
  })
})
