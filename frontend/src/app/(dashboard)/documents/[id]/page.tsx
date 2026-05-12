'use client'

import { useMemo, useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import api from '@/lib/api'
import { useApi } from '@/hooks/use-api'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'
import type { ReceivedDocument, ReceivedDocumentStatus } from '@/types'
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle,
  Clock,
  Download,
  FileSpreadsheet,
  Loader2,
  Play,
} from 'lucide-react'

const STATUS_OPTIONS: Array<{ value: ReceivedDocumentStatus; label: string }> = [
  { value: 'received', label: 'Recebido' },
  { value: 'classifying', label: 'Em classificação' },
  { value: 'extracting', label: 'Em extracção' },
  { value: 'reviewing', label: 'Em revisão' },
  { value: 'validated', label: 'Validado' },
  { value: 'imported', label: 'Importado' },
  { value: 'archived', label: 'Arquivado' },
]

const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Baixa' },
  { value: 'normal', label: 'Normal' },
  { value: 'high', label: 'Alta' },
]

const statusStyle: Record<ReceivedDocumentStatus, string> = {
  received: 'bg-blue-50 text-blue-700 border-blue-200',
  classifying: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  extracting: 'bg-amber-50 text-amber-700 border-amber-200',
  reviewing: 'bg-purple-50 text-purple-700 border-purple-200',
  validated: 'bg-green-50 text-green-700 border-green-200',
  imported: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  archived: 'bg-gray-50 text-gray-600 border-gray-200',
}

const uploadStatusLabel = {
  uploaded: 'Carregado',
  processing: 'Em processamento',
  processed: 'Processado',
  error: 'Erro',
  validated: 'Validado',
}

const uploadStatusStyle = {
  uploaded: 'bg-blue-50 text-blue-700',
  processing: 'bg-amber-50 text-amber-700',
  processed: 'bg-green-50 text-green-700',
  error: 'bg-red-50 text-red-700',
  validated: 'bg-emerald-50 text-emerald-700',
}

