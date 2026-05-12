'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/auth'
import { LogOut, Menu, User } from 'lucide-react'

type HeaderProps = {
  onMenuClick?: () => void
}

const Header = ({ onMenuClick }: HeaderProps) => {
  const { user, logout } = useAuthStore()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <header className="flex items-center justify-between gap-3 border-b border-gray-200 bg-white px-4 py-3 md:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 md:hidden"
          aria-label="Abrir menu"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="min-w-0">
          <h1 className="truncate text-base font-semibold text-gray-900 md:text-lg">
            Observatório do Mercado de Telecomunicações
          </h1>
          <p className="text-xs text-gray-500">Guiné-Bissau — ARN</p>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-2 md:gap-4">
        {user && (
          <div className="flex items-center gap-2 md:gap-3">
            <div className="hidden text-right sm:block">
              <p className="max-w-32 truncate text-sm font-medium text-gray-700">
                {user.first_name || user.username}
              </p>
              <p className="text-xs text-gray-500">{user.role_display}</p>
            </div>
            <Link
              href="/profile"
              className="flex h-9 w-9 items-center justify-center rounded-full bg-arn-primary transition-colors hover:bg-arn-secondary"
              aria-label="Ver perfil"
            >
              <User className="w-4 h-4 text-white" />
            </Link>
            <button
              type="button"
              onClick={handleLogout}
              className="p-2 text-gray-400 transition-colors hover:text-gray-600"
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
