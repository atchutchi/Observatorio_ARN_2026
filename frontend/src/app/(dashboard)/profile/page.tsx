'use client'

import { useState } from 'react'
import { User, Mail, Phone, Briefcase, Building2, Shield, Save, Loader2 } from 'lucide-react'
import { useAuthStore } from '@/lib/auth'
import api from '@/lib/api'
import toast from 'react-hot-toast'

const ProfilePage = () => {
  const { user, fetchProfile } = useAuthStore()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [form, setForm] = useState({
    first_name: user?.first_name ?? '',
    last_name: user?.last_name ?? '',
    email: user?.email ?? '',
    phone: user?.phone ?? '',
    position: user?.position ?? '',
  })

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await api.patch('/auth/profile/', form)
      await fetchProfile()
      setIsEditing(false)
      toast.success('Perfil actualizado com sucesso')
    } catch {
      toast.error('Erro ao actualizar perfil')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    setForm({
      first_name: user?.first_name ?? '',
      last_name: user?.last_name ?? '',
      email: user?.email ?? '',
      phone: user?.phone ?? '',
      position: user?.position ?? '',
    })
    setIsEditing(false)
  }

  if (!user) return null

  const roleColors: Record<string, string> = {
    admin_arn: 'bg-red-100 text-red-800',
    analyst_arn: 'bg-blue-100 text-blue-800',
    operator_telecel: 'bg-rose-100 text-rose-800',
    operator_orange: 'bg-orange-100 text-orange-800',
    operator_starlink: 'bg-gray-100 text-gray-800',
    viewer: 'bg-green-100 text-green-800',
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Meu Perfil</h2>
        <p className="text-gray-500 text-sm mt-1">Gerir informações pessoais e preferências</p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-arn-primary to-arn-secondary p-8">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center">
              <User className="w-10 h-10 text-white" />
            </div>
            <div className="text-white">
              <h3 className="text-xl font-bold">
                {user.first_name && user.last_name
                  ? `${user.first_name} ${user.last_name}`
                  : user.username}
              </h3>
              <p className="text-white/70 text-sm">{user.email || 'Sem email'}</p>
              <div className="flex items-center gap-2 mt-2">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${roleColors[user.role] || 'bg-gray-100 text-gray-800'}`}>
                  {user.role_display}
                </span>
                {user.operator_name && (
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-white/20 text-white">
                    {user.operator_name}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold text-gray-900">Informações Pessoais</h4>
            {!isEditing ? (
              <button
                type="button"
                onClick={() => setIsEditing(true)}
                className="btn-primary text-sm"
              >
                Editar
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="btn-secondary text-sm"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={handleSave}
                  disabled={isSaving}
                  className="btn-primary text-sm flex items-center gap-2"
                >
                  {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                  Guardar
                </button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
                <User className="w-4 h-4 inline mr-1" />
                Primeiro Nome
              </label>
              {isEditing ? (
                <input
                  id="first_name"
                  type="text"
                  value={form.first_name}
                  onChange={(e) => handleChange('first_name', e.target.value)}
                  className="input-field"
                />
              ) : (
                <p className="text-gray-900 py-2">{user.first_name || '—'}</p>
              )}
            </div>

            <div>
              <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
                <User className="w-4 h-4 inline mr-1" />
                Apelido
              </label>
              {isEditing ? (
                <input
                  id="last_name"
                  type="text"
                  value={form.last_name}
                  onChange={(e) => handleChange('last_name', e.target.value)}
                  className="input-field"
                />
              ) : (
                <p className="text-gray-900 py-2">{user.last_name || '—'}</p>
              )}
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                <Mail className="w-4 h-4 inline mr-1" />
                Email
              </label>
              {isEditing ? (
                <input
                  id="email"
                  type="email"
                  value={form.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  className="input-field"
                />
              ) : (
                <p className="text-gray-900 py-2">{user.email || '—'}</p>
              )}
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                <Phone className="w-4 h-4 inline mr-1" />
                Telefone
              </label>
              {isEditing ? (
                <input
                  id="phone"
                  type="tel"
                  value={form.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  className="input-field"
                />
              ) : (
                <p className="text-gray-900 py-2">{user.phone || '—'}</p>
              )}
            </div>

            <div>
              <label htmlFor="position" className="block text-sm font-medium text-gray-700 mb-1">
                <Briefcase className="w-4 h-4 inline mr-1" />
                Cargo
              </label>
              {isEditing ? (
                <input
                  id="position"
                  type="text"
                  value={form.position}
                  onChange={(e) => handleChange('position', e.target.value)}
                  className="input-field"
                />
              ) : (
                <p className="text-gray-900 py-2">{user.position || '—'}</p>
              )}
            </div>

            <div>
              <p className="block text-sm font-medium text-gray-700 mb-1">
                <Shield className="w-4 h-4 inline mr-1" />
                Perfil de Acesso
              </p>
              <p className="text-gray-900 py-2">{user.role_display}</p>
            </div>

            {user.operator_name && (
              <div>
                <p className="block text-sm font-medium text-gray-700 mb-1">
                  <Building2 className="w-4 h-4 inline mr-1" />
                  Operador
                </p>
                <p className="text-gray-900 py-2">{user.operator_name}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Informações da Conta</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-sm">
          <div>
            <p className="text-gray-500">Nome de utilizador</p>
            <p className="text-gray-900 font-medium">{user.username}</p>
          </div>
          <div>
            <p className="text-gray-500">ID</p>
            <p className="text-gray-900 font-medium">#{user.id}</p>
          </div>
          {user.operator_type && (
            <div>
              <p className="text-gray-500">Tipo de Operador</p>
              <p className="text-gray-900 font-medium">{user.operator_type}</p>
            </div>
          )}
          {user.operator_code && (
            <div>
              <p className="text-gray-500">Código do Operador</p>
              <p className="text-gray-900 font-medium">{user.operator_code}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
