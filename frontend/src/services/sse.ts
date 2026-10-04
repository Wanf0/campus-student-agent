import type { SSEEvent } from '../types'

/**
 * 解析 SSE 响应体为类型化事件流。
 * 后端事件格式：`data: {json}\n\n`
 */
export async function* parseSSE(response: Response): AsyncGenerator<SSEEvent> {
  if (!response.body) {
    throw new Error('响应体为空')
  }
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''

    for (const part of parts) {
      const line = part.trim()
      if (!line.startsWith('data:')) continue
      const payload = line.slice(5).trim()
      if (!payload) continue
      try {
        yield JSON.parse(payload) as SSEEvent
      } catch {
        // 忽略无法解析的帧
      }
    }
  }
}
