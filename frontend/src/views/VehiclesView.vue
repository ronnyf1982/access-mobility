<template>
  <div class="veh-page">
    <!-- Seitenheader -->
    <div class="veh-header">
      <div>
        <h1 class="veh-title">Fahrzeuge</h1>
        <p class="veh-subtitle">
          Pflegen Sie hier Fahrzeuge und deren Ausstattung. Diese Angaben werden später genutzt,
          um passende Fahrten, Touren und Fahrzeuge vorzuschlagen.
        </p>
      </div>
      <button
        v-if="view === 'list'"
        class="am-btn am-btn-primary veh-add-btn"
        @click="openCreate"
        aria-label="Neues Fahrzeug anlegen"
      >
        <i class="pi pi-plus" aria-hidden="true"></i>
        Fahrzeug anlegen
      </button>
    </div>

    <!-- ── Listenansicht ────────────────────────────────────────────────── -->
    <template v-if="view === 'list'">
      <!-- Filter-Tabs -->
      <div class="veh-filter-bar" role="group" aria-label="Fahrzeugliste filtern">
        <button
          v-for="f in FILTER_OPTIONS"
          :key="f.value"
          class="veh-filter-btn"
          :class="{ 'veh-filter-btn--active': filterMode === f.value }"
          @click="filterMode = f.value"
          :aria-pressed="filterMode === f.value"
        >
          {{ f.label }}
          <span class="veh-filter-count">{{ filterCounts[f.value] }}</span>
        </button>
      </div>

      <div
        v-if="store.loading"
        class="veh-loading"
        role="status"
        aria-live="polite"
        aria-label="Fahrzeuge werden geladen"
      >
        <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
        Fahrzeuge werden geladen …
      </div>

      <div v-else-if="store.vehicles.length === 0" class="veh-empty am-card">
        <i class="pi pi-car veh-empty-icon" aria-hidden="true"></i>
        <p>Noch keine Fahrzeuge angelegt.</p>
        <button class="am-btn am-btn-primary" @click="openCreate">Erstes Fahrzeug anlegen</button>
      </div>

      <div v-else-if="filteredVehicles.length === 0" class="veh-empty am-card">
        <i class="pi pi-filter veh-empty-icon" aria-hidden="true"></i>
        <p>Keine Fahrzeuge in dieser Ansicht.</p>
      </div>

      <div v-else class="veh-list" role="list" aria-label="Fahrzeugliste">
        <div
          v-for="vehicle in filteredVehicles"
          :key="vehicle.id"
          class="veh-card am-card"
          :class="{ 'veh-card--inactive': !vehicle.is_active }"
          role="listitem"
        >
          <!-- Kopfzeile der Karte -->
          <div class="veh-card-head">
            <div class="veh-card-title-group">
              <span class="veh-card-name">{{ vehicle.name }}</span>
              <span class="veh-card-plate">{{ vehicle.license_plate }}</span>
            </div>
            <div class="veh-card-badges">
              <span class="am-badge am-badge-neutral">{{ vehicleTypeLabel(vehicle.vehicle_type) }}</span>
              <span
                v-if="!vehicle.is_active"
                class="am-badge"
                style="background:var(--am-danger-bg);color:var(--am-danger);border:1px solid var(--am-danger)"
              >Inaktiv</span>
            </div>
          </div>

          <!-- Kapazität -->
          <div class="veh-card-caps">
            <span class="veh-cap-item" :title="`${vehicle.seat_count} Sitzplätze`">
              <i class="pi pi-users" aria-hidden="true"></i>
              {{ vehicle.seat_count }} Sitz
            </span>
            <span class="veh-cap-item" :title="`${vehicle.wheelchair_space_count} Rollstuhlplätze`">
              <i class="pi pi-circle-fill" aria-hidden="true"></i>
              {{ vehicle.wheelchair_space_count }} Rollstuhl
            </span>
            <span v-if="vehicle.escort_seat_count" class="veh-cap-item" :title="`${vehicle.escort_seat_count} Begleitplätze`">
              <i class="pi pi-heart" aria-hidden="true"></i>
              {{ vehicle.escort_seat_count }} Begleitung
            </span>
          </div>

          <!-- Ausstattungs-Chips -->
          <div class="veh-card-equip" role="group" aria-label="Ausstattung">
            <span v-if="vehicle.has_ramp"                     class="veh-equip-chip"><i class="pi pi-sort-amount-up-alt" aria-hidden="true"></i> Rampe</span>
            <span v-if="vehicle.has_lift"                     class="veh-equip-chip"><i class="pi pi-chevron-circle-up" aria-hidden="true"></i> Lift</span>
            <span v-if="vehicle.has_wheelchair_restraint"     class="veh-equip-chip"><i class="pi pi-lock" aria-hidden="true"></i> Rollstuhl-Sicherung</span>
            <span v-if="vehicle.supports_electric_wheelchair" class="veh-equip-chip"><i class="pi pi-bolt" aria-hidden="true"></i> E-Rollstuhl</span>
            <span v-if="vehicle.supports_stretcher_transport" class="veh-equip-chip"><i class="pi pi-minus" aria-hidden="true"></i> Liegendtransport</span>
            <span v-if="vehicle.has_child_seat"               class="veh-equip-chip"><i class="pi pi-star" aria-hidden="true"></i> Kindersitz</span>
            <span v-if="vehicle.has_low_entry"                class="veh-equip-chip"><i class="pi pi-arrow-down" aria-hidden="true"></i> Niedriger Einstieg</span>
            <span v-if="vehicle.has_extra_wide_door"          class="veh-equip-chip"><i class="pi pi-arrows-h" aria-hidden="true"></i> Breite Tür</span>
            <span v-if="vehicle.supports_non_emergency_medical_transport" class="veh-equip-chip veh-equip-chip--medical"><i class="pi pi-star" aria-hidden="true"></i> KTP</span>
            <span
              v-if="!vehicle.has_ramp && !vehicle.has_lift && !vehicle.has_wheelchair_restraint && !vehicle.supports_electric_wheelchair && !vehicle.supports_stretcher_transport && !vehicle.has_child_seat && !vehicle.has_low_entry && !vehicle.has_extra_wide_door && !vehicle.supports_non_emergency_medical_transport"
              class="veh-equip-none"
            >Keine Sonderausstattung</span>
          </div>

          <!-- Bestätigungs-Banner für endgültiges Löschen -->
          <div v-if="pendingDeleteId === vehicle.id" class="veh-delete-confirm" role="alert">
            <i class="pi pi-exclamation-triangle" aria-hidden="true"></i>
            <span>Fahrzeug <strong>{{ vehicle.name }}</strong> endgültig löschen? Dies kann nicht rückgängig gemacht werden.</span>
            <div class="veh-delete-confirm-actions">
              <button
                class="am-btn am-btn-ghost veh-action-btn veh-action-btn--danger"
                @click="handlePermanentDelete(vehicle.id)"
                :aria-label="`${vehicle.name} endgültig löschen bestätigen`"
              >
                <i class="pi pi-trash" aria-hidden="true"></i>
                Endgültig löschen
              </button>
              <button
                class="am-btn am-btn-ghost veh-action-btn"
                @click="pendingDeleteId = null"
                aria-label="Löschen abbrechen"
              >
                Abbrechen
              </button>
            </div>
          </div>

          <!-- Aktionen -->
          <div v-else class="veh-card-actions">
            <button
              class="am-btn am-btn-ghost veh-action-btn"
              @click="openEdit(vehicle)"
              :aria-label="`${vehicle.name} bearbeiten`"
            >
              <i class="pi pi-pencil" aria-hidden="true"></i>
              Bearbeiten
            </button>
            <button
              v-if="vehicle.is_active"
              class="am-btn am-btn-ghost veh-action-btn veh-action-btn--danger"
              @click="handleDeactivate(vehicle)"
              :aria-label="`${vehicle.name} deaktivieren`"
            >
              <i class="pi pi-ban" aria-hidden="true"></i>
              Deaktivieren
            </button>
            <button
              v-else
              class="am-btn am-btn-ghost veh-action-btn veh-action-btn--success"
              @click="handleReactivate(vehicle)"
              :aria-label="`${vehicle.name} wieder aktivieren`"
            >
              <i class="pi pi-check-circle" aria-hidden="true"></i>
              Wieder aktivieren
            </button>
            <button
              class="am-btn am-btn-ghost veh-action-btn veh-action-btn--danger"
              @click="pendingDeleteId = vehicle.id"
              :aria-label="`${vehicle.name} endgültig löschen`"
            >
              <i class="pi pi-trash" aria-hidden="true"></i>
              Löschen
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Formular (Erstellen / Bearbeiten) ──────────────────────────── -->
    <template v-if="view === 'form'">
      <div class="veh-form-header">
        <button
          class="am-btn am-btn-ghost"
          @click="closeForm"
          aria-label="Zurück zur Fahrzeugliste"
        >
          <i class="pi pi-arrow-left" aria-hidden="true"></i>
          Zurück zur Liste
        </button>
        <h2 class="veh-form-title">
          {{ editingId ? 'Fahrzeug bearbeiten' : 'Neues Fahrzeug anlegen' }}
        </h2>
      </div>

      <!-- Erfolg / Fehler -->
      <div v-if="saveSuccess" class="veh-alert veh-alert--success" role="alert" aria-live="assertive">
        <i class="pi pi-check-circle" aria-hidden="true"></i>
        {{ editingId ? 'Fahrzeug wurde gespeichert.' : 'Fahrzeug wurde angelegt.' }}
      </div>
      <div v-if="saveError" class="veh-alert veh-alert--error" role="alert" aria-live="assertive">
        <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
        {{ saveError }}
      </div>

      <form class="veh-form" @submit.prevent="handleSave" novalidate>
        <!-- ── Stammdaten ── -->
        <section class="am-card veh-section" aria-labelledby="f-basis">
          <h3 id="f-basis" class="veh-section-title">
            <i class="pi pi-car" aria-hidden="true"></i>
            Fahrzeugdaten
          </h3>

          <div class="veh-field-row">
            <div class="veh-field">
              <label for="f-name" class="veh-label">
                Bezeichnung <span class="veh-required" aria-hidden="true">*</span>
              </label>
              <input
                id="f-name"
                v-model="form.name"
                type="text"
                class="veh-input"
                required
                aria-required="true"
                placeholder="z. B. Rollstuhlbus 1"
              />
            </div>
            <div class="veh-field">
              <label for="f-plate" class="veh-label">
                Kennzeichen <span class="veh-required" aria-hidden="true">*</span>
              </label>
              <input
                id="f-plate"
                v-model="form.license_plate"
                type="text"
                class="veh-input"
                required
                aria-required="true"
                placeholder="z. B. B-AB 1234"
              />
            </div>
          </div>

          <div class="veh-field">
            <label for="f-type" class="veh-label">
              Fahrzeugtyp <span class="veh-required" aria-hidden="true">*</span>
            </label>
            <select id="f-type" v-model="form.vehicle_type" class="veh-select" required aria-required="true">
              <option value="" disabled>Bitte wählen …</option>
              <option v-for="t in VEHICLE_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>

          <div class="veh-field">
            <label for="f-base" class="veh-label">Standort / Basisadresse</label>
            <input
              id="f-base"
              v-model="form.home_base_address"
              type="text"
              class="veh-input"
              placeholder="z. B. Musterstraße 1, 10115 Berlin"
            />
          </div>
        </section>

        <!-- ── Kapazität ── -->
        <section class="am-card veh-section" aria-labelledby="f-kap">
          <h3 id="f-kap" class="veh-section-title">
            <i class="pi pi-users" aria-hidden="true"></i>
            Kapazität
          </h3>
          <div class="veh-field-row veh-field-row--3">
            <div class="veh-field">
              <label for="f-seats" class="veh-label">Sitzplätze</label>
              <input id="f-seats" v-model.number="form.seat_count" type="number" min="0" class="veh-input" aria-label="Anzahl Sitzplätze" />
            </div>
            <div class="veh-field">
              <label for="f-wc" class="veh-label">Rollstuhlplätze</label>
              <input id="f-wc" v-model.number="form.wheelchair_space_count" type="number" min="0" class="veh-input" aria-label="Anzahl Rollstuhlplätze" />
            </div>
            <div class="veh-field">
              <label for="f-escort" class="veh-label">Begleitplätze</label>
              <input id="f-escort" v-model.number="form.escort_seat_count" type="number" min="0" class="veh-input" aria-label="Anzahl Begleitplätze" />
            </div>
          </div>
        </section>

        <!-- ── Ausstattung ── -->
        <section class="am-card veh-section" aria-labelledby="f-equip">
          <h3 id="f-equip" class="veh-section-title">
            <i class="pi pi-wrench" aria-hidden="true"></i>
            Ausstattung
          </h3>
          <p class="veh-section-desc">Wählen Sie alles aus, was vorhanden ist.</p>

          <div class="veh-equip-grid" role="group" aria-label="Ausstattungsmerkmale">
            <button
              v-for="opt in EQUIPMENT_OPTIONS"
              :key="opt.key"
              type="button"
              class="veh-equip-card"
              :class="{ 'veh-equip-card--active': form[opt.key as EquipKey] as boolean }"
              role="checkbox"
              :aria-checked="!!(form[opt.key as EquipKey] as boolean)"
              :aria-label="`${opt.label}: ${opt.description}`"
              @click="toggleEquip(opt.key as EquipKey)"
            >
              <div class="veh-equip-icon" aria-hidden="true">
                <i :class="['pi', opt.icon]"></i>
              </div>
              <div class="veh-equip-text">
                <span class="veh-equip-label">{{ opt.label }}</span>
                <span class="veh-equip-desc">{{ opt.description }}</span>
              </div>
              <div class="veh-equip-check" aria-hidden="true">
                <i class="pi pi-check"></i>
              </div>
            </button>
          </div>
        </section>

        <!-- ── Medizinische Ausstattung / Krankentransport ── -->
        <section class="am-card veh-section" aria-labelledby="f-medical">
          <h3 id="f-medical" class="veh-section-title">
            <i class="pi pi-heart" aria-hidden="true"></i>
            Medizinische Ausstattung / Krankentransport
          </h3>
          <p class="veh-section-desc">
            Nur ausfüllen, wenn das Fahrzeug für Liegend- oder qualifizierten Krankentransport ausgestattet ist.
            Kein Rettungsdienst / Notfallmedizin.
          </p>

          <div class="veh-equip-grid" role="group" aria-label="Medizinische Ausstattung">
            <button
              v-for="opt in MEDICAL_OPTIONS"
              :key="opt.key"
              type="button"
              class="veh-equip-card"
              :class="{ 'veh-equip-card--active': form[opt.key as MedKey] as boolean }"
              role="checkbox"
              :aria-checked="!!(form[opt.key as MedKey] as boolean)"
              :aria-label="`${opt.label}: ${opt.description}`"
              @click="toggleMed(opt.key as MedKey)"
            >
              <div class="veh-equip-icon" aria-hidden="true">
                <i :class="['pi', opt.icon]"></i>
              </div>
              <div class="veh-equip-text">
                <span class="veh-equip-label">{{ opt.label }}</span>
                <span class="veh-equip-desc">{{ opt.description }}</span>
              </div>
              <div class="veh-equip-check" aria-hidden="true">
                <i class="pi pi-check"></i>
              </div>
            </button>
          </div>

          <div class="veh-field">
            <label for="f-compartment-notes" class="veh-label">Hinweise zum Patientenraum</label>
            <textarea id="f-compartment-notes" v-model="form.patient_compartment_notes" class="veh-textarea" rows="2" placeholder="z. B. Patientenraum klimatisiert, Trennwand vorhanden"></textarea>
          </div>
        </section>

        <!-- ── Maße, Gewicht & Zufahrt ── -->
        <section class="am-card veh-section" aria-labelledby="f-dimensions">
          <h3 id="f-dimensions" class="veh-section-title">
            <i class="pi pi-map" aria-hidden="true"></i>
            Maße, Gewicht &amp; Zufahrt
          </h3>
          <p class="veh-section-desc">
            Diese Angaben helfen später bei der Routenplanung und Stellplatzprüfung.
            Alle Felder sind freiwillig.
          </p>

          <div class="veh-field-row veh-field-row--3">
            <div class="veh-field">
              <label for="f-length" class="veh-label">Länge (cm)</label>
              <input id="f-length" v-model.number="form.vehicle_length_cm" type="number" min="0" class="veh-input" placeholder="z. B. 699" />
            </div>
            <div class="veh-field">
              <label for="f-width" class="veh-label">Breite (cm)</label>
              <input id="f-width" v-model.number="form.vehicle_width_cm" type="number" min="0" class="veh-input" placeholder="z. B. 198" />
            </div>
            <div class="veh-field">
              <label for="f-width-mirrors" class="veh-label">Breite mit Spiegeln (cm)</label>
              <input id="f-width-mirrors" v-model.number="form.vehicle_width_with_mirrors_cm" type="number" min="0" class="veh-input" placeholder="z. B. 224" />
            </div>
          </div>

          <div class="veh-field-row veh-field-row--3">
            <div class="veh-field">
              <label for="f-height" class="veh-label">Höhe (cm)</label>
              <input id="f-height" v-model.number="form.vehicle_height_cm" type="number" min="0" class="veh-input" placeholder="z. B. 270" />
            </div>
            <div class="veh-field">
              <label for="f-wheelbase" class="veh-label">Radstand (cm)</label>
              <input id="f-wheelbase" v-model.number="form.wheelbase_cm" type="number" min="0" class="veh-input" placeholder="z. B. 391" />
            </div>
            <div class="veh-field">
              <label for="f-turning" class="veh-label">Wendekreis (m)</label>
              <input id="f-turning" v-model.number="form.turning_circle_m" type="number" min="0" step="0.1" class="veh-input" placeholder="z. B. 13.4" />
            </div>
          </div>

          <div class="veh-field-row veh-field-row--3">
            <div class="veh-field">
              <label for="f-empty-weight" class="veh-label">Leergewicht (kg)</label>
              <input id="f-empty-weight" v-model.number="form.empty_weight_kg" type="number" min="0" class="veh-input" placeholder="z. B. 2480" />
            </div>
            <div class="veh-field">
              <label for="f-gvw" class="veh-label">Zul. Gesamtgewicht (kg)</label>
              <input id="f-gvw" v-model.number="form.gross_vehicle_weight_kg" type="number" min="0" class="veh-input" placeholder="z. B. 5000" />
            </div>
            <div class="veh-field">
              <label for="f-payload" class="veh-label">Nutzlast (kg)</label>
              <input id="f-payload" v-model.number="form.payload_capacity_kg" type="number" min="0" class="veh-input" placeholder="z. B. 2520" />
            </div>
          </div>

          <div class="veh-equip-grid" role="group" aria-label="Zufahrtseigenschaften">
            <button
              v-for="opt in DIMENSION_ACCESS_OPTIONS"
              :key="opt.key"
              type="button"
              class="veh-equip-card"
              :class="{ 'veh-equip-card--active': form[opt.key as DimKey] as boolean }"
              role="checkbox"
              :aria-checked="!!(form[opt.key as DimKey] as boolean)"
              :aria-label="`${opt.label}: ${opt.description}`"
              @click="toggleDim(opt.key as DimKey)"
            >
              <div class="veh-equip-icon" aria-hidden="true">
                <i :class="['pi', opt.icon]"></i>
              </div>
              <div class="veh-equip-text">
                <span class="veh-equip-label">{{ opt.label }}</span>
                <span class="veh-equip-desc">{{ opt.description }}</span>
              </div>
              <div class="veh-equip-check" aria-hidden="true">
                <i class="pi pi-check"></i>
              </div>
            </button>
          </div>

          <div class="veh-field">
            <label for="f-access-notes" class="veh-label">Zufahrtshinweise</label>
            <textarea id="f-access-notes" v-model="form.access_restriction_notes" class="veh-textarea" rows="2" placeholder="z. B. nur Stellplatz P1-P3 geeignet, keine Tiefgarage unter 2 m"></textarea>
          </div>
        </section>

        <!-- ── Hinweise ── -->
        <section class="am-card veh-section" aria-labelledby="f-notes">
          <h3 id="f-notes" class="veh-section-title">
            <i class="pi pi-comment" aria-hidden="true"></i>
            Hinweise
          </h3>
          <div class="veh-field">
            <label for="f-equip-notes" class="veh-label">Ausstattungshinweise</label>
            <textarea id="f-equip-notes" v-model="form.equipment_notes" class="veh-textarea" rows="2" placeholder="z. B. Rampe manuell, Lift max. 250 kg"></textarea>
          </div>
          <div class="veh-field">
            <label for="f-gen-notes" class="veh-label">Allgemeine Hinweise</label>
            <textarea id="f-gen-notes" v-model="form.general_notes" class="veh-textarea" rows="2"></textarea>
          </div>
        </section>

        <!-- ── Speichern ── -->
        <div class="veh-save-bar">
          <button type="submit" class="am-btn am-btn-primary veh-save-btn" :disabled="store.saving" :aria-busy="store.saving">
            <i v-if="store.saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
            <i v-else class="pi pi-save" aria-hidden="true"></i>
            {{ store.saving ? 'Wird gespeichert …' : (editingId ? 'Änderungen speichern' : 'Fahrzeug anlegen') }}
          </button>
          <button type="button" class="am-btn am-btn-ghost" @click="closeForm">
            Abbrechen
          </button>
        </div>
      </form>
    </template>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useVehicleStore } from '@/stores/vehicle'
