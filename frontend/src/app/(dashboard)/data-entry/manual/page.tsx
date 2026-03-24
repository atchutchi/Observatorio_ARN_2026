'use client'

import { useState, useEffect, useCallback, type FormEvent } from 'react'
import { useAuthStore } from '@/lib/auth'
import { useApi } from '@/hooks/use-api'
import api from '@/lib/api'
import { cn, formatNumber } from '@/lib/utils'
import toast from 'react-hot-toast'
import type { IndicatorCategory, Indicator, Period } from '@/types'
import { Save, ChevronRight } from 'lucide-react'

type FormValues = Record<number, string>

const ManualEntryPage = () => {
  const user = useAuthStore((s) => s.user)
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [selectedYear, setSelectedYear] = useState<number>(2024)
  const [selectedQuarter, setSelectedQuarter] = useState<number>(1)
  const [formValues, setFormValues] = useState<FormValues>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { data: categories } = useApi<IndicatorCategory[]>({
    url: '/indicator-categories/',
  })

  const { data: categoryDetail } = useApi<IndicatorCategory>({
    url: `/indicator-categories/${selectedCategory}/`,
    enabled: !!selectedCategory,
  })

  const { data: periods } = useApi<Period[]>({
    url: '/periods/',
    params: { year: selectedYear, quarter: selectedQuarter },
    enabled: !!selectedYear && !!selectedQuarter,
  })

  const isCumulative = categoryDetail?.is_cumulative ?? false

  const handleValueChange = (indicatorId: number, value: string) => {
    setFormValues((prev) => ({ ...prev, [indicatorId]: value }))
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!user?.operator || !periods?.length) return

    setIsSubmitting(true)
    try {
      if (isCumulative) {
        const entries = Object.entries(formValues)
          .filter(([, v]) => v !== '' && v !== undefined)
          .map(([indicatorId, value]) => {
            const [indId, cumType] = indicatorId.toString().split('_')
            return {
              indicator: parseInt(indId),
              operator: user.operator,
              year: selectedYear,
              cumulative_type: cumType || '3M',
              value,
            }
          })

        await api.post('/cumulative-data/bulk_create/', { entries })
      } else {
        const entries = Object.entries(formValues)
          .filter(([, v]) => v !== '' && v !== undefined)
          .flatMap(([indicatorId, value]) =>
            periods!.map((period) => ({
              indicator: parseInt(indicatorId),
              operator: user.operator,
              period: period.id,
              value,
            }))
          )

        await api.post('/data/bulk_create/', { entries })
      }
      toast.success('Dados submetidos com sucesso')
      setFormValues({})
    } catch {
      toast.error('Erro ao submeter dados')
    } finally {
      setIsSubmitting(false)
    }
  }

  const currentYears = Array.from({ length: 9 }, (_, i) => 2018 + i)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Entrada Manual de Dados</h2>
        <p className="text-gray-500 text-sm mt-1">
          Introduza os dados do indicador seleccionado
        </p>
      </div>

      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
              Indicador
            </label>
            <select
              id="category"
              className="input-field"
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value)
                setFormValues({})
              }}
            >
              <option value="">Seleccione um indicador</option>
              {categories?.map((cat) => (
                <option key={cat.code} value={cat.code}>
                  {cat.order}. {cat.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="year" className="block text-sm font-medium text-gray-700 mb-1">
              Ano
            </label>
            <select
              id="year"
              className="input-field"
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
            >
              {currentYears.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>

          {!isCumulative && (
            <div>
              <label htmlFor="quarter" className="block text-sm font-medium text-gray-700 mb-1">
                Trimestre
              </label>
              <select
                id="quarter"
                className="input-field"
                value={selectedQuarter}
                onChange={(e) => setSelectedQuarter(parseInt(e.target.value))}
              >
                <option value={1}>Q1 (Jan-Mar)</option>
                <option value={2}>Q2 (Abr-Jun)</option>
                <option value={3}>Q3 (Jul-Set)</option>
                <option value={4}>Q4 (Out-Dez)</option>
              </select>
            </div>
          )}
        </div>
      </div>

      {selectedCategory && categoryDetail && (
        <form onSubmit={handleSubmit} className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {categoryDetail.name}
              {isCumulative && (
                <span className="ml-2 text-xs font-normal text-amber-600 bg-amber-50 px-2 py-1 rounded">
                  Cumulativo
                </span>
              )}
            </h3>
            <button
              type="submit"
              disabled={isSubmitting || Object.keys(formValues).length === 0}
              className="btn-primary flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {isSubmitting ? 'A submeter...' : 'Submeter Dados'}
            </button>
          </div>

          {isCumulative ? (
            <CumulativeForm
              indicators={categoryDetail.indicators}
              values={formValues}
              onChange={handleValueChange}
            />
          ) : (
            <MonthlyForm
              indicators={categoryDetail.indicators}
              values={formValues}
              onChange={handleValueChange}
            />
          )}
        </form>
      )}
    </div>
  )
}

type FormProps = {
  indicators: Indicator[]
  values: FormValues
  onChange: (id: number, value: string) => void
}

const MonthlyForm = ({ indicators, values, onChange }: FormProps) => {
  return (
    <div className="space-y-1">
      <div className="grid grid-cols-12 gap-2 text-xs font-medium text-gray-500 pb-2 border-b">
        <div className="col-span-6">Indicador</div>
        <div className="col-span-6">Valor</div>
      </div>
      {indicators.map((indicator) => (
        <IndicatorRow
          key={indicator.id}
          indicator={indicator}
          values={values}
          onChange={onChange}
        />
      ))}
    </div>
  )
}

const CumulativeForm = ({ indicators, values, onChange }: FormProps) => {
  const cumTypes = ['3M', '6M', '9M', '12M']

  return (
    <div className="space-y-1">
      <div className="grid grid-cols-12 gap-2 text-xs font-medium text-gray-500 pb-2 border-b">
        <div className="col-span-4">Indicador</div>
        {cumTypes.map((t) => (
          <div key={t} className="col-span-2 text-center">{t}</div>
        ))}
      </div>
      {indicators.map((indicator) => (
        <CumulativeIndicatorRow
          key={indicator.id}
          indicator={indicator}
          cumTypes={cumTypes}
          values={values}
          onChange={onChange}
        />
      ))}
    </div>
  )
}

type RowProps = {
  indicator: Indicator
  values: FormValues
  onChange: (id: number, value: string) => void
}

const IndicatorRow = ({ indicator, values, onChange }: RowProps) => {
  const isParent = indicator.children && indicator.children.length > 0

  return (
    <>
      <div className={cn(
        'grid grid-cols-12 gap-2 py-2 items-center',
        indicator.level === 0 && 'bg-gray-50 font-semibold',
      )}>
        <div
          className="col-span-6 text-sm"
          style={{ paddingLeft: `${indicator.level * 20}px` }}
        >
          {indicator.level > 0 && <ChevronRight className="w-3 h-3 inline mr-1 text-gray-400" />}
          <span className="text-gray-400 mr-2">{indicator.code}</span>
          {indicator.name}
        </div>
        <div className="col-span-6">
          {!isParent && (
            <input
              type="number"
              step="any"
              className="input-field text-sm py-1"
              placeholder="0"
              value={values[indicator.id] ?? ''}
              onChange={(e) => onChange(indicator.id, e.target.value)}
            />
          )}
        </div>
      </div>
      {indicator.children?.map((child) => (
        <IndicatorRow
          key={child.id}
          indicator={child}
          values={values}
          onChange={onChange}
        />
      ))}
    </>
  )
}

type CumRowProps = RowProps & { cumTypes: string[] }

const CumulativeIndicatorRow = ({ indicator, cumTypes, values, onChange }: CumRowProps) => {
  const isParent = indicator.children && indicator.children.length > 0

  return (
    <>
      <div className={cn(
        'grid grid-cols-12 gap-2 py-2 items-center',
        indicator.level === 0 && 'bg-gray-50 font-semibold',
      )}>
        <div
          className="col-span-4 text-sm"
          style={{ paddingLeft: `${indicator.level * 16}px` }}
        >
          <span className="text-gray-400 mr-2">{indicator.code}</span>
          {indicator.name}
        </div>
        {cumTypes.map((ct) => (
          <div key={ct} className="col-span-2">
            {!isParent && (
              <input
                type="number"
                step="any"
                className="input-field text-sm py-1 text-center"
                placeholder="0"
                value={values[`${indicator.id}_${ct}` as unknown as number] ?? ''}
                onChange={(e) => onChange(`${indicator.id}_${ct}` as unknown as number, e.target.value)}
              />
            )}
          </div>
        ))}
      </div>
      {indicator.children?.map((child) => (
        <CumulativeIndicatorRow
          key={child.id}
          indicator={child}
          cumTypes={cumTypes}
          values={values}
          onChange={onChange}
        />
      ))}
    </>
  )
}

export default ManualEntryPage
