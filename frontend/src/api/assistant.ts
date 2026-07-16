import apiClient from './client'

export interface AssistantCapability {
  id: string
  label: string
  available: boolean
  planned_sprint?: number
}

export interface AssistantCapabilitiesResponse {
  role: string
  voice_mode_enabled: boolean
  capabilities: AssistantCapability[]
}

export async function fetchAssistantCapabilities(): Promise<AssistantCapabilitiesResponse> {
  const { data } = await apiClient.get<AssistantCapabilitiesResponse>('/assistant/capabilities')
  return data
}
