import type {
  SpontaneousRideBookRequest,
  SpontaneousRideBookResponse,
  SpontaneousRideMatchRequest,
  SpontaneousRideMatchResult,
} from '@/types'
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

export async function bookSpontaneousRide(
  payload: SpontaneousRideBookRequest,
): Promise<SpontaneousRideBookResponse> {
  const { data } = await apiClient.post<SpontaneousRideBookResponse>(
    '/spontaneous-rides/book',
    payload,
  )
  return data
}
