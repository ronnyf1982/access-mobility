"""
Zentrale Konfiguration der Transporttyp-Schnellauswahl-Vorlagen.

Presets sind Vorschläge für Laien — sie setzen typische Felder vor,
die der Nutzer danach individuell anpassen kann. Das Matching selbst
nutzt die gespeicherten Detailfelder, nicht den Preset-Namen.

Späterer Ausbau: admin-konfigurierbar oder DB-basiert.
"""

from typing import Any

# Felder, die von irgendeinem Preset gesetzt werden können.
# Beim Wechsel der Schnellauswahl werden exakt diese Felder zurückgesetzt.
# attendant_type_required ist kein bool — wird separat auf "none" zurückgesetzt.
PRESET_CONTROLLED_PROFILE_FIELDS: list[str] = [
    "needs_stretcher_transport",
    "requires_transport_chair",
    "requires_two_person_assistance",
    "requires_medical_transport",
    "brings_oxygen",
    "requires_oxygen_mount",
    "brings_medical_device",
    "requires_medical_equipment_storage",
    "requires_infusion_mount",
    "requires_special_positioning",
    "infection_or_hygiene_note",
    "requires_medical_attendant",
]

TRANSPORT_PRESETS: list[dict[str, Any]] = [
    {
        "id": "accessible_ride",
        "label": "Barrierefreie Fahrt",
        "description": (
            "Standard-Fahrt mit barrierefreiem Fahrzeug. "
            "Kein medizinisches Personal erforderlich."
        ),
        "icon_key": "car_accessible",
        # Nur allgemeine Mobilitätsfelder — keine medizinischen Detailfelder.
        "suggested_profile_fields": [
            "uses_wheelchair",
            "uses_rollator",
            "uses_crutches",
            "needs_ramp",
            "needs_lift",
            "needs_entry_assistance",
            "needs_door_to_door_assistance",
        ],
        "suggested_field_values": {},
        "suggested_vehicle_requirements": [
            "has_ramp",
            "has_lift",
            "has_wheelchair_restraint",
            "has_low_entry",
            "has_extra_wide_door",
        ],
        "suggested_driver_requirements": [
            "can_assist_wheelchair",
            "can_secure_wheelchair",
            "can_operate_lift",
        ],
        "preset_controlled_profile_fields": PRESET_CONTROLLED_PROFILE_FIELDS,
    },
    {
        "id": "patient_ride_no_medical_care",
        "label": "Patientenfahrt (ohne Betreuung)",
        "description": (
            "Geplanter Transport eines Patienten ohne medizinische Betreuung "
            "während der Fahrt."
        ),
        "icon_key": "patient_no_care",
        # Kein Liegendtransport, keine medizinische Begleitung, keine med. Geräte.
        "suggested_profile_fields": [
            "requires_wheelchair_space",
            "needs_entry_assistance",
            "requires_extra_time",
        ],
        "suggested_field_values": {},
        "suggested_vehicle_requirements": [
            "has_ramp",
            "has_low_entry",
            "has_first_aid_kit",
        ],
        "suggested_driver_requirements": [
            "has_passenger_transport_license",
            "can_assist_wheelchair",
        ],
        "preset_controlled_profile_fields": PRESET_CONTROLLED_PROFILE_FIELDS,
    },
    {
        "id": "stretcher_ride",
        "label": "Liegendtransport",
        "description": (
            "Fahrgast kann nicht sitzen. "
            "Transport erfolgt ausschließlich liegend."
        ),
        "warning": (
            "Nur für qualifizierte Fahrzeuge mit fest eingebauter Transportliege "
            "und entsprechend geschulten Fahrern."
        ),
        "icon_key": "stretcher",
        # Liegend und Lagerung — aber keine automatische med. Begleitung oder Geräte.
        "suggested_profile_fields": [
            "needs_stretcher_transport",
            "requires_special_positioning",
        ],
        "suggested_field_values": {},
        "suggested_vehicle_requirements": [
            "has_stretcher",
            "has_stretcher_mount",
            "supports_stretcher_transport",
            "has_first_aid_kit",
        ],
        "suggested_driver_requirements": [
            "can_handle_stretcher",
            "has_stretcher_handling_training",
            "has_first_aid_training",
        ],
        "preset_controlled_profile_fields": PRESET_CONTROLLED_PROFILE_FIELDS,
    },
    {
        "id": "qualified_medical_transport",
        "label": "Qualifizierter Krankentransport (KTP)",
        "description": (
            "Transport mit medizinisch geschultem Personal. "
            "Kein Notfalltransport, kein Rettungsdienst."
        ),
        "warning": (
            "Dieser Transporttyp erfordert spezifische Fahrzeugausstattung und "
            "Fahrerqualifikationen gemäß KTP-Standard. Kein Ersatz für Notfallrettung."
        ),
        "icon_key": "medical_transport",
        # Nur Basismarkierung: med. Transport + Begleitung erforderlich.
        # Sauerstoff, Geräte, Hygiene abhängig vom konkreten Fahrgast — nicht auto-setzen.
        "suggested_profile_fields": [
            "requires_medical_transport",
            "requires_medical_attendant",
        ],
        "suggested_field_values": {
            "attendant_type_required": "unknown",
        },
        "suggested_vehicle_requirements": [
            "supports_non_emergency_medical_transport",
            "has_medical_equipment_storage",
            "has_first_aid_kit",
            "has_hygiene_equipment",
        ],
        "suggested_driver_requirements": [
            "can_support_medical_transport",
            "has_rettungssanitaeter_qualification",
            "has_hygiene_training",
        ],
        "preset_controlled_profile_fields": PRESET_CONTROLLED_PROFILE_FIELDS,
    },
    {
        "id": "recurring_school_work_facility_route",
        "label": "Wiederkehrende Schul-/Arbeits-/Einrichtungsfahrt",
        "description": (
            "Regelmäßiger Transport zu Schule, Werkstatt, Tagesstätte "
            "oder ähnlichen Einrichtungen."
        ),
        "icon_key": "recurring_route",
        # Keine medizinischen Felder — dient dem späteren Touren-/Buchungsmodul.
        "suggested_profile_fields": [
            "uses_wheelchair",
            "uses_rollator",
            "needs_escort",
            "needs_entry_assistance",
            "needs_door_to_door_assistance",
            "requires_extra_time",
        ],
        "suggested_field_values": {},
        "suggested_vehicle_requirements": [
            "has_ramp",
            "has_lift",
            "has_wheelchair_restraint",
            "has_child_seat",
        ],
        "suggested_driver_requirements": [
            "can_assist_wheelchair",
            "can_secure_wheelchair",
            "has_passenger_transport_license",
        ],
        "preset_controlled_profile_fields": PRESET_CONTROLLED_PROFILE_FIELDS,
    },
]
