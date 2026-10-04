import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TracePanel from './TracePanel.vue'
import type { ChatMessage } from '../types'

function msg(overrides: Partial<ChatMessage> = {}): ChatMessage {
  return { id: '1', role: 'assistant', content: '', ...overrides }
}

describe('TracePanel', () => {
  it('无 runId 时不渲染', () => {
    const w = mount(TracePanel, { props: { message: msg({ runId: undefined }) } })
    expect(w.find('.trace').exists()).toBe(false)
  })

  it('渲染 run_id 与意图', async () => {
    const w = mount(TracePanel, { props: { message: msg({ runId: 'r1', intent: 'qa' }) } })
    expect(w.find('.trace-toggle').exists()).toBe(true)
    await w.find('.trace-toggle').trigger('click')
    expect(w.text()).toContain('run_id')
    expect(w.text()).toContain('校园问答')
  })

  it('展示耗时', async () => {
    const w = mount(TracePanel, { props: { message: msg({ runId: 'r1', latencyMs: 1234 }) } })
    await w.find('.trace-toggle').trigger('click')
    expect(w.text()).toContain('1234 ms')
  })
})
