import type { TrustStatus } from '../types/chat'

const CONFIG: Record<TrustStatus, { label: string; className: string }> = {
  grounded: { label: '✓ Grounded in sources', className: 'bg-green-50 text-green-700' },
  low_confidence: { label: '⚠ Limited context found', className: 'bg-amber-50 text-amber-700' },
  fallback: { label: '⚠ Live AI unavailable — showing sourced excerpts', className: 'bg-slate-100 text-slate-600' },
}

export function TrustBadge({ status }: { status: TrustStatus | '' }) {
  if (!status) return null
  const config = CONFIG[status]
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}
