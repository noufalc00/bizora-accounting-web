import { useState, useEffect } from 'react'
import api from '../lib/api'
import { Plus, Edit, Trash2, Search } from 'lucide-react'

interface SalesItem {
  id: number
  voucher_no: string
  voucher_date: string
  party_name: string
  net_amount: number
  payment_mode: string
}

export default function SalesPage() {
  const [sales, setSales] = useState<SalesItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchSales()
  }, [])

  const fetchSales = async () => {
    try {
      const response = await api.get('/api/sales')
      setSales(response.data)
    } catch (error) {
      console.error('Error fetching sales:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredSales = sales.filter(
    (sale) =>
      sale.party_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      sale.voucher_no.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return <div className="text-gray-500">Loading sales...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Sales</h1>
        <button className="btn btn-primary flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          New Sale
        </button>
      </div>

      <div className="card">
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search sales..."
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
              {filteredSales.map((sale) => (
                <tr key={sale.id}>
                  <td>{sale.voucher_no}</td>
                  <td>{sale.voucher_date}</td>
                  <td>{sale.party_name}</td>
                  <td>₹{sale.net_amount.toFixed(2)}</td>
                  <td className="capitalize">{sale.payment_mode}</td>
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
              {filteredSales.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center text-gray-500 py-8">
                    No sales found
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
