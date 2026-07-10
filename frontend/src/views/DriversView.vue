<template>
  <div class="drv-page">
    <!-- Seitenheader -->
    <div class="drv-header">
      <div>
        <h1 class="drv-title">Fahrer</h1>
        <p class="drv-subtitle">
          Pflegen Sie hier Fahrer und Qualifikationen. Diese Angaben helfen später, Fahrten
          sicher und passend zuzuordnen.
        </p>
      </div>
      <button
        v-if="view === 'list'"
        class="am-btn am-btn-primary drv-add-btn"
        @click="openCreate"
        aria-label="Neues Fahrerprofil anlegen"
      >
        <i class="pi pi-plus" aria-hidden="true"></i>
        Fahrerprofil anlegen
      </button>
    </div>

    <!-- ── Listenansicht ────────────────────────────────────────────────── -->
    <template v-if="view === 'list'">
      <!-- Filter-Tabs -->
      <div class="drv-filter-bar" role="group" aria-label="Fahrerliste filtern">
        <button
          v-for="f in FILTER_OPTIONS"
          :key="f.value"
          class="drv-filter-btn"
          :class="{ 'drv-filter-btn--active': filterMode === f.value }"
          @click="filterMode = f.value"
          :aria-pressed="filterMode === f.value"
        >
          {{ f.label }}
          <span class="drv-filter-count">{{ filterCounts[f.value] }}</span>
        </button>
      </div>

      <div
        v-if="store.loading"
        class="drv-loading"
        role="status"
        aria-live="polite"
        aria-label="Fahrer werden geladen"
      >
        <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
        Fahrer werden geladen …
      </div>

      <div v-else-if="store.drivers.length === 0" class="drv-empty am-card">
        <i class="pi pi-id-card drv-empty-icon" aria-hidden="true"></i>
        <p>Noch keine Fahrerprofile angelegt.</p>
        <button class="am-btn am-btn-primary" @click="openCreate">Erstes Fahrerprofil anlegen</button>
      </div>

      <div v-else-if="filteredDrivers.length === 0" class="drv-empty am-card">
        <i class="pi pi-filter drv-empty-icon" aria-hidden="true"></i>
        <p>Keine Fahrer in dieser Ansicht.</p>
      </div>

      <div v-else class="drv-list" role="list" aria-label="Fahrerliste">
        <div
          v-for="driver in filteredDrivers"
          :key="driver.id"
          class="drv-card am-card"
          :class="{ 'drv-card--inactive': !driver.is_active }"
          role="listitem"
        >
          <!-- Kopfzeile -->
          <div class="drv-card-head">
            <div class="drv-card-avatar" aria-hidden="true">{{ initials(driver.display_name) }}</div>
            <div class="drv-card-info">
              <span class="drv-card-name">{{ driver.display_name }}</span>
              <span v-if="driver.phone" class="drv-card-phone">{{ driver.phone }}</span>
            </div>
            <span
              v-if="!driver.is_active"
              class="am-badge"
              style="background:var(--am-danger-bg);color:var(--am-danger);border:1px solid var(--am-danger)"
            >Inaktiv</span>
          </div>

          <!-- Qualifikations-Badges -->
          <div class="drv-card-quals" role="group" aria-label="Qualifikationen">
            <span v-for="q in activeQuals(driver)" :key="q.key" class="drv-qual-chip">
              <i :class="['pi', q.icon]" aria-hidden="true"></i>
              {{ q.label }}
            </span>
            <span v-if="activeQuals(driver).length === 0" class="drv-qual-none">Keine Qualifikationen hinterlegt</span>
          </div>

          <!-- Bestätigungs-Banner für endgültiges Löschen -->
          <div v-if="pendingDeleteId === driver.id" class="drv-delete-confirm" role="alert">
            <i class="pi pi-exclamation-triangle" aria-hidden="true"></i>
            <span>Fahrerprofil <strong>{{ driver.display_name }}</strong> endgültig löschen? Dies kann nicht rückgängig gemacht werden.</span>
            <div class="drv-delete-confirm-actions">
              <button
                class="am-btn am-btn-ghost drv-action-btn drv-action-btn--danger"
                @click="handlePermanentDelete(driver.id)"
                :aria-label="`${driver.display_name} endgültig löschen bestätigen`"
              >
                <i class="pi pi-trash" aria-hidden="true"></i>
                Endgültig löschen
              </button>
              <button
                class="am-btn am-btn-ghost drv-action-btn"
                @click="pendingDeleteId = null"
                aria-label="Löschen abbrechen"
              >
                Abbrechen
              </button>
            </div>
          </div>

          <!-- Aktionen -->
          <div v-else class="drv-card-actions">
            <button
              class="am-btn am-btn-ghost drv-action-btn"
              @click="openEdit(driver)"
              :aria-label="`${driver.display_name} bearbeiten`"
            >
              <i class="pi pi-pencil" aria-hidden="true"></i>
              Bearbeiten
            </button>
            <button
              v-if="driver.is_active"
              class="am-btn am-btn-ghost drv-action-btn drv-action-btn--danger"
              @click="handleDeactivate(driver)"
              :aria-label="`${driver.display_name} deaktivieren`"
            >
              <i class="pi pi-ban" aria-hidden="true"></i>
              Deaktivieren
            </button>
            <button
              v-else
              class="am-btn am-btn-ghost drv-action-btn drv-action-btn--success"
              @click="handleReactivate(driver)"
              :aria-label="`${driver.display_name} wieder aktivieren`"
            >
              <i class="pi pi-check-circle" aria-hidden="true"></i>
              Wieder aktivieren
            </button>
            <button
              class="am-btn am-btn-ghost drv-action-btn drv-action-btn--danger"
              @click="pendingDeleteId = driver.id"
              :aria-label="`${driver.display_name} endgültig löschen`"
            >
              <i class="pi pi-trash" aria-hidden="true"></i>
              Löschen
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Formular ──────────────────────────────────────────────────────── -->
    <template v-if="view === 'form'">
      <div class="drv-form-header">
        <button class="am-btn am-btn-ghost" @click="closeForm" aria-label="Zurück zur Fahrerliste">
          <i class="pi pi-arrow-left" aria-hidden="true"></i>
          Zurück zur Liste
        </button>
        <h2 class="drv-form-title">
          {{ editingId ? 'Fahrerprofil bearbeiten' : 'Neues Fahrerprofil anlegen' }}
        </h2>
      </div>

      <div v-if="saveSuccess" class="drv-alert drv-alert--success" role="alert" aria-live="assertive">
        <i class="pi pi-check-circle" aria-hidden="true"></i>
        {{ editingId ? 'Fahrerprofil wurde gespeichert.' : 'Fahrerprofil wurde angelegt.' }}
      </div>
      <div v-if="saveError" class="drv-alert drv-alert--error" role="alert" aria-live="assertive">
        <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
        {{ saveError }}
      </div>

      <form class="drv-form" @submit.prevent="handleSave" novalidate>
        <!-- ── Stammdaten ── -->
        <section class="am-card drv-section" aria-labelledby="df-basis">
          <h3 id="df-basis" class="drv-section-title">
            <i class="pi pi-user" aria-hidden="true"></i>
            Fahrerdaten
          </h3>
          <div class="drv-field-row">
            <div class="drv-field">
              <label for="df-name" class="drv-label">
                Anzeigename <span class="drv-required" aria-hidden="true">*</span>
              </label>
              <input
                id="df-name"
                v-model="form.display_name"
                type="text"
                class="drv-input"
                required
                aria-required="true"
                placeholder="Vor- und Nachname"
              />
            </div>
            <div class="drv-field">
              <label for="df-phone" class="drv-label">Telefon</label>
              <input
                id="df-phone"
                v-model="form.phone"
                type="tel"
                class="drv-input"
                placeholder="+49 30 …"
              />
            </div>
          </div>
          <div class="drv-field">
            <label for="df-base" class="drv-label">Startpunkt / Basisadresse</label>
            <input
              id="df-base"
              v-model="form.home_base_address"
              type="text"
              class="drv-input"
              placeholder="z. B. Musterstraße 1, 10115 Berlin"
            />
          </div>
        </section>

        <!-- ── Grundqualifikationen ── -->
        <section class="am-card drv-section" aria-labelledby="df-quals">
          <h3 id="df-quals" class="drv-section-title">
            <i class="pi pi-check-square" aria-hidden="true"></i>
            Grundqualifikationen
          </h3>
          <p class="drv-section-desc">Wählen Sie alle vorhandenen Qualifikationen aus.</p>

          <div class="drv-qual-grid" role="group" aria-label="Grundqualifikationen auswählen">
            <button
              v-for="qual in QUAL_OPTIONS"
              :key="qual.key"
              type="button"
              class="drv-qual-card"
              :class="{ 'drv-qual-card--active': form[qual.key as QualKey] as boolean }"
              role="checkbox"
              :aria-checked="!!(form[qual.key as QualKey] as boolean)"
              :aria-label="`${qual.label}: ${qual.description}`"
              @click="toggleQual(qual.key as QualKey)"
            >
              <div class="drv-qual-icon" aria-hidden="true">
                <i :class="['pi', qual.icon]"></i>
              </div>
              <div class="drv-qual-text">
                <span class="drv-qual-label">{{ qual.label }}</span>
                <span class="drv-qual-desc">{{ qual.description }}</span>
              </div>
              <div class="drv-qual-check" aria-hidden="true">
                <i class="pi pi-check"></i>
              </div>
            </button>
          </div>
        </section>

        <!-- ── Medizinische Qualifikationen ── -->
        <section class="am-card drv-section" aria-labelledby="df-med-quals">
          <h3 id="df-med-quals" class="drv-section-title">
            <i class="pi pi-heart" aria-hidden="true"></i>
            Medizinische Qualifikationen
          </h3>
          <p class="drv-section-desc">
            Sanitäts- und Pflegeausbildungen — nur ausfüllen, wenn vorhanden und nachweisbar.
            Kein Notfallrettungsdienst.
          </p>

          <div class="drv-qual-grid" role="group" aria-label="Medizinische Qualifikationen auswählen">
            <button
              v-for="qual in MED_QUAL_OPTIONS"
              :key="qual.key"
              type="button"
              class="drv-qual-card"
              :class="{ 'drv-qual-card--active': form[qual.key as MedQualKey] as boolean }"
              role="checkbox"
              :aria-checked="!!(form[qual.key as MedQualKey] as boolean)"
              :aria-label="`${qual.label}: ${qual.description}`"
              @click="toggleMedQual(qual.key as MedQualKey)"
            >
              <div class="drv-qual-icon" aria-hidden="true">
                <i :class="['pi', qual.icon]"></i>
              </div>
              <div class="drv-qual-text">
                <span class="drv-qual-label">{{ qual.label }}</span>
                <span class="drv-qual-desc">{{ qual.description }}</span>
              </div>
              <div class="drv-qual-check" aria-hidden="true">
                <i class="pi pi-check"></i>
              </div>
            </button>
          </div>
        </section>

        <!-- ── Technische Zusatzausbildungen ── -->
        <section class="am-card drv-section" aria-labelledby="df-tech-quals">
          <h3 id="df-tech-quals" class="drv-section-title">
            <i class="pi pi-wrench" aria-hidden="true"></i>
            Technische Zusatzausbildungen
          </h3>
          <p class="drv-section-desc">
            Gerätebezogene Schulungen und Nachweise zu spezifischen Hilfsmitteln.
          </p>

          <div class="drv-qual-grid" role="group" aria-label="Technische Ausbildungen auswählen">
            <button
              v-for="qual in TECH_TRAINING_OPTIONS"
              :key="qual.key"
              type="button"
              class="drv-qual-card"
              :class="{ 'drv-qual-card--active': form[qual.key as TechKey] as boolean }"
              role="checkbox"
              :aria-checked="!!(form[qual.key as TechKey] as boolean)"
              :aria-label="`${qual.label}: ${qual.description}`"
              @click="toggleTech(qual.key as TechKey)"
            >
              <div class="drv-qual-icon" aria-hidden="true">
                <i :class="['pi', qual.icon]"></i>
              </div>
              <div class="drv-qual-text">
                <span class="drv-qual-label">{{ qual.label }}</span>
                <span class="drv-qual-desc">{{ qual.description }}</span>
              </div>
              <div class="drv-qual-check" aria-hidden="true">
                <i class="pi pi-check"></i>
              </div>
            </button>
          </div>
        </section>

        <!-- ── Hinweise ── -->
        <section class="am-card drv-section" aria-labelledby="df-notes">
          <h3 id="df-notes" class="drv-section-title">
            <i class="pi pi-comment" aria-hidden="true"></i>
            Hinweise
          </h3>
          <div class="drv-field">
            <label for="df-avail" class="drv-label">Verfügbarkeitshinweise</label>
            <textarea id="df-avail" v-model="form.availability_notes" class="drv-textarea" rows="2" placeholder="z. B. nur Montag–Freitag"></textarea>
          </div>
          <div class="drv-field">
            <label for="df-qual-notes" class="drv-label">Qualifikationshinweise</label>
            <textarea id="df-qual-notes" v-model="form.qualification_notes" class="drv-textarea" rows="2" placeholder="z. B. Zertifikat gültig bis 2028"></textarea>
          </div>
          <div class="drv-field">
            <label for="df-gen" class="drv-label">Allgemeine Hinweise</label>
            <textarea id="df-gen" v-model="form.general_notes" class="drv-textarea" rows="2"></textarea>
          </div>
        </section>

        <!-- ── Speichern ── -->
        <div class="drv-save-bar">
          <button type="submit" class="am-btn am-btn-primary drv-save-btn" :disabled="store.saving" :aria-busy="store.saving">
            <i v-if="store.saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
            <i v-else class="pi pi-save" aria-hidden="true"></i>
            {{ store.saving ? 'Wird gespeichert …' : (editingId ? 'Änderungen speichern' : 'Fahrerprofil anlegen') }}
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
import { useDriverProfileStore } from '@/stores/driverProfile'
import { useAuthStore } from '@/stores/auth'
import type { DriverProfile } from '@/types'

