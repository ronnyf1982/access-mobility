import apiClient from './client'
import type {
  TransportRequestRead,
  TransportRequestListItem,
  TransportRequestCreate,
  TransportRequestUpdate,
  TransportRequestAssign,
  MatchingOptionsResponse,
} from '@/types'

export async function getTransportRequests(): Promise<TransportRequestListItem[]> {
  const { data } = await apiClient.get<TransportRequestListItem[]>('/transport-requests')
  return data
}

export async function getTransportRequest(id: string): Promise<TransportRequestRead> {
  const { data } = await apiClient.get<TransportRequestRead>(`/transport-requests/${id}`)
  return data
}

export async function createTransportRequest(
  payload: TransportRequestCreate,
): Promise<TransportRequestRead> {
  const { data } = await apiClient.post<TransportRequestRead>('/transport-requests', payload)
  return data
}

export async function updateTransportRequest(
  id: string,
  payload: TransportRequestUpdate,
): Promise<TransportRequestRead> {
  const { data } = await apiClient.put<TransportRequestRead>(`/transport-requests/${id}`, payload)
  return data
}

export async function submitTransportRequest(id: string): Promise<TransportRequestRead> {
  const { data } = await apiClient.post<TransportRequestRead>(`/transport-requests/${id}/submit`)
  return data
}

export async function cancelTransportRequest(id: string): Promise<TransportRequestRead> {
  const { data } = await apiClient.post<TransportRequestRead>(`/transport-requests/${id}/cancel`)
  return data
}

export async function getMatchingOptions(id: string): Promise<MatchingOptionsResponse> {
  const { data } = await apiClient.get<MatchingOptionsResponse>(
    `/transport-requests/${id}/matching-options`,
  )
  return data
}

export async function assignTransportRequest(
  id: string,
  payload: TransportRequestAssign,
): Promise<TransportRequestRead> {
  const { data } = await apiClient.post<TransportRequestRead>(
    `/transport-requests/${id}/assign`,
    payload,
  )
  return data
}

export async function unassignTransportRequest(id: string): Promise<TransportRequestRead> {
  const { data } = await apiClient.post<TransportRequestRead>(
    `/transport-requests/${id}/unassign`,
  )
  return data
}
