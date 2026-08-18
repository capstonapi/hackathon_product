import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'

import { deleteAccount as apiDeleteAccount, login as apiLogin, logout as apiLogout, register as apiRegister } from '../api/auth'
import { clearToken, getToken, setToken } from '../services/authTokenStorage'
import type { LoginPayload, RegisterPayload } from '../types/auth'

interface AuthContextValue {
  isAuthenticated: boolean
  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => Promise<void>
  deleteAccount: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() => getToken())

  const login = useCallback(async (payload: LoginPayload) => {
    const response = await apiLogin(payload)
    setToken(response.token)
    setTokenState(response.token)
  }, [])

  const register = useCallback(async (payload: RegisterPayload) => {
    const response = await apiRegister(payload)
    setToken(response.token)
    setTokenState(response.token)
  }, [])

  const logout = useCallback(async () => {
    try {
      await apiLogout()
    } finally {
      clearToken()
      setTokenState(null)
    }
  }, [])

  const deleteAccount = useCallback(async () => {
    await apiDeleteAccount()
    clearToken()
    setTokenState(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ isAuthenticated: token !== null, login, register, logout, deleteAccount }),
    [token, login, register, logout, deleteAccount],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
