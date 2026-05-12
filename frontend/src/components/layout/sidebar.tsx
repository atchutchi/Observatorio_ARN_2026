'use client'

import Image from 'next/image'
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
  Inbox,
  Upload,
  CheckCircle,
  History,
  Users,
  Phone,
  PhoneIncoming,
  Globe,
  Wifi,
  Monitor,
  Activity,
  CreditCard,
  Briefcase,
  Building2,
  TrendingUp,
  GitCompare,
  PieChart,
  UserCog,
  X,
  PanelLeftClose,
  PanelLeftOpen,
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
  { label: 'Documentos', href: '/documents', icon: Inbox, roles: ['admin_arn', 'analyst_arn'] },
  {
    label: 'Análise', href: '/analysis', icon: BarChart3,
    children: [
      { label: 'Estações Móveis', href: '/analysis/estacoes_moveis', icon: Users },
      { label: 'Tráfego Originado', href: '/analysis/trafego_originado', icon: Phone },
      { label: 'Tráfego Terminado', href: '/analysis/trafego_terminado', icon: PhoneIncoming },
      { label: 'Roaming', href: '/analysis/trafego_roaming', icon: Globe },
      { label: 'LBI', href: '/analysis/lbi', icon: Wifi },
      { label: 'Internet Fixo', href: '/analysis/internet_fixo', icon: Monitor },
      { label: 'Internet Tráfego', href: '/analysis/internet_trafic', icon: Activity },
      { label: 'Tarifário Voz', href: '/analysis/tarifario_voz', icon: CreditCard },
      { label: 'Receitas', href: '/analysis/receitas', icon: Briefcase },
      { label: 'Empregos', href: '/analysis/empregos', icon: Building2 },
      { label: 'Investimento', href: '/analysis/investimento', icon: TrendingUp },
      { label: 'Comparativa', href: '/analysis/comparative', icon: GitCompare },
      { label: 'Análise de Mercado', href: '/analysis/market', icon: PieChart },
    ],
  },
  { label: 'Relatórios', href: '/reports', icon: FileText },
  { label: 'Assistente IA', href: '/assistant', icon: MessageSquare },
  {
    label: 'Configurações', href: '/settings', icon: Settings, roles: ['admin_arn'],
    children: [
      { label: 'Visão Geral', href: '/settings', icon: Settings },
      { label: 'Utilizadores', href: '/settings/users', icon: UserCog },
    ],
  },
]

type SidebarProps = {
  isOpen?: boolean
  isCollapsed?: boolean
  onClose?: () => void
  onCollapseToggle?: () => void
}

const Sidebar = ({
  isOpen = false,
  isCollapsed = false,
  onClose,
  onCollapseToggle,
}: SidebarProps) => {
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
    <aside className={cn(
      'fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-arn-primary transition-[width,transform] duration-200 md:sticky md:top-0 md:z-auto md:min-h-screen md:translate-x-0',
      isCollapsed ? 'md:w-20' : 'md:w-64',
      isOpen ? 'translate-x-0' : '-translate-x-full',
    )}>
      <div className={cn('p-6', isCollapsed && 'md:px-3')}>
        <div className="flex items-center justify-between gap-3">
          <Link
            href="/"
            className={cn(
              'group flex min-w-0 items-center gap-3',
              isCollapsed && 'md:justify-center',
            )}
            onClick={onClose}
            title="Observatório Telecom GB"
          >
            <div className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-lg bg-white p-1">
              <Image
                src="/logos/arn.png"
                alt="ARN - Autoridade Reguladora Nacional"
                width={64}
                height={29}
                className="h-auto w-8 object-contain"
              />
            </div>
            <div className={cn('min-w-0', isCollapsed && 'md:hidden')}>
              <h2 className="text-white font-semibold text-sm leading-tight group-hover:text-white/90 transition-colors">Observatório</h2>
              <p className="text-white/60 text-xs">Telecom GB</p>
            </div>
          </Link>
          <button
            type="button"
            onClick={onCollapseToggle}
            className="hidden rounded-lg p-2 text-white/70 hover:bg-white/10 hover:text-white md:flex"
            aria-label={isCollapsed ? 'Expandir menu' : 'Minimizar menu'}
            title={isCollapsed ? 'Expandir menu' : 'Minimizar menu'}
          >
            {isCollapsed ? (
              <PanelLeftOpen className="h-5 w-5" />
            ) : (
              <PanelLeftClose className="h-5 w-5" />
            )}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-white/70 hover:bg-white/10 hover:text-white md:hidden"
            aria-label="Fechar menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>

      <nav className={cn('flex-1 space-y-1 overflow-y-auto px-3', isCollapsed && 'md:px-2')}>
        {NAV_ITEMS.filter(hasAccess).map((item) => (
          <div key={item.href}>
            <Link
              href={item.children ? item.children[0].href : item.href}
              onClick={onClose}
              title={item.label}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isCollapsed && 'md:justify-center md:px-0',
                isActive(item.href)
                  ? 'bg-white/15 text-white'
                  : 'text-white/70 hover:bg-white/10 hover:text-white'
              )}
            >
              <item.icon className="w-5 h-5 shrink-0" />
              <span className={cn('truncate', isCollapsed && 'md:hidden')}>
                {item.label}
              </span>
            </Link>

            {item.children && isActive(item.href) && (
              <div className={cn(
                'ml-8 mt-1 space-y-0.5 max-h-72 overflow-y-auto',
                isCollapsed && 'md:hidden',
              )}>
                {item.children.filter(hasAccess).map((child) => (
                  <Link
                    key={child.href}
                    href={child.href}
                    onClick={onClose}
                    title={child.label}
                    className={cn(
                      'flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-colors',
                      pathname === child.href
                        ? 'bg-white/15 text-white'
                        : 'text-white/50 hover:bg-white/10 hover:text-white'
                    )}
                  >
                    <child.icon className="w-3.5 h-3.5 shrink-0" />
                    {child.label}
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>

      <div className={cn('p-4 border-t border-white/10', isCollapsed && 'md:px-2')}>
        <p className="text-white/40 text-xs text-center">
          <span className={cn(isCollapsed && 'md:hidden')}>
            ARN Guiné-Bissau &copy; {new Date().getFullYear()}
          </span>
          <span className={cn('hidden', isCollapsed && 'md:inline')}>
            ARN
          </span>
        </p>
      </div>
    </aside>
  )
}

export default Sidebar
