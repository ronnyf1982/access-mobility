import type { DriverProfile, DriverProfileCreate, DriverProfileUpdate } from '@/types'
import apiClient from './client'

export interface DriverOptionItem {
  key: string
  label: string
  icon: string
  description: string
}

export interface DriverOptions {
  qualification_options: DriverOptionItem[]
  medical_qualification_options: DriverOptionItem[]
  technical_training_options: DriverOptionItem[]
}

export async function getDrivers(params?: { organization_id?: string; active_only?: boolean }): Promise<DriverProfile[]> {
  const { data } = await apiClient.get<DriverProfile[]>('/drivers', { params })
  return data
}

export async function getDriver(id: string): Promise<DriverProfile> {
  const { data } = await apiClient.get<DriverProfile>(`/drivers/${id}`)
  return data
}

export async function createDriver(payload: DriverProfileCreate): Promise<DriverProfile> {
  const { data } = await apiClient.post<DriverProfile>('/drivers', payload)
  return data
}

export async function updateDriver(id: string, payload: DriverProfileUpdate): Promise<DriverProfile> {
  const { data } = await apiClient.put<DriverProfile>(`/drivers/${id}`, payload)
  return data
}

export async function deactivateDriver(id: string): Promise<DriverProfile> {
  const { data } = await apiClient.delete<DriverProfile>(`/drivers/${id}`)
  return data
}

export async function permanentDeleteDriver(id: string): Promise<void> {
  await apiClient.delete(`/drivers/${id}/permanent`)
}

export async function getDriverOptions(): Promise<DriverOptions> {
  const { data } = await apiClient.get<DriverOptions>('/drivers/options')
  return data
}
