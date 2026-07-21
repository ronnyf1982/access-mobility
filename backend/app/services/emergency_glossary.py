"""Static emergency first-aid glossary — no DB, no external API."""
from app.schemas.emergency import EmergencyGlossaryEntry

GLOSSARY: list[EmergencyGlossaryEntry] = [
    EmergencyGlossaryEntry(
        key="epilepsy",
        title="Epileptischer Anfall",
        immediate_action_title="Jetzt handeln: Epileptischer Anfall",
        first_aid_steps=[
            "Ruhe bewahren — die Person nicht festhalten.",
            "Verletzungsgefahr beseitigen: Harte Gegenstände wegräumen, Kopf polstern.",
            "Person in stabile Seitenlage bringen, sobald Zuckungen nachlassen.",
            "Kleidung am Hals lockern, Atmung beobachten.",
            "Zeit messen: Anfallsdauer notieren.",
            "Nach Ende des Anfalls ruhig und klar sprechen, orientieren.",
        ],
        do_not_do=[
            "Nichts in den Mund stecken (kein Löffel, kein Beißkeil).",
            "Person nicht festhalten oder gewaltsam bewegen.",
            "Keine Flüssigkeit einflößen.",
        ],
        call_112_when=[
            "Anfall dauert länger als 5 Minuten.",
            "Zweiter Anfall ohne Wiedererlangung des Bewusstseins dazwischen.",
            "Person kommt nach dem Anfall nicht zu sich.",
            "Person ist verletzt.",
            "Erster bekannter Anfall der Person.",
        ],
        call_112_script_hint=(
            "Ich bin Fahrer von Fahrando. Mein Fahrgast hat einen epileptischen Anfall. "
            "Standort: {location}. Anfallsdauer bisher ca. {duration} Minuten."
        ),
        source_note="Quelle: Deutsches Rotes Kreuz, Erste-Hilfe-Grundregeln",
    ),
    EmergencyGlossaryEntry(
        key="hypoglycemia",
        title="Unterzuckerung (Hypoglykämie)",
        immediate_action_title="Jetzt handeln: Unterzuckerung",
        first_aid_steps=[
            "Person nach Diabetes und mitgeführtem Traubenzucker fragen.",
            "Wenn bei Bewusstsein: Traubenzucker, Fruchtsaft oder zuckerhaltiges Getränk geben.",
            "Person hinsetzen und ruhig halten.",
            "Nach 10–15 Minuten prüfen, ob Besserung eintritt.",
        ],
        do_not_do=[
            "Bewusstloser Person nichts zu trinken oder essen geben (Erstickungsgefahr).",
            "Kein Insulin geben — nur Zucker erhöhen.",
        ],
        call_112_when=[
            "Person ist bewusstlos.",
            "Keine Besserung nach Zuckergabe.",
            "Person ist desorientiert und unkooperativ.",
        ],
        call_112_script_hint=(
            "Ich bin Fahrer von Fahrando. Mein Fahrgast hat vermutlich eine Unterzuckerung (Diabetes). "
            "Standort: {location}."
        ),
        source_note="Quelle: Deutsche Diabetes Gesellschaft, Erste-Hilfe-Leitfaden",
    ),
    EmergencyGlossaryEntry(
        key="anaphylaxis",
        title="Allergische Reaktion / Anaphylaxie",
        immediate_action_title="Jetzt handeln: Schwere allergische Reaktion",
        first_aid_steps=[
            "Notruf 112 sofort — Anaphylaxie ist lebensbedrohlich.",
            "Nach Adrenalin-Autoinjektor (EpiPen) in Tasche/Gepäck fragen.",
            "Falls vorhanden: Adrenalin am äußeren Oberschenkel injizieren.",
            "Bei Atemnot: Oberkörper erhöht hinsetzen. Bei Schock: flach mit hochgelegten Beinen.",
            "Auslöser entfernen, Atmung und Bewusstsein beobachten.",
        ],
        do_not_do=[
            "Person nicht alleine lassen.",
            "Keine Flüssigkeit bei Atemnot einflößen.",
        ],
        call_112_when=[
            "Immer sofort — Anaphylaxie ist immer ein Notfall.",
            "Atemnot, Schwellung im Hals- oder Gesichtsbereich.",
            "Kreislaufkollaps oder Bewusstlosigkeit.",
        ],
        call_112_script_hint=(
            "Ich bin Fahrer von Fahrando. Mein Fahrgast hat eine schwere allergische Reaktion. "
            "Standort: {location}."
        ),
        source_note="Quelle: DAAB (Deutscher Allergie- und Asthmabund), Notfallplan Anaphylaxie",
    ),
    EmergencyGlossaryEntry(
        key="cardiac_emergency",
        title="Herznotfall / Herzstillstand",
        immediate_action_title="Jetzt handeln: Herznotfall",
        first_aid_steps=[
            "Notruf 112 sofort.",
            "Person ansprechen und Schultern schütteln — reagiert sie?",
            "Bei Bewusstlosigkeit und fehlender normaler Atmung: sofort Herzdruckmassage.",
            "Herzdruckmassage: Mitte des Brustkorbs, 5–6 cm tief, 100–120 Mal pro Minute.",
            "30 Kompressionen, dann 2 Beatmungen (wenn geschult). Ohne Schulung: nur Kompressionen.",
            "Weiter bis Rettungsdienst übernimmt oder Person sich erholt.",
        ],
        do_not_do=[
            "Nicht aufhören bis professionelle Hilfe kommt.",
            "Keine Herzdruckmassage bei normaler Atmung und vorhandenem Bewusstsein.",
        ],
        call_112_when=[
            "Immer sofort — kein Puls oder keine normale Atmung.",
        ],
        call_112_script_hint=(
            "Ich bin Fahrer von Fahrando. Mein Fahrgast ist bewusstlos, atmet nicht normal — "
            "ich vermute Herzstillstand. Ich führe Herzdruckmassage durch. Standort: {location}."
        ),
        source_note="Quelle: Deutsches Rotes Kreuz, ERC-Leitlinien Reanimation",
    ),
    EmergencyGlossaryEntry(
        key="unconsciousness",
        title="Bewusstlosigkeit / Ohnmacht",
        immediate_action_title="Jetzt handeln: Bewusstlosigkeit",
        first_aid_steps=[
            "Person laut ansprechen und leicht an der Schulter berühren.",
            "Keine Reaktion: Atmung prüfen (sehen, hören, fühlen — max. 10 Sekunden).",
            "Bei normaler Atmung: stabile Seitenlage einleiten.",
            "Atemwege freihalten: Kopf leicht überstrecken, Kinn anheben.",
            "Vitalzeichen regelmäßig beobachten.",
        ],
        do_not_do=[
            "Person nicht alleine lassen.",
            "Keine Flüssigkeit einflößen.",
            "Nicht aufrecht setzen.",
        ],
        call_112_when=[
            "Person kommt nicht innerhalb 1–2 Minuten zu sich.",
            "Keine normale Atmung — dann Herzdruckmassage beginnen.",
            "Unbekannte Ursache der Bewusstlosigkeit.",
        ],
        call_112_script_hint=(
            "Ich bin Fahrer von Fahrando. Mein Fahrgast ist bewusstlos, atmet aber normal. "
            "Stabile Seitenlage eingeleitet. Standort: {location}."
        ),
        source_note="Quelle: Deutsches Rotes Kreuz, Erste-Hilfe-Grundregeln",
    ),
    EmergencyGlossaryEntry(
        key="breathing_emergency",
        title="Atemnotfall",
        immediate_action_title="Jetzt handeln: Atemnot",
        first_aid_steps=[
            "Notruf 112 bei plötzlicher oder sich verschlechternder Atemnot.",
            "Person aufrecht hinsetzen, beengende Kleidung lockern.",
            "Ruhig sprechen, Panik vermeiden.",
            "Bei Asthma: nach Asthmaspray fragen und Anwendung ermöglichen.",
            "Frischluft verschaffen (Fenster öffnen).",
        ],
        do_not_do=[
            "Person nicht flach hinlegen — erschwert das Atmen.",
            "Keine Medikamente ohne Wissen der Person verabreichen.",
        ],
        call_112_when=[
            "Starke Atemnot, blaue Lippen oder Fingernägel.",
            "Person kann kaum oder nicht mehr sprechen.",
            "Bewusstsein trübt sich ein.",
        ],
        call_112_script_hint=(
            "Ich bin Fahrer von Fahrando. Mein Fahrgast hat schwere Atemnot. "
            "Standort: {location}."
        ),
        source_note="Quelle: Deutsches Rotes Kreuz, Erste-Hilfe-Leitfaden Atemnot",
    ),
    EmergencyGlossaryEntry(
        key="stroke",
        title="Schlaganfall",
        immediate_action_title="Jetzt handeln: Schlaganfall (FAST-Test)",
        first_aid_steps=[
            "FAST-Test: Face (Gesicht hängt?), Arms (Arm kann nicht gehoben werden?), "
            "Speech (Sprechen undeutlich?), Time (sofort 112!).",
            "Notruf 112 sofort — jede Minute zählt.",
            "Person ruhig hinsetzen oder in stabile Lage bringen.",
            "Zeitpunkt der ersten Symptome notieren.",
            "Keine Flüssigkeit geben (Schluckstörung möglich).",
        ],
        do_not_do=[
            "Keine Zeit verlieren — bei Schlaganfall zählt jede Minute.",
            "Kein Aspirin ohne ärztliche Anweisung.",
            "Person nicht schlafen lassen.",
        ],
        call_112_when=[
            "Immer sofort bei Verdacht — FAST-Test positiv.",
        ],
        call_112_script_hint=(
            "Ich bin Fahrer von Fahrando. Mein Fahrgast hat möglicherweise einen Schlaganfall. "
            "FAST-Test auffällig. Erste Symptome: {symptom_time}. Standort: {location}."
        ),
        source_note="Quelle: Deutsche Schlaganfall-Gesellschaft, FAST-Schema",
    ),
    EmergencyGlossaryEntry(
        key="panic_attack",
        title="Panikattacke / Psychische Krise",
        immediate_action_title="Jetzt handeln: Panikattacke",
        first_aid_steps=[
            "Ruhe bewahren, ruhige und klare Stimme verwenden.",
            "Sicheren Ort aufsuchen — Fahrzeug abstellen wenn möglich.",
            "Sagen: 'Sie sind in Sicherheit. Ich bin bei Ihnen.' — ruhig wiederholen.",
            "Atemübung anleiten: 4 Sek. einatmen, 4 halten, 6 ausatmen.",
            "Keine schnellen Bewegungen, keine lauten Geräusche.",
            "Person nicht alleine lassen bis sie sich beruhigt hat.",
        ],
        do_not_do=[
            "Nicht sagen 'Reiß dich zusammen' oder 'Ist doch nichts'.",
            "Nicht zu viele Fragen auf einmal stellen.",
            "Keine Medikamente ohne Wissen der Person.",
        ],
        call_112_when=[
            "Person verletzt sich selbst oder andere.",
            "Bewusstseinsverlust oder Kollaps.",
            "Panikattacke geht in reale medizinische Notlage über.",
        ],
        call_112_script_hint=None,
        source_note="Quelle: Deutsche Gesellschaft für Psychiatrie und Psychotherapie (DGPPN)",
    ),
]

