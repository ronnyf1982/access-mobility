<template>
  <div class="tr-page">
    <!-- Header -->
    <div class="tr-header">
      <div>
        <h1 class="tr-title">Fahrten anfragen</h1>
        <p class="tr-subtitle">
          Neue Transportanfrage erstellen oder Ihre bisherigen Anfragen verwalten.
        </p>
      </div>
      <button
        v-if="mode === 'list'"
        class="am-btn am-btn-primary"
        @click="startCreate"
        aria-label="Neue Transportanfrage erstellen"
      >
        <i class="pi pi-plus" aria-hidden="true"></i>
        Neue Anfrage
      </button>
      <button
        v-else
        class="am-btn am-btn-ghost"
        @click="backToList"
        aria-label="Zurück zur Liste"
      >
        <i class="pi pi-arrow-left" aria-hidden="true"></i>
        Zurück zur Liste
      </button>
    </div>

    <!-- ── LISTE ─────────────────────────────────────────────────────────── -->
    <div v-if="mode === 'list'">
      <div
        v-if="store.loading"
        class="tr-loading"
        role="status"
        aria-live="polite"
        aria-label="Anfragen werden geladen"
      >
        <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
        Anfragen werden geladen …
      </div>

      <div v-else-if="store.requests.length === 0" class="tr-empty am-card">
        <i class="pi pi-inbox tr-empty-icon" aria-hidden="true"></i>
        <p class="tr-empty-text">Noch keine Transportanfragen vorhanden.</p>
        <button class="am-btn am-btn-primary" @click="startCreate">
          <i class="pi pi-plus" aria-hidden="true"></i>
          Erste Anfrage erstellen
        </button>
      </div>

      <div v-else class="tr-list">
        <div
          v-for="req in store.requests"
          :key="req.id"
          class="tr-card am-card"
          :class="`tr-card--${req.status}`"
          role="article"
          :aria-label="`Anfrage ${formatDate(req.pickup_date)}, Status: ${statusLabel(req.status)}`"
        >
          <div class="tr-card-top">
            <span
              class="tr-status-badge"
              :class="`tr-status-badge--${req.status}`"
              :aria-label="`Status: ${statusLabel(req.status)}`"
            >
              <i :class="['pi', statusIcon(req.status)]" aria-hidden="true"></i>
              {{ statusLabel(req.status) }}
            </span>
            <span class="tr-card-type" v-if="req.transport_type_id">
              {{ typeLabel(req.transport_type_id) }}
            </span>
            <span class="tr-card-date">
              <i class="pi pi-calendar" aria-hidden="true"></i>
              {{ formatDate(req.pickup_date) }}
              <span v-if="req.pickup_time">um {{ req.pickup_time }}</span>
            </span>
          </div>

          <div class="tr-card-route" v-if="req.pickup_address || req.destination_address">
            <div class="tr-route-item">
              <i class="pi pi-map-marker tr-route-icon tr-route-icon--from" aria-hidden="true"></i>
              <span class="tr-route-addr">{{ req.pickup_address || '—' }}</span>
            </div>
            <div class="tr-route-arrow" aria-hidden="true">
              <i class="pi pi-arrow-right"></i>
              <span v-if="req.is_round_trip" class="tr-round-trip-chip">Hin &amp; Rück</span>
            </div>
            <div class="tr-route-item">
              <i class="pi pi-flag tr-route-icon tr-route-icon--to" aria-hidden="true"></i>
              <span class="tr-route-addr">{{ req.destination_address || '—' }}</span>
            </div>
          </div>
          <div v-else class="tr-card-route-empty">
            Noch keine Adresse angegeben
          </div>

          <div class="tr-card-actions">
            <button
              v-if="req.status !== 'cancelled'"
              class="am-btn am-btn-ghost tr-card-btn"
              @click="openEdit(req.id)"
              :aria-label="`Anfrage vom ${formatDate(req.pickup_date)} bearbeiten`"
            >
              <i class="pi pi-pencil" aria-hidden="true"></i>
              Bearbeiten
            </button>
            <button
              v-if="req.status !== 'cancelled'"
              class="am-btn am-btn-ghost tr-card-btn tr-card-btn--danger"
              @click="confirmCancel(req.id)"
              :aria-label="`Anfrage vom ${formatDate(req.pickup_date)} stornieren`"
            >
              <i class="pi pi-times" aria-hidden="true"></i>
              Stornieren
            </button>
            <span v-if="req.status === 'cancelled'" class="tr-cancelled-note">
              Storniert {{ req.cancelled_at ? formatDate(req.cancelled_at) : '' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- ── FORMULAR (Erstellen / Bearbeiten) ───────────────────────────── -->
    <form v-else class="tr-form" @submit.prevent="handleSave" novalidate>
      <!-- Fehler / Erfolg -->
      <div
        v-if="formError"
        class="tr-alert tr-alert--error"
        role="alert"
        aria-live="assertive"
      >
        <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
        {{ formError }}
      </div>
      <div
        v-if="formSuccess"
        class="tr-alert tr-alert--success"
        role="alert"
        aria-live="assertive"
      >
        <i class="pi pi-check-circle" aria-hidden="true"></i>
        {{ formSuccess }}
      </div>

      <!-- Abschnitt 1: Für wen -->
      <section class="tr-section am-card" aria-labelledby="s1-heading">
        <h2 id="s1-heading" class="tr-section-title">
          <i class="pi pi-user" aria-hidden="true"></i>
          Für wen ist die Fahrt?
        </h2>
        <div class="tr-for-self" role="group" aria-label="Fahrgast auswählen">
          <button
            type="button"
            class="tr-for-btn tr-for-btn--active"
            aria-pressed="true"
            aria-label="Für mich selbst — ausgewählt"
          >
            <i class="pi pi-user" aria-hidden="true"></i>
            <span>Für mich selbst</span>
          </button>
          <button
            type="button"
            class="tr-for-btn tr-for-btn--soon"
            disabled
            aria-disabled="true"
            title="Buchung für andere Personen folgt in einem späteren Sprint"
          >
            <i class="pi pi-users" aria-hidden="true"></i>
            <span>Für andere Person</span>
            <span class="soon-chip" aria-label="In Entwicklung">bald</span>
          </button>
        </div>
      </section>

      <!-- Abschnitt 2: Transporttyp -->
      <section class="tr-section am-card" aria-labelledby="s2-heading">
        <h2 id="s2-heading" class="tr-section-title">
          <i class="pi pi-bolt" aria-hidden="true"></i>
          Welche Art von Fahrt?
        </h2>
        <p class="tr-section-desc">
          Wählen Sie den passenden Transporttyp. Die Auswahl ist ein Vorschlag — Sie können
          die Anforderungen im nächsten Schritt anpassen.
        </p>
        <div class="tr-type-grid" role="group" aria-label="Transporttyp auswählen">
          <button
            v-for="tt in transportTypes"
            :key="tt.id"
            type="button"
            class="tr-type-card"
            :class="{ 'tr-type-card--active': form.transport_type_id === tt.id }"
            :aria-pressed="form.transport_type_id === tt.id"
            :aria-label="`${tt.label}: ${tt.description}`"
            @click="selectTransportType(tt)"
          >
            <span class="tr-type-label">{{ tt.label }}</span>
            <span class="tr-type-desc">{{ tt.description }}</span>
            <span v-if="tt.warning" class="tr-type-warning">
              <i class="pi pi-exclamation-triangle" aria-hidden="true"></i>
              {{ tt.warning }}
            </span>
          </button>
        </div>
      </section>

      <!-- Abschnitt 3: Wann und wohin -->
      <section class="tr-section am-card" aria-labelledby="s3-heading">
        <h2 id="s3-heading" class="tr-section-title">
          <i class="pi pi-calendar" aria-hidden="true"></i>
          Wann und wohin?
        </h2>

        <!-- Zeit -->
        <div class="tr-field-row">
          <div class="tr-field">
            <label for="pickup-date" class="tr-label">
              Abholdatum <span class="tr-required" aria-hidden="true">*</span>
            </label>
            <input
              id="pickup-date"
              v-model="form.pickup_date"
              type="date"
              class="tr-input"
              required
              aria-required="true"
            />
          </div>
          <div class="tr-field">
            <label for="pickup-time" class="tr-label">
              Abholzeit <span class="tr-required" aria-hidden="true">*</span>
            </label>
            <input
              id="pickup-time"
              v-model="form.pickup_time"
              type="time"
              class="tr-input"
              required
              aria-required="true"
            />
          </div>
          <div class="tr-field">
            <label for="arrival-time" class="tr-label">
              Gewünschte Ankunftszeit
              <span class="tr-optional-badge">optional</span>
            </label>
            <input
              id="arrival-time"
              v-model="form.arrival_time"
              type="time"
              class="tr-input"
            />
          </div>
        </div>

        <!-- Abholadresse -->
        <div class="tr-field">
          <label for="pickup-addr" class="tr-label">
            Abholadresse <span class="tr-required" aria-hidden="true">*</span>
          </label>
          <input
            id="pickup-addr"
            v-model="form.pickup_address"
            type="text"
            class="tr-input"
            placeholder="Straße, Hausnummer, PLZ Ort"
            required
            aria-required="true"
          />
        </div>
        <div class="tr-field">
          <label for="pickup-details" class="tr-label">
            Abholhinweise
            <span class="tr-optional-badge">optional</span>
          </label>
          <p class="tr-field-hint">Klingel, Etage, Wohnung, Barrierehinweis</p>
          <textarea
            id="pickup-details"
            v-model="form.pickup_details"
            class="tr-textarea"
            rows="2"
            aria-label="Abholhinweise"
          ></textarea>
        </div>

        <!-- Zieladresse -->
        <div class="tr-field">
          <label for="dest-addr" class="tr-label">
            Zieladresse <span class="tr-required" aria-hidden="true">*</span>
          </label>
          <input
            id="dest-addr"
            v-model="form.destination_address"
            type="text"
            class="tr-input"
            placeholder="Straße, Hausnummer, PLZ Ort"
            required
            aria-required="true"
          />
        </div>
        <div class="tr-field">
          <label for="dest-details" class="tr-label">
            Zielhinweise
            <span class="tr-optional-badge">optional</span>
          </label>
          <p class="tr-field-hint">Eingang, Abteilung, Zugangsinformation</p>
          <textarea
            id="dest-details"
            v-model="form.destination_details"
            class="tr-textarea"
            rows="2"
            aria-label="Zielhinweise"
          ></textarea>
        </div>

        <!-- Rückfahrt -->
        <div class="tr-toggle-row">
          <span class="tr-toggle-label">
            Hin- und Rückfahrt
            <span class="tr-toggle-sub">Benötigen Sie auch eine Rückfahrt?</span>
          </span>
          <button
            type="button"
            class="tr-toggle-btn"
            :class="{ 'tr-toggle-btn--on': form.is_round_trip }"
            role="switch"
            :aria-checked="form.is_round_trip"
            aria-label="Hin- und Rückfahrt"
            @click="form.is_round_trip = !form.is_round_trip"
          >
            <span class="tr-toggle-knob"></span>
          </button>
        </div>

        <div v-if="form.is_round_trip" class="tr-return-block">
          <div class="tr-toggle-row">
            <span class="tr-toggle-label">
              Rückfahrtzeit bekannt
              <span class="tr-toggle-sub">Kennen Sie die gewünschte Rückfahrtzeit bereits?</span>
            </span>
            <button
              type="button"
              class="tr-toggle-btn"
              :class="{ 'tr-toggle-btn--on': form.return_time_known }"
              role="switch"
              :aria-checked="form.return_time_known"
              aria-label="Rückfahrtzeit bekannt"
              @click="form.return_time_known = !form.return_time_known"
            >
              <span class="tr-toggle-knob"></span>
            </button>
          </div>
          <div v-if="form.return_time_known" class="tr-field">
            <label for="return-time" class="tr-label">Gewünschte Rückfahrtzeit</label>
            <input
              id="return-time"
              v-model="form.return_pickup_time"
              type="time"
              class="tr-input"
            />
          </div>
        </div>
      </section>

      <!-- Abschnitt 4: Besondere Anforderungen -->
      <section class="tr-section am-card" aria-labelledby="s4-heading">
        <h2 id="s4-heading" class="tr-section-title">
          <i class="pi pi-heart" aria-hidden="true"></i>
          Besondere Anforderungen
          <span class="tr-optional-badge">optional</span>
        </h2>
        <p class="tr-section-desc">
          Die Felder wurden anhand Ihres Mobilitätsprofils und der Transportart vorausgefüllt.
          Sie können alles anpassen — nur was für diese Fahrt gilt.
        </p>

        <div class="tr-req-grid" role="group" aria-label="Anforderungen auswählen">
          <button
            v-for="opt in REQUIREMENT_OPTIONS"
            :key="opt.key"
            type="button"
            class="tr-req-card"
            :class="{ 'tr-req-card--active': !!snapshotFields[opt.key] }"
            role="checkbox"
            :aria-checked="!!snapshotFields[opt.key]"
            :aria-label="`${opt.label}: ${opt.desc}`"
            @click="toggleReq(opt.key)"
          >
            <div class="tr-req-icon" aria-hidden="true">
              <i :class="['pi', opt.icon]"></i>
            </div>
            <div class="tr-req-text">
              <span class="tr-req-label">{{ opt.label }}</span>
              <span class="tr-req-desc">{{ opt.desc }}</span>
            </div>
            <div class="tr-req-check" aria-hidden="true">
              <i class="pi pi-check"></i>
            </div>
          </button>
        </div>

        <div class="tr-field" style="margin-top: 1rem">
          <label for="req-notes" class="tr-label">
            Hinweise zur Fahrt
            <span class="tr-optional-badge">optional</span>
          </label>
          <p class="tr-field-hint">
            Alles Wichtige für den Fahrdienst, das in den Feldern oben nicht abgebildet ist.
          </p>
          <textarea
            id="req-notes"
            v-model="form.notes"
            class="tr-textarea"
            rows="3"
            aria-label="Hinweise zur Fahrt"
          ></textarea>
        </div>
      </section>

      <!-- Abschnitt 5: Speichern / Absenden -->
      <div class="tr-save-bar">
        <button
          type="button"
          class="am-btn am-btn-ghost"
          :disabled="store.saving"
          @click="handleSaveDraft"
          aria-label="Als Entwurf speichern"
        >
          <i v-if="store.saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
          <i v-else class="pi pi-save" aria-hidden="true"></i>
          Als Entwurf speichern
        </button>
        <button
          type="submit"
          class="am-btn am-btn-primary"
          :disabled="store.saving"
          :aria-busy="store.saving"
          aria-label="Anfrage jetzt absenden"
        >
          <i v-if="store.saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
          <i v-else class="pi pi-send" aria-hidden="true"></i>
          {{ store.saving ? 'Wird gespeichert …' : 'Anfrage absenden' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useTransportRequestStore } from '@/stores/transportRequests'
import { useMobilityProfileStore } from '@/stores/mobilityProfile'
import { getTransportOptions } from '@/api/transportOptions'
import type { TransportType, TransportRequestCreate, MobilityProfileSnapshot, RequirementSnapshot } from '@/types'
import { TRANSPORT_REQUEST_STATUS_LABELS } from '@/types'

const store = useTransportRequestStore()
const profileStore = useMobilityProfileStore()

const mode = ref<'list' | 'form'>('list')
const editId = ref<string | null>(null)
const formError = ref('')
const formSuccess = ref('')
const transportTypes = ref<TransportType[]>([])

const BLANK_FORM: TransportRequestCreate = {
  transport_type_id: null,
  pickup_address: null,
  pickup_details: null,
  destination_address: null,
  destination_details: null,
  pickup_date: null,
  pickup_time: null,
  arrival_time: null,
  is_round_trip: false,
  return_time_known: false,
  return_pickup_time: null,
  notes: null,
}

const form = reactive<TransportRequestCreate>({ ...BLANK_FORM })
const snapshotFields = reactive<Record<string, boolean>>({})

const REQUIREMENT_OPTIONS = [
  { key: 'uses_wheelchair',               label: 'Rollstuhl',                  icon: 'pi-android',        desc: 'Fahrt mit Rollstuhl' },
  { key: 'needs_ramp',                    label: 'Rampe erforderlich',          icon: 'pi-sort-amount-up-alt', desc: 'Auffahrrampe am Fahrzeug nötig' },
  { key: 'needs_lift',                    label: 'Lift / Hebebühne',            icon: 'pi-chevron-circle-up', desc: 'Elektrische Hebebühne nötig' },
  { key: 'needs_entry_assistance',        label: 'Einstiegshilfe',             icon: 'pi-user-plus',      desc: 'Fahrerin unterstützt beim Einsteigen' },
  { key: 'needs_door_to_door_assistance', label: 'Haustür-zu-Haustür',        icon: 'pi-home',           desc: 'Begleitung von Tür zu Tür' },
  { key: 'needs_escort',                  label: 'Begleitperson mitfahrend',   icon: 'pi-users',          desc: 'Begleitperson fährt mit' },
  { key: 'requires_wheelchair_space',     label: 'Rollstuhlplatz im Fahrzeug', icon: 'pi-lock',           desc: 'Gesicherter Rollstuhlstellplatz' },
  { key: 'requires_extra_time',           label: 'Zusätzliche Zeit',           icon: 'pi-clock',          desc: 'Mehr Zeit für Ein-/Aussteigen' },
  { key: 'needs_stretcher_transport',     label: 'Liegendtransport',           icon: 'pi-minus',          desc: 'Fahrgast muss liegen' },
  { key: 'requires_transport_chair',      label: 'Tragestuhl',                 icon: 'pi-arrow-circle-up', desc: 'Tragestuhl für Treppenhäuser' },
  { key: 'requires_two_person_assistance','label': 'Zweimann-Begleitung',      icon: 'pi-users',          desc: 'Zwei Personen für Transfer nötig' },
  { key: 'requires_medical_transport',    label: 'Qual. Krankentransport',     icon: 'pi-shield',         desc: 'KTP mit geschultem Personal' },
  { key: 'requires_medical_attendant',    label: 'Med. Begleitung',            icon: 'pi-heart',          desc: 'Medizinisch qualifizierte Begleitperson' },
] as const

function statusLabel(status: string): string {
  return TRANSPORT_REQUEST_STATUS_LABELS[status as keyof typeof TRANSPORT_REQUEST_STATUS_LABELS] ?? status
}

function statusIcon(status: string): string {
  if (status === 'draft') return 'pi-pencil'
  if (status === 'requested') return 'pi-send'
  if (status === 'cancelled') return 'pi-times-circle'
  return 'pi-circle'
}

function typeLabel(id: string): string {
  return transportTypes.value.find((t) => t.id === id)?.label ?? id
}

function formatDate(val: string | null | undefined): string {
  if (!val) return '—'
  try {
    return new Date(val).toLocaleDateString('de-DE', {
      day: '2-digit', month: '2-digit', year: 'numeric',
    })
  } catch {
    return val
  }
}

function selectTransportType(tt: TransportType) {
  form.transport_type_id = form.transport_type_id === tt.id ? null : tt.id
  if (form.transport_type_id) {
    // Suggested fields → true; non-boolean values from suggested_field_values
    const resetKeys = tt.preset_controlled_profile_fields ?? []
    for (const k of resetKeys) snapshotFields[k] = false
    for (const f of tt.suggested_profile_fields) snapshotFields[f] = true
    if (tt.suggested_field_values) {
      // Non-boolean values not reflected in snapshotFields; stored in snapshot on save.
    }
  }
}

function toggleReq(key: string) {
  snapshotFields[key] = !snapshotFields[key]
}

function buildSnapshots(): {
  requirement_snapshot: RequirementSnapshot
  mobility_profile_snapshot: MobilityProfileSnapshot
} {
  const selected = Object.entries(snapshotFields)
    .filter(([, v]) => v)
    .map(([k]) => k)

  const selectedTT = transportTypes.value.find((t) => t.id === form.transport_type_id)
  const fieldValues = selectedTT?.suggested_field_values ?? {}

  return {
    requirement_snapshot: {
      transport_type_id: form.transport_type_id ?? undefined,
      selected_profile_fields: selected,
      selected_field_values: fieldValues,
      notes: form.notes,
    },
    mobility_profile_snapshot: buildMobilitySnapshot(),
  }
}

function buildMobilitySnapshot(): MobilityProfileSnapshot {
  const p = profileStore.profile
  if (!p) return {}
  return {
    uses_wheelchair: p.uses_wheelchair,
    wheelchair_type: p.wheelchair_type,
    uses_rollator: p.uses_rollator,
    uses_crutches: p.uses_crutches,
    needs_ramp: p.needs_ramp,
    needs_lift: p.needs_lift,
    needs_escort: p.needs_escort,
    needs_entry_assistance: p.needs_entry_assistance,
    needs_door_to_door_assistance: p.needs_door_to_door_assistance,
    needs_stretcher_transport: p.needs_stretcher_transport,
    requires_wheelchair_space: p.requires_wheelchair_space,
    requires_extra_time: p.requires_extra_time,
    requires_transport_chair: p.requires_transport_chair,
    requires_two_person_assistance: p.requires_two_person_assistance,
    requires_medical_transport: p.requires_medical_transport,
    requires_medical_attendant: p.requires_medical_attendant,
    attendant_type_required: p.attendant_type_required,
    brings_oxygen: p.brings_oxygen,
    requires_oxygen_mount: p.requires_oxygen_mount,
    brings_medical_device: p.brings_medical_device,
    requires_medical_equipment_storage: p.requires_medical_equipment_storage,
    requires_infusion_mount: p.requires_infusion_mount,
    requires_special_positioning: p.requires_special_positioning,
    infection_or_hygiene_note: p.infection_or_hygiene_note,
  }
}

function prefillFromProfile() {
  const p = profileStore.profile
  if (!p) return
  const fields: (keyof typeof snapshotFields)[] = [
    'uses_wheelchair', 'needs_ramp', 'needs_lift', 'needs_escort',
    'needs_entry_assistance', 'needs_door_to_door_assistance',
    'requires_wheelchair_space', 'requires_extra_time', 'needs_stretcher_transport',
    'requires_transport_chair', 'requires_two_person_assistance',
    'requires_medical_transport', 'requires_medical_attendant',
  ]
  for (const f of fields) {
    if ((p as Record<string, unknown>)[f] === true) snapshotFields[f] = true
  }
}

function startCreate() {
  editId.value = null
  Object.assign(form, BLANK_FORM)
  for (const k of Object.keys(snapshotFields)) snapshotFields[k] = false
  prefillFromProfile()
  formError.value = ''
  formSuccess.value = ''
  mode.value = 'form'
}

async function openEdit(id: string) {
  formError.value = ''
  formSuccess.value = ''
  try {
    const req = await store.loadOne(id)
    editId.value = id
    Object.assign(form, {
      transport_type_id: req.transport_type_id,
      pickup_address: req.pickup_address,
      pickup_details: req.pickup_details,
      destination_address: req.destination_address,
      destination_details: req.destination_details,
      pickup_date: req.pickup_date,
      pickup_time: req.pickup_time,
      arrival_time: req.arrival_time,
      is_round_trip: req.is_round_trip,
      return_time_known: req.return_time_known,
      return_pickup_time: req.return_pickup_time,
      notes: req.notes,
    })
    // Snapshot-Felder aus der gespeicherten Anfrage laden
    for (const k of Object.keys(snapshotFields)) snapshotFields[k] = false
    if (req.requirement_snapshot?.selected_profile_fields) {
      for (const f of req.requirement_snapshot.selected_profile_fields) {
        snapshotFields[f] = true
      }
    } else {
      prefillFromProfile()
    }
    mode.value = 'form'
  } catch {
    formError.value = 'Anfrage konnte nicht geladen werden.'
  }
}

function backToList() {
  mode.value = 'list'
  editId.value = null
  formError.value = ''
  formSuccess.value = ''
}

async function handleSaveDraft() {
  await save('draft')
}

async function handleSave() {
  await save('submit')
}

async function save(action: 'draft' | 'submit') {
  formError.value = ''
  formSuccess.value = ''
  const { requirement_snapshot, mobility_profile_snapshot } = buildSnapshots()

  try {
    if (editId.value) {
      await store.update(editId.value, {
        transport_type_id: form.transport_type_id,
        pickup_address: form.pickup_address,
        pickup_details: form.pickup_details,
        destination_address: form.destination_address,
        destination_details: form.destination_details,
        pickup_date: form.pickup_date,
        pickup_time: form.pickup_time,
        arrival_time: form.arrival_time,
        is_round_trip: form.is_round_trip,
        return_time_known: form.return_time_known,
        return_pickup_time: form.return_pickup_time,
        requirement_snapshot,
        mobility_profile_snapshot,
        notes: form.notes,
      })
      if (action === 'submit') {
        await store.submit(editId.value)
        formSuccess.value = 'Anfrage wurde abgesendet.'
      } else {
        formSuccess.value = 'Entwurf gespeichert.'
      }
    } else {
      const created = await store.create({
        ...form,
        status: action === 'draft' ? 'draft' : 'draft',
        requirement_snapshot,
        mobility_profile_snapshot,
      })
      if (action === 'submit') {
        await store.submit(created.id)
        formSuccess.value = 'Anfrage wurde abgesendet.'
      } else {
        formSuccess.value = 'Entwurf gespeichert.'
      }
      editId.value = created.id
    }
    setTimeout(() => {
      backToList()
    }, 1400)
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    formError.value = msg ?? 'Fehler beim Speichern. Bitte prüfen Sie alle Pflichtfelder.'
  }
}

async function confirmCancel(id: string) {
  if (!window.confirm('Möchten Sie diese Anfrage wirklich stornieren?')) return
  try {
    await store.cancel(id)
  } catch {
    // Reload list to show correct state
    await store.load()
  }
}

onMounted(async () => {
  const [, typesResult] = await Promise.allSettled([
    store.load(),
    getTransportOptions(),
  ])
  if (typesResult.status === 'fulfilled') transportTypes.value = typesResult.value
  if (!profileStore.profile) await profileStore.load().catch(() => {})
})
</script>

<style scoped>
.tr-page {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
  max-width: 860px;
}

.tr-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--am-space-m);
}

.tr-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.tr-subtitle {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 4px 0 0;
  line-height: 1.5;
}

/* Loading / Empty */
.tr-loading {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  color: var(--am-text-secondary);
  padding: var(--am-space-xl);
  justify-content: center;
}

.tr-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--am-space-m);
  padding: var(--am-space-xl);
  text-align: center;
}

