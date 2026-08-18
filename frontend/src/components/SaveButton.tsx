import { useAuth } from '../context/AuthContext'
import { useIsArticleSaved, useSaveArticle, useUnsaveArticle } from '../hooks/useSaved'
import { Button } from './Button'

export function SaveButton({ articleId }: { articleId: number }) {
  const { isAuthenticated } = useAuth()
  const { isSaved } = useIsArticleSaved(articleId)
  const saveMutation = useSaveArticle()
  const unsaveMutation = useUnsaveArticle()

  if (!isAuthenticated) return null

  const pending = saveMutation.isPending || unsaveMutation.isPending

  return (
    <Button
      variant={isSaved ? 'secondary' : 'primary'}
      disabled={pending}
      onClick={(event) => {
        event.preventDefault()
        if (isSaved) {
          unsaveMutation.mutate(articleId)
        } else {
          saveMutation.mutate(articleId)
        }
      }}
    >
      {isSaved ? 'Saved ✓' : 'Save'}
    </Button>
  )
}
