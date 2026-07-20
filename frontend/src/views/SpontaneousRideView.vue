<template>
  <div class="sr-view">
    <h1 class="sr-view__title">Spontane Fahrt buchen</h1>

    <!-- Schritt 1: Standortfreigabe -->
    <section v-if="phase === 'idle'" class="sr-view__section">
      <p class="sr-view__intro">
        Um passende Fahrzeuge in Ihrer Nähe zu finden, benötigen wir Ihren aktuellen Standort.
        Der Standort wird <strong>nur für diese Suche</strong> verwendet und nicht dauerhaft gespeichert.
      </p>
      <button class="sr-view__btn sr-view__btn--primary" @click="requestLocation">
        <span class="pi pi-map-marker" aria-hidden="true"></span>
        Jetzt Standort freigeben und suchen
      </button>
    </section>

    <!-- Ladezustand Geolocation -->
    <section v-else-if="phase === 'locating'" class="sr-view__section sr-view__section--centered">
      <span class="pi pi-spin pi-spinner sr-view__spinner" aria-hidden="true"></span>
      <p>Standort wird ermittelt …</p>
    </section>

    <!-- Fehler Geolocation -->
    <section v-else-if="phase === 'geo-error'" class="sr-view__section">
      <div class="sr-view__error" role="alert">
        <span class="pi pi-exclamation-triangle" aria-hidden="true"></span>
        <span>{{ geoErrorMessage }}</span>
      </div>
      <button class="sr-view__btn sr-view__btn--secondary" @click="reset">
        Erneut versuchen
      </button>
    </section>

    <!-- Suche läuft -->
    <section v-else-if="phase === 'searching'" class="sr-view__section sr-view__section--centered">
      <span class="pi pi-spin pi-spinner sr-view__spinner" aria-hidden="true"></span>
      <p>Verfügbare Fahrzeuge werden gesucht …</p>
    </section>

    <!-- Ergebnisse -->
    <section v-else-if="phase === 'results'" class="sr-view__section">
      <div class="sr-view__location-info">
        <span class="pi pi-map-marker" aria-hidden="true"></span>
        Ihr Standort: {{ pickupLat?.toFixed(4) }}, {{ pickupLon?.toFixed(4) }}
        <button class="sr-view__btn-link" @click="reset">Neue Suche</button>
      </div>

      <!-- Karte -->
      <SpontaneousRideMap
        v-if="pickupLat !== null && pickupLon !== null"
        :pickup-lat="pickupLat"
        :pickup-lon="pickupLon"
        :matches="matches"
        class="sr-view__map"
      />
      <p class="sr-view__map-note">
        Karte zeigt verfügbare Fahrzeuge (Demo-Positionen, kein Echtzeit-GPS).
      </p>

      <!-- Keine Ergebnisse -->
      <div v-if="matches.length === 0" class="sr-view__empty" role="status">
        <span class="pi pi-inbox" aria-hidden="true"></span>
        <p>Derzeit sind keine passenden Fahrzeuge verfügbar. Bitte später erneut versuchen.</p>
      </div>

      <!-- Ergebnisliste -->
      <ul v-else class="sr-view__list" aria-label="Verfügbare Fahrzeuge">
        <li v-for="m in matches" :key="m.vehicle_id" class="sr-view__list-item">
          <div class="sr-list-item">
            <div class="sr-list-item__header">
              <span class="sr-list-item__icon pi pi-car" aria-hidden="true"></span>
              <strong class="sr-list-item__name">{{ m.vehicle_label }}</strong>
              <span class="sr-list-item__type">{{ vehicleTypeLabel(m.vehicle_type) }}</span>
            </div>
            <dl class="sr-list-item__details">
              <div class="sr-list-item__detail-row">
                <dt>Entfernung</dt>
                <dd>ca. {{ m.distance_km.toFixed(1) }} km</dd>
              </div>
              <div class="sr-list-item__detail-row">
                <dt>Geschätzte Ankunft</dt>
                <dd>ca. {{ m.estimated_arrival_minutes }} Min.</dd>
              </div>
              <div v-if="m.matched_capabilities.length" class="sr-list-item__detail-row">
                <dt>Passende Ausstattung</dt>
                <dd>{{ m.matched_capabilities.join(' · ') }}</dd>
              </div>
              <div class="sr-list-item__detail-row">
                <dt>Fahrer</dt>
                <dd>{{ m.driver_display_name }}</dd>
              </div>
            </dl>
            <button
              class="sr-view__btn sr-view__btn--primary"
              :disabled="!!bookingLoading[m.vehicle_id]"
              @click="bookRide(m)"
            >
              <span v-if="bookingLoading[m.vehicle_id]" class="pi pi-spin pi-spinner" aria-hidden="true"></span>
              <span v-else class="pi pi-send" aria-hidden="true"></span>
              Fahrzeug anfragen
            </button>
          </div>
        </li>
      </ul>

      <!-- Suchergebnis-Fehler / Buchungsfehler -->
      <div v-if="searchError || bookingError" class="sr-view__error" role="alert">
        <span class="pi pi-exclamation-triangle" aria-hidden="true"></span>
        <span>{{ searchError || bookingError }}</span>
      </div>
    </section>

    <!-- Buchung angefragt + Live-Tracking -->
    <section v-else-if="phase === 'booked'" class="sr-view__section">

      <!-- Status-Header -->
      <div class="sr-view__tracking-header">
        <div class="sr-view__tracking-status" :class="trackingStatusClass" role="status" aria-live="polite">
          <span class="pi" :class="trackingStatusIcon" aria-hidden="true"></span>
          <strong>{{ trackingStatusLabel }}</strong>
        </div>
      </div>

      <!-- Karte (sobald Fahrerposition bekannt) -->
      <template v-if="trackingData?.can_track && trackingData.driver_latitude != null && pickupLat !== null && pickupLon !== null">
        <SpontaneousRideMap
          :pickup-lat="pickupLat"
          :pickup-lon="pickupLon"
          :driver-lat="trackingData.driver_latitude"
          :driver-lon="trackingData.driver_longitude ?? undefined"
          class="sr-view__map"
        />
        <p class="sr-view__map-note">
          Karte zeigt den aktuellen Fahrerstandort. Aktualisierung alle 15 Sekunden.
        </p>
      </template>

      <!-- Lade-Anzeige beim ersten Poll -->
      <div v-else-if="trackingLoading && !trackingData" class="sr-view__section sr-view__section--centered">
        <span class="pi pi-spin pi-spinner sr-view__spinner" aria-hidden="true"></span>
        <p>Verbindung wird aufgebaut …</p>
      </div>

      <!-- Fahrer abgelehnt -->
      <div v-if="trackingData?.status === 'driver_declined'" class="sr-view__error" role="alert">
        <span class="pi pi-times-circle" aria-hidden="true"></span>
        <span>Der Fahrer hat die Anfrage leider abgelehnt.</span>
      </div>

      <!-- Tracking-Detailkarte (Text) -->
      <div v-if="trackingData" class="sr-view__tracking-card">
        <dl class="sr-view__tracking-details">
          <div v-if="bookingResult" class="sr-view__tracking-row">
            <dt><span class="pi pi-truck" aria-hidden="true"></span> Fahrzeug</dt>
            <dd>{{ bookingResult.vehicle_label }}</dd>
          </div>
          <div v-if="bookingResult" class="sr-view__tracking-row">
            <dt><span class="pi pi-user" aria-hidden="true"></span> Fahrer</dt>
            <dd>{{ bookingResult.driver_display_name }}</dd>
          </div>
          <div v-if="trackingData.distance_km != null" class="sr-view__tracking-row">
            <dt><span class="pi pi-arrows-h" aria-hidden="true"></span> Entfernung</dt>
            <dd>ca. {{ trackingData.distance_km.toFixed(1) }} km</dd>
          </div>
          <div v-if="trackingData.estimated_arrival_minutes != null" class="sr-view__tracking-row">
            <dt><span class="pi pi-clock" aria-hidden="true"></span> Geschätzte Ankunft</dt>
            <dd>ca. {{ trackingData.estimated_arrival_minutes }} Min.</dd>
          </div>
          <div v-if="trackingData.last_location_update" class="sr-view__tracking-row">
            <dt><span class="pi pi-map-marker" aria-hidden="true"></span> Letzter Standort</dt>
            <dd>{{ formatTime(trackingData.last_location_update) }} Uhr</dd>
          </div>
        </dl>
      </div>

      <!-- Polling-Fehler (nicht-kritisch) -->
      <div v-if="trackingError" class="sr-view__warning" role="status">
        <span class="pi pi-exclamation-circle" aria-hidden="true"></span>
        <span>Statusabruf unterbrochen. Nächster Versuch in Kürze.</span>
      </div>

      <button
        v-if="trackingData?.status === 'driver_declined' || trackingData?.status === 'cancelled'"
        class="sr-view__btn sr-view__btn--primary"
        @click="reset"
      >
        <span class="pi pi-search" aria-hidden="true"></span>
        Erneut suchen
      </button>
      <button v-else class="sr-view__btn sr-view__btn--secondary" @click="reset">
        Abbrechen / Neue Suche
      </button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import SpontaneousRideMap from '@/components/SpontaneousRideMap.vue'
