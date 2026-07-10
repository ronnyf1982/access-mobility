from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.crud_mobility_profile import get_or_create, upsert
from app.db.session import get_db
from app.models.user import User
from app.schemas.mobility_profile import MobilityProfilePublic, MobilityProfileUpdate

router = APIRouter(prefix="/mobility-profile", tags=["mobility-profile"])

# ---------------------------------------------------------------------------
# Optionsliste — für konsistente Labels / Icons im Frontend
# ---------------------------------------------------------------------------
_WHEELCHAIR_TYPE_OPTIONS = [
    {"value": "manual", "label": "Manueller Rollstuhl"},
    {"value": "electric", "label": "Elektrorollstuhl"},
    {"value": "unknown", "label": "Rollstuhl-Typ unbekannt"},
]

_MOBILITY_NEED_OPTIONS = [
    {
        "key": "uses_wheelchair",
        "label": "Rollstuhl",
        "icon": "pi-circle-fill",
        "description": "Ich fahre mit einem Rollstuhl und benötige einen gesicherten Stellplatz im Fahrzeug.",
    },
    {
        "key": "uses_rollator",
        "label": "Rollator",
        "icon": "pi-arrows-h",
        "description": "Ich nutze einen Rollator. Er wird ggf. im Fahrzeug verstaut.",
    },
    {
        "key": "uses_crutches",
        "label": "Krücken / Gehstützen",
        "icon": "pi-arrow-up",
        "description": "Ich benutze Krücken oder Gehstützen. Eine Einstiegshilfe ist hilfreich.",
    },
    {
        "key": "is_blind_or_visually_impaired",
        "label": "Blind / sehbehindert",
        "icon": "pi-eye-slash",
        "description": "Der Fahrer / die Fahrerin holt mich an der Tür ab und führt mich verbal.",
    },
    {
        "key": "is_deaf_or_hard_of_hearing",
        "label": "Gehörlos / schwerhörig",
        "icon": "pi-volume-off",
        "description": "Bitte schriftlich oder per Geste kommunizieren. Kein Signalhorn.",
    },
    {
        "key": "needs_escort",
        "label": "Begleitperson",
        "icon": "pi-users",
        "description": "Eine Begleitperson fährt mit. Ein zusätzlicher Begleitplatz wird benötigt.",
    },
    {
        "key": "needs_entry_assistance",
        "label": "Hilfe beim Ein- und Aussteigen",
        "icon": "pi-arrow-circle-up",
        "description": "Der Fahrer / die Fahrerin unterstützt mich beim Einsteigen und Aussteigen.",
    },
    {
        "key": "needs_door_to_door_assistance",
        "label": "Tür-zu-Tür-Begleitung",
        "icon": "pi-map-marker",
        "description": "Ich werde von Haustür zu Haustür begleitet, nicht nur zum Fahrzeug.",
    },
    {
        "key": "needs_ramp",
        "label": "Rampe erforderlich",
        "icon": "pi-sort-amount-up-alt",
        "description": "Das Fahrzeug muss über eine Auffahrrampe für Rollstühle verfügen.",
    },
    {
        "key": "needs_lift",
        "label": "Lift / Hebebühne",
        "icon": "pi-chevron-circle-up",
        "description": "Das Fahrzeug muss über eine elektrische Hebebühne verfügen.",
    },
    {
        "key": "needs_stretcher_transport",
        "label": "Liegendtransport",
        "icon": "pi-minus",
        "description": "Ich kann nicht sitzen. Der Transport muss liegend erfolgen.",
    },
]

