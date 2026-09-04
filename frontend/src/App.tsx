import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './lib/auth'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import SalesPage from './pages/SalesPage'
import PurchasePage from './pages/PurchasePage'
import ProductsPage from './pages/ProductsPage'
import PartiesPage from './pages/PartiesPage'
import AccountsPage from './pages/AccountsPage'
import ReportsPage from './pages/ReportsPage'
import Layout from './components/Layout'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) {
    return <Navigate to="/login" />
  }
  return <>{children}</>
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/sales" element={<SalesPage />} />
                    <Route path="/purchases" element={<PurchasePage />} />
                    <Route path="/products" element={<ProductsPage />} />
                    <Route path="/parties" element={<PartiesPage />} />
                    <Route path="/accounts" element={<AccountsPage />} />
                    <Route path="/reports" element={<ReportsPage />} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
