import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, AuthTokens } from '@/types'
import api from '@/lib/api'

type AuthState = {
  user: User | null
  tokens: AuthTokens | null
  isLoading: boolean
  setTokens: (tokens: AuthTokens) => void
  setUser: (user: User) => void
  login: (username: string, password: string) => Promise<void>
  fetchProfile: () => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isLoading: false,

      setTokens: (tokens) => set({ tokens }),
      setUser: (user) => set({ user }),

      login: async (username, password) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/auth/token/', { username, password })
          const tokens: AuthTokens = {
            access: response.data.access,
            refresh: response.data.refresh,
          }
          set({ tokens })
          await get().fetchProfile()
        } finally {
          set({ isLoading: false })
        }
      },

      fetchProfile: async () => {
        try {
          const response = await api.get('/auth/profile/')
          set({ user: response.data })
        } catch {
          set({ user: null, tokens: null })
        }
      },

      logout: () => {
        set({ user: null, tokens: null })
      },
    }),
    {
      name: 'observatorio-auth',
      partialize: (state) => ({
        tokens: state.tokens,
        user: state.user,
      }),
    }
  )
)
