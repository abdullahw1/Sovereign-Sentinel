'use client'

import { useState } from 'react'
import { api } from '@/lib/api'

interface CommandCenterProps {
  onAgentLog: (log: any) => void
}

export default function CommandCenter({ onAgentLog }: CommandCenterProps) {
  const [loading, setLoading] = useState<string | null>(null)
  const [results, setResults] = useState<Record<string, any>>({})

  const runOSINTScout = async () => {
    setLoading('osint')
    try {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'OSINT_Scout',
        action: 'Triggering immediate scan...',
        reasoning: 'User requested geopolitical intelligence scan',
        outcome: 'pending'
      })

      const result = await api.triggerImmediateScan()
      
      setResults(prev => ({ ...prev, osint: result }))
      
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'OSINT_Scout',
        action: 'Scan completed',
        reasoning: `Analyzed ${result.sourceArticles?.length || 0} articles`,
        outcome: `Risk Score: ${result.globalRiskScore}/100, Sentiment: ${result.sentiment}`
      })
    } catch (error: any) {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'OSINT_Scout',
        action: 'Scan failed',
        reasoning: error.message,
        outcome: 'error'
      })
    } finally {
      setLoading(null)
    }
  }

  const runForensicAuditor = async () => {
    setLoading('forensic')
    try {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Forensic_Auditor',
        action: 'Analyzing loan portfolio...',
        reasoning: 'User requested PIK toggle detection',
        outcome: 'pending'
      })

      const result = await api.runForensicAnalysis()
      
      setResults(prev => ({ ...prev, forensic: result }))
      
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Forensic_Auditor',
        action: 'Analysis completed',
        reasoning: `Portfolio: ${result.totalLoans} loans, $${(result.totalExposure || 0).toLocaleString()} exposure`,
        outcome: `🚨 ${result.criticalCount || 0} CRITICAL | ${result.pikToggles} PIK toggles | ${result.flaggedLoans?.length || 0} flagged`
      })
    } catch (error: any) {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Forensic_Auditor',
        action: 'Analysis failed',
        reasoning: error.message,
        outcome: 'error'
      })
    } finally {
      setLoading(null)
    }
  }

  const runPolicyBrain = async () => {
    setLoading('policy')
    try {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Policy_Brain',
        action: 'Evaluating risk correlation...',
        reasoning: 'User requested policy evaluation',
        outcome: 'pending'
      })

      const result = await api.runPolicyEvaluation()
      
      setResults(prev => ({ ...prev, policy: result }))
      
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Policy_Brain',
        action: 'Evaluation completed',
        reasoning: result.reasoning || 'Risk correlation analyzed',
        outcome: `Status: ${result.status}, Recommended Hedge: ${result.recommendedHedge}%`
      })
    } catch (error: any) {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Policy_Brain',
        action: 'Evaluation failed',
        reasoning: error.message,
        outcome: 'error'
      })
    } finally {
      setLoading(null)
    }
  }

  const triggerVoiceAlert = async () => {
    setLoading('voice')
    try {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Voice_Alert',
        action: 'Generating audio alert...',
        reasoning: 'User requested voice alert',
        outcome: 'pending'
      })

      const result = await api.broadcastMockAlert()
      
      setResults(prev => ({ ...prev, voice: result }))
      
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Voice_Alert',
        action: 'Alert broadcasted',
        reasoning: 'Audio alert sent to dashboard',
        outcome: 'Check left panel for audio player'
      })
    } catch (error: any) {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Voice_Alert',
        action: 'Alert failed',
        reasoning: error.message,
        outcome: 'error'
      })
    } finally {
      setLoading(null)
    }
  }

  const executeHedge = async () => {
    setLoading('treasury')
    try {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Treasury_Commander',
        action: 'Executing Bitcoin hedge...',
        reasoning: 'User requested hedge execution',
        outcome: 'pending'
      })

      const result = await api.executeMockHedge()
      
      setResults(prev => ({ ...prev, treasury: result }))
      
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Treasury_Commander',
        action: 'Hedge executed',
        reasoning: `${result.result?.agent_reasoning_steps || 6} reasoning steps completed`,
        outcome: `${result.result?.amount} BTC purchased for $${result.result?.totalCost?.toLocaleString()}`
      })
    } catch (error: any) {
      onAgentLog({
        timestamp: new Date().toISOString(),
        agent: 'Treasury_Commander',
        action: 'Hedge failed',
        reasoning: error.message,
        outcome: 'error'
      })
    } finally {
      setLoading(null)
    }
  }

  const runFullWorkflow = async () => {
    setLoading('full')
    
    onAgentLog({
      timestamp: new Date().toISOString(),
      agent: 'System',
      action: 'Starting full workflow...',
      reasoning: 'Running all agents in sequence',
      outcome: 'pending'
    })

    await runOSINTScout()
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    await runForensicAuditor()
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    await runPolicyBrain()
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    await triggerVoiceAlert()
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    await executeHedge()
    
    onAgentLog({
      timestamp: new Date().toISOString(),
      agent: 'System',
      action: 'Full workflow completed',
      reasoning: 'All agents executed successfully',
      outcome: 'Check results below'
    })
    
    setLoading(null)
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-bold mb-4 text-blue-400">⚡ Command Center</h2>
      <p className="text-gray-400 text-sm mb-6">
        Trigger agents and view results in real-time
      </p>

      {/* Agent Buttons */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
        <button
          onClick={runOSINTScout}
          disabled={loading !== null}
          className="px-4 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
        >
          {loading === 'osint' ? (
            <>
              <span className="animate-spin">⏳</span>
              Running...
            </>
          ) : (
            <>
              🌍 OSINT Scout
            </>
          )}
        </button>

        <button
          onClick={runForensicAuditor}
          disabled={loading !== null}
          className="px-4 py-3 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
        >
          {loading === 'forensic' ? (
            <>
              <span className="animate-spin">⏳</span>
              Running...
            </>
          ) : (
            <>
              🔍 Forensic Auditor
            </>
          )}
        </button>

        <button
          onClick={runPolicyBrain}
          disabled={loading !== null}
          className="px-4 py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
        >
          {loading === 'policy' ? (
            <>
              <span className="animate-spin">⏳</span>
              Running...
            </>
          ) : (
            <>
              🧠 Policy Brain
            </>
          )}
        </button>

        <button
          onClick={triggerVoiceAlert}
          disabled={loading !== null}
          className="px-4 py-3 bg-orange-600 hover:bg-orange-500 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
        >
          {loading === 'voice' ? (
            <>
              <span className="animate-spin">⏳</span>
              Running...
            </>
          ) : (
            <>
              🔊 Voice Alert
            </>
          )}
        </button>

        <button
          onClick={executeHedge}
          disabled={loading !== null}
          className="px-4 py-3 bg-yellow-600 hover:bg-yellow-500 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
        >
          {loading === 'treasury' ? (
            <>
              <span className="animate-spin">⏳</span>
              Running...
            </>
          ) : (
            <>
              💰 Treasury Commander
            </>
          )}
        </button>

        <button
          onClick={runFullWorkflow}
          disabled={loading !== null}
          className="px-4 py-3 bg-red-600 hover:bg-red-500 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
        >
          {loading === 'full' ? (
            <>
              <span className="animate-spin">⏳</span>
              Running...
            </>
          ) : (
            <>
              🚀 Run All
            </>
          )}
        </button>
      </div>

      {/* Results Display */}
      {Object.keys(results).length > 0 && (
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-3 text-gray-300">Latest Results</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {results.osint && (
              <div className="bg-blue-900 bg-opacity-30 rounded p-3 border border-blue-700">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">🌍</span>
                  <span className="font-semibold text-blue-300">OSINT Scout</span>
                </div>
                <div className="text-sm text-gray-300">
                  <p>Risk Score: <span className="font-bold text-blue-400">{results.osint.globalRiskScore}/100</span></p>
                  <p>Sentiment: <span className="font-bold">{results.osint.sentiment}</span></p>
                  <p>Sectors: {results.osint.affectedSectors?.join(', ') || 'N/A'}</p>
                </div>
              </div>
            )}

            {results.forensic && (
              <div className="bg-purple-900 bg-opacity-30 rounded p-3 border border-purple-700">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">🔍</span>
                  <span className="font-semibold text-purple-300">Forensic Auditor</span>
                </div>
                <div className="text-sm text-gray-300 space-y-1">
                  <p>Total Loans: <span className="font-bold">{results.forensic.totalLoans || 0}</span></p>
                  <p>Total Exposure: <span className="font-bold text-yellow-400">${(results.forensic.totalExposure || 0).toLocaleString()}</span></p>
                  <p>Flagged: <span className="font-bold text-red-400">{results.forensic.flaggedLoans?.length || 0}</span> ({results.forensic.criticalCount || 0} critical)</p>
                  <p>PIK Toggles: <span className="font-bold text-orange-400">{results.forensic.pikToggles || 0}</span></p>
                  
                  {results.forensic.flaggedLoans && results.forensic.flaggedLoans.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-purple-600">
                      <p className="font-semibold mb-1">Flagged Loans:</p>
                      {results.forensic.flaggedLoans.map((loan: any) => (
                        <div key={loan.loanId} className="text-xs bg-purple-950 p-2 rounded mb-1">
                          <p className="font-bold">{loan.borrower} ({loan.loanId})</p>
                          <p>Balance: ${loan.outstandingBalance?.toLocaleString()} | Risk: {loan.riskLevel}</p>
                          {loan.pikToggleDetected && (
                            <p className="text-orange-300">🚨 PIK Toggle: {loan.previousType} → PIK</p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {results.policy && (
              <div className="bg-green-900 bg-opacity-30 rounded p-3 border border-green-700">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">🧠</span>
                  <span className="font-semibold text-green-300">Policy Brain</span>
                </div>
                <div className="text-sm text-gray-300">
                  <p>Status: <span className="font-bold text-red-400">{results.policy.status}</span></p>
                  <p>Recommended Hedge: <span className="font-bold">{results.policy.recommendedHedge}%</span></p>
                </div>
              </div>
            )}

            {results.voice && (
              <div className="bg-orange-900 bg-opacity-30 rounded p-3 border border-orange-700">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">🔊</span>
                  <span className="font-semibold text-orange-300">Voice Alert</span>
                </div>
                <div className="text-sm text-gray-300">
                  <p>Status: <span className="font-bold text-green-400">Broadcasted</span></p>
                  <p>Check left panel for audio player</p>
                </div>
              </div>
            )}

            {results.treasury && (
              <div className="bg-yellow-900 bg-opacity-30 rounded p-3 border border-yellow-700">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">💰</span>
                  <span className="font-semibold text-yellow-300">Treasury Commander</span>
                </div>
                <div className="text-sm text-gray-300">
                  <p>Status: <span className="font-bold text-green-400">{results.treasury.result?.status}</span></p>
                  <p>BTC Amount: <span className="font-bold">{results.treasury.result?.amount?.toFixed(8)}</span></p>
                  <p>Total Cost: <span className="font-bold">${results.treasury.result?.totalCost?.toLocaleString()}</span></p>
                  <p>Trade ID: <span className="text-xs">{results.treasury.result?.tradeId}</span></p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
