import apiClient from './client'
import type {
  PassengerSavedAddress,
  PassengerSavedAddressCreate,
  PassengerSavedAddressUpdate,
} from '@/types'

const BASE = '/passenger-saved-addresses'

export async function listAddresses(): Promise<PassengerSavedAddress[]> {
  const resp = await apiClient.get<PassengerSavedAddress[]>(`${BASE}/`)
  return resp.data
}

export async function createAddress(
  data: PassengerSavedAddressCreate,
): Promise<PassengerSavedAddress> {
  const resp = await apiClient.post<PassengerSavedAddress>(`${BASE}/`, data)
  return resp.data
}

export async function updateAddress(
  id: string,
  data: PassengerSavedAddressUpdate,
): Promise<PassengerSavedAddress> {
  const resp = await apiClient.patch<PassengerSavedAddress>(`${BASE}/${id}`, data)
  return resp.data
}

export async function deleteAddress(id: string): Promise<void> {
  await apiClient.delete(`${BASE}/${id}`)
}
