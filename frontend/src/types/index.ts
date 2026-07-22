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
  voice_mode_enabled: boolean
  needs_onboarding: boolean
  onboarding_completed_at: string | null
  first_login_at: string | null
  last_login_at: string | null
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

// ─── Fahrzeuge ────────────────────────────────────────────────────────────────

export type VehicleTypeName =
  | 'standard_car'
  | 'comfort_car'
  | 'wheelchair_van'
  | 'wheelchair_bus'
  | 'multi_passenger_van'
  | 'stretcher_vehicle'
  | 'other'

export const VEHICLE_TYPE_LABELS: Record<VehicleTypeName, string> = {
  standard_car:       'Standard-PKW',
  comfort_car:        'Kombi / Komfort-PKW',
  wheelchair_van:     'Rollstuhl-Van',
  wheelchair_bus:     'Rollstuhlbus',
  multi_passenger_van:'Mehrsitzer-Van',
  stretcher_vehicle:  'Liegendtransportfahrzeug',
  other:              'Sonstiges',
}

export interface Vehicle {
  id: string
  organization_id: string
  name: string
  license_plate: string
  vehicle_type: VehicleTypeName
  is_active: boolean
  seat_count: number
  wheelchair_space_count: number
  escort_seat_count: number | null
  has_ramp: boolean
  has_lift: boolean
  has_wheelchair_restraint: boolean
  supports_electric_wheelchair: boolean
  supports_stretcher_transport: boolean
  has_child_seat: boolean
  has_low_entry: boolean
  has_extra_wide_door: boolean
  has_stretcher: boolean
  has_stretcher_mount: boolean
  has_medical_equipment_storage: boolean
  has_oxygen_mount: boolean
  has_first_aid_kit: boolean
  has_hygiene_equipment: boolean
  supports_non_emergency_medical_transport: boolean
  has_transport_chair: boolean
  has_infusion_mount: boolean
  supports_two_person_crew: boolean
  patient_compartment_notes: string | null
  vehicle_length_cm: number | null
  vehicle_width_cm: number | null
  vehicle_width_with_mirrors_cm: number | null
  vehicle_height_cm: number | null
  wheelbase_cm: number | null
  turning_circle_m: number | null
  empty_weight_kg: number | null
  gross_vehicle_weight_kg: number | null
  payload_capacity_kg: number | null
  requires_large_parking_space: boolean
  suitable_for_narrow_streets: boolean
  suitable_for_underground_parking: boolean
  has_parking_assist: boolean
  access_restriction_notes: string | null
  home_base_address: string | null
  current_location_notes: string | null
  equipment_notes: string | null
  general_notes: string | null
  created_at: string
  updated_at: string
}

export type VehicleUpdate = Partial<Omit<Vehicle, 'id' | 'created_at' | 'updated_at'>>

export interface VehicleCreate extends VehicleUpdate {
  organization_id: string
  name: string
  license_plate: string
  vehicle_type: VehicleTypeName
}

// ─── Fahrer ───────────────────────────────────────────────────────────────────

export interface DriverProfile {
  id: string
  user_id: string
  organization_id: string
  display_name: string
  phone: string | null
  is_active: boolean
  can_assist_wheelchair: boolean
  can_secure_wheelchair: boolean
  can_operate_lift: boolean
  can_assist_blind_passengers: boolean
  can_assist_deaf_passengers: boolean
  can_handle_stretcher: boolean
  has_first_aid_training: boolean
  has_passenger_transport_license: boolean
  can_support_medical_transport: boolean
  has_sanitaetshelfer_training: boolean
  has_rettungshelfer_qualification: boolean
  has_rettungssanitaeter_qualification: boolean
  has_rettungsassistent_qualification: boolean
  has_notfallsanitaeter_qualification: boolean
  has_nursing_qualification: boolean
  has_medical_assistant_qualification: boolean
  has_hygiene_training: boolean
  has_infection_protection_training: boolean
  has_wheelchair_restraint_training: boolean
  has_lift_operation_training: boolean
  has_stretcher_handling_training: boolean
  has_transport_chair_training: boolean
  has_oxygen_equipment_training: boolean
  home_base_address: string | null
  availability_notes: string | null
  qualification_notes: string | null
  general_notes: string | null
  created_at: string
  updated_at: string
}

