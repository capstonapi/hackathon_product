import { useState } from 'react'
import { ArticleGrid } from '../components/ArticleGrid'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { Pagination } from '../components/Pagination'
import { useAuth } from '../context/AuthContext'
import { useSavedArticles } from '../hooks/useSaved'

export function SavedPage() { const [page,setPage]=useState(1); const {isAuthenticated}=useAuth(); const query=useSavedArticles({page,page_size:12}); if(!isAuthenticated) return <div><h1 className="text-3xl font-bold">Saved Articles</h1><div className="mt-6"><EmptyState title="Sign in to save articles" description="Saved articles are tied to your account." /></div></div>; return <div><h1 className="text-3xl font-bold">Saved Articles</h1><div className="mt-6">{query.isError?<ErrorState error={query.error} onRetry={()=>query.refetch()}/>:query.data?.results.length===0?<EmptyState title="Nothing saved yet" description="Use Save on an article to build your reading list."/>:<ArticleGrid articles={query.data?.results} loading={query.isLoading}/>} {query.data&&<Pagination page={page} hasNext={Boolean(query.data.next)} hasPrevious={Boolean(query.data.previous)} count={query.data.count} onPageChange={setPage}/>}</div></div> }
