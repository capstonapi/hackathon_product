import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { AppLayout } from './layouts/AppLayout'
import { ArticleChatPage } from './pages/ArticleChatPage'
import { ArticleDetailPage } from './pages/ArticleDetailPage'
import { HistoryPage } from './pages/HistoryPage'
import { HomePage } from './pages/HomePage'
import { LatestPage } from './pages/LatestPage'
import { LibraryPage } from './pages/LibraryPage'
import { SavedPage } from './pages/SavedPage'
import { SearchPage } from './pages/SearchPage'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<HomePage />} />
            <Route path="latest" element={<LatestPage />} />
            <Route path="library" element={<LibraryPage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="saved" element={<SavedPage />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="article/:id" element={<ArticleDetailPage />} />
            <Route path="article/:id/chat" element={<ArticleChatPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