import type { Vehicle, VehicleTypeName } from '@/types'
import { VEHICLE_TYPE_LABELS } from '@/types'

const store = useVehicleStore()

type View = 'list' | 'form'
const view = ref<View>('list')
const editingId = ref<string | null>(null)
const saveSuccess = ref(false)
const saveError = ref('')
const pendingDeleteId = ref<string | null>(null)

type FilterMode = 'all' | 'active' | 'inactive'
const filterMode = ref<FilterMode>('all')

const FILTER_OPTIONS: Array<{ value: FilterMode; label: string }> = [
  { value: 'all', label: 'Alle' },
  { value: 'active', label: 'Aktiv' },
  { value: 'inactive', label: 'Inaktiv' },
]

const filterCounts = computed(() => ({
  all: store.vehicles.length,
  active: store.vehicles.filter((v) => v.is_active).length,
  inactive: store.vehicles.filter((v) => !v.is_active).length,
}))

const filteredVehicles = computed(() => {
  if (filterMode.value === 'active') return store.vehicles.filter((v) => v.is_active)
  if (filterMode.value === 'inactive') return store.vehicles.filter((v) => !v.is_active)
  return store.vehicles
})

const VEHICLE_TYPES = Object.entries(VEHICLE_TYPE_LABELS).map(([value, label]) => ({ value: value as VehicleTypeName, label }))

