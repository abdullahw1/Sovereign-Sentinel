// Core data types for Sovereign Sentinel

export interface NewsArticle {
  title: string
  url: string
  publishedDate: string
  snippet: string
  relevanceScore: number
}

export interface RiskAssessment {
  timestamp: string
  globalRiskScore: number
  affectedSectors: string[]
  sourceArticles: NewsArticle[]
  sentiment: 'positive' | 'neutral' | 'negative' | 'critical'
}

export interface LoanRecord {
  loanId: string
  borrower: string
  industry: string
  interestType: 'PIK' | 'Cash' | 'Hybrid'
  principalAmount: number
  outstandingBalance: number
  maturityDate: string
  covenants: string[]
}

export interface FlaggedLoan extends LoanRecord {
  flagReason: string
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  correlatedEvent: string
  flaggedAt: string
  confidence?: number
  reasoning?: string
}

export interface Alert {
  alertId: string
  timestamp: string
  severity: 'info' | 'warning' | 'critical'
  title: string
  message: string
  actionRequired: boolean
  recommendedHedge: number
}

export interface AgentLog {
  timestamp: string
  agent: 'OSINT_Scout' | 'Forensic_Auditor' | 'Policy_Brain' | 'Treasury_Commander'
  action: string
  reasoning: string
  outcome: string
}

export interface ServiceStatus {
  service: string
  status: 'operational' | 'degraded' | 'down'
  lastCheck: string
  message?: string
}

export interface DashboardState {
  currentRiskScore: number
  flaggedLoans: FlaggedLoan[]
  activeAlerts: Alert[]
  systemStatus: ServiceStatus[]
  recentAgentActivity: AgentLog[]
}

export interface PolicyConfig {
  riskThreshold: number
  pikExposureLimit: number
  autoExecuteEnabled: boolean
  hedgePercentages: Record<string, number>
  customRules: any[]
}

export interface PolicyOverride {
  overrideId: string
  timestamp: string
  field: keyof PolicyConfig
  oldValue: any
  newValue: any
  appliedBy: string
  reason: string
}

export interface AudioAlertResult {
  alertId: string
  audioUrl: string
  audioPath?: string
  status: 'generated' | 'failed'
  script: string
  duration: number
  error?: string
}

export interface AuthorizationResult {
  authorized: boolean
  timestamp: string
  alertId: string
  action: string
}
