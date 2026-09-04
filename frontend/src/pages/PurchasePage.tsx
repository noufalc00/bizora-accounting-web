import React, { useState, useEffect } from 'react'
import api from '../lib/api'
import { Plus, Edit, Trash2, Search } from 'lucide-react'

interface PurchaseItem {
  id: number
  voucher_no: string
  voucher_date: string
  party_name: string
  net_amount: number
  payment_mode: string
}

export default function PurchasePage() {
  const [purchases, setPurchases] = useState<PurchaseItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchPurchases()
  }, [])

  const fetchPurchases = async () => {
    try {
      const response = await api.get('/api/purchases')
      setPurchases(response.data)
    } catch (error) {
      console.error('Error fetching purchases:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredPurchases = purchases.filter(
    (purchase) =>
      purchase.party_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      purchase.voucher_no.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return <div className="text-gray-500">Loading purchases...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Purchases</h1>
        <button className="btn btn-primary flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          New Purchase
        </button>
      </div>

      <div className="card">
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search purchases..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Voucher No</th>
                <th>Date</th>
                <th>Party</th>
                <th>Amount</th>
                <th>Payment Mode</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPurchases.map((purchase) => (
                <tr key={purchase.id}>
                  <td>{purchase.voucher_no}</td>
                  <td>{purchase.voucher_date}</td>
                  <td>{purchase.party_name}</td>
                  <td>₹{purchase.net_amount.toFixed(2)}</td>
                  <td className="capitalize">{purchase.payment_mode}</td>
                  <td>
                    <div className="flex space-x-2">
                      <button className="text-blue-600 hover:text-blue-800">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-800">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredPurchases.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center text-gray-500 py-8">
                    No purchases found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