const store = useDriverProfileStore()
const authStore = useAuthStore()

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
  all: store.drivers.length,
  active: store.drivers.filter((d) => d.is_active).length,
  inactive: store.drivers.filter((d) => !d.is_active).length,
}))

const filteredDrivers = computed(() => {
  if (filterMode.value === 'active') return store.drivers.filter((d) => d.is_active)
  if (filterMode.value === 'inactive') return store.drivers.filter((d) => !d.is_active)
  return store.drivers
})

type QualKey =
  | 'can_assist_wheelchair'
  | 'can_secure_wheelchair'
  | 'can_operate_lift'
  | 'can_assist_blind_passengers'
  | 'can_assist_deaf_passengers'
  | 'can_handle_stretcher'
  | 'has_first_aid_training'
  | 'has_passenger_transport_license'
  | 'can_support_medical_transport'

type MedQualKey =
  | 'has_sanitaetshelfer_training'
  | 'has_rettungshelfer_qualification'
  | 'has_rettungssanitaeter_qualification'
  | 'has_rettungsassistent_qualification'
  | 'has_notfallsanitaeter_qualification'
  | 'has_nursing_qualification'
  | 'has_medical_assistant_qualification'

type TechKey =
  | 'has_hygiene_training'
  | 'has_infection_protection_training'
  | 'has_wheelchair_restraint_training'
  | 'has_lift_operation_training'
  | 'has_stretcher_handling_training'
  | 'has_transport_chair_training'
  | 'has_oxygen_equipment_training'

