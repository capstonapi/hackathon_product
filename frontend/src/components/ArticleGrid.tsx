import type { ArticleListItem, RelatedArticle } from '../types/article'
import { ArticleCard } from './ArticleCard'
import { ArticleCardSkeletonGrid } from './Skeleton'

export function ArticleGrid({ articles, loading }: { articles?: (ArticleListItem | RelatedArticle)[]; loading?: boolean }) {
  if (loading) return <ArticleCardSkeletonGrid />
  return <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
    {articles?.map(article => <ArticleCard key={article.id} id={article.id} title={article.title} source={article.source} publishedAt={article.published_at} summary={article.summary} category={'category' in article ? article.category : undefined} distance={'distance' in article ? article.distance : undefined} />)}
  </div>
}