import { findSpontaneousMatches, bookSpontaneousRide, getTrackingStatus } from '@/api/spontaneous'
import type { SpontaneousRideBookResponse, SpontaneousRideMatchResult, SpontaneousRideTracking } from '@/types'
import { VEHICLE_TYPE_LABELS } from '@/types'

type Phase = 'idle' | 'locating' | 'geo-error' | 'searching' | 'results' | 'booked'

const TRACKING_POLL_INTERVAL_MS = 15_000
const TERMINAL_STATUSES = new Set(['driver_declined', 'completed', 'cancelled'])

const phase = ref<Phase>('idle')
const pickupLat = ref<number | null>(null)
const pickupLon = ref<number | null>(null)
const matches = ref<SpontaneousRideMatchResult[]>([])
const geoErrorMessage = ref('')
const searchError = ref('')
const bookingLoading = ref<Record<string, boolean>>({})
const bookingError = ref<string | null>(null)
const bookingResult = ref<SpontaneousRideBookResponse | null>(null)

// Tracking state
const trackingData = ref<SpontaneousRideTracking | null>(null)
const trackingLoading = ref(false)
const trackingError = ref(false)
let trackingInterval: ReturnType<typeof setInterval> | null = null

// ── Tracking-Polling ──────────────────────────────────────────────────────────