_GLOSSARY_BY_KEY: dict[str, EmergencyGlossaryEntry] = {e.key: e for e in GLOSSARY}


def get_all_glossary_entries() -> list[EmergencyGlossaryEntry]:
    return GLOSSARY


def get_glossary_entry(key: str) -> EmergencyGlossaryEntry | None:
    return _GLOSSARY_BY_KEY.get(key)


def get_relevant_entries_for_profile(
    profile,
    emergency_mode: bool,
) -> list[EmergencyGlossaryEntry]:
    """Return glossary entries relevant to a passenger's visible conditions."""
    def disabilities_visible() -> bool:
        if emergency_mode:
            return profile.show_disabilities_to_driver or profile.show_disabilities_in_emergency
        return profile.show_disabilities_to_driver

    def comm_visible() -> bool:
        if emergency_mode:
            return profile.show_communication_notes_to_driver or profile.show_communication_notes_in_emergency
        return profile.show_communication_notes_to_driver

    keys: list[str] = []
    if getattr(profile, "has_epilepsy", False) and disabilities_visible():
        keys.append("epilepsy")
    if (getattr(profile, "is_deaf_or_hard_of_hearing", False) or getattr(profile, "is_mute", False)) and comm_visible():
        pass  # communication notes section covers this — no dedicated glossary entry required
    return [_GLOSSARY_BY_KEY[k] for k in keys if k in _GLOSSARY_BY_KEY]
