// API client for backend communication

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new ApiError(response.status, `API error: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new Error(`Network error: ${error}`)
  }
}

export const api = {
  // Dashboard state
  getDashboardState: () => fetchApi<any>('/api/dashboard/state'),
  
  // Risk assessment
  getCurrentRiskScore: () => fetchApi<any>('/api/risk/current'),
  
  // Loans
  getFlaggedLoans: () => fetchApi<any[]>('/api/loans/flagged'),
  togglePIKStatus: (loanId: string, newStatus: string) =>
    fetchApi<any>(`/api/loans/${loanId}/pik-status`, {
      method: 'POST',
      body: JSON.stringify({ status: newStatus }),
    }),
  
  // Alerts
  getActiveAlerts: () => fetchApi<any[]>('/api/alerts/active'),
  
  // Policy
  getPolicyConfig: () => fetchApi<any>('/api/policy/config'),
  applyPolicyOverride: (override: any) =>
    fetchApi<any>('/api/policy/override', {
      method: 'POST',
      body: JSON.stringify(override),
    }),
  
  // Agent logs
  getAgentLogs: (limit?: number) =>
    fetchApi<any[]>(`/api/logs/agents${limit ? `?limit=${limit}` : ''}`),
  
  // System status
  getSystemStatus: () => fetchApi<any[]>('/api/system/status'),
  
  // Voice alerts
  generateAudioAlert: (alertId: string) =>
    fetchApi<any>(`/api/alerts/${alertId}/generate-audio`, {
      method: 'POST',
    }),
  authorizeAlert: (alertId: string, action: 'approve' | 'dismiss') =>
    fetchApi<any>(`/api/alerts/${alertId}/authorize?action=${action}`, {
      method: 'POST',
    }),
  broadcastMockAlert: () =>
    fetchApi<any>('/api/test/broadcast-mock-alert', {
      method: 'POST',
    }),
  
  // Agent execution
  triggerImmediateScan: () =>
    fetchApi<any>('/api/scan/immediate', {
      method: 'POST',
    }),
  runForensicAnalysis: () =>
    fetchApi<any>('/api/forensic/analyze', {
      method: 'POST',
    }),
  runPolicyEvaluation: () =>
    fetchApi<any>('/api/policy/evaluate', {
      method: 'POST',
    }),
  executeMockHedge: () =>
    fetchApi<any>('/api/test/execute-mock-hedge', {
      method: 'POST',
    }),
  
  // Company analysis
  analyzeCompany: (data: any) =>
    fetchApi<any>('/api/company/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}