const QUAL_OPTIONS: Array<{ key: QualKey; label: string; icon: string; description: string }> = [
  { key: 'can_assist_wheelchair',           label: 'Rollstuhl begleiten',              icon: 'pi-circle-fill',       description: 'Fahrer unterstützt und begleitet Fahrgäste mit Rollstuhl' },
  { key: 'can_secure_wheelchair',           label: 'Rollstuhl sichern',                icon: 'pi-lock',              description: 'Fahrer sichert Rollstühle korrekt mit Gurtsystem' },
  { key: 'can_operate_lift',                label: 'Lift bedienen',                    icon: 'pi-chevron-circle-up', description: 'Fahrer ist geschult im Bedienen von Hebebühnen' },
  { key: 'can_assist_blind_passengers',     label: 'Blinde Fahrgäste unterstützen',    icon: 'pi-eye-slash',         description: 'Fahrer holt Fahrgäste an der Haustür ab und begleitet verbal' },
  { key: 'can_assist_deaf_passengers',      label: 'Gehörlose Fahrgäste unterstützen', icon: 'pi-volume-off',        description: 'Fahrer kommuniziert schriftlich oder per Geste' },
  { key: 'can_handle_stretcher',            label: 'Liegendtransport begleiten',       icon: 'pi-minus',             description: 'Fahrer ist für Liegendtransporte und Transportliegen geschult' },
  { key: 'has_first_aid_training',          label: 'Erste-Hilfe-Schulung',             icon: 'pi-heart',             description: 'Gültige Erste-Hilfe-Ausbildung vorhanden' },
  { key: 'has_passenger_transport_license', label: 'Personenbeförderungsschein',       icon: 'pi-id-card',           description: 'Gültiger Personenbeförderungsschein (P-Schein) vorhanden' },
  { key: 'can_support_medical_transport',   label: 'Med. Krankentransport (KTP)',      icon: 'pi-star',              description: 'Fahrer qualifiziert für qualifizierten Krankentransport (nicht Rettungsdienst)' },
]

