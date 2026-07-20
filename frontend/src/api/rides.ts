import type { RideStatusEvent } from '@/types'
import apiClient from './client'

export async function getRideStatusEvents(requestId: string): Promise<RideStatusEvent[]> {
  const { data } = await apiClient.get<RideStatusEvent[]>(
    `/transport-requests/${requestId}/status-events`,
  )
  return data
}
