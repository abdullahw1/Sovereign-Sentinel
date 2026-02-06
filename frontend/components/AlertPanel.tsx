'use client'

import { Alert } from '@/types'

interface AlertPanelProps {
  alerts: Alert[]
  onDismiss?: (alertId: string) => void
}

export default function AlertPanel({ alerts, onDismiss }: AlertPanelProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-900 border-red-500 text-red-100'
      case 'warning': return 'bg-orange-900 border-orange-500 text-orange-100'
      case 'info': return 'bg-blue-900 border-blue-500 text-blue-100'
      default: return 'bg-gray-800 border-gray-600 text-gray-100'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return '🚨'
      case 'warning': return '⚠️'
      case 'info': return 'ℹ️'
      default: return '📢'
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const criticalAlerts = alerts.filter(a => a.severity === 'critical')
  const otherAlerts = alerts.filter(a => a.severity !== 'critical')

  return (
    <div className="space-y-4">
      {/* Critical Alerts - Always prominent */}
      {criticalAlerts.length > 0 && (
        <div className="bg-red-900 bg-opacity-30 border-2 border-red-500 rounded-lg p-6 animate-pulse">
          <div className="flex items-start gap-4">
            <span className="text-4xl">{getSeverityIcon('critical')}</span>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-red-100 mb-2">CRITICAL ALERT</h2>
              {criticalAlerts.map((alert) => (
                <div key={alert.alertId} className="mb-4 last:mb-0">
                  <h3 className="text-lg font-semibold text-red-100 mb-1">{alert.title}</h3>
                  <p className="text-red-200 mb-2">{alert.message}</p>
                  {alert.actionRequired && (
                    <div className="bg-red-800 bg-opacity-50 rounded p-3 mb-2">
                      <p className="text-sm font-semibold text-red-100">ACTION REQUIRED</p>
                      {alert.recommendedHedge > 0 && (
                        <p className="text-sm text-red-200 mt-1">
                          Recommended Hedge: {alert.recommendedHedge}% BTC
                        </p>
                      )}
                    </div>
                  )}
                  <p className="text-xs text-red-300">{formatTime(alert.timestamp)}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Other Alerts */}
      {otherAlerts.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold mb-4 text-gray-300">
            Active Alerts <span className="text-sm font-normal text-gray-500">({otherAlerts.length})</span>
          </h2>
          <div className="space-y-3">
            {otherAlerts.map((alert) => (
              <div
                key={alert.alertId}
                className={`rounded-lg p-4 border ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <span className="text-2xl">{getSeverityIcon(alert.severity)}</span>
                    <div className="flex-1">
                      <h3 className="font-semibold mb-1">{alert.title}</h3>
                      <p className="text-sm opacity-90">{alert.message}</p>
                      <p className="text-xs opacity-70 mt-2">{formatTime(alert.timestamp)}</p>
                    </div>
                  </div>
                  {onDismiss && (
                    <button
                      onClick={() => onDismiss(alert.alertId)}
                      className="text-sm opacity-70 hover:opacity-100"
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No alerts state */}
      {alerts.length === 0 && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold mb-4 text-gray-300">Active Alerts</h2>
          <p className="text-gray-500 text-center py-8">No active alerts</p>
        </div>
      )}
    </div>
  )
}
