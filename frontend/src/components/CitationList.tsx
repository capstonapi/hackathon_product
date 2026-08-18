import type { Citation } from '../types/chat'

export function CitationList({ citations }: { citations: Citation[] }) {
  if (citations.length === 0) return null
  return (
    <ol className="mt-2 space-y-1 border-t border-slate-200 pt-2 text-xs text-slate-500">
      {citations.map((citation) => (
        <li key={citation.marker}>
          [{citation.marker}]{' '}
          <a href={citation.url} target="_blank" rel="noreferrer" className="font-medium text-brand-600 hover:underline">
            {citation.title}
          </a>{' '}
          — {citation.source}{citation.published_at ? ` · published ${new Date(citation.published_at).toLocaleDateString()}` : ''}{citation.retrieved_at ? ` · retrieved ${new Date(citation.retrieved_at).toLocaleDateString()}` : ''}
        </li>
      ))}
    </ol>
  )
}
