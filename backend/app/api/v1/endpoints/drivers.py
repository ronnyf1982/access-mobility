import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.driver_profile import DriverProfileCreate, DriverProfilePublic, DriverProfileUpdate

router = APIRouter(prefix="/drivers", tags=["drivers"])

QUALIFICATION_OPTIONS = [
    {
        "key": "can_assist_wheelchair",
        "label": "Rollstuhl begleiten",
        "icon": "pi-circle-fill",
        "description": "Fahrer kann Fahrgäste mit Rollstuhl unterstützen und begleiten",
    },
    {
        "key": "can_secure_wheelchair",
        "label": "Rollstuhl sichern",
        "icon": "pi-lock",
        "description": "Fahrer kann Rollstühle mit Gurtsystem korrekt sichern",
    },
    {
        "key": "can_operate_lift",
        "label": "Lift bedienen",
        "icon": "pi-chevron-circle-up",
        "description": "Fahrer ist geschult im Bedienen elektrischer Hebebühnen",
    },
    {
        "key": "can_assist_blind_passengers",
        "label": "Blinde Fahrgäste unterstützen",
        "icon": "pi-eye-slash",
        "description": "Fahrer holt Fahrgäste an der Haustür ab und begleitet sie verbal",
    },
    {
        "key": "can_assist_deaf_passengers",
        "label": "Gehörlose Fahrgäste unterstützen",
        "icon": "pi-volume-off",
        "description": "Fahrer kommuniziert schriftlich oder per Geste",
    },
    {
        "key": "can_handle_stretcher",
        "label": "Liegendtransport begleiten",
        "icon": "pi-minus",
        "description": "Fahrer ist für Liegendtransporte und Transportliegen geschult",
    },
    {
        "key": "has_first_aid_training",
        "label": "Erste-Hilfe-Schulung",
        "icon": "pi-heart",
        "description": "Gültige Erste-Hilfe-Ausbildung vorhanden",
    },
    {
        "key": "has_passenger_transport_license",
        "label": "Personenbeförderungsschein",
        "icon": "pi-id-card",
        "description": "Gültiger Personenbeförderungsschein (P-Schein) vorhanden",
    },
    {
        "key": "can_support_medical_transport",
        "label": "Med. Krankentransport",
        "icon": "pi-star",
        "description": "Fahrer ist qualifiziert fuer qualifizierten Krankentransport (KTP, nicht Rettungsdienst)",
    },
]

MEDICAL_QUALIFICATION_OPTIONS = [
    {
        "key": "has_sanitaetshelfer_training",
        "label": "Sanitätshelfer",
        "icon": "pi-heart",
        "description": "Sanitätshelfer-Ausbildung (SanH) abgeschlossen",
    },
    {
        "key": "has_rettungshelfer_qualification",
        "label": "Rettungshelfer",
        "icon": "pi-heart-fill",
        "description": "Rettungshelfer-Qualifikation (RH) vorhanden",
    },
    {
        "key": "has_rettungssanitaeter_qualification",
        "label": "Rettungssanitäter",
        "icon": "pi-shield",
        "description": "Rettungssanitäter-Qualifikation (RettSan / RS) vorhanden",
    },
    {
        "key": "has_rettungsassistent_qualification",
        "label": "Rettungsassistent",
        "icon": "pi-shield",
        "description": "Rettungsassistent-Qualifikation (RA) vorhanden",
    },
    {
        "key": "has_notfallsanitaeter_qualification",
        "label": "Notfallsanitäter",
        "icon": "pi-star",
        "description": "Notfallsanitäter-Qualifikation (NotSan) vorhanden — höchste nichtärztliche Qualifikation",
    },
    {
        "key": "has_nursing_qualification",
        "label": "Pflegefachkraft",
        "icon": "pi-users",
        "description": "Examinierte Pflegefachkraft (Gesundheits- und Krankenpflege o. ä.)",
    },
    {
        "key": "has_medical_assistant_qualification",
        "label": "Med. Fachangestellte/r",
        "icon": "pi-id-card",
        "description": "Medizinische Fachangestellte/r (MFA) oder vergleichbare Qualifikation",
    },
]

