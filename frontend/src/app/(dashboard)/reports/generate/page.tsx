'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import api from '@/lib/api'
import toast from 'react-hot-toast'

const CURRENT_YEAR = new Date().getFullYear()
const YEARS = Array.from({ length: CURRENT_YEAR - 2017 }, (_, i) => 2018 + i).reverse()

const GenerateReportPage = () => {
  const router = useRouter()
  const [reportType, setReportType] = useState<'quarterly' | 'annual'>('quarterly')
  const [year, setYear] = useState(CURRENT_YEAR)
  const [quarter, setQuarter] = useState(1)
  const [title, setTitle] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedReport, setGeneratedReport] = useState<{ id: number; status: string } | null>(null)
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
    }
  }, [])

  const pollStatus = useCallback((reportId: number) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)

    pollIntervalRef.current = setInterval(async () => {
      try {
        const res = await api.get(`/reports/${reportId}/`)
        const reportStatus = res.data.status
        setGeneratedReport({ id: reportId, status: reportStatus })

        if (reportStatus === 'ready' || reportStatus === 'error') {
          if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
          pollIntervalRef.current = null
          setIsGenerating(false)
          if (reportStatus === 'ready') {
            toast.success('Relatório gerado com sucesso!')
          } else {
            toast.error('Erro ao gerar relatório')
          }
        }
      } catch {
        if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
        pollIntervalRef.current = null
        setIsGenerating(false)
      }
    }, 3000)
  }, [])

  const handleGenerate = async () => {
    setIsGenerating(true)
    try {
      const payload: Record<string, string | number | null> = {
        report_type: reportType,
        year,
        quarter: reportType === 'quarterly' ? quarter : null,
      }
      if (title) payload.title = title

      const res = await api.post('/reports/generate/', payload)
      setGeneratedReport({ id: res.data.id, status: 'generating' })
      toast.success('Geração iniciada...')
      pollStatus(res.data.id)
    } catch {
      setIsGenerating(false)
      toast.error('Erro ao iniciar geração')
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={() => router.push('/reports')}
          className="p-2 hover:bg-gray-100 rounded-lg"
          aria-label="Voltar"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Gerar Relatório</h2>
          <p className="text-gray-500 text-sm mt-0.5">
            Crie um relatório PDF e Excel com os dados do observatório
          </p>
        </div>
      </div>

      <div className="card space-y-6">
        <div>
          <label htmlFor="reportType" className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Relatório
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setReportType('quarterly')}
              className={`p-4 rounded-xl border-2 text-left transition-colors ${
                reportType === 'quarterly'
                  ? 'border-arn-primary bg-arn-primary/5'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <p className="font-semibold text-gray-900">Trimestral</p>
              <p className="text-xs text-gray-500 mt-1">Relatório de um trimestre específico</p>
            </button>
            <button
              type="button"
              onClick={() => setReportType('annual')}
              className={`p-4 rounded-xl border-2 text-left transition-colors ${
                reportType === 'annual'
                  ? 'border-arn-primary bg-arn-primary/5'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <p className="font-semibold text-gray-900">Anual</p>
              <p className="text-xs text-gray-500 mt-1">Relatório completo do ano</p>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="year" className="block text-sm font-medium text-gray-700 mb-1">Ano</label>
            <select
              id="year"
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="input-field"
            >
              {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
          {reportType === 'quarterly' && (
            <div>
              <label htmlFor="quarter" className="block text-sm font-medium text-gray-700 mb-1">Trimestre</label>
              <select
                id="quarter"
                value={quarter}
                onChange={(e) => setQuarter(Number(e.target.value))}
                className="input-field"
              >
                <option value={1}>Q1 (Jan - Mar)</option>
                <option value={2}>Q2 (Abr - Jun)</option>
                <option value={3}>Q3 (Jul - Set)</option>
                <option value={4}>Q4 (Out - Dez)</option>
              </select>
            </div>
          )}
        </div>

        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Título (opcional)
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input-field"
            placeholder={`Observatório Telecom GB — ${reportType === 'quarterly' ? `Q${quarter} ` : ''}${year}`}
          />
        </div>

        <button
          type="button"
          onClick={handleGenerate}
          disabled={isGenerating}
          className="btn-primary w-full flex items-center justify-center gap-2 py-3"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              A gerar relatório...
            </>
          ) : (
            <>
              <FileText className="w-5 h-5" />
              Gerar Relatório
            </>
          )}
        </button>
      </div>

      {generatedReport && (
        <div className={`card border-2 ${
          generatedReport.status === 'ready' ? 'border-green-200 bg-green-50' :
          generatedReport.status === 'error' ? 'border-red-200 bg-red-50' :
          'border-blue-200 bg-blue-50'
        }`}>
          <div className="flex items-center gap-3">
            {generatedReport.status === 'generating' && (
              <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
            )}
            {generatedReport.status === 'ready' && (
              <CheckCircle className="w-6 h-6 text-green-600" />
            )}
            {generatedReport.status === 'error' && (
              <AlertCircle className="w-6 h-6 text-red-500" />
            )}
            <div>
              <p className="font-semibold text-gray-900">
                {generatedReport.status === 'generating' && 'A processar...'}
                {generatedReport.status === 'ready' && 'Relatório pronto!'}
                {generatedReport.status === 'error' && 'Erro na geração'}
              </p>
              <p className="text-sm text-gray-600">
                {generatedReport.status === 'ready' && 'Vá à lista de relatórios para descarregar.'}
                {generatedReport.status === 'generating' && 'Pode demorar alguns segundos...'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default GenerateReportPage
