'use client'

import { useEffect, useMemo, useState } from 'react'
import api from '@/lib/api'

const MIN_YEAR = 2018
const FALLBACK_YEAR = new Date().getFullYear()

const buildYears = (maxYear: number) =>
  Array.from({ length: Math.max(maxYear, MIN_YEAR) - MIN_YEAR + 1 }, (_, i) => MIN_YEAR + i).reverse()

export const useDashboardYears = () => {
  const [latestYear, setLatestYear] = useState<number | null>(null)
  const [year, setYear] = useState<number | null>(null)

  useEffect(() => {
    let isActive = true

    const fetchLatestYear = async () => {
      try {
        const response = await api.get('/dashboard/latest-year/')
        const resolvedYear = Number(response.data.year) || FALLBACK_YEAR
        if (!isActive) return
        setLatestYear(resolvedYear)
        setYear((current) => current ?? resolvedYear)
      } catch {
        if (!isActive) return
        setLatestYear(FALLBACK_YEAR)
        setYear((current) => current ?? FALLBACK_YEAR)
      }
    }

    fetchLatestYear()

    return () => {
      isActive = false
    }
  }, [])

  const years = useMemo(
    () => buildYears(latestYear ?? FALLBACK_YEAR),
    [latestYear],
  )

  return {
    year,
    setYear,
    years,
    latestYear,
    isYearReady: year !== null,
  }
}
