import type { ParseResumeResponse, OptimizeRequest, OptimizeResponse } from '@/types'

const API_BASE = (import.meta.env.VITE_RESUME_API_BASE as string | undefined)?.trim()
const BASE_URL = API_BASE && API_BASE.length > 0 ? API_BASE : '/api/resume'

export async function parseResume(file: File): Promise<ParseResumeResponse> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE_URL}/parse`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Parse failed')
  }
  return res.json()
}

export async function optimizeContent(req: OptimizeRequest): Promise<OptimizeResponse> {
  const res = await fetch(`${BASE_URL}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Optimize failed')
  }
  return res.json()
}
