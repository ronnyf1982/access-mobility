import type { TokenResponse, UserPublic } from '@/types'
import apiClient from './client'

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', { email, password })
  return data
}

export async function fetchMe(): Promise<UserPublic> {
  const { data } = await apiClient.get<UserPublic>('/auth/me')
  return data
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout')
}
