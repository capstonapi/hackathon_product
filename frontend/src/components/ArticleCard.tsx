import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { formatRelativeDate } from '../utils/formatDate'
import { CategoryBadge } from './CategoryBadge'

interface ArticleCardProps {
  id: number
  title: string
  source?: string | null
  publishedAt?: string | null
  summary?: string | null
  category?: string
  distance?: number | null
  action?: ReactNode
}

export function ArticleCard({ id, title, source, publishedAt, summary, category, distance, action }: ArticleCardProps) {
  return (
    <article className="flex flex-col gap-2 rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-center justify-between gap-2">
        {category ? <CategoryBadge label={category} /> : <span />}
        {typeof distance === 'number' && (
          <span className="text-xs text-slate-400">match {(1 - distance).toFixed(2)}</span>
        )}
      </div>
      <h3 className="text-base font-semibold leading-snug text-slate-900">
        <Link to={`/article/${id}`} className="hover:text-brand-700">
          {title}
        </Link>
      </h3>
      {summary && <p className="line-clamp-3 text-sm text-slate-600">{summary}</p>}
      <div className="mt-auto flex items-center justify-between gap-2 pt-2 text-xs text-slate-400">
        <span>
          {source ?? 'Unknown source'} · {formatRelativeDate(publishedAt)}
        </span>
        {action}
      </div>
    </article>
  )
}
