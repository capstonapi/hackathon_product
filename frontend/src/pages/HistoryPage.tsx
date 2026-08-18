import { useState } from 'react'
import { Link } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { Pagination } from '../components/Pagination'
import { useAuth } from '../context/AuthContext'
import { useHistory } from '../hooks/useHistory'
import { formatRelativeDate } from '../utils/formatDate'

export function HistoryPage() { const [page,setPage]=useState(1); const {isAuthenticated}=useAuth(); const query=useHistory({page,page_size:15}); if(!isAuthenticated) return <div><h1 className="text-3xl font-bold">Reading History</h1><div className="mt-6"><EmptyState title="Sign in to view history" description="Your article conversations will appear here."/></div></div>; return <div><h1 className="text-3xl font-bold">Reading History</h1><p className="mt-2 text-slate-600">Continue article-specific conversations.</p><div className="mt-6 space-y-3">{query.isError?<ErrorState error={query.error} onRetry={()=>query.refetch()}/>:query.data?.results.length===0?<EmptyState title="No history yet" description="Ask a question about an article to start a conversation."/>:query.data?.results.map(item=><Link to={`/article/${item.article_id}/chat`} key={item.id} className="block rounded-lg border bg-white p-4 transition hover:border-brand-300"><div className="flex justify-between gap-3"><h2 className="font-semibold">{item.article_title}</h2><time className="shrink-0 text-xs text-slate-400">{formatRelativeDate(item.updated_at)}</time></div>{item.last_message&&<p className="mt-2 line-clamp-2 text-sm text-slate-600">{item.last_message}</p>}</Link>)}{query.data&&<Pagination page={page} hasNext={Boolean(query.data.next)} hasPrevious={Boolean(query.data.previous)} count={query.data.count} onPageChange={setPage}/>}</div></div> }
