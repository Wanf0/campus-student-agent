import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ToolStatus from './ToolStatus.vue'
import type { ToolEvent } from '../types'

describe('ToolStatus', () => {
  it('渲染工具成功状态', () => {
    const tools: ToolEvent[] = [{ tool: 'query_score', status: 'ok' }]
    const w = mount(ToolStatus, { props: { tools } })
    expect(w.text()).toContain('查询成绩')
    expect(w.text()).toContain('成功')
  })

  it('渲染缺少参数状态', () => {
    const tools: ToolEvent[] = [{ tool: 'query_timetable', status: 'missing_params', missing: ['student_group'] }]
    const w = mount(ToolStatus, { props: { tools } })
    expect(w.text()).toContain('查询课表')
    expect(w.text()).toContain('student_group')
  })

  it('渲染失败状态', () => {
    const tools: ToolEvent[] = [{ tool: 'query_timetable', status: 'error' }]
    const w = mount(ToolStatus, { props: { tools } })
    expect(w.text()).toContain('失败')
  })

  it('无工具调用时不渲染', () => {
    const w = mount(ToolStatus, { props: { tools: [] } })
    expect(w.find('.tool-status').exists()).toBe(false)
  })
})
