import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ClarificationCard from './ClarificationCard.vue'

describe('ClarificationCard', () => {
  it('渲染澄清问题与班级选项', () => {
    const w = mount(ClarificationCard, {
      props: { clarification: { missing: ['student_group'], question: '需要补充参数：student_group' } },
    })
    expect(w.text()).toContain('需要补充参数')
    expect(w.text()).toContain('A 班')
    expect(w.text()).toContain('B 班')
  })

  it('点击 A 班发出完整重查询', async () => {
    const w = mount(ClarificationCard, {
      props: { clarification: { missing: ['student_group'], question: '需要补充参数：student_group' } },
    })
    await w.findAll('button')[0].trigger('click')
    expect(w.emitted('answer')).toBeTruthy()
    expect(w.emitted('answer')![0]).toEqual(['查A班的课表'])
  })

  it('点击 B 班发出完整重查询', async () => {
    const w = mount(ClarificationCard, {
      props: { clarification: { missing: ['student_group'], question: '需要补充参数：student_group' } },
    })
    await w.findAll('button')[1].trigger('click')
    expect(w.emitted('answer')![0]).toEqual(['查B班的课表'])
  })
})