const MED_QUAL_OPTIONS: Array<{ key: MedQualKey; label: string; icon: string; description: string }> = [
  { key: 'has_sanitaetshelfer_training',         label: 'Sanitätshelfer',          icon: 'pi-heart',      description: 'Sanitätshelfer-Ausbildung (SanH) abgeschlossen' },
  { key: 'has_rettungshelfer_qualification',     label: 'Rettungshelfer',          icon: 'pi-heart-fill', description: 'Rettungshelfer-Qualifikation (RH) vorhanden' },
  { key: 'has_rettungssanitaeter_qualification', label: 'Rettungssanitäter',       icon: 'pi-shield',     description: 'Rettungssanitäter-Qualifikation (RettSan / RS) vorhanden' },
  { key: 'has_rettungsassistent_qualification',  label: 'Rettungsassistent',       icon: 'pi-shield',     description: 'Rettungsassistent-Qualifikation (RA) vorhanden' },
  { key: 'has_notfallsanitaeter_qualification',  label: 'Notfallsanitäter',        icon: 'pi-star',       description: 'Notfallsanitäter-Qualifikation (NotSan) — höchste nichtärztliche Qualifikation' },
  { key: 'has_nursing_qualification',            label: 'Pflegefachkraft',         icon: 'pi-users',      description: 'Examinierte Pflegefachkraft (Gesundheits- und Krankenpflege o. ä.)' },
  { key: 'has_medical_assistant_qualification',  label: 'Med. Fachangestellte/r',  icon: 'pi-id-card',    description: 'Medizinische Fachangestellte/r (MFA) oder vergleichbar' },
]

