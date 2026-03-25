'use client'

import { useState, useCallback, useEffect } from 'react'
import {
  Users, Plus, Pencil, Trash2, Search, X, Loader2, Shield, ChevronDown,
} from 'lucide-react'
import api from '@/lib/api'
import { useAuthStore } from '@/lib/auth'
import toast from 'react-hot-toast'
import type { User, UserRole } from '@/types'

type UserFormData = {
  username: string
  email: string
  first_name: string
  last_name: string
  password: string
  role: UserRole
  operator: number | null
  phone: string
  position: string
}

type OperatorOption = { id: number; name: string; code: string }

const EMPTY_FORM: UserFormData = {
  username: '', email: '', first_name: '', last_name: '',
  password: '', role: 'viewer', operator: null, phone: '', position: '',
}

const ROLE_LABELS: Record<UserRole, string> = {
  admin_arn: 'Administrador ARN',
  analyst_arn: 'Analista ARN',
  operator_telecel: 'Operador Telecel',
  operator_orange: 'Operador Orange',
  operator_starlink: 'Operador Starlink',
  viewer: 'Visualizador',
}

const ROLE_COLORS: Record<string, string> = {
  admin_arn: 'bg-red-100 text-red-800',
  analyst_arn: 'bg-blue-100 text-blue-800',
  operator_telecel: 'bg-rose-100 text-rose-800',
  operator_orange: 'bg-orange-100 text-orange-800',
  operator_starlink: 'bg-gray-100 text-gray-800',
  viewer: 'bg-green-100 text-green-800',
}