type EquipKey =
  | 'has_ramp'
  | 'has_lift'
  | 'has_wheelchair_restraint'
  | 'supports_electric_wheelchair'
  | 'supports_stretcher_transport'
  | 'has_child_seat'
  | 'has_low_entry'
  | 'has_extra_wide_door'

type MedKey =
  | 'has_stretcher'
  | 'has_stretcher_mount'
  | 'has_medical_equipment_storage'
  | 'has_oxygen_mount'
  | 'has_first_aid_kit'
  | 'has_hygiene_equipment'
  | 'supports_non_emergency_medical_transport'
  | 'has_transport_chair'
  | 'has_infusion_mount'
  | 'supports_two_person_crew'

type DimKey =
  | 'requires_large_parking_space'
  | 'suitable_for_narrow_streets'
  | 'suitable_for_underground_parking'
  | 'has_parking_assist'

const EQUIPMENT_OPTIONS: Array<{ key: EquipKey; label: string; icon: string; description: string }> = [
  { key: 'has_ramp',                     label: 'Rampe',                    icon: 'pi-sort-amount-up-alt', description: 'Auffahrrampe vorhanden (manuell oder elektrisch)' },
  { key: 'has_lift',                     label: 'Lift / Hebebühne',         icon: 'pi-chevron-circle-up',  description: 'Elektrische Hebebühne für Rollstühle' },
  { key: 'has_wheelchair_restraint',     label: 'Rollstuhl-Sicherung',      icon: 'pi-lock',               description: 'Gurtsystem zur Sicherung von Rollstühlen' },
  { key: 'supports_electric_wheelchair', label: 'Elektrorollstuhl geeignet',icon: 'pi-bolt',               description: 'Hebebühne und Fixierung für Elektrorollstühle ausgelegt' },
  { key: 'supports_stretcher_transport', label: 'Liegendtransport',         icon: 'pi-minus',              description: 'Transportliege eingebaut oder montierbar' },
  { key: 'has_child_seat',               label: 'Kindersitz',               icon: 'pi-star',               description: 'Kindersitz vorhanden oder nachrüstbar' },
  { key: 'has_low_entry',                label: 'Niedriger Einstieg',       icon: 'pi-arrow-down',         description: 'Fahrzeug hat abgesenkten Einstieg oder Kneeling-Funktion' },
  { key: 'has_extra_wide_door',          label: 'Extra breite Tür',         icon: 'pi-arrows-h',           description: 'Seitentür besonders breit — geeignet für große Rollstühle' },
]

