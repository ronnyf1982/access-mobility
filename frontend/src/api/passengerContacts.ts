import axios from 'axios'
import type { PassengerContact, PassengerContactCreate, PassengerContactUpdate, EmergencyFileResponse } from '@/types'

const BASE = '/api/v1/passenger-contacts'
const DRIVER_BASE = '/api/v1/driver/transport-requests'

export async function listContacts(): Promise<PassengerContact[]> {
  const resp = await axios.get<PassengerContact[]>(`${BASE}/`)
  return resp.data
}

export async function createContact(data: PassengerContactCreate): Promise<PassengerContact> {
  const resp = await axios.post<PassengerContact>(`${BASE}/`, data)
  return resp.data
}

export async function updateContact(id: string, data: PassengerContactUpdate): Promise<PassengerContact> {
  const resp = await axios.patch<PassengerContact>(`${BASE}/${id}`, data)
  return resp.data
}

export async function deleteContact(id: string): Promise<void> {
  await axios.delete(`${BASE}/${id}`)
}

export async function getEmergencyFile(
  requestId: string,
  emergencyMode = false,
): Promise<EmergencyFileResponse> {
  const resp = await axios.get<EmergencyFileResponse>(
    `${DRIVER_BASE}/${requestId}/emergency-file`,
    { params: { emergency_mode: emergencyMode } },
  )
  return resp.data
}
