export interface ArticleListItem {
  id: number
  category: string
  title: string
  description: string | null
  url: string
  source: string | null
  published_at: string | null
  image_url: string | null
  summary: string | null
  fetched_at: string
  verification: Verification
}

export interface Verification {
  status: 'VERIFIED'
  source_trust: number
  quality_score?: number
  freshness_score?: number
  corroborating_sources: Array<{ article_id: number; source: string; url: string; title: string; similarity: number; trust_score: number }>
}

export interface Entity {
  text: string
  label: string
}

export interface ArticleDetail extends ArticleListItem {
  content: string | null
  entities: Entity[] | null
  keywords: string[] | null
  extraction_method: string | null
  authors: string[] | null
  background: string | null
  timeline: string | null
  importance: string | null
  expected_impact: string | null
  context_article_ids: number[] | null
  has_insights: boolean
  claims: Claim[]
}

export interface ClaimEvidence { source: string; title: string; url: string; excerpt: string; stance: 'supports' | 'contradicts'; retrieved_at: string }
export interface Claim { id: number; text: string; status: 'SUPPORTED' | 'CONTRADICTED' | 'MIXED' | 'INSUFFICIENT_EVIDENCE'; evidence: ClaimEvidence[] }

export interface RelatedArticle {
  id: number
  title: string
  source: string | null
  published_at: string | null
  url: string
  summary: string | null
  distance: number | null
}

export interface TimelineEvent {
  id: number
  title: string
  source: string | null
  published_at: string | null
  url: string
}

export interface TimelineResponse {
  narrative: string | null
  events: TimelineEvent[]
}

export type SearchMode = 'semantic' | 'keyword'

export interface ArticleListParams {
  category?: string
  source?: string
  date_from?: string
  date_to?: string
  page?: number
}

export interface ArticleSearchParams extends ArticleListParams {
  q: string
  mode?: SearchMode
}