.tr-empty-icon {
  font-size: 3rem;
  color: var(--am-text-secondary);
  opacity: 0.4;
}

.tr-empty-text {
  color: var(--am-text-secondary);
  margin: 0;
}

/* Liste */
.tr-list {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.tr-card {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
}

.tr-card--cancelled {
  opacity: 0.65;
}

.tr-card-top {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.tr-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tr-status-badge--draft {
  background: var(--am-bg-raised);
  color: var(--am-text-secondary);
  border: 1px solid var(--am-border);
}

.tr-status-badge--requested {
  background: rgba(34, 197, 94, 0.12);
  color: var(--am-success);
  border: 1px solid var(--am-success);
}

.tr-status-badge--cancelled {
  background: var(--am-danger-bg);
  color: var(--am-danger);
  border: 1px solid var(--am-danger);
}

.tr-card-type {
  font-size: 0.8rem;
  color: var(--am-text-secondary);
  background: var(--am-bg-raised);
  padding: 3px 8px;
  border-radius: var(--am-radius-s);
  border: 1px solid var(--am-border);
}

.tr-card-date {
  margin-left: auto;
  font-size: 0.82rem;
  color: var(--am-text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.tr-card-route {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: var(--am-space-s) var(--am-space-m);
  background: var(--am-bg-base);
  border-radius: var(--am-radius-s);
  border: 1px solid var(--am-border);
}

.tr-card-route-empty {
  font-size: 0.82rem;
  color: var(--am-text-secondary);
  font-style: italic;
}

.tr-route-item {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
}

.tr-route-icon {
  font-size: 0.9rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.tr-route-icon--from { color: var(--am-accent); }
.tr-route-icon--to   { color: var(--am-success); }

.tr-route-addr {
  font-size: 0.875rem;
  color: var(--am-text-primary);
  line-height: 1.4;
}

.tr-route-arrow {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  padding-left: 3px;
  color: var(--am-text-secondary);
  font-size: 0.8rem;
}

.tr-round-trip-chip {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 99px;
  background: var(--am-accent-bg);
  color: var(--am-accent);
  border: 1px solid rgba(255, 214, 0, 0.3);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tr-card-actions {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

.tr-card-btn {
  font-size: 0.82rem;
  min-height: 36px;
  padding: 0 var(--am-space-m);
}

.tr-card-btn--danger:hover {
  background: var(--am-danger-bg);
  color: var(--am-danger);
  border-color: var(--am-danger);
}

.tr-cancelled-note {
  font-size: 0.78rem;
  color: var(--am-text-secondary);
  font-style: italic;
}

/* Alerts */
.tr-alert {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  border-radius: var(--am-radius-s);
  font-size: 0.875rem;
}

.tr-alert--success {
  background: var(--am-success-bg);
  border: 1px solid var(--am-success);
  color: var(--am-success);
}

.tr-alert--error {
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  color: var(--am-danger);
}

/* Form */
.tr-form {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

.tr-section {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.tr-section-title {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 1rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.tr-section-title .pi { color: var(--am-accent); font-size: 1rem; }

.tr-section-desc {
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* For-who */
.tr-for-self {
  display: flex;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

.tr-for-btn {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  padding: 10px var(--am-space-m);
  border-radius: var(--am-radius-s);
  border: 2px solid var(--am-border);
  background: var(--am-bg-raised);
  color: var(--am-text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  min-height: 44px;
  position: relative;
  transition: all var(--am-transition);
}

.tr-for-btn--active {
  border-color: var(--am-accent);
  background: var(--am-accent-bg);
  color: var(--am-text-primary);
  font-weight: 600;
}

.tr-for-btn--soon {
  opacity: 0.5;
  cursor: default;
}

.soon-chip {
  margin-left: var(--am-space-s);
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 99px;
  background: var(--am-bg-base);
  color: var(--am-text-secondary);
  border: 1px solid var(--am-border);
  text-transform: uppercase;
}

/* Transport type grid */
.tr-type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--am-space-s);
}

.tr-type-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 2px solid var(--am-border);
  border-radius: var(--am-radius-m);
  cursor: pointer;
  text-align: left;
  transition: border-color var(--am-transition), background var(--am-transition);
  min-height: 80px;
}

.tr-type-card:hover { border-color: var(--am-border-strong); }

.tr-type-card--active {
  border-color: var(--am-accent);
  background: var(--am-accent-bg);
}

.tr-type-label {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--am-text-primary);
}

.tr-type-desc {
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  line-height: 1.4;
}

.tr-type-warning {
  font-size: 0.7rem;
  color: var(--am-danger);
  display: flex;
  align-items: flex-start;
  gap: 4px;
  margin-top: 2px;
}

/* Fields */
.tr-field-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--am-space-m);
}

@media (max-width: 680px) {
  .tr-field-row { grid-template-columns: 1fr; }
}

.tr-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tr-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
}

.tr-required { color: var(--am-danger); }

.tr-optional-badge {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 99px;
  background: var(--am-bg-raised);
  color: var(--am-text-secondary);
  border: 1px solid var(--am-border);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tr-field-hint {
  font-size: 0.78rem;
  color: var(--am-text-secondary);
  margin: 0;
  line-height: 1.4;
}

.tr-input {
  height: 44px;
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.9rem;
  padding: 0 var(--am-space-m);
  outline: none;
  transition: border-color var(--am-transition);
  box-sizing: border-box;
  width: 100%;
}

.tr-input:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.tr-textarea {
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.9rem;
  padding: var(--am-space-s) var(--am-space-m);
  outline: none;
  resize: vertical;
  transition: border-color var(--am-transition);
  width: 100%;
  min-height: 70px;
  box-sizing: border-box;
  font-family: inherit;
}

.tr-textarea:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

/* Toggle */
.tr-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  min-height: 56px;
}

.tr-toggle-label {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
  flex: 1;
}

.tr-toggle-sub {
  font-size: 0.78rem;
  font-weight: 400;
  color: var(--am-text-secondary);
}

.tr-toggle-btn {
  position: relative;
  width: 44px;
  height: 24px;
  border-radius: 99px;
  background: var(--am-border-strong);
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  transition: background var(--am-transition);
  padding: 0;
}

.tr-toggle-btn--on { background: var(--am-accent); }

.tr-toggle-knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  transition: transform var(--am-transition);
  display: block;
}

.tr-toggle-btn--on .tr-toggle-knob { transform: translateX(20px); }

.tr-return-block {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
  padding-left: var(--am-space-m);
  border-left: 2px solid var(--am-accent);
}

/* Requirement cards */
.tr-req-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--am-space-s);
}

.tr-req-card {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 2px solid var(--am-border);
  border-radius: var(--am-radius-m);
  cursor: pointer;
  text-align: left;
  transition: border-color var(--am-transition), background var(--am-transition);
  min-height: 72px;
  position: relative;
}

.tr-req-card:hover { border-color: var(--am-border-strong); }

.tr-req-card--active {
  border-color: var(--am-accent);
  background: var(--am-accent-bg);
}

.tr-req-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--am-radius-s);
  background: var(--am-bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--am-text-secondary);
  font-size: 1rem;
  transition: color var(--am-transition), background var(--am-transition);
}

.tr-req-card--active .tr-req-icon {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
}

.tr-req-text { flex: 1; min-width: 0; }

.tr-req-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin-bottom: 2px;
}

.tr-req-desc {
  display: block;
  font-size: 0.72rem;
  color: var(--am-text-secondary);
  line-height: 1.3;
}

.tr-req-check {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--am-border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: transparent;
  font-size: 0.6rem;
  transition: all var(--am-transition);
}

.tr-req-card--active .tr-req-check {
  background: var(--am-accent);
  border-color: var(--am-accent);
  color: var(--am-text-on-accent);
}

/* Save bar */
.tr-save-bar {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  flex-wrap: wrap;
  padding: var(--am-space-m) 0;
}
</style>