_MEDICAL_DETAIL_OPTIONS = [
    {
        "key": "requires_transport_chair",
        "label": "Tragestuhl erforderlich",
        "icon": "pi-arrow-circle-up",
        "description": "Ich benötige einen Tragestuhl (z. B. für Treppenhäuser ohne Aufzug).",
    },
    {
        "key": "requires_two_person_assistance",
        "label": "Zweimann-Begleitung",
        "icon": "pi-users",
        "description": "Für den Transfer oder Transport sind zwei Personen erforderlich.",
    },
    {
        "key": "requires_medical_transport",
        "label": "Qualifizierter Krankentransport",
        "icon": "pi-shield",
        "description": "Ich benötige einen qualifizierten Krankentransport (KTP) mit medizinisch geschultem Personal.",
    },
    {
        "key": "brings_oxygen",
        "label": "Eigenes Sauerstoffgerät",
        "icon": "pi-circle",
        "description": "Ich bringe ein mobiles Sauerstoffgerät mit.",
    },
    {
        "key": "requires_oxygen_mount",
        "label": "Sauerstoffhalterung benötigt",
        "icon": "pi-sort-amount-up-alt",
        "description": "Das Fahrzeug muss über eine Halterung für Sauerstoffgeräte verfügen.",
    },
    {
        "key": "brings_medical_device",
        "label": "Eigenes Medizingerät",
        "icon": "pi-inbox",
        "description": "Ich transportiere ein medizinisches Gerät (Pumpe, Monitor o. ä.).",
    },
    {
        "key": "requires_medical_equipment_storage",
        "label": "Med. Stauraum benötigt",
        "icon": "pi-inbox",
        "description": "Das Fahrzeug muss Stauraum für medizinisches Equipment bieten.",
    },
    {
        "key": "requires_infusion_mount",
        "label": "Infusionsständer benötigt",
        "icon": "pi-sort-amount-up-alt",
        "description": "Während der Fahrt läuft eine Infusion — Halterung im Fahrzeug erforderlich.",
    },
    {
        "key": "requires_special_positioning",
        "label": "Spezielle Lagerung",
        "icon": "pi-minus",
        "description": "Ich benötige eine besondere Lagerungsposition während der Fahrt.",
    },
    {
        "key": "infection_or_hygiene_note",
        "label": "Hygiene- / Infektionshinweis",
        "icon": "pi-shield",
        "description": "Es liegt ein Hygiene- oder Infektionsschutzhinweis vor (z. B. Isolierpflicht).",
    },
    {
        "key": "requires_medical_attendant",
        "label": "Med. Begleitung erforderlich",
        "icon": "pi-heart",
        "description": "Für die Fahrt ist eine medizinisch qualifizierte Begleitperson notwendig.",
    },
]

_ATTENDANT_TYPE_OPTIONS = [
    {"value": "none", "label": "Keine medizinische Begleitung"},
    {"value": "escort_person", "label": "Begleitperson (keine med. Qualifikation)"},
    {"value": "second_assistant", "label": "Zweite Hilfsperson (z. B. für Transfer)"},
    {"value": "paramedic", "label": "Rettungssanitäter / -helfer"},
    {"value": "medical_professional", "label": "Pflegefachkraft / Arzt"},
    {"value": "unknown", "label": "Unbekannt / bitte klären"},
]


@router.get("/options")
def get_options() -> dict:
    """Gibt verfügbare Optionen und Labels zurück — ohne Auth nutzbar."""
    return {
        "wheelchair_types": _WHEELCHAIR_TYPE_OPTIONS,
        "mobility_needs": _MOBILITY_NEED_OPTIONS,
        "medical_detail_options": _MEDICAL_DETAIL_OPTIONS,
        "attendant_type_options": _ATTENDANT_TYPE_OPTIONS,
    }


@router.get("/me", response_model=MobilityProfilePublic)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MobilityProfilePublic:
    """Gibt das eigene Mobilitätsprofil zurück.

    Falls noch keines existiert, wird automatisch ein leeres Profil angelegt.
    Hinweis: Nur Nutzer mit Rolle passenger haben fachlich ein Profil.
    RBAC-Einschränkung nach Rolle folgt in Sprint 6.
    """
    profile, created = get_or_create(db, current_user.id)
    if created:
        db.commit()
    return MobilityProfilePublic.model_validate(profile)


@router.put("/me", response_model=MobilityProfilePublic)
def update_my_profile(
    payload: MobilityProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MobilityProfilePublic:
    """Erstellt oder aktualisiert das eigene Mobilitätsprofil.

    Partielle Updates: nur gesendete Felder werden geschrieben.
    Hinweis: RBAC-Einschränkung nach Rolle folgt in Sprint 6.
    """
    profile = upsert(db, current_user.id, payload)
    db.commit()
    return MobilityProfilePublic.model_validate(profile)