export type DriverProfileUpdate = Partial<Omit<DriverProfile, 'id' | 'user_id' | 'organization_id' | 'created_at' | 'updated_at'>>

export interface DriverProfileCreate extends DriverProfileUpdate {
  user_id: string
  organization_id: string
  display_name: string
}

// ─── Mobilitätsprofil ────────────────────────────────────────────────────────

export type WheelchairType = 'manual' | 'electric' | 'unknown'

export type AttendantType =
  | 'none'
  | 'escort_person'
  | 'second_assistant'
  | 'paramedic'
  | 'medical_professional'
  | 'unknown'

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
  requires_transport_chair: boolean
  requires_two_person_assistance: boolean
  requires_medical_transport: boolean
  brings_oxygen: boolean
  requires_oxygen_mount: boolean
  brings_medical_device: boolean
  requires_medical_equipment_storage: boolean
  requires_infusion_mount: boolean
  requires_special_positioning: boolean
  infection_or_hygiene_note: boolean
  requires_medical_attendant: boolean
  attendant_type_required: AttendantType
  medical_device_notes: string | null
  medical_transport_notes: string | null
  communication_notes: string | null
  medical_notes: string | null
  general_notes: string | null
  // Sprint 12E — Notfallinformationen
  has_epilepsy: boolean
  is_mute: boolean
  other_disabilities_notes: string | null
  known_conditions: string | null
  medication_notes: string | null
  allergy_notes: string | null
  emergency_care_notes: string | null
  what_helps_notes: string | null
  what_to_avoid_notes: string | null
  additional_emergency_notes: string | null
  body_height_cm: number | null
  body_weight_kg: number | null
  gender: string | null
  // Sprint 12E — Sichtbarkeitseinstellungen
  show_disabilities_to_driver: boolean
  show_disabilities_in_emergency: boolean
  show_medication_to_driver: boolean
  show_medication_in_emergency: boolean
  show_emergency_notes_to_driver: boolean
  show_emergency_notes_in_emergency: boolean
  show_communication_notes_to_driver: boolean
  show_communication_notes_in_emergency: boolean
  show_body_data_in_emergency: boolean
  show_contacts_to_driver: boolean
  show_contacts_in_emergency: boolean
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

// ─── Transportanfragen ───────────────────────────────────────────────────────

export type TransportRequestStatus =
  | 'draft'
  | 'requested'
  | 'assigned'
  | 'completed'
  | 'cancelled'
  | 'spontaneous_requested'
  | 'driver_declined'

export const TRANSPORT_REQUEST_STATUS_LABELS: Record<TransportRequestStatus, string> = {
  draft: 'Entwurf',
  requested: 'Anfrage gestellt',
  assigned: 'Zugewiesen',
  completed: 'Abgeschlossen',
  cancelled: 'Storniert',
  spontaneous_requested: 'Sofortfahrt angefragt',
  driver_declined: 'Vom Fahrer abgelehnt',
}

export interface RequirementSnapshot {
  transport_type_id?: string
  selected_profile_fields?: string[]
  selected_field_values?: Record<string, unknown>
  notes?: string | null
}

export interface MobilityProfileSnapshot {
  uses_wheelchair?: boolean
  wheelchair_type?: string | null
  uses_rollator?: boolean
  uses_crutches?: boolean
  needs_ramp?: boolean
  needs_lift?: boolean
  needs_escort?: boolean
  needs_entry_assistance?: boolean
  needs_door_to_door_assistance?: boolean
  needs_stretcher_transport?: boolean
  requires_wheelchair_space?: boolean
  requires_extra_time?: boolean
  requires_transport_chair?: boolean
  requires_two_person_assistance?: boolean
  requires_medical_transport?: boolean
  requires_medical_attendant?: boolean
  attendant_type_required?: string
  brings_oxygen?: boolean
  requires_oxygen_mount?: boolean
  brings_medical_device?: boolean
  requires_medical_equipment_storage?: boolean
  requires_infusion_mount?: boolean
  requires_special_positioning?: boolean
  infection_or_hygiene_note?: boolean
}

