'use client'

import { useState } from 'react'
import { FlaggedLoan } from '@/types'

interface LoanTableProps {
  loans: FlaggedLoan[]
  onTogglePIKStatus?: (loanId: string, newStatus: string) => void
}

export default function LoanTable({ loans, onTogglePIKStatus }: LoanTableProps) {
  const [editingLoan, setEditingLoan] = useState<string | null>(null)

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return 'text-red-500'
      case 'high': return 'text-orange-500'
      case 'medium': return 'text-yellow-500'
      case 'low': return 'text-green-500'
      default: return 'text-gray-400'
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const handleToggleStatus = (loanId: string, currentStatus: string) => {
    const newStatus = currentStatus === 'PIK' ? 'Cash' : 'PIK'
    onTogglePIKStatus?.(loanId, newStatus)
    setEditingLoan(null)
  }

  if (loans.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-lg font-semibold mb-4 text-gray-300">Flagged Loans</h2>
        <p className="text-gray-500 text-center py-8">No flagged loans at this time</p>
      </div>
    )
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-lg font-semibold mb-4 text-gray-300">
        Flagged Loans <span className="text-sm font-normal text-gray-500">({loans.length})</span>
      </h2>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Loan ID</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Borrower</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Industry</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Type</th>
              <th className="text-right py-3 px-4 text-sm font-semibold text-gray-400">Exposure</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Risk</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Reason</th>
            </tr>
          </thead>
          <tbody>
            {loans.map((loan) => (
              <tr key={loan.loanId} className="border-b border-gray-700 hover:bg-gray-750">
                <td className="py-3 px-4 text-sm font-mono">{loan.loanId}</td>
                <td className="py-3 px-4 text-sm">{loan.borrower}</td>
                <td className="py-3 px-4 text-sm">
                  <span className="px-2 py-1 bg-gray-700 rounded text-xs">{loan.industry}</span>
                </td>
                <td className="py-3 px-4 text-sm">
                  {editingLoan === loan.loanId ? (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleToggleStatus(loan.loanId, loan.interestType)}
                        className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs"
                      >
                        Toggle
                      </button>
                      <button
                        onClick={() => setEditingLoan(null)}
                        className="px-2 py-1 bg-gray-600 hover:bg-gray-700 rounded text-xs"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setEditingLoan(loan.loanId)}
                      className="px-2 py-1 bg-purple-600 bg-opacity-20 border border-purple-500 border-opacity-50 rounded text-xs hover:bg-opacity-30"
                    >
                      {loan.interestType}
                    </button>
                  )}
                </td>
                <td className="py-3 px-4 text-sm text-right font-semibold">
                  {formatCurrency(loan.outstandingBalance)}
                </td>
                <td className="py-3 px-4 text-sm">
                  <span className={`font-semibold uppercase text-xs ${getRiskColor(loan.riskLevel)}`}>
                    {loan.riskLevel}
                  </span>
                </td>
                <td className="py-3 px-4 text-sm text-gray-400 max-w-xs truncate" title={loan.flagReason}>
                  {loan.flagReason}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
