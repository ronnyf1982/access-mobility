export interface PreviewAccessUser {
  id: number
  email: string
  first_name: string | null
  last_name: string | null
  is_active: boolean
  note: string | null
  last_used_at: string | null
  created_at: string
  updated_at: string
}

export interface PreviewAccessUserCreate {
  email: string
  password: string
  first_name?: string | null
  last_name?: string | null
  is_active?: boolean
  note?: string | null
}

export interface PreviewAccessUserUpdate {
  first_name?: string | null
  last_name?: string | null
  note?: string | null
}

export interface PreviewAccessPasswordReset {
  new_password: string
  confirm_password: string
}

function authHeader(): { Authorization: string } {
  const token = localStorage.getItem('am_token')
  return { Authorization: `Bearer ${token ?? ''}` }
}

const BASE = '/api/v1/platform-admin/test-access-users'

export async function listPreviewUsers(params?: {
  search?: string
  is_active?: boolean
}): Promise<PreviewAccessUser[]> {
  const url = new URL(BASE, window.location.origin)
  if (params?.search) url.searchParams.set('search', params.search)
  if (params?.is_active !== undefined) url.searchParams.set('is_active', String(params.is_active))

  const res = await fetch(url.toString(), { headers: authHeader() })
  if (!res.ok) throw Object.assign(new Error('list_preview_users'), { response: res, status: res.status })
  return res.json()
}

export async function createPreviewUser(payload: PreviewAccessUserCreate): Promise<PreviewAccessUser> {
  const res = await fetch(BASE, {
    method: 'POST',
    headers: { ...authHeader(), 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw Object.assign(new Error('create_preview_user'), { response: res, status: res.status, body })
  }
  return res.json()
}

export async function getPreviewUser(id: number): Promise<PreviewAccessUser> {
  const res = await fetch(`${BASE}/${id}`, { headers: authHeader() })
  if (!res.ok) throw Object.assign(new Error('get_preview_user'), { response: res, status: res.status })
  return res.json()
}

export async function updatePreviewUser(id: number, payload: PreviewAccessUserUpdate): Promise<PreviewAccessUser> {
  const res = await fetch(`${BASE}/${id}`, {
    method: 'PATCH',
    headers: { ...authHeader(), 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw Object.assign(new Error('update_preview_user'), { response: res, status: res.status, body })
  }
  return res.json()
}

export async function activatePreviewUser(id: number): Promise<PreviewAccessUser> {
  const res = await fetch(`${BASE}/${id}/activate`, {
    method: 'POST',
    headers: authHeader(),
  })
  if (!res.ok) throw Object.assign(new Error('activate_preview_user'), { response: res, status: res.status })
  return res.json()
}

export async function deactivatePreviewUser(id: number): Promise<PreviewAccessUser> {
  const res = await fetch(`${BASE}/${id}/deactivate`, {
    method: 'POST',
    headers: authHeader(),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw Object.assign(new Error('deactivate_preview_user'), { response: res, status: res.status, body })
  }
  return res.json()
}

export async function resetPreviewUserPassword(id: number, payload: PreviewAccessPasswordReset): Promise<void> {
  const res = await fetch(`${BASE}/${id}/reset-password`, {
    method: 'POST',
    headers: { ...authHeader(), 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw Object.assign(new Error('reset_preview_password'), { response: res, status: res.status, body })
  }
}
