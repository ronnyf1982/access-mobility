import type { Vehicle, VehicleCreate, VehicleUpdate } from '@/types'
import apiClient from './client'

export interface VehicleOptionItem {
  key: string
  label: string
  icon: string
  description: string
}

export interface VehicleOptions {
  vehicle_types: Array<{ value: string; label: string }>
  equipment_options: VehicleOptionItem[]
  medical_equipment_options: VehicleOptionItem[]
  dimension_access_options: VehicleOptionItem[]
}

export async function getVehicles(params?: { organization_id?: string; active_only?: boolean }): Promise<Vehicle[]> {
  const { data } = await apiClient.get<Vehicle[]>('/vehicles', { params })
  return data
}

export async function getVehicle(id: string): Promise<Vehicle> {
  const { data } = await apiClient.get<Vehicle>(`/vehicles/${id}`)
  return data
}

export async function createVehicle(payload: VehicleCreate): Promise<Vehicle> {
  const { data } = await apiClient.post<Vehicle>('/vehicles', payload)
  return data
}

export async function updateVehicle(id: string, payload: VehicleUpdate): Promise<Vehicle> {
  const { data } = await apiClient.put<Vehicle>(`/vehicles/${id}`, payload)
  return data
}

export async function deactivateVehicle(id: string): Promise<Vehicle> {
  const { data } = await apiClient.delete<Vehicle>(`/vehicles/${id}`)
  return data
}

export async function permanentDeleteVehicle(id: string): Promise<void> {
  await apiClient.delete(`/vehicles/${id}/permanent`)
}

export async function getVehicleOptions(): Promise<VehicleOptions> {
  const { data } = await apiClient.get<VehicleOptions>('/vehicles/options')
  return data
}
