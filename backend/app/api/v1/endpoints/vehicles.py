import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.vehicle import VehicleType
from app.schemas.vehicle import VehicleCreate, VehiclePublic, VehicleUpdate

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

VEHICLE_TYPE_LABELS = {
    VehicleType.standard_car:      "Standard-PKW",
    VehicleType.comfort_car:       "Kombi / Komfort-PKW",
    VehicleType.wheelchair_van:    "Rollstuhl-Van",
    VehicleType.wheelchair_bus:    "Rollstuhlbus",
    VehicleType.multi_passenger_van: "Mehrsitzer-Van",
    VehicleType.stretcher_vehicle: "Liegendtransportfahrzeug",
    VehicleType.other:             "Sonstiges",
}

EQUIPMENT_OPTIONS = [
    {
        "key": "has_ramp",
        "label": "Rampe",
        "icon": "pi-sort-amount-up-alt",
        "description": "Auffahrrampe vorhanden (manuell oder elektrisch)",
    },
    {
        "key": "has_lift",
        "label": "Lift / Hebebühne",
        "icon": "pi-chevron-circle-up",
        "description": "Elektrische Hebebühne für Rollstühle",
    },
    {
        "key": "has_wheelchair_restraint",
        "label": "Rollstuhl-Sicherung",
        "icon": "pi-lock",
        "description": "Gurtsystem zur Sicherung von Rollstühlen",
    },
    {
        "key": "supports_electric_wheelchair",
        "label": "Elektrorollstuhl geeignet",
        "icon": "pi-bolt",
        "description": "Hebebühne und Fixierung für Elektrorollstühle ausgelegt",
    },
    {
        "key": "supports_stretcher_transport",
        "label": "Liegendtransport",
        "icon": "pi-minus",
        "description": "Transportliege eingebaut oder montierbar",
    },
    {
        "key": "has_child_seat",
        "label": "Kindersitz",
        "icon": "pi-star",
        "description": "Kindersitz vorhanden oder nachrüstbar",
    },
    {
        "key": "has_low_entry",
        "label": "Niedriger Einstieg",
        "icon": "pi-arrow-down",
        "description": "Fahrzeug hat abgesenkten Einstieg oder Kneeling-Funktion",
    },
    {
        "key": "has_extra_wide_door",
        "label": "Extra breite Tür",
        "icon": "pi-arrows-h",
        "description": "Seitentür besonders breit — geeignet für große Rollstühle",
    },
]

MEDICAL_EQUIPMENT_OPTIONS = [
    {
        "key": "has_stretcher",
        "label": "Transportliege",
        "icon": "pi-minus",
        "description": "Fest eingebaute oder mitgeführte Transportliege vorhanden",
    },
    {
        "key": "has_stretcher_mount",
        "label": "Liegenaufnahme",
        "icon": "pi-lock",
        "description": "Befestigungssystem für Krankentragen / Tragestühle verbaut",
    },
    {
        "key": "has_medical_equipment_storage",
        "label": "Med. Stauraum",
        "icon": "pi-inbox",
        "description": "Abgetrennter Stauraum für medizinisches Equipment (Trolley, Taschen)",
    },
    {
        "key": "has_oxygen_mount",
        "label": "Sauerstoffhalterung",
        "icon": "pi-circle",
        "description": "Halterung und Sicherung für mobile Sauerstoffgeräte vorhanden",
    },
    {
        "key": "has_first_aid_kit",
        "label": "Erste-Hilfe-Ausstattung",
        "icon": "pi-heart",
        "description": "Erste-Hilfe-Koffer nach DIN 13157 oder höher vorhanden",
    },
    {
        "key": "has_hygiene_equipment",
        "label": "Hygienebedarf",
        "icon": "pi-shield",
        "description": "Schutzausrüstung, Desinfektionsmittel, Einwegmaterial vorhanden",
    },
    {
        "key": "supports_non_emergency_medical_transport",
        "label": "Qual. Krankentransport (KTP)",
        "icon": "pi-star",
        "description": "Fahrzeug ist für qualifizierten Krankentransport (nicht Rettung) ausgestattet",
    },
    {
        "key": "has_transport_chair",
        "label": "Tragestuhl",
        "icon": "pi-arrow-circle-up",
        "description": "Tragestuhl (Transportrollstuhl) für enge Zugänge vorhanden",
    },
    {
        "key": "has_infusion_mount",
        "label": "Infusionshalterung",
        "icon": "pi-sort-amount-up-alt",
        "description": "Halterung für Infusionsständer im Patientenraum vorhanden",
    },
    {
        "key": "supports_two_person_crew",
        "label": "Zweimann-Besatzung",
        "icon": "pi-users",
        "description": "Fahrzeug ist für Besatzung mit zwei Personen ausgelegt (z. B. für schwere Patienten)",
    },
]

DIMENSION_ACCESS_OPTIONS = [
    {
        "key": "requires_large_parking_space",
        "label": "Großer Stellplatz erforderlich",
        "icon": "pi-map",
        "description": "Fahrzeug benötigt einen überbreiten oder überlangen Parkplatz",
    },
    {
        "key": "suitable_for_narrow_streets",
        "label": "Geeignet für enge Straßen",
        "icon": "pi-arrows-h",
        "description": "Fahrzeug ist schmal genug für einspurige Zuwegungen",
    },
    {
        "key": "suitable_for_underground_parking",
        "label": "Tiefgaragengeeignet",
        "icon": "pi-arrow-down",
        "description": "Fahrzeughöhe erlaubt Zufahrt in Tiefgaragen (Standardhöhe ≤ 2,0 m)",
    },
    {
        "key": "has_parking_assist",
        "label": "Einparkhilfe",
        "icon": "pi-wifi",
        "description": "Fahrzeug hat Parksensor oder Kamerasystem",
    },
]


@router.get("/options")
def get_options():
    return {
        "vehicle_types": [
            {"value": t.value, "label": VEHICLE_TYPE_LABELS[t]}
            for t in VehicleType
        ],
        "equipment_options": EQUIPMENT_OPTIONS,
        "medical_equipment_options": MEDICAL_EQUIPMENT_OPTIONS,
        "dimension_access_options": DIMENSION_ACCESS_OPTIONS,
    }


@router.get("", response_model=list[VehiclePublic])
def list_vehicles(
    organization_id: Optional[uuid.UUID] = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    if organization_id:
        return crud.crud_vehicle.get_by_org(db, organization_id, active_only=active_only)
    return crud.crud_vehicle.get_all(db, active_only=active_only)


@router.post("", response_model=VehiclePublic, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    vehicle = crud.crud_vehicle.create(db, payload)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/{vehicle_id}", response_model=VehiclePublic)
def get_vehicle(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    vehicle = crud.crud_vehicle.get_by_id(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Fahrzeug nicht gefunden")
    return vehicle


@router.put("/{vehicle_id}", response_model=VehiclePublic)
def update_vehicle(
    vehicle_id: uuid.UUID,
    payload: VehicleUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    vehicle = crud.crud_vehicle.get_by_id(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Fahrzeug nicht gefunden")
    vehicle = crud.crud_vehicle.update(db, vehicle, payload)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", response_model=VehiclePublic)
def deactivate_vehicle(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    vehicle = crud.crud_vehicle.get_by_id(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Fahrzeug nicht gefunden")
    vehicle = crud.crud_vehicle.soft_delete(db, vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanent_delete_vehicle(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    vehicle = crud.crud_vehicle.get_by_id(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Fahrzeug nicht gefunden")
    crud.crud_vehicle.hard_delete(db, vehicle)
    db.commit()
