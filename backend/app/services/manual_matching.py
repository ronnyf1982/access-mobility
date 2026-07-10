"""Manuelles Matching: bewertet Fahrzeuge und Fahrer für eine Transportanfrage.

Gibt Eignung, Warnungen und fehlende Anforderungen zurück.
Trifft keine automatischen Entscheidungen — unterstützt den Disponenten.
Alle Bewertungen sind Hinweise, keine rechtliche oder medizinische Freigabe.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.schemas.transport_request import (
    MatchingDriverOption,
    MatchingOptionsResponse,
    MatchingVehicleOption,
    MatchStatus,
)

if TYPE_CHECKING:
    from app.models.driver_profile import DriverProfile
    from app.models.transport_request import TransportRequest
    from app.models.vehicle import Vehicle

_STATUS_ORDER = {"suitable": 0, "warning": 1, "unsuitable": 2}

_BOOL_FIELDS = [
    "uses_wheelchair", "needs_ramp", "needs_lift", "needs_escort",
    "needs_entry_assistance", "needs_door_to_door_assistance",
    "needs_stretcher_transport", "requires_wheelchair_space",
    "requires_extra_time", "requires_transport_chair",
    "requires_two_person_assistance", "requires_medical_transport",
    "requires_medical_attendant", "brings_oxygen", "requires_oxygen_mount",
    "brings_medical_device", "requires_medical_equipment_storage",
    "requires_infusion_mount", "requires_special_positioning",
    "infection_or_hygiene_note",
]


def _extract_needs(request: TransportRequest) -> set[str]:
    """Zusammenführung beider Snapshots → Menge aller Anforderungsfelder."""
    needs: set[str] = set()
    rs = request.requirement_snapshot or {}
    for field in rs.get("selected_profile_fields") or []:
        needs.add(field)
    mps = request.mobility_profile_snapshot or {}
    for field in _BOOL_FIELDS:
        if mps.get(field) is True:
            needs.add(field)
    return needs


def evaluate_vehicle(request: TransportRequest, vehicle: Vehicle) -> MatchingVehicleOption:
    needs = _extract_needs(request)
    hard_missing: list[str] = []
    soft_missing: list[str] = []
    matched: list[str] = []
    reasons: list[str] = []

    if "needs_stretcher_transport" in needs:
        if vehicle.supports_stretcher_transport:
            matched.append("supports_stretcher_transport")
        else:
            hard_missing.append("Liegendtransport-Grundausstattung")
            reasons.append("Fahrzeug unterstützt keinen Liegendtransport. Bitte fachlich prüfen.")
        if vehicle.has_stretcher:
            matched.append("has_stretcher")
        else:
            hard_missing.append("Transportliege (has_stretcher)")
            reasons.append("Keine Transportliege vorhanden.")
        if vehicle.has_stretcher_mount:
            matched.append("has_stretcher_mount")
        else:
            hard_missing.append("Liegenaufnahme / Gurtsicherung (has_stretcher_mount)")
            reasons.append("Keine Liegenaufnahme vorhanden.")

    if "requires_transport_chair" in needs:
        if vehicle.has_transport_chair:
            matched.append("has_transport_chair")
        else:
            hard_missing.append("Tragestuhl (has_transport_chair)")
            reasons.append("Kein Tragestuhl vorhanden. Möglicherweise nicht geeignet.")

    if "brings_oxygen" in needs or "requires_oxygen_mount" in needs:
        if vehicle.has_oxygen_mount:
            matched.append("has_oxygen_mount")
        else:
            hard_missing.append("Sauerstoffhalterung (has_oxygen_mount)")
            reasons.append("Keine Sauerstoffhalterung. Fahrgast bringt Sauerstoffgerät mit.")

    if "brings_medical_device" in needs or "requires_medical_equipment_storage" in needs:
        if vehicle.has_medical_equipment_storage:
            matched.append("has_medical_equipment_storage")
        else:
            hard_missing.append("Med. Stauraum (has_medical_equipment_storage)")
            reasons.append("Kein gesicherter Stauraum für medizinisches Equipment.")

    if "requires_infusion_mount" in needs:
        if vehicle.has_infusion_mount:
            matched.append("has_infusion_mount")
        else:
            hard_missing.append("Infusionshalterung (has_infusion_mount)")
            reasons.append("Keine Infusionshalterung vorhanden.")

    if "requires_medical_transport" in needs:
        if vehicle.supports_non_emergency_medical_transport:
            matched.append("supports_non_emergency_medical_transport")
        else:
            soft_missing.append("Qual. Krankentransport-Ausstattung")
            reasons.append(
                "Fahrzeug nicht als qualifizierter Krankentransport erfasst. Bitte fachlich prüfen."
            )
        if vehicle.has_first_aid_kit:
            matched.append("has_first_aid_kit")
        else:
            soft_missing.append("Erste-Hilfe-Ausstattung")
            reasons.append("Keine Erste-Hilfe-Ausstattung erfasst.")
        if vehicle.has_hygiene_equipment:
            matched.append("has_hygiene_equipment")
        else:
            soft_missing.append("Hygienebedarf")
            reasons.append("Keine Hygienebedarf-Ausstattung erfasst.")

    if "requires_two_person_assistance" in needs:
        if vehicle.supports_two_person_crew:
            matched.append("supports_two_person_crew")
        else:
            soft_missing.append("Zweimann-Besatzung (supports_two_person_crew)")
            reasons.append("Fahrzeug nicht für Zweimann-Besatzung ausgelegt. Bitte prüfen.")

    if "uses_wheelchair" in needs or "requires_wheelchair_space" in needs:
        wc_count = vehicle.wheelchair_space_count or 0
        if wc_count > 0:
            matched.append(f"wheelchair_space_count={wc_count}")
        else:
            hard_missing.append("Rollstuhlplatz (wheelchair_space_count > 0)")
            reasons.append("Kein Rollstuhlplatz im Fahrzeug vorhanden.")
        if vehicle.has_ramp or vehicle.has_lift:
            matched.append("has_ramp_or_lift")
        else:
            soft_missing.append("Rampe oder Lift")
            reasons.append("Weder Rampe noch Lift vorhanden. Einstieg für Rollstuhl möglicherweise nicht möglich.")
        if vehicle.has_wheelchair_restraint:
            matched.append("has_wheelchair_restraint")
        else:
            soft_missing.append("Rollstuhlsicherung (has_wheelchair_restraint)")
            reasons.append("Keine Rollstuhlsicherung erfasst. Bitte prüfen.")

    if not needs:
        reasons.append("Keine spezifischen Anforderungen in der Anfrage — alle Fahrzeuge grundsätzlich geeignet.")

    if hard_missing:
        status = MatchStatus.unsuitable
    elif soft_missing:
        status = MatchStatus.warning
    else:
        status = MatchStatus.suitable

    return MatchingVehicleOption(
        vehicle_id=vehicle.id,
        name=vehicle.name,
        license_plate=vehicle.license_plate,
        vehicle_type=vehicle.vehicle_type.value,
        status=status,
        reasons=reasons,
        missing_requirements=hard_missing + soft_missing,
        matched_requirements=matched,
    )


def evaluate_driver(request: TransportRequest, driver: DriverProfile) -> MatchingDriverOption:
    needs = _extract_needs(request)
    hard_missing: list[str] = []
    soft_missing: list[str] = []
    matched: list[str] = []
    reasons: list[str] = []

    if "needs_stretcher_transport" in needs:
        if driver.can_handle_stretcher:
            matched.append("can_handle_stretcher")
        else:
            hard_missing.append("Liegendtransport-Begleitung (can_handle_stretcher)")
            reasons.append("Fahrer:in ist nicht für Liegendtransport-Begleitung qualifiziert.")
        if driver.has_stretcher_handling_training:
            matched.append("has_stretcher_handling_training")
        else:
            soft_missing.append("Liegendtransport-Training")
            reasons.append("Kein Liegendtransport-Training erfasst. Bitte fachlich prüfen.")

    if "requires_transport_chair" in needs:
        if driver.has_transport_chair_training:
            matched.append("has_transport_chair_training")
        else:
            soft_missing.append("Tragestuhl-Training")
            reasons.append("Kein Tragestuhl-Training erfasst. Möglicherweise nicht geeignet.")

    if "requires_medical_transport" in needs:
        if driver.can_support_medical_transport:
            matched.append("can_support_medical_transport")
        else:
            soft_missing.append("Qual. Krankentransport-Qualifikation")
            reasons.append(
                "Fahrer:in nicht für qualifizierten Krankentransport qualifiziert. Bitte fachlich prüfen."
            )
        if driver.has_first_aid_training:
            matched.append("has_first_aid_training")
        else:
            soft_missing.append("Erste-Hilfe-Training")
            reasons.append("Kein Erste-Hilfe-Training erfasst.")

    if "requires_medical_attendant" in needs:
        med_quals = [
            driver.has_sanitaetshelfer_training,
            driver.has_rettungshelfer_qualification,
            driver.has_rettungssanitaeter_qualification,
            driver.has_rettungsassistent_qualification,
            driver.has_notfallsanitaeter_qualification,
            driver.has_nursing_qualification,
            driver.has_medical_assistant_qualification,
        ]
        if any(med_quals):
            matched.append("medical_qualification")
        else:
            soft_missing.append("Med. Qualifikation (SanH / RettSan / Pflege o. ä.)")
            reasons.append(
                "Keine medizinische Qualifikation erfasst. "
                "Medizinisch qualifizierte Begleitung laut Anfrage erforderlich. Bitte prüfen."
            )

    if "infection_or_hygiene_note" in needs:
        if driver.has_hygiene_training:
            matched.append("has_hygiene_training")
        else:
            soft_missing.append("Hygieneschulung")
            reasons.append("Keine Hygieneschulung erfasst. Hygiene-/Infektionsschutzhinweis liegt vor.")
        if driver.has_infection_protection_training:
            matched.append("has_infection_protection_training")
        else:
            soft_missing.append("Infektionsschutz-Training (IfSG)")
            reasons.append("Kein Infektionsschutz-Training nach IfSG erfasst.")

    if "uses_wheelchair" in needs or "requires_wheelchair_space" in needs:
        if driver.can_secure_wheelchair:
            matched.append("can_secure_wheelchair")
        else:
            soft_missing.append("Rollstuhlsicherung (can_secure_wheelchair)")
            reasons.append(
                "Fahrer:in hat keine Qualifikation zur Rollstuhlsicherung erfasst. Bitte prüfen."
            )
        if driver.has_wheelchair_restraint_training:
            matched.append("has_wheelchair_restraint_training")
        else:
            soft_missing.append("Rollstuhlsicherungs-Training (zertifiziert)")
            reasons.append("Kein zertifiziertes Rollstuhlsicherungs-Training erfasst.")

    if not needs:
        reasons.append("Keine spezifischen Anforderungen in der Anfrage — alle Fahrer:innen grundsätzlich geeignet.")

    if hard_missing:
        status = MatchStatus.unsuitable
    elif soft_missing:
        status = MatchStatus.warning
    else:
        status = MatchStatus.suitable

    return MatchingDriverOption(
        driver_profile_id=driver.id,
        display_name=driver.display_name,
        status=status,
        reasons=reasons,
        missing_requirements=hard_missing + soft_missing,
        matched_requirements=matched,
    )


def evaluate_request_options(
    request: TransportRequest,
    vehicles: list[Vehicle],
    drivers: list[DriverProfile],
) -> MatchingOptionsResponse:
    vehicle_results = sorted(
        [evaluate_vehicle(request, v) for v in vehicles],
        key=lambda o: _STATUS_ORDER[o.status.value],
    )
    driver_results = sorted(
        [evaluate_driver(request, d) for d in drivers],
        key=lambda o: _STATUS_ORDER[o.status.value],
    )
    return MatchingOptionsResponse(
        request_id=request.id,
        vehicles=vehicle_results,
        drivers=driver_results,
    )