const TECH_TRAINING_OPTIONS: Array<{ key: TechKey; label: string; icon: string; description: string }> = [
  { key: 'has_hygiene_training',              label: 'Hygieneschulung',               icon: 'pi-shield',             description: 'Schulung im Bereich Hygiene und Infektionsschutz absolviert' },
  { key: 'has_infection_protection_training', label: 'Infektionsschutz (IfSG)',        icon: 'pi-ban',                description: 'Spezifische Schulung zum Infektionsschutz nach IfSG' },
  { key: 'has_wheelchair_restraint_training', label: 'Rollstuhl-Sicherung (Zerti.)',  icon: 'pi-lock',               description: 'Zertifizierte Schulung zur Rollstuhlsicherung' },
  { key: 'has_lift_operation_training',       label: 'Liftsystem-Bedienung',          icon: 'pi-chevron-circle-up',  description: 'Schulung im Bedienen elektrischer Hebebühnen und Liftsysteme' },
  { key: 'has_stretcher_handling_training',   label: 'Liegendtransport (Trage)',      icon: 'pi-minus',              description: 'Schulung in Ergonomie und sicherem Umgang mit Krankentragen' },
  { key: 'has_transport_chair_training',      label: 'Tragestuhl-Bedienung',          icon: 'pi-arrow-circle-up',    description: 'Schulung im Einsatz von Tragestühlen in engen Treppenhäusern' },
  { key: 'has_oxygen_equipment_training',     label: 'Sauerstoffgeräte',              icon: 'pi-circle',             description: 'Schulung im Umgang mit mobilen Sauerstoffgeräten und -halterungen' },
]

const EMPTY_FORM = () => ({
  display_name: '',
  phone: null as string | null,
  home_base_address: null as string | null,
  can_assist_wheelchair: false,
  can_secure_wheelchair: false,
  can_operate_lift: false,
  can_assist_blind_passengers: false,
  can_assist_deaf_passengers: false,
  can_handle_stretcher: false,
  has_first_aid_training: false,
  has_passenger_transport_license: false,
  can_support_medical_transport: false,
  has_sanitaetshelfer_training: false,
  has_rettungshelfer_qualification: false,
  has_rettungssanitaeter_qualification: false,
  has_rettungsassistent_qualification: false,
  has_notfallsanitaeter_qualification: false,
  has_nursing_qualification: false,
  has_medical_assistant_qualification: false,
  has_hygiene_training: false,
  has_infection_protection_training: false,
  has_wheelchair_restraint_training: false,
  has_lift_operation_training: false,
  has_stretcher_handling_training: false,
  has_transport_chair_training: false,
  has_oxygen_equipment_training: false,
  availability_notes: null as string | null,
  qualification_notes: null as string | null,
  general_notes: null as string | null,
})

