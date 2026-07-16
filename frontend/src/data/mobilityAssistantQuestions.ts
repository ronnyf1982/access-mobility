import type { MobilityProfileUpdate } from '@/types'

export type AnswerValue = 'yes' | 'no' | 'unknown' | 'skip'

export interface FieldMapping {
  field: keyof MobilityProfileUpdate | 'voice_mode_enabled'
  model: 'mobilityProfile' | 'user'
  value: boolean
}

export interface AssistantQuestion {
  id: string
  text: string
  hint?: string
  // Fields to set when answered "yes"
  yesFields: FieldMapping[]
  // Optional: note shown in summary when no real field exists
  missingFieldNote?: string
}

// Only maps to fields that exist in the current MobilityProfile model.
// Missing fields are documented below.
export const MOBILITY_ASSISTANT_QUESTIONS: AssistantQuestion[] = [
  {
    id: 'voice_mode',
    text: 'Möchten Sie die App hauptsächlich per Sprache bedienen?',
    hint: 'Sie können diese Einstellung jederzeit in den Einstellungen ändern.',
    yesFields: [
      { field: 'voice_mode_enabled', model: 'user', value: true },
    ],
  },
  {
    id: 'blind',
    text: 'Sind Sie blind oder stark sehbehindert?',
    hint: 'Der Fahrer wird Sie an der Haustür abholen und verbal begleiten.',
    yesFields: [
      { field: 'is_blind_or_visually_impaired', model: 'mobilityProfile', value: true },
    ],
    // Fehlende Felder: needs_screen_reader_optimized_ui, prefers_voice_guidance
    // → Roadmap: Sprint 10+
  },
  {
    id: 'entry_assistance',
    text: 'Benötigen Sie Hilfe beim Ein- oder Aussteigen?',
    hint: 'Der Fahrer unterstützt Sie beim Einsteigen und Aussteigen.',
    yesFields: [
      { field: 'needs_entry_assistance', model: 'mobilityProfile', value: true },
    ],
    // Fehlende Felder: requires_driver_assistance, needs_boarding_assistance
    // → bestehend abgedeckt durch needs_entry_assistance
  },
  {
    id: 'door_to_door',
    text: 'Soll der Fahrer Sie an der Haustür abholen und dorthin bringen?',
    hint: 'Tür-zu-Tür-Begleitung von und bis zur Haustür.',
    yesFields: [
      { field: 'needs_door_to_door_assistance', model: 'mobilityProfile', value: true },
    ],
  },
  {
    id: 'wait_alone',
    text: 'Dürfen Sie alleine auf das Fahrzeug warten?',
    hint: 'Wenn nein, wird im Auftrag ein entsprechender Hinweis für den Fahrer hinterlegt.',
    yesFields: [],
    // Kein passendes Feld im Modell. Fehlende Felder: may_not_wait_alone
    // → Roadmap: Kleines Modell-Update in späterem Sprint
    missingFieldNote: 'Hinweis „Bitte nicht alleine warten lassen" — Feld noch nicht im Modell, folgt in späterer Version.',
  },
  {
    id: 'wheelchair',
    text: 'Nutzen Sie einen Rollstuhl?',
    hint: 'Ein gesicherter Rollstuhlplatz wird im Fahrzeug reserviert.',
    yesFields: [
      { field: 'uses_wheelchair', model: 'mobilityProfile', value: true },
      { field: 'requires_wheelchair_space', model: 'mobilityProfile', value: true },
    ],
  },
  {
    id: 'rollator',
    text: 'Nutzen Sie einen Rollator oder eine Gehhilfe (Krücken)?',
    hint: 'Rollator oder Krücken werden im Fahrzeug verstaut.',
    yesFields: [
      { field: 'uses_rollator', model: 'mobilityProfile', value: true },
    ],
    // Fehlende Felder: uses_walker, uses_mobility_aid — abgedeckt durch uses_rollator
  },
  {
    id: 'stretcher',
    text: 'Müssen Sie liegend transportiert werden?',
    hint: 'Ein Liegendtransport-Fahrzeug wird zugewiesen.',
    yesFields: [
      { field: 'needs_stretcher_transport', model: 'mobilityProfile', value: true },
    ],
  },
  {
    id: 'oxygen_or_medical',
    text: 'Führen Sie Sauerstoff oder medizinische Geräte mit?',
    hint: 'Das Fahrzeug muss entsprechende Halterungen oder Lagerungsmöglichkeiten haben.',
    yesFields: [
      { field: 'brings_oxygen', model: 'mobilityProfile', value: true },
      { field: 'brings_medical_device', model: 'mobilityProfile', value: true },
    ],
    // Fehlende Felder: carries_oxygen, carries_medical_equipment
    // → abgedeckt durch brings_oxygen / brings_medical_device
  },
  {
    id: 'companion',
    text: 'Soll eine Begleitperson mitfahren?',
    hint: 'Ein zusätzlicher Sitzplatz für eine Begleitperson wird berücksichtigt.',
    yesFields: [
      { field: 'needs_escort', model: 'mobilityProfile', value: true },
    ],
    // Fehlende Felder: has_companion, companion_required
    // → abgedeckt durch needs_escort
  },
]

// Human-readable labels for the summary view
export const FIELD_LABELS: Partial<Record<keyof MobilityProfileUpdate | 'voice_mode_enabled', string>> = {
  voice_mode_enabled: 'Sprachführung aktivieren',
  is_blind_or_visually_impaired: 'Blind / stark sehbehindert',
  needs_entry_assistance: 'Hilfe beim Ein-/Aussteigen',
  needs_door_to_door_assistance: 'Tür-zu-Tür-Begleitung',
  uses_wheelchair: 'Rollstuhl',
  requires_wheelchair_space: 'Rollstuhlplatz im Fahrzeug',
  uses_rollator: 'Rollator / Gehhilfe',
  needs_stretcher_transport: 'Liegendtransport',
  brings_oxygen: 'Sauerstoff mitgeführt',
  brings_medical_device: 'Medizinisches Gerät mitgeführt',
  needs_escort: 'Begleitperson fährt mit',
}
