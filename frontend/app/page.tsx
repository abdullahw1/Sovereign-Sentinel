"use client";

import { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import {
  getLatestRiskAssessment,
  triggerImmediateScan,
  getScanStatus,
  type RiskAssessment,
  type ScanStatus,
} from "@/services/api";
import { Shield, Activity, AlertTriangle, TrendingUp, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

const queryClient = new QueryClient();

function DashboardContent() {
  const [scanning, setScanning] = useState(false);

  const { data: riskAssessment, isLoading: riskLoading, refetch: refetchRisk } = useQuery({
    queryKey: ["risk-assessment"],
    queryFn: getLatestRiskAssessment,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const { data: scanStatus } = useQuery({
    queryKey: ["scan-status"],
    queryFn: getScanStatus,
    refetchInterval: 5000,
  });

  const handleTriggerScan = async () => {
    setScanning(true);
    try {
      await triggerImmediateScan();
      await refetchRisk();
    } catch (error) {
      console.error("Failed to trigger scan:", error);
    } finally {
      setScanning(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 80) return "text-red-500";
    if (score >= 60) return "text-orange-500";
    if (score >= 40) return "text-yellow-500";
    return "text-green-500";
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "critical":
        return "bg-red-500/10 text-red-500 border-red-500/30";
      case "negative":
        return "bg-orange-500/10 text-orange-500 border-orange-500/30";
      case "neutral":
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/30";
      case "positive":
        return "bg-green-500/10 text-green-500 border-green-500/30";
      default:
        return "bg-gray-500/10 text-gray-500 border-gray-500/30";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="h-14 border-b border-border/50 glass flex items-center justify-between px-4 shrink-0 z-50">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
            <Shield className="w-4 h-4 text-primary" />
          </div>
          <span className="text-sm font-semibold tracking-tight">
            Sovereign <span className="text-primary">Sentinel</span>
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleTriggerScan}
            disabled={scanning}
          >
            {scanning ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                Scanning...
              </>
            ) : (
              <>
                <Activity className="w-3.5 h-3.5 mr-1.5" />
                Scan Now
              </>
            )}
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Financial War Room</h1>
            <p className="text-muted-foreground mt-1">Shadow Default Detection System</p>
          </div>
        </div>

        {/* Risk Assessment Card */}
        {riskLoading ? (
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center py-12">
                <div className="text-center space-y-2">
                  <RefreshCw className="w-8 h-8 text-primary animate-spin mx-auto" />
                  <p className="text-sm text-muted-foreground">Loading risk assessment...</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : riskAssessment ? (
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Global Risk Assessment
                </CardTitle>
                <CardDescription>
                  Last updated: {new Date(riskAssessment.timestamp).toLocaleString()}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Risk Score</span>
                    <span className={`text-2xl font-bold ${getRiskColor(riskAssessment.global_risk_score)}`}>
                      {riskAssessment.global_risk_score.toFixed(1)}
                    </span>
                  </div>
                  <Progress value={riskAssessment.global_risk_score} className="h-2" />
                </div>
                <div>
                  <Badge className={getSentimentColor(riskAssessment.sentiment)}>
                    {riskAssessment.sentiment.toUpperCase()}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Affected Sectors
                </CardTitle>
                <CardDescription>Geopolitical risk sectors</CardDescription>
              </CardHeader>
              <CardContent>
                {riskAssessment.affected_sectors.length > 0 ? (
                  <div className="space-y-2">
                    {riskAssessment.affected_sectors.map((sector, idx) => (
                      <Badge key={idx} variant="outline" className="mr-2 mb-2">
                        {sector}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No affected sectors detected</p>
                )}
              </CardContent>
            </Card>
          </div>
        ) : (
          <Card>
            <CardContent className="p-6">
              <div className="text-center py-12">
                <p className="text-muted-foreground">No risk assessment available</p>
                <Button onClick={handleTriggerScan} className="mt-4" disabled={scanning}>
                  Run Initial Scan
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* News Articles */}
        {riskAssessment?.source_articles && riskAssessment.source_articles.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Recent Intelligence</CardTitle>
              <CardDescription>Latest geopolitical news and events</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {riskAssessment.source_articles.slice(0, 5).map((article, idx) => (
                  <div key={idx} className="border-b border-border/50 pb-4 last:border-0 last:pb-0">
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-primary transition-colors"
                    >
                      <h3 className="font-medium text-sm mb-1">{article.title}</h3>
                    </a>
                    <p className="text-xs text-muted-foreground line-clamp-2">{article.snippet}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(article.published_date).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Scan Status */}
        {scanStatus && (
          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${scanStatus.is_running ? "bg-green-500 animate-pulse" : "bg-gray-500"}`} />
                  <span className="text-sm">
                    Scheduler: {scanStatus.is_running ? "Running" : "Stopped"}
                  </span>
                </div>
                <span className="text-sm text-muted-foreground">
                  Interval: {scanStatus.interval_minutes} minutes
                </span>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}

export default function Home() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <DashboardContent />
      </TooltipProvider>
    </QueryClientProvider>
  );
}
