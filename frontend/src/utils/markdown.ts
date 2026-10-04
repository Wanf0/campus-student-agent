import { marked } from 'marked'
import DOMPurify from 'dompurify'

export function renderMarkdown(text: string): string {
  const html = marked.parse(text || '', { async: false }) as string
  return DOMPurify.sanitize(html)
}

export function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

export function excerpt(text: string, max = 140): string {
  const t = text.trim().replace(/\s+/g, ' ')
  return t.length > max ? t.slice(0, max) + '…' : t
}