function startTracking(): void {
  pollTracking()
  trackingInterval = setInterval(pollTracking, TRACKING_POLL_INTERVAL_MS)
}

function stopTracking(): void {
  if (trackingInterval !== null) {
    clearInterval(trackingInterval)
    trackingInterval = null
  }
}

async function pollTracking(): Promise<void> {
  const requestId = bookingResult.value?.request_id
  if (!requestId) return
  trackingLoading.value = true
  trackingError.value = false
  try {
    trackingData.value = await getTrackingStatus(requestId)
    if (TERMINAL_STATUSES.has(trackingData.value.status)) {
      stopTracking()
    }
  } catch {
    trackingError.value = true
  } finally {
    trackingLoading.value = false
  }
}

// Polling starten, sobald Phase 'booked' wird
watch(
  () => phase.value,
  (newPhase) => {
    if (newPhase === 'booked') {
      startTracking()
    } else {
      stopTracking()
    }
  },
)

onUnmounted(() => stopTracking())

// ── Tracking-Anzeige ──────────────────────────────────────────────────────────

const trackingStatusLabel = computed<string>(() => {
  if (!trackingData.value) return 'Verbindung wird aufgebaut …'
  return trackingData.value.ride_status_label
})

const trackingStatusClass = computed<string>(() => {
  const s = trackingData.value?.status
  if (s === 'assigned') return 'sr-view__tracking-status--active'
  if (s === 'driver_declined' || s === 'cancelled') return 'sr-view__tracking-status--error'
  if (s === 'completed') return 'sr-view__tracking-status--done'
  return 'sr-view__tracking-status--waiting'
})