TECHNICAL_TRAINING_OPTIONS = [
    {
        "key": "has_hygiene_training",
        "label": "Hygieneschulung",
        "icon": "pi-shield",
        "description": "Schulung im Bereich Hygiene und Infektionsschutz absolviert",
    },
    {
        "key": "has_infection_protection_training",
        "label": "Infektionsschutz",
        "icon": "pi-ban",
        "description": "Spezifische Schulung zum Infektionsschutz nach IfSG",
    },
    {
        "key": "has_wheelchair_restraint_training",
        "label": "Rollstuhl-Sicherung (zertifiziert)",
        "icon": "pi-lock",
        "description": "Zertifizierte Schulung zur Rollstuhlsicherung (z. B. REHA-Stuhl-System)",
    },
    {
        "key": "has_lift_operation_training",
        "label": "Liftsystem-Bedienung",
        "icon": "pi-chevron-circle-up",
        "description": "Schulung im Bedienen elektrischer Hebebühnen und Liftsysteme",
    },
    {
        "key": "has_stretcher_handling_training",
        "label": "Liegendtransport (Trage)",
        "icon": "pi-minus",
        "description": "Schulung in Ergonomie und sicherem Umgang mit Krankentragen / Bahren",
    },
    {
        "key": "has_transport_chair_training",
        "label": "Tragestuhl-Bedienung",
        "icon": "pi-arrow-circle-up",
        "description": "Schulung im Einsatz von Tragestühlen in engen Treppenhäusern",
    },
    {
        "key": "has_oxygen_equipment_training",
        "label": "Sauerstoffgeräte",
        "icon": "pi-circle",
        "description": "Schulung im Umgang mit mobilen Sauerstoffgeräten und -halterungen",
    },
]


@router.get("/options")
def get_options():
    return {
        "qualification_options": QUALIFICATION_OPTIONS,
        "medical_qualification_options": MEDICAL_QUALIFICATION_OPTIONS,
        "technical_training_options": TECHNICAL_TRAINING_OPTIONS,
    }


@router.get("", response_model=list[DriverProfilePublic])
def list_drivers(
    organization_id: Optional[uuid.UUID] = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    if organization_id:
        return crud.crud_driver_profile.get_by_org(db, organization_id, active_only=active_only)
    return crud.crud_driver_profile.get_all(db, active_only=active_only)


@router.post("", response_model=DriverProfilePublic, status_code=status.HTTP_201_CREATED)
def create_driver(
    payload: DriverProfileCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    driver = crud.crud_driver_profile.create(db, payload)
    db.commit()
    db.refresh(driver)
    return driver


@router.get("/{driver_id}", response_model=DriverProfilePublic)
def get_driver(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    driver = crud.crud_driver_profile.get_by_id(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Fahrerprofil nicht gefunden")
    return driver


@router.put("/{driver_id}", response_model=DriverProfilePublic)
def update_driver(
    driver_id: uuid.UUID,
    payload: DriverProfileUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    driver = crud.crud_driver_profile.get_by_id(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Fahrerprofil nicht gefunden")
    driver = crud.crud_driver_profile.update(db, driver, payload)
    db.commit()
    db.refresh(driver)
    return driver


@router.delete("/{driver_id}", response_model=DriverProfilePublic)
def deactivate_driver(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    driver = crud.crud_driver_profile.get_by_id(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Fahrerprofil nicht gefunden")
    driver = crud.crud_driver_profile.soft_delete(db, driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.delete("/{driver_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanent_delete_driver(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    driver = crud.crud_driver_profile.get_by_id(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Fahrerprofil nicht gefunden")
    crud.crud_driver_profile.hard_delete(db, driver)
    db.commit()
