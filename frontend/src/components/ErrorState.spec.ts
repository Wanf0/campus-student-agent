import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorState from './ErrorState.vue'

describe('ErrorState', () => {
  it('渲染错误消息', () => {
    const w = mount(ErrorState, { props: { message: '网络错误', retryable: false } })
    expect(w.text()).toContain('网络错误')
  })

  it('可重试时显示重试按钮并发出事件', async () => {
    const w = mount(ErrorState, { props: { message: '连接中断', retryable: true } })
    expect(w.find('.retry-btn').exists()).toBe(true)
    await w.find('.retry-btn').trigger('click')
    expect(w.emitted('retry')).toBeTruthy()
  })

  it('不可重试时不显示重试按钮', () => {
    const w = mount(ErrorState, { props: { message: '查询失败', retryable: false } })
    expect(w.find('.retry-btn').exists()).toBe(false)
  })
})
