'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/auth'
import { LogOut, User } from 'lucide-react'

const Header = () => {
  const { user, logout } = useAuthStore()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div>
        <h1 className="text-lg font-semibold text-gray-900">
          Observatório do Mercado de Telecomunicações
        </h1>
        <p className="text-xs text-gray-500">Guiné-Bissau — ARN</p>
      </div>

      <div className="flex items-center gap-4">
        {user && (
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-700">
                {user.first_name || user.username}
              </p>
              <p className="text-xs text-gray-500">{user.role_display}</p>
            </div>
            <Link
              href="/profile"
              className="w-9 h-9 bg-arn-primary rounded-full flex items-center justify-center hover:bg-arn-secondary transition-colors"
              aria-label="Ver perfil"
            >
              <User className="w-4 h-4 text-white" />
            </Link>
            <button
              type="button"
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Terminar sessão"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header
