// @vitest-environment node
import { describe, it, expect } from 'vitest'
import { parseSSE } from './sse'

function makeResponse(sseString: string): Response {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(sseString))
      controller.close()
    },
  })
  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' } })
}

describe('parseSSE', () => {
  it('解析完整事件流', async () => {
    const data =
      'data: {"event":"start","intent":"qa","run_id":"r1"}\n\n' +
      'data: {"event":"status","phase":"retrieving"}\n\n' +
      'data: {"event":"evidence","items":[{"text":"t","source_title":"s","source_authority":1}]}\n\n' +
      'data: {"event":"token","content":"你好"}\n\n' +
      'data: {"event":"done","citations":[]}\n\n'
    const events = []
    for await (const ev of parseSSE(makeResponse(data))) {
      events.push(ev)
    }
    expect(events).toHaveLength(5)
    expect(events[0]).toEqual({ event: 'start', intent: 'qa', run_id: 'r1' })
    expect(events[1]).toEqual({ event: 'status', phase: 'retrieving' })
    expect(events[2].event).toBe('evidence')
    expect(events[2].items).toHaveLength(1)
    expect(events[3]).toEqual({ event: 'token', content: '你好' })
  })

  it('处理跨 chunk 的分帧', async () => {
    const encoder = new TextEncoder()
    const full = 'data: {"event":"token","content":"abcdef"}\n\n'
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(full.slice(0, 15)))
        controller.enqueue(encoder.encode(full.slice(15)))
        controller.close()
      },
    })
    const resp = new Response(stream)
    const events = []
    for await (const ev of parseSSE(resp)) events.push(ev)
    expect(events).toHaveLength(1)
    expect(events[0]).toEqual({ event: 'token', content: 'abcdef' })
  })

  it('忽略无法解析的帧', async () => {
    const data = 'data: {invalid json}\n\ndata: {"event":"token","content":"ok"}\n\n'
    const events = []
    for await (const ev of parseSSE(makeResponse(data))) events.push(ev)
    expect(events).toHaveLength(1)
    expect(events[0].event).toBe('token')
  })

  it('空响应体抛出错误', async () => {
    await expect(async () => {
      for await (const _ of parseSSE(new Response(null))) {
        /* noop */
      }
    }).rejects.toThrow()
  })
})