const MEDICAL_OPTIONS: Array<{ key: MedKey; label: string; icon: string; description: string }> = [
  { key: 'has_stretcher',                           label: 'Transportliege',              icon: 'pi-minus',              description: 'Fest eingebaute oder mitgeführte Transportliege vorhanden' },
  { key: 'has_stretcher_mount',                     label: 'Liegenaufnahme',              icon: 'pi-lock',               description: 'Befestigungssystem für Krankentragen / Tragestühle verbaut' },
  { key: 'has_medical_equipment_storage',           label: 'Med. Stauraum',               icon: 'pi-inbox',              description: 'Abgetrennter Stauraum für medizinisches Equipment' },
  { key: 'has_oxygen_mount',                        label: 'Sauerstoffhalterung',         icon: 'pi-circle',             description: 'Halterung und Sicherung für mobile Sauerstoffgeräte' },
  { key: 'has_first_aid_kit',                       label: 'Erste-Hilfe-Ausstattung',     icon: 'pi-heart',              description: 'Erste-Hilfe-Koffer nach DIN 13157 oder höher vorhanden' },
  { key: 'has_hygiene_equipment',                   label: 'Hygienebedarf',               icon: 'pi-shield',             description: 'Schutzausrüstung, Desinfektionsmittel, Einwegmaterial' },
  { key: 'supports_non_emergency_medical_transport',label: 'Qual. Krankentransport (KTP)',icon: 'pi-star',               description: 'Fahrzeug für qualifizierten Krankentransport ausgestattet (nicht Rettung)' },
  { key: 'has_transport_chair',                     label: 'Tragestuhl',                  icon: 'pi-arrow-circle-up',    description: 'Tragestuhl (Transportrollstuhl) für enge Zugänge vorhanden' },
  { key: 'has_infusion_mount',                      label: 'Infusionshalterung',           icon: 'pi-sort-amount-up-alt', description: 'Halterung für Infusionsständer im Patientenraum vorhanden' },
  { key: 'supports_two_person_crew',                label: 'Zweimann-Besatzung',           icon: 'pi-users',              description: 'Fahrzeug ist für Besatzung mit zwei Personen ausgelegt' },
]

