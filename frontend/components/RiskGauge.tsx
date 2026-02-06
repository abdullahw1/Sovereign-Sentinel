'use client'

interface RiskGaugeProps {
  score: number
  sentiment?: 'positive' | 'neutral' | 'negative' | 'critical'
}

export default function RiskGauge({ score, sentiment }: RiskGaugeProps) {
  const getColor = () => {
    if (score >= 80) return 'text-red-500'
    if (score >= 70) return 'text-orange-500'
    if (score >= 50) return 'text-yellow-500'
    return 'text-green-500'
  }

  const getBackgroundColor = () => {
    if (score >= 80) return 'bg-red-500'
    if (score >= 70) return 'bg-orange-500'
    if (score >= 50) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getStatus = () => {
    if (score >= 80) return 'CRITICAL'
    if (score >= 70) return 'HIGH'
    if (score >= 50) return 'ELEVATED'
    return 'NORMAL'
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-lg font-semibold mb-4 text-gray-300">Global Risk Score</h2>
      
      <div className="flex items-center justify-center mb-4">
        <div className="relative w-48 h-48">
          {/* Circular gauge background */}
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="96"
              cy="96"
              r="88"
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              className="text-gray-700"
            />
            <circle
              cx="96"
              cy="96"
              r="88"
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              strokeDasharray={`${(score / 100) * 553} 553`}
              className={getColor()}
              strokeLinecap="round"
            />
          </svg>
          
          {/* Score display */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-5xl font-bold ${getColor()}`}>{score}</span>
            <span className="text-sm text-gray-400 mt-1">/ 100</span>
          </div>
        </div>
      </div>

      <div className="text-center">
        <div className={`inline-block px-4 py-2 rounded-full ${getBackgroundColor()} bg-opacity-20 border ${getColor()} border-opacity-50`}>
          <span className={`font-semibold ${getColor()}`}>{getStatus()}</span>
        </div>
        
        {sentiment && (
          <div className="mt-3 text-sm text-gray-400">
            Sentiment: <span className="text-gray-300 capitalize">{sentiment}</span>
          </div>
        )}
      </div>
    </div>
  )
}
