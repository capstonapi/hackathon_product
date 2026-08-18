import { ApiError } from '../types/api'
import { Button } from './Button'

function messageFor(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error) return error.message
  return 'Something went wrong.'
}

interface ErrorStateProps {
  error?: unknown
  onRetry?: () => void
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-lg border border-red-200 bg-red-50 p-8 text-center">
      <p className="text-sm font-medium text-red-800">{messageFor(error)}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  )
}
