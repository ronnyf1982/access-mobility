export type UserRole =
  | 'passenger'
  | 'trusted_person'
  | 'organization_admin'
  | 'organization_coordinator'
  | 'provider_admin'
  | 'dispatcher'
  | 'driver'
  | 'platform_admin'

export interface UserPublic {
  id: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  is_active: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserPublic
}

export const ROLE_LABELS: Record<UserRole, string> = {
  passenger: 'Fahrgast',
  trusted_person: 'Vertrauensperson',
  organization_admin: 'Organisations-Admin',
  organization_coordinator: 'Koordinator:in',
  provider_admin: 'Fahrdienst-Admin',
  dispatcher: 'Disponent:in',
  driver: 'Fahrer:in',
  platform_admin: 'Plattform-Admin',
}

export const ROLE_CONTEXT: Record<UserRole, string> = {
  passenger: 'Hier sehen Sie Ihre gebuchten Fahrten und können neue Fahrten anfragen.',
  trusted_person:
    'Als Vertrauensperson können Sie Fahrten für freigegebene Personen einsehen und buchen.',
  organization_admin:
    'Als Organisations-Admin verwalten Sie Ihre Organisation, Mitglieder und Fahrtkontingente.',
  organization_coordinator:
    'Als Koordinator:in können Sie Fahrten für Mitglieder Ihrer Organisation buchen.',
  provider_admin:
    'Als Fahrdienst-Admin verwalten Sie Ihren Fahrdienst, Fahrzeuge und Fahrer:innen.',
  dispatcher: 'Als Disponent:in teilen Sie Fahrten Fahrzeugen und Fahrer:innen zu.',
  driver: 'Als Fahrer:in sehen Sie Ihre zugewiesenen Aufträge und Tourenpläne.',
  platform_admin:
    'Als Plattform-Admin haben Sie Zugriff auf alle Bereiche der Plattform.',
}
