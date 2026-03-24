'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/auth'
import Sidebar from '@/components/layout/sidebar'
import Header from '@/components/layout/header'

const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const { tokens, user, fetchProfile } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!tokens) {
      router.push('/login')
      return
    }
    if (!user) {
      fetchProfile()
    }
  }, [tokens, user, fetchProfile, router])

  if (!tokens) return null

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-6 bg-gray-50 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout
