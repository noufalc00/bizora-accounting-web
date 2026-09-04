import React, { useState, useEffect } from 'react'
import api from '../lib/api'
import { LayoutDashboard, ShoppingCart, Package, TrendingUp, Users, DollarSign } from 'lucide-react'

interface DashboardStats {
  total_sales: number
  total_purchases: number
  total_products: number
  total_parties: number
  net_profit: number
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    total_sales: 0,
    total_purchases: 0,
    total_products: 0,
    total_parties: 0,
    net_profit: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      // Fetch basic stats (simplified - in real app would use dedicated endpoint)
      const [productsRes, partiesRes] = await Promise.all([
        api.get('/api/products'),
        api.get('/api/parties'),
      ])
      
      setStats({
        total_sales: 0,
        total_purchases: 0,
        total_products: productsRes.data.length,
        total_parties: partiesRes.data.length,
        net_profit: 0,
      })
    } catch (error) {
      console.error('Error fetching dashboard stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      title: 'Total Sales',
      value: `₹${stats.total_sales.toLocaleString()}`,
      icon: ShoppingCart,
      color: 'bg-blue-500',
    },
    {
      title: 'Total Purchases',
      value: `₹${stats.total_purchases.toLocaleString()}`,
      icon: Package,
      color: 'bg-green-500',
    },
    {
      title: 'Products',
      value: stats.total_products,
      icon: Package,
      color: 'bg-purple-500',
    },
    {
      title: 'Parties',
      value: stats.total_parties,
      icon: Users,
      color: 'bg-orange-500',
    },
    {
      title: 'Net Profit',
      value: `₹${stats.net_profit.toLocaleString()}`,
      icon: TrendingUp,
      color: 'bg-teal-500',
    },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <LayoutDashboard className="w-6 h-6 text-gray-500" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {statCards.map((stat) => (
          <div key={stat.title} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg ${stat.color}`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="text-gray-500 text-center py-8">
            No recent activity
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <button className="btn btn-primary">New Sale</button>
            <button className="btn btn-secondary">New Purchase</button>
            <button className="btn btn-secondary">Add Product</button>
            <button className="btn btn-secondary">Add Party</button>
          </div>
        </div>
      </div>
    </div>
  )
}
