'use client'

import { useEffect, useState } from 'react'
import RiskGauge from '@/components/RiskGauge'
import LoanTable from '@/components/LoanTable'
import AlertPanel from '@/components/AlertPanel'
import AgentChatLog from '@/components/AgentChatLog'
import PolicyOverridePanel from '@/components/PolicyOverridePanel'
import AudioAlertPlayer from '@/components/AudioAlertPlayer'
import CommandCenter from '@/components/CommandCenter'
import CompanyAnalysisPanel from '@/components/CompanyAnalysisPanel'
import { DashboardState, FlaggedLoan, Alert, AgentLog, PolicyConfig, PolicyOverride, AudioAlertResult } from '@/types'
import { api } from '@/lib/api'
import { getWebSocketClient } from '@/lib/websocket'

export default function Home() {
  const [dashboardState, setDashboardState] = useState<DashboardState>({
    currentRiskScore: 0,
    flaggedLoans: [],
    activeAlerts: [],
    systemStatus: [],
    recentAgentActivity: [],
  })
  const [policyConfig, setPolicyConfig] = useState<PolicyConfig>({
    riskThreshold: 70,
    pikExposureLimit: 5000000,
    autoExecuteEnabled: false,
    hedgePercentages: { energy: 15, currency: 20, sovereign: 25 },
    customRules: [],
  })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [audioAlert, setAudioAlert] = useState<AudioAlertResult | null>(null)

  // Load initial data
  useEffect(() => {
    loadDashboardData()
    loadPolicyConfig()
  }, [])

  // Set up WebSocket subscriptions
  useEffect(() => {
    const ws = getWebSocketClient()
    ws.connect()

    const unsubscribeRisk = ws.subscribe('risk_update', (message) => {
      setDashboardState(prev => ({
        ...prev,
        currentRiskScore: message.data.globalRiskScore || prev.currentRiskScore,
      }))
    })

    const unsubscribeAgent = ws.subscribe('agent_log', (message) => {
      setDashboardState(prev => ({
        ...prev,
        recentAgentActivity: [message.data, ...prev.recentAgentActivity].slice(0, 50),
      }))
    })

    const unsubscribeAlert = ws.subscribe('alert', (message) => {
      setDashboardState(prev => ({
        ...prev,
        activeAlerts: [message.data, ...prev.activeAlerts],
      }))
    })

    const unsubscribeLoan = ws.subscribe('loan_update', (message) => {
      loadDashboardData() // Reload full data on loan updates
    })

    const unsubscribePolicy = ws.subscribe('policy_update', (message) => {
      loadPolicyConfig()
    })

    const unsubscribeAudioAlert = ws.subscribe('audio_alert', (message) => {
      setAudioAlert(message.data)
    })

    return () => {
      unsubscribeRisk()
      unsubscribeAgent()
      unsubscribeAlert()
      unsubscribeLoan()
      unsubscribePolicy()
      unsubscribeAudioAlert()
    }
  }, [])

  const loadDashboardData = async () => {
    try {
      const data = await api.getDashboardState()
      setDashboardState(data)
      setError(null)
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      setError('Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }

  const loadPolicyConfig = async () => {
    try {
      const config = await api.getPolicyConfig()
      setPolicyConfig(config)
    } catch (err) {
      console.error('Failed to load policy config:', err)
    }
  }

  const handleTogglePIKStatus = async (loanId: string, newStatus: string) => {
    try {
      await api.togglePIKStatus(loanId, newStatus)
      await loadDashboardData()
    } catch (err) {
      console.error('Failed to toggle PIK status:', err)
      alert('Failed to update loan status')
    }
  }

  const handleApplyPolicyOverride = async (override: Partial<PolicyOverride>) => {
    try {
      const fullOverride = {
        ...override,
        overrideId: `override_${Date.now()}`,
        timestamp: new Date().toISOString(),
        appliedBy: 'dashboard_user',
      }
      await api.applyPolicyOverride(fullOverride)
      await loadPolicyConfig()
    } catch (err) {
      console.error('Failed to apply policy override:', err)
      alert('Failed to apply policy override')
    }
  }

  const handleApproveAlert = async (alertId: string) => {
    try {
      await api.authorizeAlert(alertId, 'approve')
      setAudioAlert(null)
    } catch (err) {
      console.error('Failed to approve alert:', err)
      alert('Failed to approve alert')
    }
  }

  const handleDismissAlert = async (alertId: string) => {
    try {
      await api.authorizeAlert(alertId, 'dismiss')
      setAudioAlert(null)
    } catch (err) {
      console.error('Failed to dismiss alert:', err)
      alert('Failed to dismiss alert')
    }
  }

  const handleAgentLog = (log: AgentLog) => {
    setDashboardState(prev => ({
      ...prev,
      recentAgentActivity: [log, ...prev.recentAgentActivity].slice(0, 50),
    }))
  }

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading War Room...</p>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button
            onClick={loadDashboardData}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
          >
            Retry
          </button>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen p-6">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Sovereign Sentinel</h1>
        <p className="text-gray-400">Financial War Room - Shadow Default Detection System</p>
      </header>

      {/* Command Center - Full Width */}
      <div className="mb-6">
        <CommandCenter onAgentLog={handleAgentLog} />
      </div>

      {/* Company Analysis Panel - Full Width */}
      <div className="mb-6">
        <CompanyAnalysisPanel onAgentLog={handleAgentLog} />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Risk & Alerts */}
        <div className="space-y-6">
          <RiskGauge score={dashboardState.currentRiskScore} />
          
          {/* Audio Alert Player */}
          {audioAlert && audioAlert.status === 'generated' && (
            <AudioAlertPlayer
              audioUrl={audioAlert.audioUrl}
              alertId={audioAlert.alertId}
              script={audioAlert.script}
              onApprove={handleApproveAlert}
              onDismiss={handleDismissAlert}
            />
          )}
          
          <AlertPanel alerts={dashboardState.activeAlerts} />
        </div>

        {/* Middle Column - Loans & Policy */}
        <div className="lg:col-span-2 space-y-6">
          <LoanTable
            loans={dashboardState.flaggedLoans}
            onTogglePIKStatus={handleTogglePIKStatus}
          />
          <PolicyOverridePanel
            config={policyConfig}
            onApplyOverride={handleApplyPolicyOverride}
          />
        </div>
      </div>

      {/* Agent Activity Log - Full Width */}
      <div className="mt-6">
        <AgentChatLog logs={dashboardState.recentAgentActivity} />
      </div>
    </main>
  )
}