export interface TransportRequestRead {
  id: string
  requester_user_id: string
  passenger_user_id: string
  organization_id: string | null
  transport_type_id: string | null
  status: TransportRequestStatus
  pickup_address: string | null
  pickup_details: string | null
  destination_address: string | null
  destination_details: string | null
  pickup_date: string | null
  pickup_time: string | null
  arrival_time: string | null
  is_round_trip: boolean
  return_time_known: boolean
  return_pickup_time: string | null
  requirement_snapshot: RequirementSnapshot | null
  mobility_profile_snapshot: MobilityProfileSnapshot | null
  notes: string | null
  // Disposition
  assigned_vehicle_id: string | null
  assigned_driver_profile_id: string | null
  assigned_by_user_id: string | null
  assigned_at: string | null
  assignment_notes: string | null
  // Timestamps
  created_at: string
  updated_at: string
  submitted_at: string | null
  cancelled_at: string | null
  // Fahrgast-Kontaktdaten (für Dispo-Rollen, sonst null)
  passenger_display_name?: string | null
  passenger_email?: string | null
  passenger_phone?: string | null
  passenger_emergency_contact_name?: string | null
  passenger_emergency_contact_phone?: string | null
}

export interface TransportRequestListItem extends Pick<
  TransportRequestRead,
  | 'id' | 'requester_user_id' | 'passenger_user_id' | 'transport_type_id' | 'status'
  | 'pickup_address' | 'destination_address' | 'pickup_date' | 'pickup_time'
  | 'is_round_trip' | 'created_at' | 'submitted_at' | 'cancelled_at'
  | 'assigned_vehicle_id' | 'assigned_driver_profile_id' | 'assigned_at' | 'assignment_notes'
  | 'passenger_display_name' | 'passenger_phone' | 'passenger_email'
> {
  is_spontaneous: boolean
  pickup_latitude: number | null
  pickup_longitude: number | null
  last_status_label?: string | null
}

export interface TransportRequestCreate {
  passenger_user_id?: string | null
  organization_id?: string | null
  transport_type_id?: string | null
  status?: TransportRequestStatus
  pickup_address?: string | null
  pickup_details?: string | null
  destination_address?: string | null
  destination_details?: string | null
  pickup_date?: string | null
  pickup_time?: string | null
  arrival_time?: string | null
  is_round_trip?: boolean
  return_time_known?: boolean
  return_pickup_time?: string | null
  requirement_snapshot?: RequirementSnapshot | null
  mobility_profile_snapshot?: MobilityProfileSnapshot | null
  notes?: string | null
}

export type TransportRequestUpdate = Omit<TransportRequestCreate, 'passenger_user_id' | 'organization_id' | 'status'>

export interface TransportRequestAssign {
  vehicle_id: string
  driver_profile_id: string
  assignment_notes?: string | null
}

// ─── Matching ─────────────────────────────────────────────────────────────────

export type MatchStatus = 'suitable' | 'warning' | 'unsuitable'

export const MATCH_STATUS_LABELS: Record<MatchStatus, string> = {
  suitable: 'Geeignet',
  warning: 'Bedingt geeignet',
  unsuitable: 'Nicht geeignet',
}

export interface MatchingVehicleOption {
  vehicle_id: string
  name: string
  license_plate: string
  vehicle_type: string
  status: MatchStatus
  reasons: string[]
  missing_requirements: string[]
  matched_requirements: string[]
}

export interface MatchingDriverOption {
  driver_profile_id: string
  display_name: string
  status: MatchStatus
  reasons: string[]
  missing_requirements: string[]
  matched_requirements: string[]
}

