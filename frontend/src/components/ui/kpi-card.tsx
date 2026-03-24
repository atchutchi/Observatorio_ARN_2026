import { cn } from '@/lib/utils'
import type { LucideIcon } from 'lucide-react'

type KPICardProps = {
  title: string
  value: string
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  icon: LucideIcon
  color?: string
}

const KPICard = ({ title, value, change, changeType = 'neutral', icon: Icon, color }: KPICardProps) => {
  return (
    <div className="card flex items-start justify-between">
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {change && (
          <p className={cn(
            'text-xs font-medium',
            changeType === 'positive' && 'text-green-600',
            changeType === 'negative' && 'text-red-600',
            changeType === 'neutral' && 'text-gray-500',
          )}>
            {change}
          </p>
        )}
      </div>
      <div
        className="w-12 h-12 rounded-xl flex items-center justify-center"
        style={{ backgroundColor: color ? `${color}15` : '#1B2A4A15' }}
      >
        <Icon className="w-6 h-6" style={{ color: color || '#1B2A4A' }} />
      </div>
    </div>
  )
}

export default KPICard
