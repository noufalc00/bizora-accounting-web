import { useState, useEffect } from 'react'
import api from '../lib/api'
import { Plus, Edit, Trash2, Search } from 'lucide-react'

interface Product {
  id: number
  name: string
  code: string | null
  category: string | null
  unit: string | null
  purchase_price: number
  sale_price: number
  gst_rate: number
  stock_quantity: number
  is_active: boolean
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await api.get('/api/products')
      setProducts(response.data)
    } catch (error) {
      console.error('Error fetching products:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredProducts = products.filter(
    (product) =>
      product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (product.code && product.code.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  if (loading) {
    return <div className="text-gray-500">Loading products...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Products</h1>
        <button className="btn btn-primary flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Product
        </button>
      </div>

      <div className="card">
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search products..."
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
                <th>Name</th>
                <th>Code</th>
                <th>Category</th>
                <th>Unit</th>
                <th>Purchase Price</th>
                <th>Sale Price</th>
                <th>GST %</th>
                <th>Stock</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredProducts.map((product) => (
                <tr key={product.id}>
                  <td>{product.name}</td>
                  <td>{product.code || '-'}</td>
                  <td>{product.category || '-'}</td>
                  <td>{product.unit || '-'}</td>
                  <td>₹{product.purchase_price.toFixed(2)}</td>
                  <td>₹{product.sale_price.toFixed(2)}</td>
                  <td>{product.gst_rate}%</td>
                  <td>{product.stock_quantity.toFixed(2)}</td>
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
              {filteredProducts.length === 0 && (
                <tr>
                  <td colSpan={9} className="text-center text-gray-500 py-8">
                    No products found
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
