'use client'

import { useState } from 'react'
import { PolicyConfig, PolicyOverride } from '@/types'

interface PolicyOverridePanelProps {
  config: PolicyConfig
  onApplyOverride?: (override: Partial<PolicyOverride>) => void
}

export default function PolicyOverridePanel({ config, onApplyOverride }: PolicyOverridePanelProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedConfig, setEditedConfig] = useState(config)
  const [reason, setReason] = useState('')

  const handleSave = () => {
    if (!reason.trim()) {
      alert('Please provide a reason for the policy override')
      return
    }

    // Find what changed
    const changes: Partial<PolicyOverride>[] = []
    
    if (editedConfig.riskThreshold !== config.riskThreshold) {
      changes.push({
        field: 'riskThreshold',
        oldValue: config.riskThreshold,
        newValue: editedConfig.riskThreshold,
        reason,
      })
    }

    if (editedConfig.pikExposureLimit !== config.pikExposureLimit) {
      changes.push({
        field: 'pikExposureLimit',
        oldValue: config.pikExposureLimit,
        newValue: editedConfig.pikExposureLimit,
        reason,
      })
    }

    if (editedConfig.autoExecuteEnabled !== config.autoExecuteEnabled) {
      changes.push({
        field: 'autoExecuteEnabled',
        oldValue: config.autoExecuteEnabled,
        newValue: editedConfig.autoExecuteEnabled,
        reason,
      })
    }

    // Apply each change
    changes.forEach(change => onApplyOverride?.(change))

    setIsEditing(false)
    setReason('')
  }

  const handleCancel = () => {
    setEditedConfig(config)
    setReason('')
    setIsEditing(false)
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-300">Policy Configuration</h2>
        {!isEditing ? (
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-semibold"
          >
            Edit Policy
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm font-semibold"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded text-sm font-semibold"
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      <div className="space-y-4">
        {/* Risk Threshold */}
        <div>
          <label className="block text-sm font-semibold text-gray-400 mb-2">
            Risk Threshold
          </label>
          {isEditing ? (
            <input
              type="number"
              min="0"
              max="100"
              value={editedConfig.riskThreshold}
              onChange={(e) => setEditedConfig({ ...editedConfig, riskThreshold: Number(e.target.value) })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-gray-100 focus:outline-none focus:border-blue-500"
            />
          ) : (
            <div className="px-3 py-2 bg-gray-750 rounded text-gray-100">
              {config.riskThreshold}
            </div>
          )}
          <p className="text-xs text-gray-500 mt-1">Score above which status escalates to CRITICAL</p>
        </div>

        {/* PIK Exposure Limit */}
        <div>
          <label className="block text-sm font-semibold text-gray-400 mb-2">
            PIK Exposure Limit ($)
          </label>
          {isEditing ? (
            <input
              type="number"
              min="0"
              value={editedConfig.pikExposureLimit}
              onChange={(e) => setEditedConfig({ ...editedConfig, pikExposureLimit: Number(e.target.value) })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-gray-100 focus:outline-none focus:border-blue-500"
            />
          ) : (
            <div className="px-3 py-2 bg-gray-750 rounded text-gray-100">
              {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(config.pikExposureLimit)}
            </div>
          )}
          <p className="text-xs text-gray-500 mt-1">Maximum allowed PIK loan exposure</p>
        </div>

        {/* Auto Execute */}
        <div>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={isEditing ? editedConfig.autoExecuteEnabled : config.autoExecuteEnabled}
              onChange={(e) => isEditing && setEditedConfig({ ...editedConfig, autoExecuteEnabled: e.target.checked })}
              disabled={!isEditing}
              className="w-5 h-5 rounded bg-gray-700 border-gray-600 text-blue-600 focus:ring-blue-500"
            />
            <div>
              <span className="text-sm font-semibold text-gray-400">Auto-Execute Hedges</span>
              <p className="text-xs text-gray-500">Automatically execute hedges without manual approval</p>
            </div>
          </label>
        </div>

        {/* Hedge Percentages */}
        <div>
          <label className="block text-sm font-semibold text-gray-400 mb-2">
            Hedge Percentages by Sector
          </label>
          <div className="space-y-2">
            {Object.entries(config.hedgePercentages).map(([sector, percentage]) => (
              <div key={sector} className="flex items-center justify-between px-3 py-2 bg-gray-750 rounded">
                <span className="text-sm text-gray-300 capitalize">{sector}</span>
                <span className="text-sm font-semibold text-gray-100">{percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Reason field when editing */}
        {isEditing && (
          <div>
            <label className="block text-sm font-semibold text-gray-400 mb-2">
              Reason for Override *
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Explain why you're making this policy change..."
              rows={3}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-gray-100 focus:outline-none focus:border-blue-500"
            />
          </div>
        )}
      </div>
    </div>
  )
}