const DIMENSION_ACCESS_OPTIONS: Array<{ key: DimKey; label: string; icon: string; description: string }> = [
  { key: 'requires_large_parking_space',     label: 'Großer Stellplatz erforderlich',icon: 'pi-map',        description: 'Fahrzeug benötigt überbreiten oder überlangen Parkplatz' },
  { key: 'suitable_for_narrow_streets',      label: 'Geeignet für enge Straßen',     icon: 'pi-arrows-h',   description: 'Fahrzeug ist schmal genug für einspurige Zuwegungen' },
  { key: 'suitable_for_underground_parking', label: 'Tiefgaragengeeignet',            icon: 'pi-arrow-down', description: 'Fahrzeughöhe erlaubt Zufahrt in Tiefgaragen (≤ 2,0 m)' },
  { key: 'has_parking_assist',               label: 'Einparkhilfe',                  icon: 'pi-wifi',       description: 'Fahrzeug hat Parksensor oder Kamerasystem' },
]

function getDefaultOrgId(): string {
  return store.vehicles[0]?.organization_id ?? ''
}

const EMPTY_FORM = () => ({
  name: '',
  license_plate: '',
  vehicle_type: '' as VehicleTypeName | '',
  seat_count: 0,
  wheelchair_space_count: 0,
  escort_seat_count: null as number | null,
  has_ramp: false,
  has_lift: false,
  has_wheelchair_restraint: false,
  supports_electric_wheelchair: false,
  supports_stretcher_transport: false,
  has_child_seat: false,
  has_low_entry: false,
  has_extra_wide_door: false,
  has_stretcher: false,
  has_stretcher_mount: false,
  has_medical_equipment_storage: false,
  has_oxygen_mount: false,
  has_first_aid_kit: false,
  has_hygiene_equipment: false,
  supports_non_emergency_medical_transport: false,
  has_transport_chair: false,
  has_infusion_mount: false,
  supports_two_person_crew: false,
  patient_compartment_notes: null as string | null,
  vehicle_length_cm: null as number | null,
  vehicle_width_cm: null as number | null,
  vehicle_width_with_mirrors_cm: null as number | null,
  vehicle_height_cm: null as number | null,
  wheelbase_cm: null as number | null,
  turning_circle_m: null as number | null,
  empty_weight_kg: null as number | null,
  gross_vehicle_weight_kg: null as number | null,
  payload_capacity_kg: null as number | null,
  requires_large_parking_space: false,
  suitable_for_narrow_streets: false,
  suitable_for_underground_parking: false,
  has_parking_assist: false,
  access_restriction_notes: null as string | null,
  home_base_address: null as string | null,
  equipment_notes: null as string | null,
  general_notes: null as string | null,
})

