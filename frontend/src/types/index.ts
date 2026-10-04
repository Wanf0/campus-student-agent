/// <reference types="vite/client" />

export type Intent = 'qa' | 'academic' | 'study' | 'psychology' | 'planning'

export type Phase = 'routing' | 'retrieving' | 'rewriting' | 'tool_calling' | 'generating'

export interface Evidence {
  text: string
  source_title: string
  source_authority: number
  publish_date?: string | null
  effective_from?: string | null
  effective_to?: string | null
  version?: string | null
  department?: string | null
  doc_type?: string
  retrieval_score?: number | null
  rerank_score?: number | null
}

export interface Citation {
  title: string
  authority: string
  publish_date?: string | null
}

export type ToolStatus = 'start' | 'ok' | 'error' | 'missing_params'

export interface ToolEvent {
  tool: string
  status: ToolStatus
  missing?: string[]
}

export interface ClarificationRequest {
  missing: string[]
  question: string
}

export interface SSEEvent {
  event:
    | 'start'
    | 'status'
    | 'evidence'
    | 'tool_call'
    | 'clarification'
    | 'token'
    | 'error'
    | 'done'
  intent?: Intent
  phase?: Phase
  items?: Evidence[]
  tool?: string
  status?: ToolStatus
  missing?: string[]
  question?: string
  content?: string
  message?: string
  retryable?: boolean
  citations?: Citation[]
  run_id?: string
  conversation_id?: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  streaming?: boolean
  intent?: Intent
  phase?: Phase
  evidence?: Evidence[]
  citations?: Citation[]
  toolCalls?: ToolEvent[]
  clarification?: ClarificationRequest | null
  error?: string | null
  retryable?: boolean
  runId?: string
}

export interface Conversation {
  id: number
  title: string
  user_id: number
}

export function authorityLabel(authority: number): string {
  return { 4: '校级', 3: '院级', 2: '部门', 1: '未知' }[authority] ?? '未知'
}

export function intentLabel(intent: string): string {
  const map: Record<string, string> = {
    qa: '校园问答',
    academic: '教务查询',
    study: '学习辅导',
    psychology: '心理陪伴',
    planning: '学习规划',
  }
  return map[intent] ?? intent
}

export function toolLabel(tool: string): string {
  const map: Record<string, string> = {
    query_timetable: '查询课表',
    query_score: '查询成绩',
    query_exam: '查询考试安排',
    search_knowledge: '检索知识库',
  }
  return map[tool] ?? tool
}
