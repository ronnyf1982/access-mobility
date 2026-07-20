import type { SpontaneousRideMatchRequest, SpontaneousRideMatchResult } from '@/types'
import apiClient from './client'

export async function findSpontaneousMatches(
  payload: SpontaneousRideMatchRequest,
): Promise<SpontaneousRideMatchResult[]> {
  const { data } = await apiClient.post<SpontaneousRideMatchResult[]>(
    '/spontaneous-rides/matches',
    payload,
  )
  return data
}
