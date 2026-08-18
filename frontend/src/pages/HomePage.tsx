import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'
import { ArticleGrid } from '../components/ArticleGrid'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { useCategories } from '../hooks/useCategories'
import { useLatestArticles } from '../hooks/useArticles'
import { useAuth } from '../context/AuthContext'
import { useHistory } from '../hooks/useHistory'
import { useSavedArticles } from '../hooks/useSaved'

function Section({ title, link, children }: { title: string; link?: string; children: ReactNode }) {
  return <section className="space-y-4"><div className="flex items-baseline justify-between"><h2 className="text-xl font-bold text-slate-900">{title}</h2>{link && <Link className="text-sm font-medium text-brand-700 hover:underline" to={link}>View all</Link>}</div>{children}</section>
}

export function HomePage() {
  const latest = useLatestArticles({ page_size: 6 })
  const categories = useCategories()
  const { isAuthenticated } = useAuth()
  const saved = useSavedArticles({ page_size: 3 })
  const history = useHistory({ page_size: 3 })
  return <div className="space-y-10">
    <section className="rounded-2xl bg-slate-900 px-6 py-10 text-white sm:px-10"><p className="mb-2 text-sm font-semibold uppercase tracking-widest text-brand-300">Your news workspace</p><h1 className="max-w-2xl text-3xl font-bold tracking-tight sm:text-4xl">Understand what matters, without losing the thread.</h1><p className="mt-3 max-w-xl text-slate-300">Track the latest reporting, search your library, and ask grounded questions about any story.</p><Link to="/latest" className="mt-6 inline-flex rounded-md bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-100">Explore latest news</Link></section>
    <Section title="Browse by topic"><div className="flex flex-wrap gap-2">{categories.data?.map(c => <Link key={c.key} to={`/library?category=${encodeURIComponent(c.key)}`} className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 hover:border-brand-300 hover:text-brand-700">{c.title} <span className="text-slate-400">{c.count}</span></Link>)}{categories.isError && <ErrorState error={categories.error} onRetry={() => categories.refetch()} />}</div></Section>
    <Section title="Latest news" link="/latest">{latest.isError ? <ErrorState error={latest.error} onRetry={() => latest.refetch()} /> : <ArticleGrid articles={latest.data?.results} loading={latest.isLoading} />}</Section>
    {isAuthenticated && <div className="grid gap-8 lg:grid-cols-2"><Section title="Continue reading" link="/history">{history.data?.results.length ? <div className="space-y-2">{history.data.results.map(item => <Link key={item.id} to={`/article/${item.article_id}/chat`} className="block rounded-lg border bg-white p-4 hover:border-brand-300"><p className="font-semibold">{item.article_title}</p><p className="mt-1 text-sm text-slate-500">{item.last_message || 'Open conversation'}</p></Link>)}</div> : <EmptyState title="No reading history yet" description="Open an article and start a conversation to continue it here." />}</Section><Section title="Saved articles" link="/saved">{saved.data?.results.length ? <ArticleGrid articles={saved.data.results} /> : <EmptyState title="No saved articles" description="Save stories to keep them close at hand." />}</Section></div>}
  </div>
}
