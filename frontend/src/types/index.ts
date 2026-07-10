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
  platform_admin: 'Als Plattform-Admin haben Sie Zugriff auf alle Bereiche der Plattform.',
}

// ─── Mobilitätsprofil ────────────────────────────────────────────────────────

export type WheelchairType = 'manual' | 'electric' | 'unknown'

export interface MobilityProfile {
  id: string
  user_id: string
  display_name: string | null
  date_of_birth: string | null
  emergency_contact_name: string | null
  emergency_contact_phone: string | null
  uses_wheelchair: boolean
  wheelchair_type: WheelchairType | null
  uses_rollator: boolean
  uses_crutches: boolean
  is_blind_or_visually_impaired: boolean
  is_deaf_or_hard_of_hearing: boolean
  needs_escort: boolean
  needs_entry_assistance: boolean
  needs_door_to_door_assistance: boolean
  needs_ramp: boolean
  needs_lift: boolean
  needs_stretcher_transport: boolean
  can_transfer_to_seat: boolean | null
  has_own_wheelchair: boolean | null
  requires_wheelchair_space: boolean
  requires_extra_time: boolean
  communication_notes: string | null
  medical_notes: string | null
  general_notes: string | null
  created_at: string
  updated_at: string
}

export type MobilityProfileUpdate = Partial<Omit<MobilityProfile, 'id' | 'user_id' | 'created_at' | 'updated_at'>>

export interface MobilityNeedOption {
  key: keyof MobilityProfile
  label: string
  icon: string
  description: string
}

export const MOBILITY_NEED_KEYS: Array<keyof MobilityProfile> = [
  'uses_wheelchair',
  'uses_rollator',
  'uses_crutches',
  'is_blind_or_visually_impaired',
  'is_deaf_or_hard_of_hearing',
  'needs_escort',
  'needs_entry_assistance',
  'needs_door_to_door_assistance',
  'needs_ramp',
  'needs_lift',
  'needs_stretcher_transport',
]
