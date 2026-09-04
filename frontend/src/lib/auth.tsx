import React, { createContext, useContext, useState, useEffect } from 'react'
import api from './api'

interface User {
  id: number
  username: string
  role: string
  company_id: number
}

interface AuthContextType {
  user: User | null
  login: (username: string, password: string, company_id?: number) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const userData = localStorage.getItem('user_data')
    if (token && userData) {
      setUser(JSON.parse(userData))
      setIsAuthenticated(true)
    }
  }, [])

  const login = async (username: string, password: string, company_id?: number) => {
    try {
      const response = await api.post('/api/auth/login', {
        username,
        password,
        company_id,
      })
      
      const { access_token, user_id, company_id: cid, username: uname, role } = response.data
      
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('user_data', JSON.stringify({
        id: user_id,
        username: uname,
        role,
        company_id: cid,
      }))
      
      setUser({ id: user_id, username: uname, role, company_id: cid })
      setIsAuthenticated(true)
    } catch (error) {
      throw new Error('Login failed')
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_data')
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
