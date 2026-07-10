import apiClient from './client'
import type { TransportType } from '@/types'

export async function getTransportOptions(): Promise<TransportType[]> {
  const res = await apiClient.get<TransportType[]>('/transport-options')
  return res.data
}