const trackingStatusIcon = computed<string>(() => {
  const s = trackingData.value?.status
  if (s === 'assigned') return 'pi-car'
  if (s === 'driver_declined' || s === 'cancelled') return 'pi-times-circle'
  if (s === 'completed') return 'pi-check-circle'
  return 'pi-spin pi-spinner'
})

// ── Helfer ────────────────────────────────────────────────────────────────────

function vehicleTypeLabel(type: string): string {
  return VEHICLE_TYPE_LABELS[type as keyof typeof VEHICLE_TYPE_LABELS] ?? type
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
}

function reset(): void {
  stopTracking()
  phase.value = 'idle'
  pickupLat.value = null
  pickupLon.value = null
  matches.value = []
  geoErrorMessage.value = ''
  searchError.value = ''
  bookingLoading.value = {}
  bookingError.value = null
  bookingResult.value = null
  trackingData.value = null
  trackingError.value = false
  trackingLoading.value = false
}

async function bookRide(match: SpontaneousRideMatchResult): Promise<void> {
  if (!pickupLat.value || !pickupLon.value) return
  bookingLoading.value[match.vehicle_id] = true
  bookingError.value = null
  try {
    const result = await bookSpontaneousRide({
      driver_id: match.driver_id,
      vehicle_id: match.vehicle_id,
      pickup_latitude: pickupLat.value,
      pickup_longitude: pickupLon.value,
    })
    bookingResult.value = result
    phase.value = 'booked'
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    bookingError.value = e?.response?.data?.detail ?? 'Buchung fehlgeschlagen. Bitte erneut versuchen.'
  } finally {
    bookingLoading.value[match.vehicle_id] = false
  }
}

async function searchMatches(lat: number, lon: number): Promise<void> {
  phase.value = 'searching'
  searchError.value = ''
  try {
    matches.value = await findSpontaneousMatches({
      pickup_latitude: lat,
      pickup_longitude: lon,
    })
    phase.value = 'results'
  } catch {
    searchError.value = 'Die Suche konnte nicht abgeschlossen werden. Bitte erneut versuchen.'
    phase.value = 'results'
  }
}

function requestLocation(): void {
  if (!navigator.geolocation) {
    geoErrorMessage.value = 'Ihr Browser unterstützt keine Standortermittlung.'
    phase.value = 'geo-error'
    return
  }
  phase.value = 'locating'
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      pickupLat.value = pos.coords.latitude
      pickupLon.value = pos.coords.longitude
      searchMatches(pos.coords.latitude, pos.coords.longitude)
    },
    (err) => {
      if (err.code === GeolocationPositionError.PERMISSION_DENIED) {
        geoErrorMessage.value =
          'Standortzugriff wurde verweigert. Bitte erlauben Sie den Standortzugriff in den Browser-Einstellungen.'
      } else if (err.code === GeolocationPositionError.POSITION_UNAVAILABLE) {
        geoErrorMessage.value = 'Standort nicht verfügbar. Bitte später erneut versuchen.'
      } else {
        geoErrorMessage.value = 'Standortermittlung fehlgeschlagen. Bitte erneut versuchen.'
      }
      phase.value = 'geo-error'
    },
    { timeout: 10000, maximumAge: 60000 },
  )
}
</script>

<style scoped>
.sr-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
}

.sr-view__title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.sr-view__section {
  margin-bottom: 1.5rem;
}

.sr-view__section--centered {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 0;
}

