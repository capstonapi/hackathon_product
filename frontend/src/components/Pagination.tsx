import { Button } from './Button'

interface PaginationProps {
  page: number
  hasNext: boolean
  hasPrevious: boolean
  onPageChange: (page: number) => void
  count?: number
}

export function Pagination({ page, hasNext, hasPrevious, onPageChange, count }: PaginationProps) {
  return (
    <nav className="flex items-center justify-between gap-4 py-4" aria-label="Pagination">
      <Button variant="secondary" onClick={() => onPageChange(page - 1)} disabled={!hasPrevious}>
        Previous
      </Button>
      <span className="text-sm text-slate-500">
        Page {page}
        {typeof count === 'number' ? ` · ${count} total` : ''}
      </span>
      <Button variant="secondary" onClick={() => onPageChange(page + 1)} disabled={!hasNext}>
        Next
      </Button>
    </nav>
  )
}
