import { ArticleGrid } from '../components/ArticleGrid'
import { ErrorState } from '../components/ErrorState'
import { Pagination } from '../components/Pagination'
import { useLatestArticles } from '../hooks/useArticles'
import { useState } from 'react'

export function LatestPage() { const [page, setPage] = useState(1); const query = useLatestArticles({ page, page_size: 12 }); return <div><h1 className="text-3xl font-bold">Latest News</h1><p className="mt-2 text-slate-600">Newly collected reporting, ordered by recency.</p><div className="mt-6">{query.isError ? <ErrorState error={query.error} onRetry={() => query.refetch()} /> : <ArticleGrid articles={query.data?.results} loading={query.isLoading} />}{query.data && <Pagination page={page} hasNext={Boolean(query.data.next)} hasPrevious={Boolean(query.data.previous)} count={query.data.count} onPageChange={setPage} />}</div></div> }
