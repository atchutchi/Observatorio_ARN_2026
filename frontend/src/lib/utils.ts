import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs))

export const formatNumber = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined) return '—'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '—'
  return new Intl.NumberFormat('pt-PT').format(num)
}

export const formatCurrency = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined) return '—'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '—'
  return new Intl.NumberFormat('pt-PT', {
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num) + ' F CFA'
}

export const OPERATOR_COLORS: Record<string, string> = {
  TELECEL: '#E30613',
  ORANGE: '#FF6600',
  STARLINK: '#000000',
}

export const getOperatorColor = (code: string): string =>
  OPERATOR_COLORS[code.toUpperCase()] ?? '#6B7280'
