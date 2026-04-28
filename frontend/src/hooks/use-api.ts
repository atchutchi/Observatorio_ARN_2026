'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import api from '@/lib/api'

type UseApiOptions<T> = {
  url: string
  params?: Record<string, string | number | boolean | undefined>
  enabled?: boolean
  initialData?: T
}

export const useApi = <T>({ url, params, enabled = true, initialData }: UseApiOptions<T>) => {
  const [data, setData] = useState<T | undefined>(initialData)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const paramsKey = JSON.stringify(params ?? {})
  const filteredParams = useMemo(
    () => {
      const parsedParams = JSON.parse(paramsKey) as Record<string, string | number | boolean>
      const entries = Object.entries(parsedParams).filter(([, v]) => v !== undefined)
      return entries.length > 0 ? Object.fromEntries(entries) : undefined
    },
    [paramsKey]
  )

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.get(url, { params: filteredParams })
      setData(response.data.results ?? response.data)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar dados'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }, [url, filteredParams])

  useEffect(() => {
    if (enabled) {
      fetchData()
    }
  }, [fetchData, enabled])

  return { data, isLoading, error, refetch: fetchData }
}
