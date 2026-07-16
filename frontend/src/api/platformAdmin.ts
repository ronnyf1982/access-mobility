import type { UserRole } from '@/types'

export interface PlatformAdminUser {
  id: number
  email: string
  first_name: string
  last_name: string
  phone: string | null
  role: UserRole
  is_active: boolean
  created_at: string
  first_login_at: string | null
  last_login_at: string | null
  onboarding_completed_at: string | null
  organization_id: number | null
  organization_name: string | null
}

export interface PlatformAdminUserCreate {
  email: string
  password: string
  first_name: string
  last_name: string
  role: UserRole
  phone?: string
  is_active?: boolean
  organization_id?: number | null
}

export interface PlatformAdminUserUpdate {
  first_name?: string
  last_name?: string
  phone?: string | null
  role?: UserRole
  is_active?: boolean
  organization_id?: number | null
}

export interface PlatformAdminPasswordReset {
  new_password: string
  confirm_password: string
}

function authHeader(): { Authorization: string } {
  const token = localStorage.getItem('am_token')
  return { Authorization: `Bearer ${token ?? ''}` }
}

const BASE = '/api/v1/platform-admin'

export async function listUsers(params?: {
  search?: string
  role?: string
  is_active?: boolean
}): Promise<PlatformAdminUser[]> {
  const url = new URL(BASE + '/users', window.location.origin)
  if (params?.search) url.searchParams.set('search', params.search)
  if (params?.role) url.searchParams.set('role', params.role)
  if (params?.is_active !== undefined) url.searchParams.set('is_active', String(params.is_active))

  const res = await fetch(url.toString(), { headers: authHeader() })
  if (!res.ok) throw Object.assign(new Error('list_users'), { response: res, status: res.status })
  return res.json()
}

export async function getUser(id: number): Promise<PlatformAdminUser> {
  const res = await fetch(`${BASE}/users/${id}`, { headers: authHeader() })
  if (!res.ok) throw Object.assign(new Error('get_user'), { response: res, status: res.status })
  return res.json()
}

export async function createUser(payload: PlatformAdminUserCreate): Promise<PlatformAdminUser> {
  const res = await fetch(`${BASE}/users`, {
    method: 'POST',
    headers: { ...authHeader(), 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw Object.assign(new Error('create_user'), { response: res, status: res.status, body })
  }
  return res.json()
}

export async function updateUser(
  id: number,
  payload: PlatformAdminUserUpdate,
): Promise<PlatformAdminUser> {
  const res = await fetch(`${BASE}/users/${id}`, {
    method: 'PATCH',
    headers: { ...authHeader(), 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw Object.assign(new Error('update_user'), { response: res, status: res.status, body })
  }
  return res.json()
}

export async function resetPassword(
  id: number,
  payload: PlatformAdminPasswordReset,
): Promise<void> {
  const res = await fetch(`${BASE}/users/${id}/reset-password`, {
    method: 'POST',
    headers: { ...authHeader(), 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw Object.assign(new Error('reset_password'), { response: res, status: res.status, body })
  }
}

export async function activateUser(id: number): Promise<PlatformAdminUser> {
  const res = await fetch(`${BASE}/users/${id}/activate`, {
    method: 'POST',
    headers: authHeader(),
  })
  if (!res.ok) throw Object.assign(new Error('activate'), { response: res, status: res.status })
  return res.json()
}

export async function deactivateUser(id: number): Promise<PlatformAdminUser> {
  const res = await fetch(`${BASE}/users/${id}/deactivate`, {
    method: 'POST',
    headers: authHeader(),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw Object.assign(new Error('deactivate'), { response: res, status: res.status, body })
  }
  return res.json()
}
