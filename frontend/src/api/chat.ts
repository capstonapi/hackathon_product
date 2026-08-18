import { apiClient } from './client'
import type { ChatRequest, ChatResponse, Message } from '../types/chat'
import { getToken } from '../services/authTokenStorage'

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>('/chat/', payload)
  return data
}

export async function streamChatMessage(payload: ChatRequest, onStatus: (status: string) => void): Promise<ChatResponse> {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/chat/stream/`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', ...(getToken() ? { Authorization: `Token ${getToken()}` } : {}) }, body: JSON.stringify(payload),
  })
  if (!response.ok || !response.body) throw new Error(`Chat request failed (${response.status})`)
  const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = ''; let result: ChatResponse | null = null
  while (true) { const { done, value } = await reader.read(); if (done) break; buffer += decoder.decode(value, { stream: true }); const events = buffer.split('\n\n'); buffer = events.pop() || ''; for (const event of events) { const type = event.match(/^event: (.+)$/m)?.[1]; const data = event.match(/^data: (.+)$/m)?.[1]; if (!data) continue; const parsed = JSON.parse(data); if (type === 'status') onStatus(parsed.status); if (type === 'answer') result = parsed } }
  if (!result) throw new Error('Chat stream ended without an answer.')
  return result
}

export async function getConversationMessages(conversationId: number): Promise<Message[]> {
  const { data } = await apiClient.get<Message[]>(`/chat/${conversationId}/`)
  return data
}
