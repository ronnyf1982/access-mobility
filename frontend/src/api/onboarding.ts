import type { UserPublic } from '@/types'
import apiClient from './client'

export interface OnboardingStatus {
  needs_onboarding: boolean
  voice_mode_enabled: boolean
  onboarding_completed_at: string | null
  mobility_profile_filled: boolean
}

export async function fetchOnboardingStatus(): Promise<OnboardingStatus> {
  const { data } = await apiClient.get<OnboardingStatus>('/onboarding/status')
  return data
}

export async function saveOnboardingPreferences(voice_mode_enabled: boolean): Promise<UserPublic> {
  const { data } = await apiClient.post<UserPublic>('/onboarding/preferences', { voice_mode_enabled })
  return data
}