const form = reactive(EMPTY_FORM())

function vehicleTypeLabel(type: VehicleTypeName): string {
  return VEHICLE_TYPE_LABELS[type] ?? type
}

function toggleEquip(key: EquipKey) {
  ;(form[key] as boolean) = !(form[key] as boolean)
}

function toggleMed(key: MedKey) {
  ;(form[key] as boolean) = !(form[key] as boolean)
}

function toggleDim(key: DimKey) {
  ;(form[key] as boolean) = !(form[key] as boolean)
}

function openCreate() {
  Object.assign(form, EMPTY_FORM())
  editingId.value = null
  saveSuccess.value = false
  saveError.value = ''
  view.value = 'form'
}

function openEdit(vehicle: Vehicle) {
  Object.assign(form, {
    name: vehicle.name,
    license_plate: vehicle.license_plate,
    vehicle_type: vehicle.vehicle_type,
    seat_count: vehicle.seat_count,
    wheelchair_space_count: vehicle.wheelchair_space_count,
    escort_seat_count: vehicle.escort_seat_count,
    has_ramp: vehicle.has_ramp,
    has_lift: vehicle.has_lift,
    has_wheelchair_restraint: vehicle.has_wheelchair_restraint,
    supports_electric_wheelchair: vehicle.supports_electric_wheelchair,
    supports_stretcher_transport: vehicle.supports_stretcher_transport,
    has_child_seat: vehicle.has_child_seat,
    has_low_entry: vehicle.has_low_entry,
    has_extra_wide_door: vehicle.has_extra_wide_door,
    has_stretcher: vehicle.has_stretcher,
    has_stretcher_mount: vehicle.has_stretcher_mount,
    has_medical_equipment_storage: vehicle.has_medical_equipment_storage,
    has_oxygen_mount: vehicle.has_oxygen_mount,
    has_first_aid_kit: vehicle.has_first_aid_kit,
    has_hygiene_equipment: vehicle.has_hygiene_equipment,
    supports_non_emergency_medical_transport: vehicle.supports_non_emergency_medical_transport,
    has_transport_chair: vehicle.has_transport_chair,
    has_infusion_mount: vehicle.has_infusion_mount,
    supports_two_person_crew: vehicle.supports_two_person_crew,
    patient_compartment_notes: vehicle.patient_compartment_notes,
    vehicle_length_cm: vehicle.vehicle_length_cm,
    vehicle_width_cm: vehicle.vehicle_width_cm,
    vehicle_width_with_mirrors_cm: vehicle.vehicle_width_with_mirrors_cm,
    vehicle_height_cm: vehicle.vehicle_height_cm,
    wheelbase_cm: vehicle.wheelbase_cm,
    turning_circle_m: vehicle.turning_circle_m,
    empty_weight_kg: vehicle.empty_weight_kg,
    gross_vehicle_weight_kg: vehicle.gross_vehicle_weight_kg,
    payload_capacity_kg: vehicle.payload_capacity_kg,
    requires_large_parking_space: vehicle.requires_large_parking_space,
    suitable_for_narrow_streets: vehicle.suitable_for_narrow_streets,
    suitable_for_underground_parking: vehicle.suitable_for_underground_parking,
    has_parking_assist: vehicle.has_parking_assist,
    access_restriction_notes: vehicle.access_restriction_notes,
    home_base_address: vehicle.home_base_address,
    equipment_notes: vehicle.equipment_notes,
    general_notes: vehicle.general_notes,
  })
  editingId.value = vehicle.id
  saveSuccess.value = false
  saveError.value = ''
  view.value = 'form'
}

