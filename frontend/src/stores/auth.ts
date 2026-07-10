import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { fetchMe, login as apiLogin, logout as apiLogout } from '@/api/auth'
import type { UserPublic, UserRole } from '@/types'

const TOKEN_KEY = 'am_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<UserPublic | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const role = computed<UserRole | null>(() => user.value?.role ?? null)
  const fullName = computed(() =>
    user.value ? `${user.value.first_name} ${user.value.last_name}` : '',
  )
  const initials = computed(() => {
    if (!user.value) return '?'
    return `${user.value.first_name[0]}${user.value.last_name[0]}`.toUpperCase()
  })

  async function login(email: string, password: string): Promise<void> {
    const response = await apiLogin(email, password)
    token.value = response.access_token
    user.value = response.user
    localStorage.setItem(TOKEN_KEY, response.access_token)
  }

  async function loadUser(): Promise<void> {
    if (!token.value) return
    user.value = await fetchMe()
  }

  async function logout(): Promise<void> {
    try {
      await apiLogout()
    } catch {
      // Server-seitige Abmeldung ist fire-and-forget
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem(TOKEN_KEY)
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    role,
    fullName,
    initials,
    login,
    loadUser,
    logout,
  }
})
