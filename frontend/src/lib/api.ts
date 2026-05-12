import axios, { type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/lib/auth'
import type { AuthTokens } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
type RetriableRequestConfig = InternalAxiosRequestConfig & { _retry?: boolean }
let refreshRequest: Promise<AuthTokens> | null = null

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const isAuthEndpoint = config.url?.includes('/auth/token')
    if (!isAuthEndpoint) {
      const tokens = useAuthStore.getState().tokens
      if (tokens?.access) {
        config.headers.Authorization = `Bearer ${tokens.access}`
      }
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as RetriableRequestConfig | undefined

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true

      const tokens = useAuthStore.getState().tokens
      if (tokens?.refresh) {
        try {
          refreshRequest ??= axios
            .post(`${API_BASE_URL}/auth/token/refresh/`, { refresh: tokens.refresh })
            .then((response) => ({
              access: response.data.access,
              refresh: response.data.refresh || tokens.refresh,
            }))
            .finally(() => {
              refreshRequest = null
            })

          const newTokens = await refreshRequest

          useAuthStore.getState().setTokens(newTokens)
          originalRequest.headers.Authorization = `Bearer ${newTokens.access}`
          return api(originalRequest)
        } catch {
          useAuthStore.getState().logout()
          if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }
      }
    }

    return Promise.reject(error)
  }
)

export default api
