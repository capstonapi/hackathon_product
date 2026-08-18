import { NavLink, Outlet } from 'react-router-dom'
import { AuthDialog } from '../components/AuthDialog'
import { useAuth } from '../context/AuthContext'

const navItems = [
  ['/', 'Home'], ['/latest', 'Latest News'], ['/library', 'News Library'], ['/search', 'Search'],
  ['/saved', 'Saved Articles'], ['/history', 'Reading History'],
]

export function AppLayout() {
  const { isAuthenticated, logout, deleteAccount } = useAuth()
  const eraseData = async () => {
    if (window.confirm('Delete your account, saved articles, and chat history permanently?')) await deleteAccount()
  }
  return <div className="min-h-screen bg-slate-50">
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center gap-6 px-4 py-3 sm:px-6">
        <NavLink to="/" className="shrink-0 text-lg font-bold tracking-tight text-slate-900">Briefly<span className="text-brand-600">.</span></NavLink>
        <nav className="flex min-w-0 gap-1 overflow-x-auto" aria-label="Main navigation">
          {navItems.map(([to, label]) => <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium ${isActive ? 'bg-brand-50 text-brand-700' : 'text-slate-600 hover:bg-slate-100'}`}>{label}</NavLink>)}
        </nav>
        <div className="ml-auto flex shrink-0 gap-1">{isAuthenticated ? <><button onClick={() => void eraseData()} className="rounded-md px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50">Delete my data</button><button onClick={() => void logout()} className="rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100">Sign out</button></> : <AuthDialog />}</div>
      </div>
    </header>
    <main className="mx-auto max-w-7xl px-4 py-7 sm:px-6"><Outlet /></main>
  </div>
}