const DocumentDetailPage = () => {
  const params = useParams()
  const id = Array.isArray(params.id) ? params.id[0] : params.id
  const [isSendingToImport, setIsSendingToImport] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)

  const {
    data: document,
    isLoading,
    refetch,
  } = useApi<ReceivedDocument>({
    url: `/received-documents/${id}/`,
    enabled: !!id,
  })

  const fileUrl = useMemo(() => {
    if (!document?.file) return ''
    if (document.file.startsWith('http')) return document.file
    const apiBase = String(api.defaults.baseURL || '').replace(/\/api\/v1\/?$/, '')
    return `${apiBase}${document.file}`
  }, [document?.file])

  const updateDocument = async (
    payload: Partial<Pick<ReceivedDocument, 'status' | 'priority'>>,
  ) => {
    if (!document) return
    setIsUpdating(true)
    try {
      await api.patch(`/received-documents/${document.id}/`, payload)
      toast.success('Documento actualizado')
      await refetch()
    } catch {
      toast.error('Erro ao actualizar documento')
    } finally {
      setIsUpdating(false)
    }
  }

  const sendToImport = async () => {
    if (!document) return
    setIsSendingToImport(true)
    try {
      const response = await api.post(`/received-documents/${document.id}/send_to_import/`)
      toast.success(response.data.detail || 'Documento enviado para importação')
      await refetch()
    } catch {
      toast.error('Erro ao enviar documento para importação')
    } finally {
      setIsSendingToImport(false)
    }
  }

  const isOverdue = document?.due_date
    && !['imported', 'archived'].includes(document.status)
    && new Date(document.due_date) < new Date(new Date().toDateString())

  if (isLoading || !document) {
    return (
      <div className="card text-center py-12">
        <div className="animate-spin w-8 h-8 border-2 border-arn-primary border-t-transparent rounded-full mx-auto" />
        <p className="text-gray-500 mt-4">A carregar documento...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <Link
            href="/documents"
            className="inline-flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-arn-primary"
          >
            <ArrowLeft className="h-4 w-4" />
            Documentos
          </Link>
          <h2 className="mt-2 text-2xl font-bold text-gray-900">{document.original_filename}</h2>
          <p className="text-gray-500 text-sm mt-1">
            {document.operator_name} · {document.year}{document.quarter ? ` Q${document.quarter}` : ''}
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {fileUrl && (
            <a
              href={fileUrl}
              target="_blank"
              rel="noreferrer"
              className="btn-secondary inline-flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Abrir ficheiro
            </a>
          )}
          <button
            type="button"
            className="btn-primary inline-flex items-center gap-2"
            onClick={sendToImport}
            disabled={isSendingToImport || document.status === 'imported'}
          >
            {isSendingToImport ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            Enviar para importação
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-gray-500">Estado</p>
          <select
            className={cn(
              'mt-2 w-full rounded-md border px-2 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-arn-primary',
              statusStyle[document.status],
            )}
            value={document.status}
            disabled={isUpdating}
            onChange={(event) => updateDocument({
              status: event.target.value as ReceivedDocumentStatus,
            })}
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>

        <div className="card">
          <p className="text-sm text-gray-500">Prioridade</p>
          <select
            className="input-field mt-2"
            value={document.priority}
            disabled={isUpdating}
            onChange={(event) => updateDocument({
              priority: event.target.value as ReceivedDocument['priority'],
            })}
          >
            {PRIORITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>

        <div className="card">
          <p className="text-sm text-gray-500">Responsável</p>
          <p className="mt-3 font-medium text-gray-900">
            {document.assigned_to_name || 'Sem responsável'}
          </p>
        </div>

        <div className="card">
          <p className="text-sm text-gray-500">Prazo interno</p>
          <p className={cn('mt-3 font-medium', isOverdue ? 'text-red-600' : 'text-gray-900')}>
            {document.due_date ? new Date(document.due_date).toLocaleDateString('pt-PT') : 'Sem prazo'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <FileSpreadsheet className="h-5 w-5 text-arn-primary" />
            <h3 className="text-base font-semibold text-gray-900">Dados do documento</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Tipo</p>
              <p className="font-medium text-gray-900">{document.document_type_display}</p>
            </div>
            <div>
              <p className="text-gray-500">Recebido por</p>
              <p className="font-medium text-gray-900">{document.received_by_name || 'Sem registo'}</p>
            </div>
            <div>
              <p className="text-gray-500">Registado em</p>
              <p className="font-medium text-gray-900">
                {new Date(document.created_at).toLocaleString('pt-PT')}
              </p>
            </div>
            <div>
              <p className="text-gray-500">Última actualização</p>
              <p className="font-medium text-gray-900">
                {new Date(document.updated_at).toLocaleString('pt-PT')}
              </p>
            </div>
          </div>

          <div className="mt-6">
            <p className="text-sm text-gray-500">Notas internas</p>
            <p className="mt-2 whitespace-pre-wrap rounded-lg border border-gray-100 bg-gray-50 p-4 text-sm text-gray-700">
              {document.notes || 'Sem notas internas.'}
            </p>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            {document.latest_import?.status === 'processed' ? (
              <CheckCircle className="h-5 w-5 text-green-500" />
            ) : document.latest_import?.status === 'error' ? (
              <AlertTriangle className="h-5 w-5 text-red-500" />
            ) : (
              <Clock className="h-5 w-5 text-amber-500" />
            )}
            <h3 className="text-base font-semibold text-gray-900">Última importação</h3>
          </div>

          {document.latest_import ? (
            <div className="space-y-4">
              <span className={cn(
                'inline-flex rounded-full px-2.5 py-1 text-xs font-medium',
                uploadStatusStyle[document.latest_import.status],
              )}>
                {uploadStatusLabel[document.latest_import.status]}
              </span>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-green-50 p-3">
                  <p className="text-xl font-bold text-green-700">
                    {document.latest_import.records_imported}
                  </p>
                  <p className="text-xs text-green-700">Importados</p>
                </div>
                <div className="rounded-lg bg-red-50 p-3">
                  <p className="text-xl font-bold text-red-700">
                    {document.latest_import.records_errors}
                  </p>
                  <p className="text-xs text-red-700">Erros</p>
                </div>
              </div>

              {document.latest_import.processing_log && (
                <pre className="max-h-72 overflow-auto rounded-lg bg-gray-900 p-4 text-xs text-gray-100">
                  {document.latest_import.processing_log}
                </pre>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-500">
              Este documento ainda não foi enviado para o pipeline de importação.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default DocumentDetailPage
