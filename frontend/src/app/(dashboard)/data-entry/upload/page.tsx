'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import { useAuthStore } from '@/lib/auth'
import api from '@/lib/api'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'
import type { FileUpload } from '@/types'
import {
  Upload, FileSpreadsheet, CheckCircle, XCircle, Loader2, AlertTriangle,
} from 'lucide-react'

const FILE_TYPES = [
  { value: 'questionnaire_telecel', label: 'Questionário Telecel' },
  { value: 'questionnaire_orange', label: 'Questionário Orange' },
  { value: 'questionnaire_starlink', label: 'Questionário Starlink' },
  { value: 'kpi_orange', label: 'KPI Orange' },
  { value: 'statistics', label: 'Dados Estatísticos Consolidados' },
  { value: 'other', label: 'Outro' },
]

const UploadPage = () => {
  const user = useAuthStore((s) => s.user)
  const [fileType, setFileType] = useState('')
  const [year, setYear] = useState(2024)
  const [quarter, setQuarter] = useState<number | ''>('')
  const [uploadResult, setUploadResult] = useState<FileUpload | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file || !fileType) {
      toast.error('Seleccione o tipo de ficheiro primeiro')
      return
    }

    setIsUploading(true)
    setUploadResult(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', fileType)
    formData.append('year', year.toString())
    if (quarter) formData.append('quarter', quarter.toString())

    try {
      const response = await api.post('/uploads/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      toast.success('Ficheiro carregado — a processar...')
      setUploadResult(response.data)
      startPolling(response.data.id)
    } catch {
      toast.error('Erro ao carregar ficheiro')
      setIsUploading(false)
    }
  }, [fileType, year, quarter])

  const startPolling = (uploadId: number) => {
    if (pollingRef.current) clearInterval(pollingRef.current)

    pollingRef.current = setInterval(async () => {
      try {
        const res = await api.get(`/uploads/${uploadId}/`)
        setUploadResult(res.data)

        if (res.data.status === 'processed' || res.data.status === 'error') {
          if (pollingRef.current) clearInterval(pollingRef.current)
          setIsUploading(false)
          if (res.data.status === 'processed') {
            toast.success(`Processado: ${res.data.records_imported} registos importados`)
          } else {
            toast.error('Erro no processamento do ficheiro')
          }
        }
      } catch {
        if (pollingRef.current) clearInterval(pollingRef.current)
        setIsUploading(false)
      }
    }, 2000)
  }

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    maxFiles: 1,
    maxSize: 52428800,
    disabled: isUploading,
  })

  const statusIcon = {
    uploaded: <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />,
    processing: <Loader2 className="w-5 h-5 text-amber-500 animate-spin" />,
    processed: <CheckCircle className="w-5 h-5 text-green-500" />,
    error: <XCircle className="w-5 h-5 text-red-500" />,
    validated: <CheckCircle className="w-5 h-5 text-green-600" />,
  }

  const statusLabel = {
    uploaded: 'Carregado',
    processing: 'Em processamento...',
    processed: 'Processado',
    error: 'Erro',
    validated: 'Validado',
  }

  const currentYears = Array.from({ length: 9 }, (_, i) => 2018 + i)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Upload de Ficheiro Excel</h2>
        <p className="text-gray-500 text-sm mt-1">
          Carregue os questionários Excel dos operadores
        </p>
      </div>

      <div className="card">
        <h3 className="text-base font-semibold text-gray-900 mb-4">Configuração</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="fileType" className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Ficheiro
            </label>
            <select
              id="fileType"
              className="input-field"
              value={fileType}
              onChange={(e) => setFileType(e.target.value)}
            >
              <option value="">Seleccione</option>
              {FILE_TYPES.map((ft) => (
                <option key={ft.value} value={ft.value}>{ft.label}</option>
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
              onChange={(e) => setYear(parseInt(e.target.value))}
            >
              {currentYears.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="quarter" className="block text-sm font-medium text-gray-700 mb-1">
              Trimestre (opcional)
            </label>
            <select
              id="quarter"
              className="input-field"
              value={quarter}
              onChange={(e) => setQuarter(e.target.value ? parseInt(e.target.value) : '')}
            >
              <option value="">Todos</option>
              <option value={1}>Q1</option>
              <option value={2}>Q2</option>
              <option value={3}>Q3</option>
              <option value={4}>Q4</option>
            </select>
          </div>
        </div>
      </div>

      <div
        {...getRootProps()}
        className={cn(
          'card border-2 border-dashed cursor-pointer transition-colors text-center py-12',
          isDragActive ? 'border-arn-primary bg-blue-50' : 'border-gray-300 hover:border-arn-secondary',
          isUploading && 'opacity-50 cursor-not-allowed',
        )}
      >
        <input {...getInputProps()} />
        <FileSpreadsheet className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        {isDragActive ? (
          <p className="text-arn-primary font-medium">Largue o ficheiro aqui...</p>
        ) : (
          <>
            <p className="text-gray-600 font-medium">
              Arraste e largue um ficheiro Excel aqui
            </p>
            <p className="text-gray-400 text-sm mt-1">
              ou clique para seleccionar (.xlsx, .xls, máx. 50MB)
            </p>
          </>
        )}
      </div>

      {uploadResult && (
        <div className="card">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Resultado do Processamento</h3>

          <div className="space-y-4">
            <div className="flex items-center gap-3">
              {statusIcon[uploadResult.status]}
              <div>
                <p className="font-medium text-gray-900">{uploadResult.original_filename}</p>
                <p className="text-sm text-gray-500">{statusLabel[uploadResult.status]}</p>
              </div>
            </div>

            {(uploadResult.status === 'processed' || uploadResult.status === 'error') && (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-2xl font-bold text-green-700">{uploadResult.records_imported}</p>
                  <p className="text-sm text-green-600">Registos importados</p>
                </div>
                <div className="bg-red-50 rounded-lg p-4">
                  <p className="text-2xl font-bold text-red-700">{uploadResult.records_errors}</p>
                  <p className="text-sm text-red-600">Erros</p>
                </div>
              </div>
            )}

            {uploadResult.processing_log && (
              <div>
                <button
                  type="button"
                  className="text-sm text-arn-primary font-medium hover:underline"
                  onClick={() => {
                    const el = document.getElementById('processing-log')
                    if (el) el.classList.toggle('hidden')
                  }}
                >
                  Ver log detalhado
                </button>
                <pre
                  id="processing-log"
                  className="hidden mt-2 bg-gray-900 text-gray-100 rounded-lg p-4 text-xs overflow-auto max-h-64"
                >
                  {uploadResult.processing_log}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default UploadPage
