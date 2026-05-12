'use client'

import { FormEvent, useMemo, useState } from 'react'
import Link from 'next/link'
import api from '@/lib/api'
import { useApi } from '@/hooks/use-api'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'
import type {
  OperatorListItem,
  ReceivedDocument,
  ReceivedDocumentStatus,
  ReceivedDocumentSummary,
} from '@/types'
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  FileSpreadsheet,
  Filter,
  Eye,
  Inbox,
  Loader2,
  Upload,
} from 'lucide-react'

const DOCUMENT_TYPES = [
  { value: 'questionnaire', label: 'Questionário preenchido' },
  { value: 'kpi_summary', label: 'Resumo KPI' },
  { value: 'supporting_document', label: 'Documento de suporte' },
  { value: 'correspondence', label: 'Correspondência' },
  { value: 'other', label: 'Outro' },
]

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

const priorityStyle: Record<string, string> = {
  low: 'bg-gray-100 text-gray-700',
  normal: 'bg-blue-100 text-blue-700',
  high: 'bg-red-100 text-red-700',
}

const DocumentsPage = () => {
  const [operatorId, setOperatorId] = useState('')
  const [documentType, setDocumentType] = useState('questionnaire')
  const [year, setYear] = useState(2024)
  const [quarter, setQuarter] = useState<number | ''>('')
  const [priority, setPriority] = useState('normal')
  const [dueDate, setDueDate] = useState('')
  const [notes, setNotes] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [filterOperator, setFilterOperator] = useState('')
  const [filterYear, setFilterYear] = useState('')
  const [filterStatus, setFilterStatus] = useState('')

  const params = useMemo(() => ({
    operator__code: filterOperator || undefined,
    year: filterYear || undefined,
    status: filterStatus || undefined,
  }), [filterOperator, filterStatus, filterYear])

  const { data: operators } = useApi<OperatorListItem[]>({ url: '/operators/' })
  const {
    data: documents,
    isLoading,
    refetch: refetchDocuments,
  } = useApi<ReceivedDocument[]>({
    url: '/received-documents/',
    params,
  })
  const {
    data: summary,
    refetch: refetchSummary,
  } = useApi<ReceivedDocumentSummary>({
    url: '/received-documents/summary/',
    params,
  })

  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: currentYear - 2018 + 1 }, (_, i) => 2018 + i)

  const resetForm = () => {
    setFile(null)
    setNotes('')
    setPriority('normal')
    setDueDate('')
    setQuarter('')
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!operatorId || !file) {
      toast.error('Seleccione o operador e o ficheiro')
      return
    }

    setIsSubmitting(true)
    const formData = new FormData()
    formData.append('operator', operatorId)
    formData.append('file', file)
    formData.append('document_type', documentType)
    formData.append('year', year.toString())
    formData.append('priority', priority)
    if (quarter) formData.append('quarter', quarter.toString())
    if (dueDate) formData.append('due_date', dueDate)
    if (notes.trim()) formData.append('notes', notes.trim())

    try {
      await api.post('/received-documents/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      toast.success('Documento registado')
      resetForm()
      await Promise.all([refetchDocuments(), refetchSummary()])
    } catch {
      toast.error('Erro ao registar documento')
    } finally {
      setIsSubmitting(false)
    }
  }

  const updateDocument = async (
    document: ReceivedDocument,
    payload: Partial<Pick<ReceivedDocument, 'status' | 'priority'>>,
  ) => {
    try {
      await api.patch(`/received-documents/${document.id}/`, payload)
      toast.success('Documento actualizado')
      await Promise.all([refetchDocuments(), refetchSummary()])
    } catch {
      toast.error('Erro ao actualizar documento')
    }
  }

  const isOverdue = (document: ReceivedDocument) => {
    if (!document.due_date || ['imported', 'archived'].includes(document.status)) return false
    return new Date(document.due_date) < new Date(new Date().toDateString())
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Documentos Recebidos</h2>
        <p className="text-gray-500 text-sm mt-1">
          Fila interna para tratar questionários, resumos KPI e anexos antes da importação.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total</p>
              <p className="text-2xl font-bold text-gray-900">{summary?.total ?? 0}</p>
            </div>
            <Inbox className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Em aberto</p>
              <p className="text-2xl font-bold text-gray-900">{summary?.open ?? 0}</p>
            </div>
            <Clock className="h-8 w-8 text-amber-500" />
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Atrasados</p>
              <p className="text-2xl font-bold text-gray-900">{summary?.overdue ?? 0}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-500" />
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Alta prioridade</p>
              <p className="text-2xl font-bold text-gray-900">{summary?.high_priority ?? 0}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div className="flex items-center gap-2">
          <Upload className="h-5 w-5 text-arn-primary" />
          <h3 className="text-base font-semibold text-gray-900">Registar documento</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label htmlFor="operator" className="block text-sm font-medium text-gray-700 mb-1">
              Operador
            </label>
            <select
              id="operator"
              className="input-field"
              value={operatorId}
              onChange={(event) => setOperatorId(event.target.value)}
            >
              <option value="">Seleccione</option>
              {operators?.map((operator) => (
                <option key={operator.id} value={operator.id}>{operator.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="documentType" className="block text-sm font-medium text-gray-700 mb-1">
              Tipo
            </label>
            <select
              id="documentType"
              className="input-field"
              value={documentType}
              onChange={(event) => setDocumentType(event.target.value)}
            >
              {DOCUMENT_TYPES.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
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
              value={year}
              onChange={(event) => setYear(parseInt(event.target.value))}
            >
              {years.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="quarter" className="block text-sm font-medium text-gray-700 mb-1">
              Trimestre
            </label>
            <select
              id="quarter"
              className="input-field"
              value={quarter}
              onChange={(event) => setQuarter(event.target.value ? parseInt(event.target.value) : '')}
            >
              <option value="">Ano completo</option>
              <option value={1}>Q1</option>
              <option value={2}>Q2</option>
              <option value={3}>Q3</option>
              <option value={4}>Q4</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
              Prioridade
            </label>
            <select
              id="priority"
              className="input-field"
              value={priority}
              onChange={(event) => setPriority(event.target.value)}
            >
              {PRIORITY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
              Prazo interno
            </label>
            <input
              id="dueDate"
              type="date"
              className="input-field"
              value={dueDate}
              onChange={(event) => setDueDate(event.target.value)}
            />
          </div>

          <div className="md:col-span-2">
            <label htmlFor="file" className="block text-sm font-medium text-gray-700 mb-1">
              Ficheiro
            </label>
            <input
              id="file"
              type="file"
              className="input-field"
              accept=".xlsx,.xls,.pdf,.doc,.docx"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </div>
        </div>

        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
            Notas internas
          </label>
          <textarea
            id="notes"
            className="input-field min-h-20"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            placeholder="Ex.: contém dados Orange 2024, confirmar receitas e LBI antes da importação."
          />
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="btn-primary inline-flex items-center gap-2"
            disabled={isSubmitting}
          >
            {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            Registar
          </button>
        </div>
      </form>

      <div className="card">
        <div className="flex items-center gap-4 flex-wrap">
          <Filter className="w-5 h-5 text-gray-400 shrink-0" />

          <select
            className="input-field max-w-[200px]"
            value={filterOperator}
            onChange={(event) => setFilterOperator(event.target.value)}
            aria-label="Filtrar por operador"
          >
            <option value="">Todos os operadores</option>
            {operators?.map((operator) => (
              <option key={operator.id} value={operator.code}>{operator.name}</option>
            ))}
          </select>

          <select
            className="input-field max-w-[150px]"
            value={filterYear}
            onChange={(event) => setFilterYear(event.target.value)}
            aria-label="Filtrar por ano"
          >
            <option value="">Todos os anos</option>
            {years.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>

          <select
            className="input-field max-w-[200px]"
            value={filterStatus}
            onChange={(event) => setFilterStatus(event.target.value)}
            aria-label="Filtrar por estado"
          >
            <option value="">Todos os estados</option>
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="card text-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-arn-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-gray-500 mt-4">A carregar...</p>
        </div>
      ) : !documents?.length ? (
        <div className="card text-center py-12">
          <FileSpreadsheet className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">Sem documentos</h3>
          <p className="text-gray-500 mt-1">Nenhum documento encontrado com os filtros actuais.</p>
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <div className="mb-3 text-sm text-gray-500">
            {documents.length} {documents.length === 1 ? 'documento' : 'documentos'} encontrados
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left py-3 px-4 font-medium text-gray-600">Documento</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Operador</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Período</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Responsável</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Prazo</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Estado</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Prioridade</th>
                <th className="text-right py-3 px-4 font-medium text-gray-600">Acções</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((document) => (
                <tr key={document.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="py-3 px-4 min-w-[260px]">
                    <Link
                      href={`/documents/${document.id}`}
                      className="font-medium text-gray-900 hover:text-arn-primary"
                    >
                      {document.original_filename}
                    </Link>
                    <p className="text-xs text-gray-500">{document.document_type_display}</p>
                    {document.latest_import && (
                      <p className="text-xs text-gray-500 mt-1">
                        Importação: {document.latest_import.status}
                      </p>
                    )}
                    {document.notes && (
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">{document.notes}</p>
                    )}
                  </td>
                  <td className="py-3 px-4 text-gray-700">{document.operator_name}</td>
                  <td className="py-3 px-4 text-gray-600">
                    {document.year}{document.quarter ? ` Q${document.quarter}` : ''}
                  </td>
                  <td className="py-3 px-4 text-gray-600">
                    {document.assigned_to_name || 'Sem responsável'}
                  </td>
                  <td className="py-3 px-4">
                    {document.due_date ? (
                      <span className={cn(
                        'text-xs font-medium',
                        isOverdue(document) ? 'text-red-600' : 'text-gray-600',
                      )}>
                        {new Date(document.due_date).toLocaleDateString('pt-PT')}
                      </span>
                    ) : (
                      <span className="text-xs text-gray-400">Sem prazo</span>
                    )}
                  </td>
                  <td className="py-3 px-4 min-w-[180px]">
                    <select
                      className={cn(
                        'w-full rounded-md border px-2 py-1 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-arn-primary',
                        statusStyle[document.status],
                      )}
                      value={document.status}
                      onChange={(event) => updateDocument(document, {
                        status: event.target.value as ReceivedDocumentStatus,
                      })}
                    >
                      {STATUS_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </td>
                  <td className="py-3 px-4 min-w-[140px]">
                    <select
                      className={cn(
                        'w-full rounded-md border border-transparent px-2 py-1 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-arn-primary',
                        priorityStyle[document.priority],
                      )}
                      value={document.priority}
                      onChange={(event) => updateDocument(document, {
                        priority: event.target.value as ReceivedDocument['priority'],
                      })}
                    >
                      {PRIORITY_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <Link
                      href={`/documents/${document.id}`}
                      className="btn-secondary inline-flex items-center gap-2 px-3 py-1.5 text-xs"
                    >
                      <Eye className="h-3.5 w-3.5" />
                      Abrir
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default DocumentsPage
