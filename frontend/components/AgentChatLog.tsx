'use client'

import { useEffect, useRef } from 'react'
import { AgentLog } from '@/types'

interface AgentChatLogProps {
  logs: AgentLog[]
  maxHeight?: string
}

export default function AgentChatLog({ logs, maxHeight = '500px' }: AgentChatLogProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Auto-scroll to bottom when new logs arrive
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs])

  const getAgentColor = (agent: string) => {
    switch (agent) {
      case 'OSINT_Scout': return 'bg-blue-600'
      case 'Forensic_Auditor': return 'bg-purple-600'
      case 'Policy_Brain': return 'bg-green-600'
      case 'Treasury_Commander': return 'bg-orange-600'
      default: return 'bg-gray-600'
    }
  }

  const getAgentIcon = (agent: string) => {
    switch (agent) {
      case 'OSINT_Scout': return '🔍'
      case 'Forensic_Auditor': return '🔬'
      case 'Policy_Brain': return '🧠'
      case 'Treasury_Commander': return '💰'
      default: return '🤖'
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

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-gray-300">
          Agent Activity Log <span className="text-sm font-normal text-gray-500">({logs.length})</span>
        </h2>
      </div>

      <div
        ref={scrollRef}
        className="overflow-y-auto p-4 space-y-4"
        style={{ maxHeight }}
      >
        {logs.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No agent activity yet</p>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="flex gap-3">
              {/* Agent avatar */}
              <div className="flex-shrink-0">
                <div className={`w-10 h-10 rounded-full ${getAgentColor(log.agent)} flex items-center justify-center text-xl`}>
                  {getAgentIcon(log.agent)}
                </div>
              </div>

              {/* Log content */}
              <div className="flex-1 bg-gray-750 rounded-lg p-3 border border-gray-700">
                <div className="flex items-start justify-between mb-2">
                  <span className="font-semibold text-sm text-gray-300">
                    {log.agent.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-gray-500">{formatTime(log.timestamp)}</span>
                </div>

                <div className="space-y-2">
                  <div>
                    <span className="text-xs text-gray-400 uppercase font-semibold">Action:</span>
                    <p className="text-sm text-gray-200 mt-1">{log.action}</p>
                  </div>

                  {log.reasoning && (
                    <div>
                      <span className="text-xs text-gray-400 uppercase font-semibold">Reasoning:</span>
                      <p className="text-sm text-gray-300 mt-1 italic">{log.reasoning}</p>
                    </div>
                  )}

                  <div>
                    <span className="text-xs text-gray-400 uppercase font-semibold">Outcome:</span>
                    <p className="text-sm text-gray-200 mt-1">{log.outcome}</p>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
