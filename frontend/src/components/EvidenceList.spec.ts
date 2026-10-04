import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EvidenceList from './EvidenceList.vue'
import type { Evidence } from '../types'

const ev: Evidence = {
  text: '国家奖学金：每人每年8000元。',
  source_title: '奖学金评定办法',
  source_authority: 4,
  publish_date: '2026-09-01',
  effective_to: '2027-09-01',
  version: '2026版',
}

describe('EvidenceList', () => {
  it('渲染证据卡片的元数据与摘录', () => {
    const w = mount(EvidenceList, { props: { evidence: [ev], citations: [] } })
    expect(w.text()).toContain('依据（Evidence）')
    expect(w.text()).toContain('奖学金评定办法')
    expect(w.text()).toContain('校级')
    expect(w.text()).toContain('发布 2026-09-01')
    expect(w.text()).toContain('版本 2026版')
  })

  it('空证据时不渲染', () => {
    const w = mount(EvidenceList, { props: { evidence: [], citations: [] } })
    expect(w.find('.evidence-panel').exists()).toBe(false)
  })

  it('未知权威等级降级为"未知"', () => {
    const w = mount(EvidenceList, {
      props: { evidence: [{ ...ev, source_authority: 1 }], citations: [] },
    })
    expect(w.text()).toContain('未知')
  })
})
