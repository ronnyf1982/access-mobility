import type { ReverseGeocodeResponse } from '@/types'
import apiClient from './client'

export async function reverseGeocode(
  latitude: number,
  longitude: number,
): Promise<ReverseGeocodeResponse> {
  const { data } = await apiClient.get<ReverseGeocodeResponse>('/geocoding/reverse', {
    params: { latitude, longitude },
  })
  return data
}
