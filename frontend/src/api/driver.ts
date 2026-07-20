import type {
  DriverDashboardContext,
  DriverShift,
  DriverShiftStartRequest,
  DriverShiftWithVehicle,
  RideStatusEvent,
  RideStatusEventCreate,
  TransportRequestListItem,
  VehicleBrief,
} from '@/types'
import apiClient from './client'

export async function getDriverContext(): Promise<DriverDashboardContext> {
  const { data } = await apiClient.get<DriverDashboardContext>('/driver/me')
  return data
}

export async function getCurrentShift(): Promise<DriverShiftWithVehicle | null> {
  const { data } = await apiClient.get<DriverShiftWithVehicle | null>('/driver/shift/current')
  return data
}

export async function startShift(payload: DriverShiftStartRequest): Promise<DriverShiftWithVehicle> {
  const { data } = await apiClient.post<DriverShiftWithVehicle>('/driver/shift/start', payload)
  return data
}

export async function endShift(): Promise<DriverShift> {
  const { data } = await apiClient.post<DriverShift>('/driver/shift/end')
  return data
}

export async function pauseShift(): Promise<DriverShift> {
  const { data } = await apiClient.post<DriverShift>('/driver/shift/pause')
  return data
}

export async function resumeShift(): Promise<DriverShift> {
  const { data } = await apiClient.post<DriverShift>('/driver/shift/resume')
  return data
}

export async function searchVehicles(licensePlate: string): Promise<VehicleBrief[]> {
  const { data } = await apiClient.get<VehicleBrief[]>('/driver/vehicles/search', {
    params: { license_plate: licensePlate },
  })
  return data
}

export async function getDriverAssignments(): Promise<TransportRequestListItem[]> {
  const { data } = await apiClient.get<TransportRequestListItem[]>('/driver/assignments')
  return data
}

export async function createRideStatusEvent(
  requestId: string,
  payload: RideStatusEventCreate,
): Promise<RideStatusEvent> {
  const { data } = await apiClient.post<RideStatusEvent>(
    `/driver/transport-requests/${requestId}/status-events`,
    payload,
  )
  return data
}

export async function getRideStatusEvents(requestId: string): Promise<RideStatusEvent[]> {
  const { data } = await apiClient.get<RideStatusEvent[]>(
    `/transport-requests/${requestId}/status-events`,
  )
  return data
}
