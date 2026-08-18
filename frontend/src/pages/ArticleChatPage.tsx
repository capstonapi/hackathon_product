import { FormEvent, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { AuthDialog } from '../components/AuthDialog'
import { CitationList } from '../components/CitationList'
import { ErrorState } from '../components/ErrorState'
import { Spinner } from '../components/Spinner'
import { TrustBadge } from '../components/TrustBadge'
import { useAuth } from '../context/AuthContext'
import { useArticle } from '../hooks/useArticles'
import { useConversation, useSendChatMessage } from '../hooks/useChat'
import { useRetrievalStatus } from '../hooks/useRetrievalStatus'

export function ArticleChatPage() {
  const id = Number(useParams().id); const { isAuthenticated } = useAuth(); const article = useArticle(id)
  const [conversationId, setConversationId] = useState<number | null>(null); const [question, setQuestion] = useState(''); const [streamStatus, setStreamStatus] = useState<string | null>(null)
  const send = useSendChatMessage(); const messages = useConversation(conversationId); const fallbackStatus = useRetrievalStatus(send.isPending); const status = streamStatus || fallbackStatus
  useEffect(() => { setConversationId(null); setStreamStatus(null) }, [id])
  const submit = (event: FormEvent) => { event.preventDefault(); const value = question.trim(); if (!value) return; setQuestion(''); setStreamStatus('Searching internal knowledge...'); send.mutate({ payload: { article_id: id, question: value, conversation_id: conversationId ?? undefined }, onStatus: setStreamStatus }, { onSuccess: response => { setConversationId(response.conversation_id); setStreamStatus(null) }, onError: () => setStreamStatus(null) }) }
  if (!isAuthenticated) return <div><h1 className="text-3xl font-bold">Article chat</h1><div className="mt-6 rounded-xl border bg-white p-6"><p className="text-slate-600">Sign in to ask questions and keep your conversation history.</p><div className="mt-4"><AuthDialog triggerLabel="Sign in to chat" /></div></div></div>
  return <div className="mx-auto max-w-3xl"><Link to={`/article/${id}`} className="text-sm font-medium text-brand-700 hover:underline">← Back to article</Link><h1 className="mt-3 text-3xl font-bold">Ask about this article</h1><p className="mt-2 text-slate-600">{article.data?.title || 'Grounded answers from the article and trusted retrieval sources.'}</p><div className="mt-6 space-y-4">{messages.data?.map(message => <div key={message.id} className={`rounded-xl p-4 ${message.role === 'user' ? 'ml-8 bg-brand-600 text-white' : 'mr-8 bg-white shadow-sm'}`}><p className="whitespace-pre-wrap">{message.content}</p>{message.role === 'assistant' && <><TrustBadge status={message.trust_status} /><CitationList citations={message.citations} /></>}</div>)}{send.isPending && <div className="rounded-xl bg-white p-4"><Spinner label={status || 'Preparing answer'} /><p className="mt-2 text-xs text-slate-500">We show retrieval progress, not private reasoning.</p></div>}{send.isError && <ErrorState error={send.error} onRetry={() => send.reset()} />}</div><form onSubmit={submit} className="sticky bottom-3 mt-6 flex gap-2 rounded-xl border bg-white p-3 shadow-lg"><label className="sr-only" htmlFor="question">Question</label><input id="question" value={question} onChange={event => setQuestion(event.target.value)} disabled={send.isPending} placeholder="Ask a focused question…" className="min-w-0 flex-1 rounded-md border px-3 py-2" /><button disabled={send.isPending || !question.trim()} className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50">Send</button></form></div>
}
