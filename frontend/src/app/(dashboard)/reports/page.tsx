'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { FileText, Download, Plus, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import api from '@/lib/api'
import { useAuthStore } from '@/lib/auth'

type Report = {
  id: number
  title: string
  report_type: string
  year: number
  quarter: number | null
  status: string
  generated_at: string
  generated_by_name: string
  pdf_url: string | null
  excel_url: string | null
}

const STATUS_CONFIG: Record<string, { icon: React.ElementType; color: string; label: string }> = {
  draft: { icon: Clock, color: 'text-gray-500', label: 'Rascunho' },
  generating: { icon: Loader2, color: 'text-blue-500', label: 'A gerar...' },
  ready: { icon: CheckCircle, color: 'text-green-600', label: 'Pronto' },
  published: { icon: CheckCircle, color: 'text-arn-primary', label: 'Publicado' },
  error: { icon: AlertCircle, color: 'text-red-500', label: 'Erro' },
}

const ReportsPage = () => {
  const [reports, setReports] = useState<Report[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const user = useAuthStore((s) => s.user)
  const isARN = user?.role === 'admin_arn' || user?.role === 'analyst_arn'

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.get('/reports/')
        setReports(res.data.results ?? res.data)
      } catch {
        // handle error
      } finally {
        setIsLoading(false)
      }
    }
    fetch()
  }, [])

  const handleDownload = async (reportId: number, format: 'pdf' | 'excel') => {
    try {
      const res = await api.get(`/reports/${reportId}/download_${format}/`, {
        responseType: 'blob',
      })
      const ext = format === 'pdf' ? 'pdf' : 'xlsx'
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `report_${reportId}.${ext}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch {
      // handle error
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Relatórios</h2>
          <p className="text-gray-500 text-sm mt-1">Relatórios trimestrais e anuais gerados</p>
        </div>
        {isARN && (
          <Link href="/reports/generate" className="btn-primary text-sm flex items-center gap-2">
            <Plus className="w-4 h-4" /> Gerar Relatório
          </Link>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card animate-pulse h-20" />
          ))}
        </div>
      ) : reports.length === 0 ? (
        <div className="card text-center py-12">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Nenhum relatório gerado</p>
          {isARN && (
            <Link href="/reports/generate" className="btn-primary text-sm mt-4 inline-flex items-center gap-2">
              <Plus className="w-4 h-4" /> Gerar primeiro relatório
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((report) => {
            const statusConf = STATUS_CONFIG[report.status] || STATUS_CONFIG.draft
            const StatusIcon = statusConf.icon

            return (
              <div key={report.id} className="card flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-arn-primary/10 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-arn-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{report.title}</h3>
                    <div className="flex items-center gap-3 mt-1">
                      <span className={`flex items-center gap-1 text-xs ${statusConf.color}`}>
                        <StatusIcon className={`w-3.5 h-3.5 ${report.status === 'generating' ? 'animate-spin' : ''}`} />
                        {statusConf.label}
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(report.generated_at).toLocaleDateString('pt-PT')}
                      </span>
                      {report.generated_by_name && (
                        <span className="text-xs text-gray-400">por {report.generated_by_name}</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {report.pdf_url && (report.status === 'ready' || report.status === 'published') && (
                    <button
                      type="button"
                      onClick={() => handleDownload(report.id, 'pdf')}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-700 rounded-lg text-xs font-medium hover:bg-red-100 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" /> PDF
                    </button>
                  )}
                  {report.excel_url && (report.status === 'ready' || report.status === 'published') && (
                    <button
                      type="button"
                      onClick={() => handleDownload(report.id, 'excel')}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 rounded-lg text-xs font-medium hover:bg-green-100 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" /> Excel
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default ReportsPage
