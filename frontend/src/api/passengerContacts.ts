import apiClient from './client'
import type { PassengerContact, PassengerContactCreate, PassengerContactUpdate, EmergencyFileResponse } from '@/types'

const BASE = '/passenger-contacts'
const DRIVER_BASE = '/driver/transport-requests'

export async function listContacts(): Promise<PassengerContact[]> {
  const resp = await apiClient.get<PassengerContact[]>(`${BASE}/`)
  return resp.data
}

export async function createContact(data: PassengerContactCreate): Promise<PassengerContact> {
  const resp = await apiClient.post<PassengerContact>(`${BASE}/`, data)
  return resp.data
}

export async function updateContact(id: string, data: PassengerContactUpdate): Promise<PassengerContact> {
  const resp = await apiClient.patch<PassengerContact>(`${BASE}/${id}`, data)
  return resp.data
}

export async function deleteContact(id: string): Promise<void> {
  await apiClient.delete(`${BASE}/${id}`)
}

export async function getEmergencyFile(
  requestId: string,
  emergencyMode = false,
): Promise<EmergencyFileResponse> {
  const resp = await apiClient.get<EmergencyFileResponse>(
    `${DRIVER_BASE}/${requestId}/emergency-file`,
    { params: { emergency_mode: emergencyMode } },
  )
  return resp.data
}
