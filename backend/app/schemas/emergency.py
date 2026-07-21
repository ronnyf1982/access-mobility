import uuid

from pydantic import BaseModel


class EmergencyGlossaryEntry(BaseModel):
    key: str
    title: str
    immediate_action_title: str
    first_aid_steps: list[str]
    do_not_do: list[str]
    call_112_when: list[str]
    call_112_script_hint: str | None
    source_note: str


class EmergencyContactItem(BaseModel):
    id: uuid.UUID
    name: str
    phone_number: str | None
    role_label: str | None
    contact_type: str
    is_emergency_contact: bool
    callable_in_emergency: bool
    priority: int


class EmergencyFileResponse(BaseModel):
    transport_request_id: uuid.UUID
    passenger_display_name: str | None
    emergency_mode: bool

    # Behinderungen / Erkrankungen
    disabilities_visible: bool
    has_epilepsy: bool
    is_mute: bool
    is_deaf_or_hard_of_hearing: bool
    uses_wheelchair: bool
    is_blind_or_visually_impaired: bool
    other_disabilities_notes: str | None
    known_conditions: str | None

    # Medikamente
    medication_visible: bool
    medication_notes: str | None
    allergy_notes: str | None

    # Notfallhinweise
    emergency_notes_visible: bool
    emergency_care_notes: str | None
    what_helps_notes: str | None
    what_to_avoid_notes: str | None
    additional_emergency_notes: str | None

    # Kommunikation
    communication_notes_visible: bool
    communication_notes: str | None

    # Körperdaten
    body_data_visible: bool
    body_height_cm: int | None
    body_weight_kg: int | None
    gender: str | None

    # Kontakte
    visible_contacts: list[EmergencyContactItem]
    primary_emergency_contact: EmergencyContactItem | None
    has_callable_emergency_contact: bool

    # Standort + 112-Zusammenfassung
    emergency_summary_for_112: str
    current_location_label: str | None
    pickup_latitude: float | None
    pickup_longitude: float | None

    # Ersthelfer-Glossar
    glossary_entries: list[EmergencyGlossaryEntry]

    medical_disclaimer: str
