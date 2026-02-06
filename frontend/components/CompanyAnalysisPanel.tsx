'use client'

import { useState } from 'react'
import { api } from '@/lib/api'

interface CompanyAnalysisPanelProps {
  onAgentLog: (log: any) => void
}

export default function CompanyAnalysisPanel({ onAgentLog }: CompanyAnalysisPanelProps) {
  const [companyName, setCompanyName] = useState('')
  const [industry, setIndustry] = useState('')
  const [financialData, setFinancialData] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const analyzeCompany = async () => {
    if (!companyName || !industry || !financialData) {
      alert('Please fill in all fields')
      return
    }

    setLoading(true)
    try {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Company_Analyzer',
        action: `Analyzing ${companyName}...`,
        reasoning: `Researching ${industry} industry trends and analyzing financial data`,
        outcome: 'pending'
      })

      // Parse financial data (expecting JSON)
      const parsedData = JSON.parse(financialData)

      const response = await api.analyzeCompany({
        company_name: companyName,
        industry: industry,
        financial_data: parsedData,
        analysis_focus: ['liquidity', 'profitability', 'solvency', 'industry_risk']
      })

      setResult(response)

      const riskLevel = response.overall_risk_score < 30 ? 'LOW' : 
                       response.overall_risk_score < 60 ? 'MEDIUM' : 
                       response.overall_risk_score < 80 ? 'HIGH' : 'CRITICAL'

      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Company_Analyzer',
        action: 'Analysis completed',
        reasoning: `Risk Score: ${response.overall_risk_score}/100`,
        outcome: `${riskLevel} RISK | ${response.recommendations?.length || 0} recommendations`
      })
    } catch (error: any) {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Company_Analyzer',
        action: 'Analysis failed',
        reasoning: error.message,
        outcome: 'error'
      })
      alert(`Analysis failed: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const loadSampleData = () => {
    setCompanyName('TechFlow Solutions, Inc.')
    setIndustry('SaaS Software')
    setFinancialData(JSON.stringify({
      income_statement: {
        total_revenue: 5000000,
        net_income: 408000,
        operating_income: 550000,
        ebitda: 675000,
        interest_expense: 45000,
        depreciation: 125000,
        principal_payments: 80000
      },
      balance_sheet: {
        total_current_assets: 1490000,
        total_current_liabilities: 863000,
        total_assets: 2020000,
        total_liabilities: 1298000,
        total_equity: 722000,
        retained_earnings: 712000,
        inventory: 0
      },
      cash_flow: {
        net_cash_from_operating: 578000
      }
    }, null, 2))
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-bold mb-4 text-green-400">🏢 Custom Company Analysis</h2>
      <p className="text-gray-400 text-sm mb-6">
        Analyze any company with financial statements and industry research
      </p>

      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Company Name
          </label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="e.g., TechFlow Solutions, Inc."
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-green-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Industry
          </label>
          <input
            type="text"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            placeholder="e.g., SaaS Software, Manufacturing, Healthcare"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-green-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Financial Data (JSON)
          </label>
          <textarea
            value={financialData}
            onChange={(e) => setFinancialData(e.target.value)}
            placeholder='{"income_statement": {...}, "balance_sheet": {...}, "cash_flow": {...}}'
            rows={8}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white font-mono text-sm focus:outline-none focus:border-green-500"
          />
          <button
            onClick={loadSampleData}
            className="mt-2 text-sm text-blue-400 hover:text-blue-300"
          >
            Load Sample Data
          </button>
        </div>

        <button
          onClick={analyzeCompany}
          disabled={loading}
          className="w-full px-6 py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors"
        >
          {loading ? '⏳ Analyzing...' : '🔍 Analyze Company'}
        </button>
      </div>

      {result && (
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-3 text-gray-300">Analysis Results</h3>
          
          <div className="space-y-4">
            {/* Risk Score */}
            <div className="bg-gray-800 rounded p-3">
              <p className="text-sm text-gray-400">Overall Risk Score</p>
              <p className={`text-3xl font-bold ${
                result.overall_risk_score < 30 ? 'text-green-400' :
                result.overall_risk_score < 60 ? 'text-yellow-400' :
                result.overall_risk_score < 80 ? 'text-orange-400' : 'text-red-400'
              }`}>
                {result.overall_risk_score}/100
              </p>
            </div>

            {/* Financial Ratios */}
            {result.financial_ratios && (
              <div className="bg-gray-800 rounded p-3">
                <p className="font-semibold text-gray-300 mb-3">📊 6 Priority Credit Metrics</p>
                
                {/* Overall Credit Score */}
                <div className="mb-3 p-2 bg-gray-900 rounded">
                  <p className="text-xs text-gray-400">Overall Credit Score</p>
                  <p className={`text-2xl font-bold ${
                    result.financial_ratios.overall_credit_score >= 80 ? 'text-green-400' :
                    result.financial_ratios.overall_credit_score >= 60 ? 'text-yellow-400' :
                    result.financial_ratios.overall_credit_score >= 40 ? 'text-orange-400' : 'text-red-400'
                  }`}>
                    {result.financial_ratios.overall_credit_score}/100
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2 bg-gray-900 rounded">
                    <p className="text-gray-400">1. DSCR</p>
                    <p className="font-bold">{result.financial_ratios.dscr}x</p>
                    <p className={`text-xs ${
                      result.financial_ratios.dscr_score >= 80 ? 'text-green-400' :
                      result.financial_ratios.dscr_score >= 50 ? 'text-yellow-400' : 'text-red-400'
                    }`}>Score: {result.financial_ratios.dscr_score}</p>
                  </div>
                  
                  <div className="p-2 bg-gray-900 rounded">
                    <p className="text-gray-400">2. Debt-to-Equity</p>
                    <p className="font-bold">{result.financial_ratios.debt_to_equity}x</p>
                    <p className={`text-xs ${
                      result.financial_ratios.de_score >= 80 ? 'text-green-400' :
                      result.financial_ratios.de_score >= 50 ? 'text-yellow-400' : 'text-red-400'
                    }`}>Score: {result.financial_ratios.de_score}</p>
                  </div>
                  
                  <div className="p-2 bg-gray-900 rounded">
                    <p className="text-gray-400">3. Current Ratio</p>
                    <p className="font-bold">{result.financial_ratios.current_ratio}</p>
                    <p className={`text-xs ${
                      result.financial_ratios.cr_score >= 80 ? 'text-green-400' :
                      result.financial_ratios.cr_score >= 50 ? 'text-yellow-400' : 'text-red-400'
                    }`}>Score: {result.financial_ratios.cr_score}</p>
                  </div>
                  
                  <div className="p-2 bg-gray-900 rounded">
                    <p className="text-gray-400">4. Interest Coverage</p>
                    <p className="font-bold">{result.financial_ratios.interest_coverage_ratio}x</p>
                    <p className={`text-xs ${
                      result.financial_ratios.icr_score >= 80 ? 'text-green-400' :
                      result.financial_ratios.icr_score >= 50 ? 'text-yellow-400' : 'text-red-400'
                    }`}>Score: {result.financial_ratios.icr_score}</p>
                  </div>
                  
                  <div className="p-2 bg-gray-900 rounded">
                    <p className="text-gray-400">5. Net Profit Margin</p>
                    <p className="font-bold">{result.financial_ratios.net_profit_margin}%</p>
                    <p className={`text-xs ${
                      result.financial_ratios.npm_score >= 80 ? 'text-green-400' :
                      result.financial_ratios.npm_score >= 50 ? 'text-yellow-400' : 'text-red-400'
                    }`}>Score: {result.financial_ratios.npm_score}</p>
                  </div>
                  
                  <div className="p-2 bg-gray-900 rounded">
                    <p className="text-gray-400">6. Altman Z-Score</p>
                    <p className="font-bold">{result.financial_ratios.altman_z_score}</p>
                    <p className={`text-xs ${
                      result.financial_ratios.z_score_interpretation === 'Safe Zone' ? 'text-green-400' :
                      result.financial_ratios.z_score_interpretation === 'Grey Zone' ? 'text-yellow-400' : 'text-red-400'
                    }`}>{result.financial_ratios.z_score_interpretation}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Risk Assessment */}
            {result.risk_assessment && (
              <div className="bg-gray-800 rounded p-3">
                <p className="font-semibold text-gray-300 mb-2">Risk Breakdown</p>
                <div className="space-y-1 text-sm">
                  <p>Liquidity: <span className="font-bold">{result.risk_assessment.liquidity_risk?.toUpperCase()}</span></p>
                  <p>Profitability: <span className="font-bold">{result.risk_assessment.profitability_risk?.toUpperCase()}</span></p>
                  <p>Solvency: <span className="font-bold">{result.risk_assessment.solvency_risk?.toUpperCase()}</span></p>
                  <p>Industry: <span className="font-bold">{result.risk_assessment.industry_risk?.toUpperCase()}</span></p>
                </div>
              </div>
            )}

            {/* Red Flags */}
            {result.risk_assessment?.red_flags && result.risk_assessment.red_flags.length > 0 && (
              <div className="bg-red-900 bg-opacity-30 rounded p-3 border border-red-700">
                <p className="font-semibold text-red-300 mb-2">🚨 Red Flags</p>
                <ul className="text-sm space-y-1">
                  {result.risk_assessment.red_flags.map((flag: string, i: number) => (
                    <li key={i} className="text-gray-300">• {flag}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Strengths */}
            {result.risk_assessment?.strengths && result.risk_assessment.strengths.length > 0 && (
              <div className="bg-green-900 bg-opacity-30 rounded p-3 border border-green-700">
                <p className="font-semibold text-green-300 mb-2">✅ Strengths</p>
                <ul className="text-sm space-y-1">
                  {result.risk_assessment.strengths.map((strength: string, i: number) => (
                    <li key={i} className="text-gray-300">• {strength}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendations */}
            {result.recommendations && result.recommendations.length > 0 && (
              <div className="bg-blue-900 bg-opacity-30 rounded p-3 border border-blue-700">
                <p className="font-semibold text-blue-300 mb-2">💡 Recommendations</p>
                <ul className="text-sm space-y-1">
                  {result.recommendations.map((rec: string, i: number) => (
                    <li key={i} className="text-gray-300">{i + 1}. {rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