const form = reactive(EMPTY_FORM())

function initials(name: string): string {
  return name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
}

function toggleQual(key: QualKey) {
  ;(form[key] as boolean) = !(form[key] as boolean)
}

function toggleMedQual(key: MedQualKey) {
  ;(form[key] as boolean) = !(form[key] as boolean)
}

function toggleTech(key: TechKey) {
  ;(form[key] as boolean) = !(form[key] as boolean)
}

const ALL_QUAL_OPTIONS = [...QUAL_OPTIONS, ...MED_QUAL_OPTIONS, ...TECH_TRAINING_OPTIONS]

function activeQuals(driver: DriverProfile) {
  return ALL_QUAL_OPTIONS.filter((q) => driver[q.key as keyof DriverProfile] === true)
}

function getDefaultOrgId(): string {
  return store.drivers[0]?.organization_id ?? ''
}

function openCreate() {
  Object.assign(form, EMPTY_FORM())
  editingId.value = null
  saveSuccess.value = false
  saveError.value = ''
  view.value = 'form'
}

function openEdit(driver: DriverProfile) {
  Object.assign(form, {
    display_name: driver.display_name,
    phone: driver.phone,
    home_base_address: driver.home_base_address,
    can_assist_wheelchair: driver.can_assist_wheelchair,
    can_secure_wheelchair: driver.can_secure_wheelchair,
    can_operate_lift: driver.can_operate_lift,
    can_assist_blind_passengers: driver.can_assist_blind_passengers,
    can_assist_deaf_passengers: driver.can_assist_deaf_passengers,
    can_handle_stretcher: driver.can_handle_stretcher,
    has_first_aid_training: driver.has_first_aid_training,
    has_passenger_transport_license: driver.has_passenger_transport_license,
    can_support_medical_transport: driver.can_support_medical_transport,
    has_sanitaetshelfer_training: driver.has_sanitaetshelfer_training,
    has_rettungshelfer_qualification: driver.has_rettungshelfer_qualification,
    has_rettungssanitaeter_qualification: driver.has_rettungssanitaeter_qualification,
    has_rettungsassistent_qualification: driver.has_rettungsassistent_qualification,
    has_notfallsanitaeter_qualification: driver.has_notfallsanitaeter_qualification,
    has_nursing_qualification: driver.has_nursing_qualification,
    has_medical_assistant_qualification: driver.has_medical_assistant_qualification,
    has_hygiene_training: driver.has_hygiene_training,
    has_infection_protection_training: driver.has_infection_protection_training,
    has_wheelchair_restraint_training: driver.has_wheelchair_restraint_training,
    has_lift_operation_training: driver.has_lift_operation_training,
    has_stretcher_handling_training: driver.has_stretcher_handling_training,
    has_transport_chair_training: driver.has_transport_chair_training,
    has_oxygen_equipment_training: driver.has_oxygen_equipment_training,
    availability_notes: driver.availability_notes,
    qualification_notes: driver.qualification_notes,
    general_notes: driver.general_notes,
  })
  editingId.value = driver.id
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
  if (!form.display_name.trim()) {
    saveError.value = 'Bitte einen Anzeigenamen eingeben.'
    return
  }
  saveSuccess.value = false
  saveError.value = ''
  try {
    if (editingId.value) {
      await store.update(editingId.value, { ...form })
    } else {
      await store.create({
        user_id: authStore.user?.id ?? '',
        organization_id: getDefaultOrgId(),
        ...form,
        display_name: form.display_name,
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

async function handleDeactivate(driver: DriverProfile) {
  try {
    await store.deactivate(driver.id)
  } catch {
    // Fehler still
  }
}

async function handleReactivate(driver: DriverProfile) {
  try {
    await store.reactivate(driver.id)
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
.drv-page {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
  max-width: 900px;
}

.drv-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.drv-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.drv-subtitle {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 4px 0 0;
  line-height: 1.5;
}

.drv-add-btn {
  flex-shrink: 0;
  min-height: 44px;
}

/* Filter-Tabs */
.drv-filter-bar {
  display: flex;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

.drv-filter-btn {
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

.drv-filter-btn:hover {
  border-color: var(--am-accent);
  color: var(--am-text-primary);
}

.drv-filter-btn--active {
  border-color: var(--am-accent);
  background: var(--am-accent-bg);
  color: var(--am-text-primary);
  font-weight: 600;
}

.drv-filter-count {
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

.drv-filter-btn--active .drv-filter-count {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
}

.drv-loading {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  color: var(--am-text-secondary);
  font-size: 0.9rem;
  padding: var(--am-space-xl);
  justify-content: center;
}

.drv-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--am-space-m);
  padding: var(--am-space-xl);
  text-align: center;
  color: var(--am-text-secondary);
}

.drv-empty-icon {
  font-size: 2.5rem;
  color: var(--am-border-strong);
}

.drv-list {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.drv-card {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}

.drv-card--inactive {
  opacity: 0.65;
}

.drv-card-head {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
}

.drv-card-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.25);
  color: var(--am-accent);
  font-size: 0.85rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.drv-card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.drv-card-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--am-text-primary);
}

.drv-card-phone {
  font-size: 0.8rem;
  color: var(--am-text-secondary);
}

.drv-card-quals {
  display: flex;
  flex-wrap: wrap;
  gap: var(--am-space-xs);
}

.drv-qual-chip {
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

.drv-qual-chip .pi {
  font-size: 0.65rem;
  color: var(--am-accent);
}

.drv-qual-none {
  font-size: 0.75rem;
  color: var(--am-text-muted);
  font-style: italic;
}

/* Bestätigungs-Banner */
.drv-delete-confirm {
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

.drv-delete-confirm-actions {
  display: flex;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

.drv-card-actions {
  display: flex;
  gap: var(--am-space-s);
  padding-top: var(--am-space-s);
  border-top: 1px solid var(--am-border);
  flex-wrap: wrap;
}

.drv-action-btn {
  font-size: 0.82rem;
  min-height: 38px;
  padding: 0 var(--am-space-m);
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
}

.drv-action-btn--danger:hover {
  color: var(--am-danger);
  background: var(--am-danger-bg);
  border-color: var(--am-danger);
}

.drv-action-btn--success:hover {
  color: var(--am-success);
  background: var(--am-success-bg);
  border-color: var(--am-success);
}

/* Form */
.drv-form-header {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.drv-form-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.drv-alert {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  border-radius: var(--am-radius-s);
  font-size: 0.875rem;
}

.drv-alert--success {
  background: var(--am-success-bg);
  border: 1px solid var(--am-success);
  color: var(--am-success);
}

.drv-alert--error {
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  color: var(--am-danger);
}

.drv-form {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

.drv-section {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.drv-section-title {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.drv-section-title .pi {
  color: var(--am-accent);
}

.drv-section-desc {
  font-size: 0.82rem;
  color: var(--am-text-secondary);
  margin: 0;
}

.drv-field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--am-space-m);
}

@media (max-width: 600px) {
  .drv-field-row {
    grid-template-columns: 1fr;
  }
}

.drv-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.drv-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
}

.drv-required {
  color: var(--am-danger);
  margin-left: 2px;
}

.drv-input {
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

.drv-input:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.drv-textarea {
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

.drv-textarea:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

/* Qualifikations-Grid */
.drv-qual-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--am-space-s);
}

.drv-qual-card {
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

.drv-qual-card:hover {
  border-color: var(--am-border-strong);
}

.drv-qual-card--active {
  border-color: var(--am-accent);
  background: var(--am-accent-bg);
}

.drv-qual-icon {
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

.drv-qual-card--active .drv-qual-icon {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
}

.drv-qual-text {
  flex: 1;
  min-width: 0;
}

.drv-qual-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin-bottom: 2px;
}

.drv-qual-desc {
  display: block;
  font-size: 0.72rem;
  color: var(--am-text-secondary);
  line-height: 1.35;
}

.drv-qual-check {
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

.drv-qual-card--active .drv-qual-check {
  background: var(--am-accent);
  border-color: var(--am-accent);
  color: var(--am-text-on-accent);
}

.drv-save-bar {
  display: flex;
  gap: var(--am-space-m);
  flex-wrap: wrap;
  padding: var(--am-space-m) 0;
}

.drv-save-btn {
  min-height: 48px;
  font-size: 0.95rem;
  padding: 0 var(--am-space-xl);
}

.drv-save-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
</style>
