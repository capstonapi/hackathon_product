export type TrustStatus = 'grounded' | 'low_confidence' | 'fallback'

export interface Citation {
  marker: number
  source: string
  title: string
  url: string
  published_at?: string | null
  retrieved_at?: string | null
}

export interface SourceDocument {
  source_type: string
  source: string
  title: string
  url: string
  relevance_score: number
  published_at?: string | null
  retrieved_at?: string | null
  trust_score?: number
}

export interface ChatRequest {
  question: string
  article_id?: number
  conversation_id?: number
}

export interface ChatResponse {
  conversation_id: number
  answer: string
  citations: Citation[]
  sources: SourceDocument[]
  trust_status: TrustStatus
  metadata: { intent: string | null }
}

export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  citations: Citation[]
  sources: SourceDocument[]
  trust_status: TrustStatus | ''
  created_at: string
}

export interface ConversationSummary {
  id: number
  article_id: number
  article_title: string
  created_at: string
  updated_at: string
  last_message: string | null
}
