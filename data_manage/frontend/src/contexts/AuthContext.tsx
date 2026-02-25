import { ReactNode, createContext, useContext, useEffect, useState } from 'react'

import { authApi } from '@/services/api'
import { AuthTokens, User } from '@/types'

interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
}

interface AuthContextType {
  user: User | null
  tokens: AuthTokens | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  register: (data: RegisterData) => Promise<void>
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [tokens, setTokens] = useState<AuthTokens | null>(() => {
    const saved = localStorage.getItem('tokens')
    return saved ? (JSON.parse(saved) as AuthTokens) : null
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (tokens) {
      void fetchUser()
    } else {
      setIsLoading(false)
    }
  }, [tokens])

  const fetchUser = async () => {
    try {
      const data = await authApi.me()
      setUser(data)
    } catch {
      logout()
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    const data = await authApi.login(username, password)
    setTokens(data)
    localStorage.setItem('tokens', JSON.stringify(data))
  }

  const logout = () => {
    setUser(null)
    setTokens(null)
    localStorage.removeItem('tokens')
  }

  const register = async (data: RegisterData) => {
    await authApi.register(data)
  }

  const refresh = async () => {
    if (!tokens?.refresh_token) {
      return
    }
    try {
      const data = await authApi.refresh(tokens.refresh_token)
      setTokens(data)
      localStorage.setItem('tokens', JSON.stringify(data))
    } catch {
      logout()
    }
  }

  return (
    <AuthContext.Provider value={{ user, tokens, isLoading, login, logout, register, refresh }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