const UsersPage = () => {
  const currentUser = useAuthStore((s) => s.user)
  const [users, setUsers] = useState<User[]>([])
  const [operators, setOperators] = useState<OperatorOption[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [form, setForm] = useState<UserFormData>(EMPTY_FORM)
  const [isSaving, setIsSaving] = useState(false)

  const fetchUsers = useCallback(async () => {
    setIsLoading(true)
    try {
      const [usersRes, opsRes] = await Promise.all([
        api.get('/users/'),
        api.get('/operators/'),
      ])
      setUsers(usersRes.data.results ?? usersRes.data)
      setOperators((opsRes.data.results ?? opsRes.data).map((o: OperatorOption) => ({
        id: o.id, name: o.name, code: o.code,
      })))
    } catch {
      toast.error('Erro ao carregar utilizadores')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => { fetchUsers() }, [fetchUsers])

  const handleCreate = () => {
    setEditingUser(null)
    setForm(EMPTY_FORM)
    setShowModal(true)
  }

  const handleEdit = (u: User) => {
    setEditingUser(u)
    setForm({
      username: u.username,
      email: u.email,
      first_name: u.first_name,
      last_name: u.last_name,
      password: '',
      role: u.role,
      operator: u.operator,
      phone: u.phone,
      position: u.position,
    })
    setShowModal(true)
  }

  const handleDelete = async (u: User) => {
    if (u.id === currentUser?.id) {
      toast.error('Não pode eliminar a sua própria conta')
      return
    }
    if (!confirm(`Tem a certeza que deseja eliminar o utilizador "${u.username}"?`)) return

    try {
      await api.delete(`/users/${u.id}/`)
      toast.success('Utilizador eliminado')
      fetchUsers()
    } catch {
      toast.error('Erro ao eliminar utilizador')
    }
  }

  const handleSubmit = async () => {
    if (!form.username || !form.role) {
      toast.error('Preencha os campos obrigatórios')
      return
    }

    setIsSaving(true)
    try {
      if (editingUser) {
        const payload: Record<string, unknown> = { ...form }
        if (!payload.password) delete payload.password
        await api.patch(`/users/${editingUser.id}/`, payload)
        toast.success('Utilizador actualizado')
      } else {
        if (!form.password || form.password.length < 8) {
          toast.error('Password deve ter pelo menos 8 caracteres')
          setIsSaving(false)
          return
        }
        await api.post('/users/', form)
        toast.success('Utilizador criado')
      }
      setShowModal(false)
      fetchUsers()
    } catch {
      toast.error(editingUser ? 'Erro ao actualizar' : 'Erro ao criar utilizador')
    } finally {
      setIsSaving(false)
    }
  }

  const handleFormChange = (field: keyof UserFormData, value: string | number | null) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const filteredUsers = users.filter((u) => {
    const matchesSearch = search === '' || [u.username, u.first_name, u.last_name, u.email]
      .some((f) => f?.toLowerCase().includes(search.toLowerCase()))
    const matchesRole = roleFilter === '' || u.role === roleFilter
    return matchesSearch && matchesRole
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Gestão de Utilizadores</h2>
          <p className="text-gray-500 text-sm mt-1">{users.length} utilizadores registados</p>
        </div>
        <button type="button" onClick={handleCreate} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Novo Utilizador
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-100 flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Pesquisar utilizadores..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-field pl-10 text-sm"
              aria-label="Pesquisar utilizadores"
            />
          </div>
          <div className="relative">
            <Shield className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="input-field pl-10 pr-8 text-sm appearance-none"
              aria-label="Filtrar por perfil"
            >
              <option value="">Todos os perfis</option>
              {(Object.keys(ROLE_LABELS) as UserRole[]).map((r) => (
                <option key={r} value={r}>{ROLE_LABELS[r]}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-arn-primary" />
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>Nenhum utilizador encontrado</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-left">
                  <th className="px-4 py-3 font-medium text-gray-500">Utilizador</th>
                  <th className="px-4 py-3 font-medium text-gray-500">Email</th>
                  <th className="px-4 py-3 font-medium text-gray-500">Perfil</th>
                  <th className="px-4 py-3 font-medium text-gray-500">Operador</th>
                  <th className="px-4 py-3 font-medium text-gray-500">Cargo</th>
                  <th className="px-4 py-3 font-medium text-gray-500 text-right">Acções</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((u) => (
                  <tr key={u.id} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 bg-arn-primary rounded-full flex items-center justify-center text-white text-xs font-bold">
                          {(u.first_name?.[0] || u.username[0]).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">
                            {u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : u.username}
                          </p>
                          <p className="text-xs text-gray-500">@{u.username}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{u.email || '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${ROLE_COLORS[u.role] || 'bg-gray-100 text-gray-800'}`}>
                        {u.role_display || ROLE_LABELS[u.role]}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{u.operator_name || '—'}</td>
                    <td className="px-4 py-3 text-gray-600">{u.position || '—'}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          type="button"
                          onClick={() => handleEdit(u)}
                          className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          aria-label={`Editar ${u.username}`}
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(u)}
                          className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          aria-label={`Eliminar ${u.username}`}
                          disabled={u.id === currentUser?.id}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" role="dialog" aria-modal="true">
          <div className="bg-white rounded-2xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900">
                {editingUser ? 'Editar Utilizador' : 'Novo Utilizador'}
              </h3>
              <button type="button" onClick={() => setShowModal(false)} className="p-2 hover:bg-gray-100 rounded-lg" aria-label="Fechar">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="modal-first_name" className="block text-sm font-medium text-gray-700 mb-1">Primeiro Nome</label>
                  <input id="modal-first_name" type="text" value={form.first_name} onChange={(e) => handleFormChange('first_name', e.target.value)} className="input-field" />
                </div>
                <div>
                  <label htmlFor="modal-last_name" className="block text-sm font-medium text-gray-700 mb-1">Apelido</label>
                  <input id="modal-last_name" type="text" value={form.last_name} onChange={(e) => handleFormChange('last_name', e.target.value)} className="input-field" />
                </div>
              </div>

              <div>
                <label htmlFor="modal-username" className="block text-sm font-medium text-gray-700 mb-1">
                  Nome de Utilizador <span className="text-red-500">*</span>
                </label>
                <input id="modal-username" type="text" value={form.username} onChange={(e) => handleFormChange('username', e.target.value)} className="input-field" disabled={!!editingUser} />
              </div>

              <div>
                <label htmlFor="modal-email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input id="modal-email" type="email" value={form.email} onChange={(e) => handleFormChange('email', e.target.value)} className="input-field" />
              </div>

              <div>
                <label htmlFor="modal-password" className="block text-sm font-medium text-gray-700 mb-1">
                  Password {!editingUser && <span className="text-red-500">*</span>}
                  {editingUser && <span className="text-xs text-gray-400 ml-1">(deixar vazio para manter)</span>}
                </label>
                <input id="modal-password" type="password" value={form.password} onChange={(e) => handleFormChange('password', e.target.value)} className="input-field" placeholder={editingUser ? '••••••••' : ''} />
              </div>

              <div>
                <label htmlFor="modal-role" className="block text-sm font-medium text-gray-700 mb-1">
                  Perfil de Acesso <span className="text-red-500">*</span>
                </label>
                <select id="modal-role" value={form.role} onChange={(e) => handleFormChange('role', e.target.value)} className="input-field">
                  {(Object.keys(ROLE_LABELS) as UserRole[]).map((r) => (
                    <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                  ))}
                </select>
              </div>

              {form.role.startsWith('operator_') && (
                <div>
                  <label htmlFor="modal-operator" className="block text-sm font-medium text-gray-700 mb-1">Operador</label>
                  <select id="modal-operator" value={form.operator ?? ''} onChange={(e) => handleFormChange('operator', e.target.value ? Number(e.target.value) : null)} className="input-field">
                    <option value="">Seleccionar operador</option>
                    {operators.map((op) => (
                      <option key={op.id} value={op.id}>{op.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="modal-phone" className="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
                  <input id="modal-phone" type="tel" value={form.phone} onChange={(e) => handleFormChange('phone', e.target.value)} className="input-field" />
                </div>
                <div>
                  <label htmlFor="modal-position" className="block text-sm font-medium text-gray-700 mb-1">Cargo</label>
                  <input id="modal-position" type="text" value={form.position} onChange={(e) => handleFormChange('position', e.target.value)} className="input-field" />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 p-6 border-t border-gray-100">
              <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Cancelar</button>
              <button type="button" onClick={handleSubmit} disabled={isSaving} className="btn-primary flex items-center gap-2">
                {isSaving && <Loader2 className="w-4 h-4 animate-spin" />}
                {editingUser ? 'Actualizar' : 'Criar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UsersPage
