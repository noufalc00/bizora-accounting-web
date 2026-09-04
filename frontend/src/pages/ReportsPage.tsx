import { useState } from 'react'
import { FileText, BarChart3, TrendingUp, Scale } from 'lucide-react'

const reports = [
  {
    id: 'trial-balance',
    name: 'Trial Balance',
    description: 'View debit and credit balances of all accounts',
    icon: Scale,
  },
  {
    id: 'profit-loss',
    name: 'Profit & Loss',
    description: 'View income and expense statement',
    icon: TrendingUp,
  },
  {
    id: 'balance-sheet',
    name: 'Balance Sheet',
    description: 'View assets and liabilities',
    icon: BarChart3,
  },
  {
    id: 'day-book',
    name: 'Day Book',
    description: 'View all daily transactions',
    icon: FileText,
  },
]

export default function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState<string | null>(null)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Reports</h1>

      {!selectedReport ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {reports.map((report) => (
            <div
              key={report.id}
              className="card cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => setSelectedReport(report.id)}
            >
              <div className="flex items-start space-x-4">
                <div className="p-3 bg-primary-100 rounded-lg">
                  <report.icon className="w-6 h-6 text-primary-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{report.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{report.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              {reports.find((r) => r.id === selectedReport)?.name}
            </h2>
            <button
              onClick={() => setSelectedReport(null)}
              className="btn btn-secondary"
            >
              Back
            </button>
          </div>
          <div className="text-gray-500 text-center py-8">
            Report content would be displayed here
          </div>
        </div>
      )}
    </div>
  )
}
