import type { MobilityProfile, MobilityProfileUpdate } from '@/types'
import apiClient from './client'

export interface MobilityProfileOptions {
  wheelchair_types: Array<{ value: string; label: string }>
  mobility_needs: Array<{ key: string; label: string; icon: string; description: string }>
}

export async function getMyProfile(): Promise<MobilityProfile> {
  const { data } = await apiClient.get<MobilityProfile>('/mobility-profile/me')
  return data
}

export async function updateMyProfile(payload: MobilityProfileUpdate): Promise<MobilityProfile> {
  const { data } = await apiClient.put<MobilityProfile>('/mobility-profile/me', payload)
  return data
}

export async function getOptions(): Promise<MobilityProfileOptions> {
  const { data } = await apiClient.get<MobilityProfileOptions>('/mobility-profile/options')
  return data
}