function closeForm() {
  view.value = 'list'
  editingId.value = null
  saveSuccess.value = false
  saveError.value = ''
}

async function handleSave() {
  if (!form.name || !form.license_plate || !form.vehicle_type) {
    saveError.value = 'Bitte Bezeichnung, Kennzeichen und Fahrzeugtyp ausfüllen.'
    return
  }
  saveSuccess.value = false
  saveError.value = ''
  try {
    const payload = {
      ...form,
      vehicle_type: form.vehicle_type as VehicleTypeName,
    }
    if (editingId.value) {
      await store.update(editingId.value, payload)
    } else {
      await store.create({
        organization_id: getDefaultOrgId(),
        ...payload,
      })
    }
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
      view.value = 'list'
    }, 1500)
  } catch {
    saveError.value = 'Speichern fehlgeschlagen. Bitte prüfen Sie Ihre Verbindung.'
  }
}

async function handleDeactivate(vehicle: Vehicle) {
  try {
    await store.deactivate(vehicle.id)
  } catch {
    // Fehler still — in Produktion als Toast
  }
}

async function handleReactivate(vehicle: Vehicle) {
  try {
    await store.reactivate(vehicle.id)
  } catch {
    // Fehler still
  }
}

async function handlePermanentDelete(id: string) {
  try {
    await store.permanentDelete(id)
    pendingDeleteId.value = null
  } catch {
    pendingDeleteId.value = null
  }
}

onMounted(() => store.load())
</script>

<style scoped>
.veh-page {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
  max-width: 900px;
}

.veh-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.veh-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.veh-subtitle {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 4px 0 0;
  line-height: 1.5;
}

.veh-add-btn {
  flex-shrink: 0;
  min-height: 44px;
}

/* Filter-Tabs */
.veh-filter-bar {
  display: flex;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

.veh-filter-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--am-space-s);
  padding: 6px 16px;
  border-radius: 99px;
  border: 1px solid var(--am-border-strong);
  background: var(--am-bg-raised);
  color: var(--am-text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all var(--am-transition);
  min-height: 36px;
}

.veh-filter-btn:hover {
  border-color: var(--am-accent);
  color: var(--am-text-primary);
}

.veh-filter-btn--active {
  border-color: var(--am-accent);
  background: var(--am-accent-bg);
  color: var(--am-text-primary);
  font-weight: 600;
}

.veh-filter-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  border-radius: 99px;
  background: var(--am-bg-base);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0 5px;
}

.veh-filter-btn--active .veh-filter-count {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
}

/* Loading / empty */
.veh-loading {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  color: var(--am-text-secondary);
  font-size: 0.9rem;
  padding: var(--am-space-xl);
  justify-content: center;
}

.veh-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--am-space-m);
  padding: var(--am-space-xl);
  text-align: center;
  color: var(--am-text-secondary);
}

.veh-empty-icon {
  font-size: 2.5rem;
  color: var(--am-border-strong);
}

