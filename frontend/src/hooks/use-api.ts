'use client'

import { useState, useEffect, useCallback } from 'react'
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

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const filteredParams = params
        ? Object.fromEntries(Object.entries(params).filter(([, v]) => v !== undefined))
        : undefined
      const response = await api.get(url, { params: filteredParams })
      setData(response.data.results ?? response.data)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar dados'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }, [url, JSON.stringify(params)])

  useEffect(() => {
    if (enabled) {
      fetchData()
    }
  }, [fetchData, enabled])

  return { data, isLoading, error, refetch: fetchData }
}
