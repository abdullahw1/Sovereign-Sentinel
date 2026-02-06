"use client";

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types matching backend models
export interface RiskAssessment {
  timestamp: string;
  global_risk_score: number;
  affected_sectors: string[];
  source_articles: NewsArticle[];
  sentiment: "positive" | "neutral" | "negative" | "critical";
}

export interface NewsArticle {
  title: string;
  url: string;
  published_date: string;
  snippet: string;
  relevance_score: number;
}

export interface LoanRecord {
  loanId: string;
  borrower: string;
  industry: string;
  interestType: "PIK" | "Cash" | "Hybrid";
  principalAmount: number;
  outstandingBalance: number;
  maturityDate: string;
  covenants: string[];
}

export interface FlaggedLoan extends LoanRecord {
  flag_reason: string;
  risk_level: "low" | "medium" | "high" | "critical";
  correlated_event: string;
  flagged_at: string;
}

export interface ScanStatus {
  is_running: boolean;
  interval_minutes: number;
  latest_assessment_available: boolean;
}

export interface AnalysisResult {
  total_loans: number;
  flagged_count: number;
  analysis_method: "ai" | "traditional";
  flagged_loans: FlaggedLoan[];
}

// API Functions

export async function getLatestRiskAssessment(): Promise<RiskAssessment> {
  const response = await fetch(`${API_BASE_URL}/api/risk/latest`);
  if (!response.ok) {
    throw new Error(`Failed to fetch risk assessment: ${response.statusText}`);
  }
  return response.json();
}

export async function triggerImmediateScan(): Promise<RiskAssessment> {
  const response = await fetch(`${API_BASE_URL}/api/scan/immediate`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(`Failed to trigger scan: ${response.statusText}`);
  }
  return response.json();
}

export async function getScanStatus(): Promise<ScanStatus> {
  const response = await fetch(`${API_BASE_URL}/api/scan/status`);
  if (!response.ok) {
    throw new Error(`Failed to fetch scan status: ${response.statusText}`);
  }
  return response.json();
}

export async function analyzePortfolio(
  loans: LoanRecord[],
  useAI: boolean = true
): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/api/analysis/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      loans,
      use_ai: useAI,
    }),
  });
  if (!response.ok) {
    throw new Error(`Failed to analyze portfolio: ${response.statusText}`);
  }
  return response.json();
}

export async function extractFinancialData(
  source: "xero" | "quickbooks" | "stripe",
  connectionId: string,
  tenantId?: string
): Promise<{ source: string; loans: LoanRecord[]; count: number; status: string }> {
  const response = await fetch(`${API_BASE_URL}/api/research/extract`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      source,
      connection_id: connectionId,
      tenant_id: tenantId,
    }),
  });
  if (!response.ok) {
    throw new Error(`Failed to extract data: ${response.statusText}`);
  }
  return response.json();
}

export async function extractAndAnalyze(
  source: "xero" | "quickbooks" | "stripe",
  connectionId: string,
  tenantId?: string,
  useAI: boolean = true
): Promise<AnalysisResult & { source: string; extracted_count: number }> {
  const response = await fetch(`${API_BASE_URL}/api/research/analyze-and-extract`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      source,
      connection_id: connectionId,
      tenant_id: tenantId,
      use_ai: useAI,
    }),
  });
  if (!response.ok) {
    throw new Error(`Failed to extract and analyze: ${response.statusText}`);
  }
  return response.json();
}

export async function getHealthCheck(): Promise<{
  status: string;
  scheduler_running: boolean;
  environment: string;
  research_agent_available: boolean;
  financial_agent_available: boolean;
}> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json();
}