/* List */
.veh-list {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.veh-card {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
  transition: border-color var(--am-transition);
}

.veh-card--inactive {
  opacity: 0.65;
}

.veh-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.veh-card-title-group {
  display: flex;
  align-items: baseline;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

.veh-card-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--am-text-primary);
}

.veh-card-plate {
  font-size: 0.78rem;
  font-family: monospace;
  color: var(--am-text-secondary);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  padding: 1px 8px;
}

.veh-card-badges {
  display: flex;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

/* Kapazität */
.veh-card-caps {
  display: flex;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.veh-cap-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
  color: var(--am-text-secondary);
}

.veh-cap-item .pi {
  font-size: 0.75rem;
  color: var(--am-accent);
}

/* Ausstattungs-Chips */
.veh-card-equip {
  display: flex;
  flex-wrap: wrap;
  gap: var(--am-space-xs);
}

.veh-equip-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 99px;
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.25);
  color: var(--am-text-primary);
}

.veh-equip-chip .pi {
  font-size: 0.65rem;
  color: var(--am-accent);
}

.veh-equip-chip--medical {
  background: color-mix(in srgb, var(--am-danger-bg) 60%, transparent);
  border-color: rgba(220, 80, 80, 0.25);
}

.veh-equip-chip--medical .pi {
  color: var(--am-danger);
}

.veh-equip-none {
  font-size: 0.75rem;
  color: var(--am-text-muted);
  font-style: italic;
}

/* Bestätigungs-Banner */
.veh-delete-confirm {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  border-radius: var(--am-radius-s);
  font-size: 0.85rem;
  color: var(--am-danger);
}

.veh-delete-confirm .pi {
  flex-shrink: 0;
}

.veh-delete-confirm-actions {
  display: flex;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

/* Karten-Aktionen */
.veh-card-actions {
  display: flex;
  gap: var(--am-space-s);
  padding-top: var(--am-space-s);
  border-top: 1px solid var(--am-border);
  flex-wrap: wrap;
}

.veh-action-btn {
  font-size: 0.82rem;
  min-height: 38px;
  padding: 0 var(--am-space-m);
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
}

.veh-action-btn--danger:hover {
  color: var(--am-danger);
  background: var(--am-danger-bg);
  border-color: var(--am-danger);
}

.veh-action-btn--success:hover {
  color: var(--am-success);
  background: var(--am-success-bg);
  border-color: var(--am-success);
}

/* Form */
.veh-form-header {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.veh-form-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.veh-alert {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  border-radius: var(--am-radius-s);
  font-size: 0.875rem;
}

.veh-alert--success {
  background: var(--am-success-bg);
  border: 1px solid var(--am-success);
  color: var(--am-success);
}

.veh-alert--error {
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  color: var(--am-danger);
}

.veh-form {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

.veh-section {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.veh-section-title {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.veh-section-title .pi {
  color: var(--am-accent);
}

.veh-section-desc {
  font-size: 0.82rem;
  color: var(--am-text-secondary);
  margin: 0;
}

.veh-field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--am-space-m);
}

.veh-field-row--3 {
  grid-template-columns: 1fr 1fr 1fr;
}

@media (max-width: 600px) {
  .veh-field-row,
  .veh-field-row--3 {
    grid-template-columns: 1fr;
  }
}

.veh-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.veh-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
}

.veh-required {
  color: var(--am-danger);
  margin-left: 2px;
}

.veh-input,
.veh-select {
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

.veh-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24'%3E%3Cpath fill='%23999' d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.veh-input:focus,
.veh-select:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.veh-textarea {
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.9rem;
  padding: var(--am-space-s) var(--am-space-m);
  outline: none;
  resize: vertical;
  width: 100%;
  min-height: 72px;
  box-sizing: border-box;
  font-family: inherit;
}

.veh-textarea:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

/* Ausstattungs-Grid */
.veh-equip-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--am-space-s);
}

.veh-equip-card {
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
  min-height: 76px;
}

.veh-equip-card:hover {
  border-color: var(--am-border-strong);
}

.veh-equip-card--active {
  border-color: var(--am-accent);
  background: var(--am-accent-bg);
}

.veh-equip-icon {
  width: 38px;
  height: 38px;
  border-radius: var(--am-radius-s);
  background: var(--am-bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1rem;
  color: var(--am-text-secondary);
  transition: background var(--am-transition), color var(--am-transition);
}

.veh-equip-card--active .veh-equip-icon {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
}

.veh-equip-text {
  flex: 1;
  min-width: 0;
}

.veh-equip-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin-bottom: 2px;
}

.veh-equip-desc {
  display: block;
  font-size: 0.72rem;
  color: var(--am-text-secondary);
  line-height: 1.35;
}

.veh-equip-check {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--am-border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  color: transparent;
  font-size: 0.6rem;
  flex-shrink: 0;
  transition: all var(--am-transition);
}

.veh-equip-card--active .veh-equip-check {
  background: var(--am-accent);
  border-color: var(--am-accent);
  color: var(--am-text-on-accent);
}

/* Save bar */
.veh-save-bar {
  display: flex;
  gap: var(--am-space-m);
  flex-wrap: wrap;
  padding: var(--am-space-m) 0;
}

.veh-save-btn {
  min-height: 48px;
  font-size: 0.95rem;
  padding: 0 var(--am-space-xl);
}

.veh-save-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
</style>