export interface MatchingOptionsResponse {
  request_id: string
  vehicles: MatchingVehicleOption[]
  drivers: MatchingDriverOption[]
}

// ─── Fahrerschicht ───────────────────────────────────────────────────────────

export type ShiftStatus = 'active' | 'paused' | 'ended'

export const SHIFT_STATUS_LABELS: Record<ShiftStatus, string> = {
  active: 'Aktiv',
  paused: 'Pause',
  ended: 'Beendet',
}

export interface VehicleBrief {
  id: string
  name: string
  license_plate: string
  vehicle_type: VehicleTypeName
  wheelchair_space_count: number
  has_ramp: boolean
  has_lift: boolean
  supports_stretcher_transport: boolean
  supports_electric_wheelchair: boolean
}

export interface DriverShift {
  id: string
  driver_profile_id: string
  vehicle_id: string
  status: ShiftStatus
  started_at: string
  ended_at: string | null
  break_started_at: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface DriverShiftWithVehicle {
  shift: DriverShift
  vehicle: VehicleBrief
}

export interface DriverShiftStartRequest {
  vehicle_id?: string | null
  license_plate?: string | null
  notes?: string | null
}

export interface DriverProfileBrief {
  id: string
  display_name: string
  default_vehicle_id: string | null
}

export interface DriverDashboardContext {
  profile: DriverProfileBrief
  default_vehicle: VehicleBrief | null
  active_shift: DriverShiftWithVehicle | null
}

// ─── TransportRequestStatus (erweitert um completed) ────────────────────────

// (TransportRequestStatus ist weiter oben als Type alias definiert)
// Wir exportieren das Label für 'completed' hier
export const TRANSPORT_REQUEST_STATUS_LABELS_EXTENDED: Record<string, string> = {
  draft: 'Entwurf',
  requested: 'Anfrage gestellt',
  assigned: 'Zugewiesen',
  completed: 'Abgeschlossen',
  cancelled: 'Storniert',
}

// ─── Fahrten-Statusereignisse ─────────────────────────────────────────────────

export type RideStatusEventType =
  | 'driver_on_way'
  | 'driver_arrived'
  | 'passenger_picked_up'
  | 'ride_started'
  | 'ride_completed'
  | 'ride_cancelled'
  | 'issue_reported'

export const RIDE_STATUS_EVENT_LABELS: Record<RideStatusEventType, string> = {
  driver_on_way:       'Fahrer ist unterwegs',
  driver_arrived:      'Fahrer ist angekommen',
  passenger_picked_up: 'Fahrgast aufgenommen',
  ride_started:        'Fahrt gestartet',
  ride_completed:      'Fahrt abgeschlossen',
  ride_cancelled:      'Fahrt storniert',
  issue_reported:      'Problem gemeldet',
}

export interface RideStatusEvent {
  id: string
  transport_request_id: string
  status: RideStatusEventType
  note: string | null
  created_by_user_id: string | null
  created_at: string
}

export interface RideStatusEventCreate {
  status: RideStatusEventType
  note?: string | null
}

// ─── Benachrichtigungseinstellungen ──────────────────────────────────────────

export type NotificationEventType = RideStatusEventType

export const NOTIFICATION_EVENT_LABELS: Record<NotificationEventType, string> = {
  driver_on_way:       'Fahrer ist unterwegs',
  driver_arrived:      'Fahrer ist angekommen',
  passenger_picked_up: 'Fahrgast wurde aufgenommen',
  ride_started:        'Fahrt gestartet',
  ride_completed:      'Fahrt abgeschlossen',
  ride_cancelled:      'Fahrt storniert',
  issue_reported:      'Problem gemeldet',
}

export interface NotificationPreference {
  id: string
  mobility_profile_id: string
  event_type: NotificationEventType
  notify_trusted_persons: boolean
  channel_in_app: boolean
  channel_email: boolean
  channel_sms: boolean
  created_at: string
  updated_at: string
}

export interface NotificationPreferenceUpsert {
  event_type: NotificationEventType
  notify_trusted_persons: boolean
  channel_in_app: boolean
  channel_email: boolean
  channel_sms: boolean
}

// ─── Spontane Fahrten (Sprint 12B) ───────────────────────────────────────────

export interface SpontaneousRideMatchRequest {
  pickup_latitude: number
  pickup_longitude: number
  passenger_user_id?: string | null
}

export interface SpontaneousRideMatchResult {
  driver_id: string
  driver_display_name: string
  vehicle_id: string
  vehicle_label: string
  vehicle_type: string
  vehicle_latitude: number
  vehicle_longitude: number
  distance_km: number
  estimated_arrival_minutes: number
  matched_capabilities: string[]
  can_accept_now: boolean
}

// ─── Spontane Fahrten (Sprint 12C) ───────────────────────────────────────────

export interface SpontaneousRideBookRequest {
  driver_id: string
  vehicle_id: string
  pickup_latitude: number
  pickup_longitude: number
  pickup_address?: string | null
  destination_address?: string | null
  passenger_user_id?: string | null
}

export interface SpontaneousRideBookResponse {
  request_id: string
  status: string
  driver_display_name: string
  vehicle_label: string
  estimated_arrival_minutes: number
}

export interface SpontaneousRideRequestItem {
  id: string
  passenger_user_id: string
  passenger_display_name: string | null
  pickup_latitude: number
  pickup_longitude: number
  pickup_address: string | null
  destination_address: string | null
  status: string
  created_at: string
}

// ─── Spontane Fahrten (Sprint 12D) ───────────────────────────────────────────

export interface DriverLocationUpdate {
  latitude: number
  longitude: number
  transport_request_id?: string | null
}

export interface SpontaneousRideTracking {
  transport_request_id: string
  status: string
  can_track: boolean
  driver_id: string | null
  driver_display_name: string | null
  vehicle_id: string | null
  vehicle_label: string | null
  driver_latitude: number | null
  driver_longitude: number | null
  pickup_latitude: number | null
  pickup_longitude: number | null
  pickup_address: string | null
  destination_address: string | null
  distance_km: number | null
  estimated_arrival_minutes: number | null
  last_location_update: string | null
  ride_status_label: string
}

// ─── Geocoding ───────────────────────────────────────────────────────────────

export interface ReverseGeocodeResponse {
  formatted_address: string | null
  street: string | null
  house_number: string | null
  postal_code: string | null
  city: string | null
  precision: string
  source: string
  message: string | null
}

// ─── Kontakte (Sprint 12E) ────────────────────────────────────────────────────

export type ContactType =
  | 'emergency_contact'
  | 'trusted_person'
  | 'caregiver'
  | 'school'
  | 'workshop'
  | 'daycare'
  | 'doctor'
  | 'nursing_service'
  | 'parent'
  | 'other'

export const CONTACT_TYPE_LABELS: Record<ContactType, string> = {
  emergency_contact: 'Notfallkontakt',
  trusted_person:    'Vertrauensperson',
  caregiver:         'Pflegeperson',
  school:            'Schule',
  workshop:          'Werkstatt / Beschäftigung',
  daycare:           'Tagesstätte',
  doctor:            'Arzt / Therapeut',
  nursing_service:   'Pflegedienst',
  parent:            'Elternteil / Familie',
  other:             'Sonstige',
}

export interface PassengerContact {
  id: string
  mobility_profile_id: string
  name: string
  phone_number: string | null
  role_label: string | null
  contact_type: ContactType
  note: string | null
  is_emergency_contact: boolean
  visible_to_driver: boolean
  visible_in_emergency: boolean
  callable_in_emergency: boolean
  priority: number
  created_at: string
  updated_at: string
}

export interface PassengerContactCreate {
  name: string
  phone_number: string
  role_label?: string | null
  contact_type?: ContactType
  note?: string | null
  is_emergency_contact?: boolean
  visible_to_driver?: boolean
  visible_in_emergency?: boolean
  callable_in_emergency?: boolean
  priority?: number
}

export interface PassengerContactUpdate {
  name?: string
  phone_number?: string
  role_label?: string | null
  contact_type?: ContactType
  note?: string | null
  is_emergency_contact?: boolean
  visible_to_driver?: boolean
  visible_in_emergency?: boolean
  callable_in_emergency?: boolean
  priority?: number
}

// ─── Notfallakte (Sprint 12E) ─────────────────────────────────────────────────

export interface EmergencyGlossaryEntry {
  key: string
  title: string
  immediate_action_title: string
  first_aid_steps: string[]
  do_not_do: string[]
  call_112_when: string[]
  call_112_script_hint: string | null
  source_note: string
}

export interface EmergencyContactItem {
  id: string
  name: string
  phone_number: string | null
  role_label: string | null
  contact_type: string
  is_emergency_contact: boolean
  callable_in_emergency: boolean
  priority: number
}

export interface EmergencyFileResponse {
  transport_request_id: string
  passenger_display_name: string | null
  emergency_mode: boolean
  disabilities_visible: boolean
  has_epilepsy: boolean
  is_mute: boolean
  is_deaf_or_hard_of_hearing: boolean
  uses_wheelchair: boolean
  is_blind_or_visually_impaired: boolean
  other_disabilities_notes: string | null
  known_conditions: string | null
  medication_visible: boolean
  medication_notes: string | null
  allergy_notes: string | null
  emergency_notes_visible: boolean
  emergency_care_notes: string | null
  what_helps_notes: string | null
  what_to_avoid_notes: string | null
  additional_emergency_notes: string | null
  communication_notes_visible: boolean
  communication_notes: string | null
  body_data_visible: boolean
  body_height_cm: number | null
  body_weight_kg: number | null
  gender: string | null
  visible_contacts: EmergencyContactItem[]
  primary_emergency_contact: EmergencyContactItem | null
  has_callable_emergency_contact: boolean
  emergency_summary_for_112: string
  current_location_label: string | null
  pickup_latitude: number | null
  pickup_longitude: number | null
  glossary_entries: EmergencyGlossaryEntry[]
  medical_disclaimer: string
}

// ─── Gespeicherte Fahrgast-Adressen ──────────────────────────────────────────

export type AddressType = 'home' | 'school' | 'work_workshop' | 'daycare' | 'doctor' | 'other'

export const ADDRESS_TYPE_LABELS: Record<AddressType, string> = {
  home: 'Zuhause',
  school: 'Schule',
  work_workshop: 'Arbeit / Werkstatt',
  daycare: 'Tagesstätte / Tagespflege',
  doctor: 'Arztpraxis',
  other: 'Sonstiges',
}

export interface PassengerSavedAddress {
  id: string
  mobility_profile_id: string
  label: string
  address_type: AddressType
  street_address: string
  postal_code: string
  city: string
  additional_info: string | null
  note: string | null
  is_default_pickup: boolean
  is_default_destination: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PassengerSavedAddressCreate {
  label: string
  address_type?: AddressType
  street_address: string
  postal_code: string
  city: string
  additional_info?: string | null
  note?: string | null
  is_default_pickup?: boolean
  is_default_destination?: boolean
  is_active?: boolean
}

export interface PassengerSavedAddressUpdate {
  label?: string
  address_type?: AddressType
  street_address?: string
  postal_code?: string
  city?: string
  additional_info?: string | null
  note?: string | null
  is_default_pickup?: boolean
  is_default_destination?: boolean
  is_active?: boolean
}

// ─── Transporttypen ──────────────────────────────────────────────────────────

export interface TransportType {
  id: string
  label: string
  description: string
  warning?: string
  icon_key: string
  suggested_profile_fields: string[]
  suggested_field_values?: Record<string, unknown>
  suggested_vehicle_requirements: string[]
  suggested_driver_requirements: string[]
  preset_controlled_profile_fields: string[]
}
