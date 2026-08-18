import { useState, type FormEvent } from 'react'
import { useAuth } from '../context/AuthContext'

export function AuthDialog({ triggerLabel = 'Sign in' }: { triggerLabel?: string }) {
  const { login, register } = useAuth()
  const [open, setOpen] = useState(false)
  const [isRegistering, setIsRegistering] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError(''); setPending(true)
    try { if (isRegistering) await register({ username, password, email: email || undefined }); else await login({ username, password }); setOpen(false) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Could not sign in. Please try again.') }
    finally { setPending(false) }
  }
  return <><button onClick={() => setOpen(true)} className="rounded-md bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700">{triggerLabel}</button>{open && <div role="dialog" aria-modal="true" aria-labelledby="auth-title" className="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-4"><form onSubmit={submit} className="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl"><div className="flex items-start justify-between gap-3"><div><h2 id="auth-title" className="text-xl font-bold">{isRegistering ? 'Create your account' : 'Sign in'}</h2><p className="mt-1 text-sm text-slate-600">Save articles and ask grounded questions.</p></div><button type="button" aria-label="Close sign in dialog" onClick={()=>setOpen(false)} className="text-xl text-slate-500">×</button></div><label className="mt-5 block text-sm font-medium">Username<input required value={username} onChange={e=>setUsername(e.target.value)} className="mt-1 w-full rounded-md border p-2" autoComplete="username"/></label>{isRegistering&&<label className="mt-3 block text-sm font-medium">Email <span className="font-normal text-slate-400">(optional)</span><input type="email" value={email} onChange={e=>setEmail(e.target.value)} className="mt-1 w-full rounded-md border p-2" autoComplete="email"/></label>}<label className="mt-3 block text-sm font-medium">Password<input required type="password" value={password} onChange={e=>setPassword(e.target.value)} className="mt-1 w-full rounded-md border p-2" autoComplete={isRegistering ? 'new-password' : 'current-password'}/></label>{error&&<p role="alert" className="mt-3 text-sm text-red-700">{error}</p>}<button disabled={pending} className="mt-5 w-full rounded-md bg-brand-600 px-3 py-2 font-medium text-white disabled:opacity-50">{pending ? 'Please wait…' : isRegistering ? 'Create account' : 'Sign in'}</button><button type="button" onClick={()=>{setIsRegistering(!isRegistering);setError('')}} className="mt-3 w-full text-sm font-medium text-brand-700 hover:underline">{isRegistering ? 'Already have an account? Sign in' : 'New here? Create an account'}</button></form></div>}</>
}
