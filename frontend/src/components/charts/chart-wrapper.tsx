'use client'

import { type ReactNode } from 'react'
import { Download, Loader2 } from 'lucide-react'

type ChartWrapperProps = {
  title: string
  subtitle?: string
  isLoading?: boolean
  error?: string | null
  isEmpty?: boolean
  height?: number
  onExport?: () => void
  children: ReactNode
}

const ChartWrapper = ({
  title,
  subtitle,
  isLoading = false,
  error = null,
  isEmpty = false,
  height = 350,
  onExport,
  children,
}: ChartWrapperProps) => {
  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-gray-900">{title}</h3>
        </div>
        <div className="flex items-center justify-center" style={{ height }}>
          <Loader2 className="w-8 h-8 animate-spin text-arn-primary" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <h3 className="text-base font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="flex items-center justify-center text-red-500" style={{ height }}>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    )
  }

  if (isEmpty) {
    return (
      <div className="card">
        <h3 className="text-base font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="flex items-center justify-center text-gray-400" style={{ height }}>
          <p className="text-sm">Sem dados disponíveis para o período seleccionado</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-gray-900">{title}</h3>
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
        {onExport && (
          <button
            type="button"
            onClick={onExport}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Exportar gráfico"
          >
            <Download className="w-4 h-4 text-gray-500" />
          </button>
        )}
      </div>
      {children}
    </div>
  )
}

export default ChartWrapper
