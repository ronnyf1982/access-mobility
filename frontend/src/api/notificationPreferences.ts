import type { NotificationPreference, NotificationPreferenceUpsert } from '@/types'
import apiClient from './client'

export async function getNotificationPreferences(): Promise<NotificationPreference[]> {
  const { data } = await apiClient.get<NotificationPreference[]>('/passenger/notification-preferences')
  return data
}

export async function saveNotificationPreferences(
  prefs: NotificationPreferenceUpsert[],
): Promise<NotificationPreference[]> {
  const { data } = await apiClient.put<NotificationPreference[]>(
    '/passenger/notification-preferences',
    prefs,
  )
  return data
}
