'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/auth'
import Sidebar from '@/components/layout/sidebar'
import Header from '@/components/layout/header'

const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const { tokens, user, hasHydrated, fetchProfile } = useAuthStore()
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    if (!hasHydrated) return
    if (!tokens) {
      router.replace('/login')
      return
    }
    if (!user) {
      fetchProfile()
    }
  }, [hasHydrated, tokens, user, fetchProfile, router])

  if (!hasHydrated || !tokens) return null

  return (
    <div className="min-h-screen bg-gray-50 md:flex">
      {isSidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          aria-label="Fechar menu"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header onMenuClick={() => setIsSidebarOpen(true)} />
        <main className="flex-1 overflow-x-hidden bg-gray-50 p-4 md:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout
