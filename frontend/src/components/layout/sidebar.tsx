'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/lib/auth'
import {
  LayoutDashboard,
  Database,
  BarChart3,
  FileText,
  MessageSquare,
  Settings,
  Upload,
  CheckCircle,
  History,
} from 'lucide-react'

type NavItem = {
  label: string
  href: string
  icon: React.ElementType
  roles?: string[]
  children?: NavItem[]
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/', icon: LayoutDashboard },
  {
    label: 'Entrada de Dados', href: '/data-entry', icon: Database,
    children: [
      { label: 'Entrada Manual', href: '/data-entry/manual', icon: Database },
      { label: 'Upload Excel', href: '/data-entry/upload', icon: Upload },
      { label: 'Validação', href: '/data-entry/validation', icon: CheckCircle, roles: ['admin_arn', 'analyst_arn'] },
      { label: 'Histórico', href: '/data-entry/history', icon: History },
    ],
  },
  { label: 'Análise', href: '/analysis', icon: BarChart3 },
  { label: 'Relatórios', href: '/reports', icon: FileText },
  { label: 'Assistente IA', href: '/assistant', icon: MessageSquare },
  { label: 'Configurações', href: '/settings', icon: Settings, roles: ['admin_arn'] },
]

const Sidebar = () => {
  const pathname = usePathname()
  const user = useAuthStore((s) => s.user)

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname.startsWith(href)
  }

  const hasAccess = (item: NavItem) => {
    if (!item.roles) return true
    return user && item.roles.includes(user.role)
  }

  return (
    <aside className="w-64 bg-arn-primary min-h-screen flex flex-col">
      <div className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">ARN</span>
          </div>
          <div>
            <h2 className="text-white font-semibold text-sm leading-tight">Observatório</h2>
            <p className="text-white/60 text-xs">Telecom GB</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {NAV_ITEMS.filter(hasAccess).map((item) => (
          <div key={item.href}>
            <Link
              href={item.children ? item.children[0].href : item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive(item.href)
                  ? 'bg-white/15 text-white'
                  : 'text-white/70 hover:bg-white/10 hover:text-white'
              )}
            >
              <item.icon className="w-5 h-5 shrink-0" />
              {item.label}
            </Link>

            {item.children && isActive(item.href) && (
              <div className="ml-8 mt-1 space-y-0.5">
                {item.children.filter(hasAccess).map((child) => (
                  <Link
                    key={child.href}
                    href={child.href}
                    className={cn(
                      'flex items-center gap-2 px-3 py-2 rounded-md text-xs font-medium transition-colors',
                      pathname === child.href
                        ? 'bg-white/15 text-white'
                        : 'text-white/50 hover:bg-white/10 hover:text-white'
                    )}
                  >
                    <child.icon className="w-4 h-4 shrink-0" />
                    {child.label}
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>

      <div className="p-4 border-t border-white/10">
        <p className="text-white/40 text-xs text-center">
          ARN Guiné-Bissau &copy; {new Date().getFullYear()}
        </p>
      </div>
    </aside>
  )
}

export default Sidebar