.sr-view__intro {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.sr-view__spinner {
  font-size: 2rem;
  color: var(--p-primary-color, #3b82f6);
}

.sr-view__btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
}

.sr-view__btn--primary {
  background: var(--p-primary-color, #3b82f6);
  color: #fff;
}

.sr-view__btn--primary:hover {
  opacity: 0.9;
}

.sr-view__btn--secondary {
  background: var(--p-surface-100, #f1f5f9);
  color: var(--p-text-color, #1e293b);
  border: 1px solid var(--p-surface-border, #dee2e6);
}

.sr-view__btn-link {
  background: none;
  border: none;
  color: var(--p-primary-color, #3b82f6);
  cursor: pointer;
  padding: 0;
  margin-left: 0.75rem;
  text-decoration: underline;
  font-size: 0.9rem;
}

.sr-view__error {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  background: var(--p-red-50, #fef2f2);
  border: 1px solid var(--p-red-200, #fecaca);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  color: var(--p-red-700, #b91c1c);
}

.sr-view__warning {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  background: var(--p-yellow-50, #fefce8);
  border: 1px solid var(--p-yellow-200, #fde68a);
  border-radius: 6px;
  padding: 0.6rem 1rem;
  margin-bottom: 1rem;
  color: var(--p-yellow-800, #92400e);
  font-size: 0.85rem;
}

.sr-view__location-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: var(--p-text-muted-color, #64748b);
  margin-bottom: 0.75rem;
}

.sr-view__map {
  margin-bottom: 0.5rem;
}

.sr-view__map-note {
  font-size: 0.78rem;
  color: var(--p-text-muted-color, #94a3b8);
  margin-bottom: 1rem;
}

.sr-view__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--p-text-muted-color, #64748b);
  font-size: 0.9rem;
}

.sr-view__empty .pi {
  font-size: 2rem;
}

.sr-view__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.sr-list-item {
  background: var(--p-surface-0, #fff);
  border: 1px solid var(--p-surface-border, #dee2e6);
  border-radius: 8px;
  padding: 1rem;
}

.sr-list-item__header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.sr-list-item__icon {
  color: var(--p-primary-color, #3b82f6);
  font-size: 1.1rem;
}

.sr-list-item__name {
  font-size: 1rem;
}

.sr-list-item__type {
  font-size: 0.8rem;
  color: var(--p-text-muted-color, #64748b);
  background: var(--p-surface-100, #f1f5f9);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.sr-list-item__details {
  margin: 0 0 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.sr-list-item__detail-row {
  display: flex;
  gap: 0.5rem;
  font-size: 0.88rem;
}

.sr-list-item__detail-row dt {
  color: var(--p-text-muted-color, #64748b);
  min-width: 9rem;
}

.sr-list-item__detail-row dd {
  margin: 0;
}

/* ── Tracking ────────────────────────────────────────────────────────────── */

.sr-view__tracking-header {
  margin-bottom: 1rem;
}

.sr-view__tracking-status {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 1rem;
  border: 2px solid transparent;
}

.sr-view__tracking-status--waiting {
  background: var(--p-blue-50, #eff6ff);
  border-color: var(--p-blue-200, #bfdbfe);
  color: var(--p-blue-700, #1d4ed8);
}

.sr-view__tracking-status--active {
  background: var(--p-green-50, #f0fdf4);
  border-color: var(--p-green-300, #86efac);
  color: var(--p-green-700, #15803d);
}

.sr-view__tracking-status--error {
  background: var(--p-red-50, #fef2f2);
  border-color: var(--p-red-200, #fecaca);
  color: var(--p-red-700, #b91c1c);
}

.sr-view__tracking-status--done {
  background: var(--p-surface-100, #f1f5f9);
  border-color: var(--p-surface-border, #dee2e6);
  color: var(--p-text-color, #1e293b);
}

.sr-view__tracking-card {
  background: var(--p-surface-0, #fff);
  border: 1px solid var(--p-surface-border, #dee2e6);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.sr-view__tracking-details {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sr-view__tracking-row {
  display: flex;
  gap: 0.75rem;
  font-size: 0.9rem;
  align-items: center;
}

.sr-view__tracking-row dt {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--p-text-muted-color, #64748b);
  min-width: 11rem;
}

.sr-view__tracking-row dd {
  margin: 0;
  font-weight: 500;
}
</style>
