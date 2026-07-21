<template>
  <div class="driver-app">

    <!-- ── Fehlermeldung ─────────────────────────────────────────────────── -->
    <div v-if="errorMsg" class="driver-error" role="alert">
      <i class="pi pi-exclamation-triangle" aria-hidden="true"></i>
      {{ errorMsg }}
      <button class="error-dismiss" aria-label="Schließen" @click="errorMsg = null">
        <i class="pi pi-times" aria-hidden="true"></i>
      </button>
    </div>

    <!-- ── Laden ─────────────────────────────────────────────────────────── -->
    <div v-if="loading" class="driver-loading" aria-live="polite">
      <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
      <span>Lädt…</span>
    </div>

    <template v-else-if="context">

      <!-- ══ STATUSKARTE ══════════════════════════════════════════════════ -->

      <!-- Keine aktive Schicht -->
      <section v-if="!context.active_shift" class="status-card status-card--idle" aria-labelledby="status-title">
        <div class="status-header">
          <span class="status-icon status-icon--idle" aria-hidden="true">
            <i class="pi pi-moon"></i>
          </span>
          <div>
            <h1 id="status-title" class="status-title">Keine aktive Schicht</h1>
            <p class="status-sub">Schicht beginnen, um Aufträge zu sehen</p>
          </div>
        </div>

        <!-- Szenario A: Standardfahrzeug vorhanden -->
        <template v-if="context.default_vehicle">
          <div class="vehicle-card vehicle-card--default">
            <i class="pi pi-truck vehicle-card-icon" aria-hidden="true"></i>
            <div class="vehicle-card-info">
              <span class="vehicle-card-plate">{{ context.default_vehicle.license_plate }}</span>
              <span class="vehicle-card-name">{{ context.default_vehicle.name }}</span>
              <div class="vehicle-tags">
                <span class="am-badge am-badge-neutral">{{ VEHICLE_TYPE_LABELS[context.default_vehicle.vehicle_type] }}</span>
                <span v-if="context.default_vehicle.has_ramp" class="am-badge am-badge-neutral">Rampe</span>
                <span v-if="context.default_vehicle.has_lift" class="am-badge am-badge-neutral">Lift</span>
                <span v-if="context.default_vehicle.wheelchair_space_count > 0" class="am-badge am-badge-neutral">
                  {{ context.default_vehicle.wheelchair_space_count }}× Rollstuhl
                </span>
              </div>
            </div>
          </div>
          <button
            class="driver-btn driver-btn--primary"
            :disabled="actionLoading"
            @click="startWithDefaultVehicle"
            aria-describedby="status-title"
          >
            <i class="pi pi-play" aria-hidden="true"></i>
            Schicht mit diesem Fahrzeug beginnen
          </button>
          <button class="driver-btn-link" @click="showPlateSearch = !showPlateSearch">
            <i class="pi pi-search" aria-hidden="true"></i>
            Anderes Fahrzeug wählen
          </button>
        </template>

        <!-- Szenario B: Kein Standardfahrzeug -->
        <template v-else>
          <p class="no-vehicle-hint">
            <i class="pi pi-info-circle" aria-hidden="true"></i>
            Kein Standardfahrzeug hinterlegt. Bitte Fahrzeug per Kennzeichen wählen.
          </p>
        </template>

        <!-- Kennzeichen-Suche (immer bei B, optional bei A) -->
        <div v-if="!context.default_vehicle || showPlateSearch" class="plate-search-section">
          <div class="plate-search-row">
            <input
              v-model="plateInput"
              class="am-input plate-input"
              type="text"
              placeholder="Kennzeichen z. B. AM-BUS-1"
              aria-label="Fahrzeugkennzeichen eingeben"
              maxlength="20"
              @keydown.enter="searchVehicle"
            />
            <button
              class="driver-btn driver-btn--secondary driver-btn--sm"
              :disabled="!plateInput.trim() || searchLoading"
              @click="searchVehicle"
            >
              <i class="pi pi-search" aria-hidden="true"></i>
              Suchen
            </button>
          </div>

          <div v-if="searchDone && vehicleResults.length === 0" class="search-empty" role="status">
            Kein aktives Fahrzeug mit Kennzeichen <strong>{{ plateInput }}</strong> gefunden.
          </div>

          <div v-if="vehicleResults.length > 0" class="vehicle-results" role="list">
            <button
              v-for="v in vehicleResults"
              :key="v.id"
              class="vehicle-result-item"
              :class="{ 'vehicle-result-item--selected': selectedVehicleId === v.id }"
              role="listitem"
              @click="selectedVehicleId = v.id"
            >
              <div class="vehicle-result-info">
                <span class="vehicle-card-plate">{{ v.license_plate }}</span>
                <span class="vehicle-card-name">{{ v.name }}</span>
                <div class="vehicle-tags">
                  <span class="am-badge am-badge-neutral">{{ VEHICLE_TYPE_LABELS[v.vehicle_type] }}</span>
                  <span v-if="v.has_ramp" class="am-badge am-badge-neutral">Rampe</span>
                  <span v-if="v.has_lift" class="am-badge am-badge-neutral">Lift</span>
                </div>
              </div>
              <i v-if="selectedVehicleId === v.id" class="pi pi-check-circle selected-check" aria-hidden="true"></i>
            </button>

            <button
              v-if="selectedVehicleId"
              class="driver-btn driver-btn--primary"
              :disabled="actionLoading"
              @click="startWithSelectedVehicle"
            >
              <i class="pi pi-play" aria-hidden="true"></i>
              Schicht beginnen
            </button>
          </div>
        </div>
      </section>

      <!-- Schicht aktiv -->
      <section v-else class="status-card" :class="statusCardClass" aria-labelledby="status-title">
        <div class="status-header">
          <span class="status-icon" :class="statusIconClass" aria-hidden="true">
            <i :class="statusIconPi"></i>
          </span>
          <div>
            <h1 id="status-title" class="status-title">{{ statusTitle }}</h1>
            <p class="status-sub">
              Beginn: {{ formatTime(context.active_shift.shift.started_at) }} Uhr
              <template v-if="context.active_shift.shift.status === 'paused' && context.active_shift.shift.break_started_at">
                · Pause seit {{ formatTime(context.active_shift.shift.break_started_at) }} Uhr
              </template>
            </p>
          </div>
        </div>

        <!-- Fahrzeug der aktiven Schicht -->
        <div class="vehicle-card vehicle-card--active">
          <i class="pi pi-truck vehicle-card-icon" aria-hidden="true"></i>
          <div class="vehicle-card-info">
            <span class="vehicle-card-plate">{{ context.active_shift.vehicle.license_plate }}</span>
            <span class="vehicle-card-name">{{ context.active_shift.vehicle.name }}</span>
            <div class="vehicle-tags">
              <span class="am-badge am-badge-neutral">{{ VEHICLE_TYPE_LABELS[context.active_shift.vehicle.vehicle_type] }}</span>
              <span v-if="context.active_shift.vehicle.has_ramp" class="am-badge am-badge-neutral">Rampe</span>
              <span v-if="context.active_shift.vehicle.has_lift" class="am-badge am-badge-neutral">Lift</span>
              <span v-if="context.active_shift.vehicle.wheelchair_space_count > 0" class="am-badge am-badge-neutral">
                {{ context.active_shift.vehicle.wheelchair_space_count }}× Rollstuhl
              </span>
            </div>
          </div>
        </div>

        <!-- Schicht-Buttons -->
        <div class="shift-btns">
          <button
            v-if="context.active_shift.shift.status === 'active'"
            class="driver-btn driver-btn--secondary"
            :disabled="actionLoading"
            @click="doPause"
          >
            <i class="pi pi-pause" aria-hidden="true"></i>
            Pause beginnen
          </button>

          <button
            v-if="context.active_shift.shift.status === 'paused'"
            class="driver-btn driver-btn--primary"
            :disabled="actionLoading"
            @click="doResume"
          >
            <i class="pi pi-play" aria-hidden="true"></i>
            Pause beenden
          </button>

          <button
            class="driver-btn driver-btn--danger"
            :disabled="actionLoading"
            @click="confirmEndShift = true"
          >
            <i class="pi pi-stop-circle" aria-hidden="true"></i>
            Schicht beenden
          </button>
        </div>
      </section>

      <!-- ══ AUFTRAGSBEREICH ═══════════════════════════════════════════════ -->

      <!-- Spontane Fahrtanfragen (ausstehend) -->
      <section class="assignments-section" aria-labelledby="spontan-req-heading">
        <div class="section-title-row">
          <h2 id="spontan-req-heading" class="section-heading">
            <i class="pi pi-bell" aria-hidden="true"></i>
            Spontane Fahrtanfragen
          </h2>
          <div class="section-title-actions">
            <span class="section-auto-refresh-label">
              <i class="pi pi-clock" aria-hidden="true"></i>
              Aktualisiert automatisch
            </span>
            <button class="driver-btn-link driver-btn-link--sm" :disabled="spontaneousLoading" @click="loadSpontaneousRequests">
              <i class="pi pi-refresh" aria-hidden="true"></i>
              Aktualisieren
            </button>
          </div>
        </div>

        <div v-if="spontaneousLoading" class="section-loading" aria-live="polite">
          <i class="pi pi-spin pi-spinner" aria-hidden="true"></i> Lädt…
        </div>
        <div v-else-if="spontaneousRequests.length === 0" class="section-placeholder">
          <i class="pi pi-inbox" aria-hidden="true"></i>
          Keine offenen Fahrtanfragen.
        </div>
        <div v-else class="assignment-list" role="list">
          <div
            v-for="req in spontaneousRequests"
            :key="req.id"
            class="assignment-card spontan-req-card"
            role="listitem"
          >
            <div v-if="req.passenger_display_name" class="assignment-passenger">
              <i class="pi pi-user" aria-hidden="true"></i>
              {{ req.passenger_display_name }}
            </div>
            <div class="assignment-route">
              <div class="assignment-address">
                <i class="pi pi-map-marker" aria-hidden="true"></i>
                <span v-if="req.pickup_address">{{ req.pickup_address }}</span>
                <span v-else-if="req.pickup_latitude != null" class="pickup-coords">
                  Aktueller Standort des Fahrgasts
                  <small>{{ req.pickup_latitude.toFixed(4) }}, {{ req.pickup_longitude.toFixed(4) }}</small>
                </span>
                <span v-else>Abholort nicht angegeben</span>
              </div>
            </div>
            <div class="spontan-req-actions">
              <button
                class="driver-btn driver-btn--success"
                :disabled="spontaneousActionLoading[req.id]"
                @click="acceptRequest(req.id)"
              >
                <i v-if="spontaneousActionLoading[req.id]" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
                <i v-else class="pi pi-check" aria-hidden="true"></i>
                Annehmen
              </button>
              <button
                class="driver-btn driver-btn--ghost"
                :disabled="spontaneousActionLoading[req.id]"
                @click="declineRequest(req.id)"
              >
                <i class="pi pi-times" aria-hidden="true"></i>
                Ablehnen
              </button>
            </div>
            <div v-if="spontaneousError[req.id]" class="ride-status-error" role="alert">
              <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
              {{ spontaneousError[req.id] }}
            </div>
          </div>
        </div>
      </section>

      <!-- Linienfahrten -->
      <section class="assignments-section" aria-labelledby="line-heading">
        <h2 id="line-heading" class="section-heading">
          <i class="pi pi-map" aria-hidden="true"></i>
          Linienfahrten
        </h2>
        <div class="section-placeholder">
          <i class="pi pi-info-circle" aria-hidden="true"></i>
          Regelmäßige Touren und optimierte Fahrgastlisten werden in einem späteren Sprint ergänzt.
        </div>
      </section>

      <!-- Spontane Fahrten -->
      <section class="assignments-section" aria-labelledby="spontan-heading">
        <div class="section-title-row">
          <h2 id="spontan-heading" class="section-heading">
            <i class="pi pi-car" aria-hidden="true"></i>
            Spontane Fahrten
          </h2>
          <button class="driver-btn-link driver-btn-link--sm" :disabled="assignmentsLoading" @click="loadAssignments">
            <i class="pi pi-refresh" aria-hidden="true"></i>
            Aktualisieren
          </button>
        </div>

        <div v-if="assignmentsLoading" class="section-loading" aria-live="polite">
          <i class="pi pi-spin pi-spinner" aria-hidden="true"></i> Lädt…
        </div>
        <div v-else-if="assignments.length === 0" class="section-placeholder">
          <i class="pi pi-inbox" aria-hidden="true"></i>
          Keine spontanen Fahrten zugewiesen.
        </div>
        <div v-else class="assignment-list" role="list">
          <div
            v-for="req in assignments"
            :key="req.id"
            class="assignment-card"
            role="listitem"
          >
            <div class="assignment-time">
              {{ req.pickup_time ?? '–' }}
            </div>
            <div class="assignment-route">
              <div class="assignment-address">
                <i class="pi pi-map-marker" aria-hidden="true"></i>
                <span v-if="req.pickup_address">{{ req.pickup_address }}</span>
                <span v-else-if="req.pickup_latitude != null" class="pickup-coords">
                  Aktueller Standort des Fahrgasts
                  <small>{{ req.pickup_latitude.toFixed(4) }}, {{ req.pickup_longitude?.toFixed(4) ?? '' }}</small>
                </span>
                <span v-else>Abholadresse nicht angegeben</span>
              </div>
              <div class="assignment-arrow" aria-hidden="true">↓</div>
              <div class="assignment-address">
                <i class="pi pi-flag" aria-hidden="true"></i>
                {{ req.destination_address ?? 'Zieladresse nicht angegeben' }}
              </div>
            </div>
            <div v-if="req.passenger_display_name" class="assignment-passenger">
              <i class="pi pi-user" aria-hidden="true"></i>
              {{ req.passenger_display_name }}
            </div>

            <!-- ── Standort teilen (nur spontane Fahrten) ────────────── -->
            <div v-if="req.is_spontaneous" class="location-share-section">
              <div class="location-privacy-notice">
                <i class="pi pi-shield" aria-hidden="true"></i>
                Standort wird nur während dieser Fahrt geteilt — kein Hintergrundtracking.
              </div>
              <div class="location-share-btns">
                <button
                  v-if="!locationSharingActive[req.id]"
                  class="driver-btn driver-btn--location driver-btn--sm"
                  @click="startLocationSharing(req.id)"
                >
                  <i class="pi pi-map-marker" aria-hidden="true"></i>
                  Standort teilen
                </button>
                <button
                  v-else
                  class="driver-btn driver-btn--location-stop driver-btn--sm"
                  @click="stopLocationSharing(req.id)"
                >
                  <i class="pi pi-times" aria-hidden="true"></i>
                  Standort stoppen
                </button>
                <span v-if="locationSharingActive[req.id]" class="location-share-active-label">
                  <i class="pi pi-circle-fill location-pulse" aria-hidden="true"></i>
                  Aktiv — alle 15 Sek.
                </span>
              </div>
              <div v-if="locationSharingError[req.id]" class="ride-status-error" role="alert">
                <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
                {{ locationSharingError[req.id] }}
              </div>
            </div>

            <!-- ── Statusverlauf ────────────────────────────────────────── -->
            <div class="ride-status-section">
              <div v-if="statusEventsLoading[req.id]" class="ride-status-loading">
                <i class="pi pi-spin pi-spinner" aria-hidden="true"></i> Lädt…
              </div>
              <template v-else>
                <!-- Letzter Status -->
                <div v-if="lastEventFor(req.id)" class="ride-status-current">
                  <i class="pi pi-clock" aria-hidden="true"></i>
                  Letzter Status:
                  <strong>{{ RIDE_STATUS_EVENT_LABELS[lastEventFor(req.id)!.status] }}</strong>
                  <span class="ride-status-time">
                    {{ formatTime(lastEventFor(req.id)!.created_at) }}
                  </span>
                </div>
                <div v-else class="ride-status-none">
                  <i class="pi pi-info-circle" aria-hidden="true"></i>
                  Noch kein Statusereignis gesetzt.
                </div>

                <!-- Statusbuttons -->
                <div class="ride-status-btns" role="group" :aria-label="`Statuswechsel für Fahrt vom ${req.pickup_date ?? ''}`">
                  <button
                    v-for="action in STATUS_ACTIONS"
                    :key="action.status"
                    class="ride-status-btn"
                    :disabled="statusActionLoading[req.id]"
                    :title="action.label"
                    @click="setStatus(req.id, action.status)"
                  >
                    <i :class="['pi', action.icon]" aria-hidden="true"></i>
                    {{ action.label }}
                  </button>
                </div>

                <!-- Problem melden mit Notiz -->
                <div class="ride-issue-section">
                  <button
                    class="ride-status-btn ride-status-btn--issue"
                    :disabled="statusActionLoading[req.id]"
                    @click="toggleIssueInput(req.id)"
                  >
                    <i class="pi pi-exclamation-triangle" aria-hidden="true"></i>
                    Problem melden
                  </button>
                  <div v-if="issueInputOpen[req.id]" class="ride-issue-input-row">
                    <input
                      v-model="issueNotes[req.id]"
                      class="am-input ride-issue-input"
                      type="text"
                      placeholder="Kurze Beschreibung des Problems (optional)"
                      maxlength="300"
                    />
                    <button
                      class="ride-status-btn ride-status-btn--issue-send"
                      :disabled="statusActionLoading[req.id]"
                      @click="reportIssue(req.id)"
                    >
                      <i class="pi pi-send" aria-hidden="true"></i>
                      Senden
                    </button>
                  </div>
                </div>

                <!-- Fehler -->
                <div v-if="statusError[req.id]" class="ride-status-error" role="alert">
                  <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
                  {{ statusError[req.id] }}
                </div>
              </template>
            </div>
          </div>
        </div>
      </section>

    </template>

    <!-- ── Bestätigungs-Dialog: Schicht beenden ──────────────────────────── -->
    <div v-if="confirmEndShift" class="confirm-overlay" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
      <div class="confirm-panel">
        <h2 id="confirm-title" class="confirm-title">Schicht wirklich beenden?</h2>
        <p class="confirm-body">Die Schicht wird mit Zeitstempel beendet und kann nicht reaktiviert werden.</p>
        <div class="confirm-btns">
          <button class="driver-btn driver-btn--ghost" :disabled="actionLoading" @click="confirmEndShift = false">
            Abbrechen
          </button>
          <button class="driver-btn driver-btn--danger" :disabled="actionLoading" @click="doEnd">
            <i v-if="actionLoading" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
            Schicht beenden
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  getDriverContext, startShift, endShift, pauseShift, resumeShift, searchVehicles,
  getDriverAssignments, createRideStatusEvent, getRideStatusEvents,
  getSpontaneousRideRequests, acceptSpontaneousRideRequest, declineSpontaneousRideRequest,
  updateDriverLocation,
} from '@/api/driver'
import type {
  DriverDashboardContext, RideStatusEvent, RideStatusEventType,
  SpontaneousRideRequestItem, TransportRequestListItem, VehicleBrief,
} from '@/types'
import { RIDE_STATUS_EVENT_LABELS, VEHICLE_TYPE_LABELS } from '@/types'

// ── State ──────────────────────────────────────────────────────────────────

const context = ref<DriverDashboardContext | null>(null)
const assignments = ref<TransportRequestListItem[]>([])
const vehicleResults = ref<VehicleBrief[]>([])
const selectedVehicleId = ref<string | null>(null)
const plateInput = ref('')
const showPlateSearch = ref(false)

const loading = ref(true)
const actionLoading = ref(false)
const searchLoading = ref(false)
const searchDone = ref(false)
const assignmentsLoading = ref(false)
const confirmEndShift = ref(false)
const errorMsg = ref<string | null>(null)

// ── Spontane Fahrtanfragen ─────────────────────────────────────────────────

const spontaneousRequests = ref<SpontaneousRideRequestItem[]>([])
const spontaneousLoading = ref(false)
const spontaneousActionLoading = ref<Record<string, boolean>>({})
const spontaneousError = ref<Record<string, string | null>>({})

const SPONTANEOUS_POLL_INTERVAL_MS = 10_000
let spontaneousPollingInterval: ReturnType<typeof setInterval> | null = null

// ── Standort-Teilen (spontane Fahrten, Sprint 12D) ────────────────────────────

const LOCATION_SHARE_INTERVAL_MS = 15_000
const locationSharingActive = ref<Record<string, boolean>>({})
const locationSharingError = ref<Record<string, string | null>>({})
const locationIntervals: Record<string, ReturnType<typeof setInterval>> = {}

async function sendLocationForRide(requestId: string, lat: number, lon: number): Promise<void> {
  try {
    await updateDriverLocation({ latitude: lat, longitude: lon, transport_request_id: requestId })
  } catch {
    // Nicht-kritisch für automatische Aktualisierungen — Fehler still ignorieren
  }
}

function stopLocationSharing(requestId: string): void {
  if (locationIntervals[requestId]) {
    clearInterval(locationIntervals[requestId])
    delete locationIntervals[requestId]
  }
  locationSharingActive.value[requestId] = false
}

function startLocationSharing(requestId: string): void {
  if (!navigator.geolocation) {
    locationSharingError.value[requestId] = 'Ihr Browser unterstützt keine Standortermittlung.'
    return
  }
  locationSharingError.value[requestId] = null
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      locationSharingActive.value[requestId] = true
      await sendLocationForRide(requestId, pos.coords.latitude, pos.coords.longitude)
      locationIntervals[requestId] = setInterval(() => {
        navigator.geolocation.getCurrentPosition(
          (p) => sendLocationForRide(requestId, p.coords.latitude, p.coords.longitude),
          () => {}, // stille Fehler bei Aktualisierungen
        )
      }, LOCATION_SHARE_INTERVAL_MS)
    },
    (err) => {
      if (err.code === GeolocationPositionError.PERMISSION_DENIED) {
        locationSharingError.value[requestId] =
          'Standortzugriff verweigert. Bitte Einstellung im Browser prüfen.'
      } else {
        locationSharingError.value[requestId] = 'Standort konnte nicht ermittelt werden.'
      }
    },
    { timeout: 10000 },
  )
}

// ── Ride Status Events ─────────────────────────────────────────────────────────

const statusEventsMap = ref<Record<string, RideStatusEvent[]>>({})
const statusEventsLoading = ref<Record<string, boolean>>({})
const statusActionLoading = ref<Record<string, boolean>>({})
const statusError = ref<Record<string, string | null>>({})
const issueInputOpen = ref<Record<string, boolean>>({})
const issueNotes = ref<Record<string, string>>({})

const STATUS_ACTIONS: Array<{ status: RideStatusEventType; label: string; icon: string }> = [
  { status: 'driver_on_way',       label: 'Ich bin unterwegs',    icon: 'pi-car' },
  { status: 'driver_arrived',      label: 'Ich bin angekommen',   icon: 'pi-map-marker' },
  { status: 'passenger_picked_up', label: 'Fahrgast aufgenommen', icon: 'pi-user-plus' },
  { status: 'ride_started',        label: 'Fahrt gestartet',      icon: 'pi-play' },
  { status: 'ride_completed',      label: 'Fahrt abgeschlossen',  icon: 'pi-check-circle' },
]

function lastEventFor(requestId: string): RideStatusEvent | undefined {
  const events = statusEventsMap.value[requestId]
  return events && events.length > 0 ? events[events.length - 1] : undefined
}

async function loadStatusEvents(requestId: string) {
  statusEventsLoading.value[requestId] = true
  try {
    statusEventsMap.value[requestId] = await getRideStatusEvents(requestId)
  } catch {
    statusEventsMap.value[requestId] = []
  } finally {
    statusEventsLoading.value[requestId] = false
  }
}

async function setStatus(requestId: string, eventStatus: RideStatusEventType) {
  statusActionLoading.value[requestId] = true
  statusError.value[requestId] = null
  try {
    const event = await createRideStatusEvent(requestId, { status: eventStatus })
    if (!statusEventsMap.value[requestId]) statusEventsMap.value[requestId] = []
    statusEventsMap.value[requestId].push(event)
    if (eventStatus === 'ride_completed' || eventStatus === 'ride_cancelled') {
      await loadAssignments()
    }
  } catch (err: unknown) {
    statusError.value[requestId] = extractError(err)
  } finally {
    statusActionLoading.value[requestId] = false
  }
}

function toggleIssueInput(requestId: string) {
  issueInputOpen.value[requestId] = !issueInputOpen.value[requestId]
  if (!issueNotes.value[requestId]) issueNotes.value[requestId] = ''
}

async function reportIssue(requestId: string) {
  statusActionLoading.value[requestId] = true
  statusError.value[requestId] = null
  try {
    const event = await createRideStatusEvent(requestId, {
      status: 'issue_reported',
      note: issueNotes.value[requestId] || null,
    })
    if (!statusEventsMap.value[requestId]) statusEventsMap.value[requestId] = []
    statusEventsMap.value[requestId].push(event)
    issueInputOpen.value[requestId] = false
    issueNotes.value[requestId] = ''
  } catch (err: unknown) {
    statusError.value[requestId] = extractError(err)
  } finally {
    statusActionLoading.value[requestId] = false
  }
}

// ── Computed ───────────────────────────────────────────────────────────────

const statusTitle = computed(() => {
  const s = context.value?.active_shift?.shift.status
  if (s === 'active') return 'Schicht aktiv'
  if (s === 'paused') return 'Pause'
  return 'Keine aktive Schicht'
})

const statusCardClass = computed(() => {
  const s = context.value?.active_shift?.shift.status
  if (s === 'active') return 'status-card--active'
  if (s === 'paused') return 'status-card--paused'
  return 'status-card--idle'
})

const statusIconClass = computed(() => {
  const s = context.value?.active_shift?.shift.status
  if (s === 'active') return 'status-icon--active'
  if (s === 'paused') return 'status-icon--paused'
  return 'status-icon--idle'
})

const statusIconPi = computed(() => {
  const s = context.value?.active_shift?.shift.status
  if (s === 'active') return 'pi pi-check-circle'
  if (s === 'paused') return 'pi pi-pause-circle'
  return 'pi pi-moon'
})

// ── Init ───────────────────────────────────────────────────────────────────

onMounted(async () => {
  await Promise.all([loadContext(), loadAssignments(), loadSpontaneousRequests()])
  spontaneousPollingInterval = setInterval(loadSpontaneousRequests, SPONTANEOUS_POLL_INTERVAL_MS)
})

onUnmounted(() => {
  for (const id of Object.keys(locationIntervals)) {
    clearInterval(locationIntervals[id])
  }
  if (spontaneousPollingInterval !== null) {
    clearInterval(spontaneousPollingInterval)
    spontaneousPollingInterval = null
  }
})

async function loadContext() {
  loading.value = true
  try {
    context.value = await getDriverContext()
  } catch {
    errorMsg.value = 'Dashboard konnte nicht geladen werden.'
  } finally {
    loading.value = false
  }
}

async function loadAssignments() {
  assignmentsLoading.value = true
  try {
    assignments.value = await getDriverAssignments()
    // Statusereignisse für alle Aufträge parallel laden
    await Promise.all(assignments.value.map((r) => loadStatusEvents(r.id)))
  } catch {
    assignments.value = []
  } finally {
    assignmentsLoading.value = false
  }
}

async function loadSpontaneousRequests() {
  spontaneousLoading.value = true
  try {
    spontaneousRequests.value = await getSpontaneousRideRequests()
  } catch {
    spontaneousRequests.value = []
  } finally {
    spontaneousLoading.value = false
  }
}

async function acceptRequest(requestId: string) {
  spontaneousActionLoading.value[requestId] = true
  spontaneousError.value[requestId] = null
  try {
    await acceptSpontaneousRideRequest(requestId)
    await Promise.all([loadSpontaneousRequests(), loadAssignments()])
  } catch (err: unknown) {
    spontaneousError.value[requestId] = extractError(err)
  } finally {
    spontaneousActionLoading.value[requestId] = false
  }
}

async function declineRequest(requestId: string) {
  spontaneousActionLoading.value[requestId] = true
  spontaneousError.value[requestId] = null
  try {
    await declineSpontaneousRideRequest(requestId)
    await loadSpontaneousRequests()
  } catch (err: unknown) {
    spontaneousError.value[requestId] = extractError(err)
  } finally {
    spontaneousActionLoading.value[requestId] = false
  }
}

// ── Fahrzeugsuche ──────────────────────────────────────────────────────────

async function searchVehicle() {
  const plate = plateInput.value.trim()
  if (!plate) return
  searchLoading.value = true
  searchDone.value = false
  vehicleResults.value = []
  selectedVehicleId.value = null
  errorMsg.value = null
  try {
    vehicleResults.value = await searchVehicles(plate)
    searchDone.value = true
  } catch {
    errorMsg.value = 'Fahrzeugsuche fehlgeschlagen.'
  } finally {
    searchLoading.value = false
  }
}

// ── Schicht starten ────────────────────────────────────────────────────────

async function startWithDefaultVehicle() {
  await doStart({})
}

async function startWithSelectedVehicle() {
  if (!selectedVehicleId.value) return
  await doStart({ vehicle_id: selectedVehicleId.value })
}

async function doStart(payload: { vehicle_id?: string }) {
  actionLoading.value = true
  errorMsg.value = null
  try {
    const result = await startShift(payload)
    if (context.value) {
      context.value = { ...context.value, active_shift: result }
    }
    showPlateSearch.value = false
    vehicleResults.value = []
    plateInput.value = ''
    selectedVehicleId.value = null
    searchDone.value = false
    await loadAssignments()
  } catch (err: unknown) {
    errorMsg.value = extractError(err)
  } finally {
    actionLoading.value = false
  }
}

// ── Schicht-Aktionen ───────────────────────────────────────────────────────

async function doPause() {
  actionLoading.value = true
  errorMsg.value = null
  try {
    await pauseShift()
    await loadContext()
  } catch (err: unknown) {
    errorMsg.value = extractError(err)
  } finally {
    actionLoading.value = false
  }
}

async function doResume() {
  actionLoading.value = true
  errorMsg.value = null
  try {
    await resumeShift()
    await loadContext()
  } catch (err: unknown) {
    errorMsg.value = extractError(err)
  } finally {
    actionLoading.value = false
  }
}

async function doEnd() {
  actionLoading.value = true
  errorMsg.value = null
  try {
    await endShift()
    await loadContext()
    confirmEndShift.value = false
    await loadAssignments()
  } catch (err: unknown) {
    errorMsg.value = extractError(err)
    confirmEndShift.value = false
  } finally {
    actionLoading.value = false
  }
}

// ── Hilfsfunktionen ────────────────────────────────────────────────────────

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
}

function extractError(err: unknown): string {
  const e = err as { response?: { data?: { detail?: string } } }
  return e?.response?.data?.detail ?? 'Unbekannter Fehler.'
}
</script>

<style scoped>
/* ─── Layout ─────────────────────────────────────────────────────────── */
.driver-app {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
  max-width: 680px;
}

/* ─── Fehler / Laden ─────────────────────────────────────────────────── */
.driver-error {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  background: var(--am-danger-bg, #fef2f2);
  color: var(--am-danger, #dc2626);
  border: 1px solid var(--am-danger, #dc2626);
  border-radius: var(--am-radius-s);
  padding: var(--am-space-m);
  font-size: 0.9rem;
}
.error-dismiss {
  margin-left: auto;
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  padding: 0 4px;
}
.driver-loading {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  color: var(--am-text-secondary);
  padding: var(--am-space-xl);
  justify-content: center;
  font-size: 1rem;
}

/* ─── Statuskarte ────────────────────────────────────────────────────── */
.status-card {
  background: var(--am-bg-card);
  border-radius: var(--am-radius-m);
  border: 2px solid var(--am-border);
  padding: var(--am-space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}
.status-card--idle  { border-color: var(--am-border); }
.status-card--active { border-color: var(--am-success, #22c55e); }
.status-card--paused { border-color: var(--am-warning, #f59e0b); }

.status-header {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
}
.status-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  font-size: 1.4rem;
  flex-shrink: 0;
}
.status-icon--idle   { background: var(--am-bg-raised); color: var(--am-text-secondary); }
.status-icon--active { background: rgba(34,197,94,0.15); color: var(--am-success, #16a34a); }
.status-icon--paused { background: rgba(245,158,11,0.15); color: var(--am-warning, #d97706); }

.status-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
}
.status-sub {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 4px 0 0;
}

/* ─── Fahrzeugkarte ──────────────────────────────────────────────────── */
.vehicle-card {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-m);
  background: var(--am-bg-raised);
  border-radius: var(--am-radius-s);
  padding: var(--am-space-m);
  border: 1px solid var(--am-border);
}
.vehicle-card--default { border-color: var(--am-accent); }
.vehicle-card--active  { border-color: var(--am-success, #22c55e); }

.vehicle-card-icon {
  font-size: 1.6rem;
  color: var(--am-accent);
  margin-top: 2px;
  flex-shrink: 0;
}
.vehicle-card-info { flex: 1; }
.vehicle-card-plate {
  display: block;
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: 0.06em;
}
.vehicle-card-name {
  display: block;
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 2px 0 6px;
}
.vehicle-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* ─── Kein Standardfahrzeug ──────────────────────────────────────────── */
.no-vehicle-hint {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.9rem;
  color: var(--am-text-secondary);
  background: var(--am-bg-raised);
  border-radius: var(--am-radius-s);
  padding: var(--am-space-m);
  border: 1px solid var(--am-border);
}

/* ─── Kennzeichen-Suche ──────────────────────────────────────────────── */
.plate-search-section {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}
.plate-search-row {
  display: flex;
  gap: var(--am-space-s);
}
.plate-input {
  flex: 1;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.search-empty {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  padding: var(--am-space-s) 0;
}
.vehicle-results {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}
.vehicle-result-item {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 2px solid var(--am-border);
  border-radius: var(--am-radius-s);
  padding: var(--am-space-m);
  cursor: pointer;
  text-align: left;
  width: 100%;
  transition: border-color var(--am-transition);
}
.vehicle-result-item:hover { border-color: var(--am-accent); }
.vehicle-result-item--selected { border-color: var(--am-accent); }
.vehicle-result-info { flex: 1; }
.selected-check { font-size: 1.2rem; color: var(--am-accent); flex-shrink: 0; }

/* ─── Schicht-Buttons ────────────────────────────────────────────────── */
.shift-btns {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

/* ─── Driver Buttons ─────────────────────────────────────────────────── */
.driver-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--am-space-s);
  padding: 16px var(--am-space-xl);
  border-radius: var(--am-radius-s);
  font-size: 1rem;
  font-weight: 700;
  border: 2px solid transparent;
  cursor: pointer;
  min-height: 56px;
  width: 100%;
  transition: opacity var(--am-transition), background var(--am-transition);
  line-height: 1;
}
.driver-btn:disabled { opacity: 0.45; cursor: not-allowed; }

.driver-btn--primary {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
  border-color: var(--am-accent);
}
.driver-btn--primary:hover:not(:disabled) { opacity: 0.9; }

.driver-btn--secondary {
  background: var(--am-bg-raised);
  color: var(--am-text-primary);
  border-color: var(--am-border);
}
.driver-btn--secondary:hover:not(:disabled) { border-color: var(--am-text-primary); }

.driver-btn--danger {
  background: var(--am-danger, #dc2626);
  color: #fff;
  border-color: var(--am-danger, #dc2626);
}
.driver-btn--danger:hover:not(:disabled) { opacity: 0.88; }

.driver-btn--ghost {
  background: transparent;
  color: var(--am-text-secondary);
  border-color: var(--am-border);
}

.driver-btn--sm { min-height: 44px; padding: 10px var(--am-space-m); font-size: 0.9rem; }

.driver-btn-link {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: var(--am-text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  padding: 4px 0;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.driver-btn-link:hover { color: var(--am-text-primary); }
.driver-btn-link--sm { font-size: 0.8rem; }

/* ─── Aufträge ───────────────────────────────────────────────────────── */
.assignments-section {
  background: var(--am-bg-card);
  border-radius: var(--am-radius-m);
  border: 1px solid var(--am-border);
  padding: var(--am-space-l) var(--am-space-xl);
}
.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--am-space-m);
}
.section-heading {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 var(--am-space-m);
}
.section-loading,
.section-placeholder {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  padding: var(--am-space-m) 0;
}
.assignment-list {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}
.assignment-card {
  display: grid;
  grid-template-columns: 56px 1fr;
  grid-template-rows: auto auto;
  gap: 4px var(--am-space-m);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  padding: var(--am-space-m);
}
.assignment-time {
  grid-row: 1 / 3;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1rem;
  color: var(--am-accent);
}
.assignment-route {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.875rem;
}
.assignment-address {
  display: flex;
  align-items: flex-start;
  gap: 6px;
}
.pickup-coords {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.pickup-coords small {
  font-size: 0.76em;
  opacity: 0.7;
}
.assignment-arrow {
  padding-left: 8px;
  color: var(--am-text-secondary);
  font-size: 0.8rem;
}
.assignment-passenger {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--am-text-secondary);
}

/* ─── Ride Status Events ─────────────────────────────────────────────────── */
.ride-status-section {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
  border-top: 1px solid var(--am-border);
  padding-top: var(--am-space-s);
  margin-top: var(--am-space-s);
}

.ride-status-loading {
  font-size: 0.8rem;
  color: var(--am-text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.ride-status-current {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  color: var(--am-text-secondary);
  flex-wrap: wrap;
}

.ride-status-current strong {
  color: var(--am-text-primary);
}

.ride-status-time {
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  margin-left: 4px;
}

.ride-status-none {
  font-size: 0.8rem;
  color: var(--am-text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.ride-status-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.ride-status-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--am-radius-s);
  border: 1px solid var(--am-border-strong);
  background: var(--am-bg-base);
  color: var(--am-text-primary);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  min-height: 36px;
  transition: background var(--am-transition), border-color var(--am-transition);
}

.ride-status-btn:hover:not(:disabled) {
  background: var(--am-accent-bg);
  border-color: var(--am-accent);
}

.ride-status-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ride-status-btn--issue {
  border-color: var(--am-danger, #dc2626);
  color: var(--am-danger, #dc2626);
}

.ride-status-btn--issue:hover:not(:disabled) {
  background: var(--am-danger-bg, #fef2f2);
  border-color: var(--am-danger, #dc2626);
}

.ride-status-btn--issue-send {
  border-color: var(--am-accent);
  background: var(--am-accent);
  color: var(--am-text-on-accent);
}

.ride-issue-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ride-issue-input-row {
  display: flex;
  gap: var(--am-space-s);
  align-items: center;
}

.ride-issue-input {
  flex: 1;
  font-size: 0.85rem;
  height: 36px;
  padding: 0 10px;
}

.ride-status-error {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--am-danger, #dc2626);
  background: var(--am-danger-bg, #fef2f2);
  padding: 6px 10px;
  border-radius: var(--am-radius-s);
  border: 1px solid var(--am-danger, #dc2626);
}

/* ─── Bestätigungs-Dialog ────────────────────────────────────────────── */
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 100;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: var(--am-space-l);
}
.confirm-panel {
  background: var(--am-bg-card);
  border-radius: var(--am-radius-m) var(--am-radius-m) 0 0;
  padding: var(--am-space-xl);
  width: 100%;
  max-width: 480px;
}
.confirm-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0 0 var(--am-space-s);
}
.confirm-body {
  font-size: 0.9rem;
  color: var(--am-text-secondary);
  margin-bottom: var(--am-space-l);
}
.confirm-btns {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

/* ─── Abschnitt Titel mit Aktionen ──────────────────────────────────── */
.section-title-actions {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
}

.section-auto-refresh-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  opacity: 0.7;
}

/* ─── Spontane Fahrtanfragen ─────────────────────────────────────────── */
.spontan-req-card {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}

.spontan-req-actions {
  display: flex;
  gap: var(--am-space-s);
}

.spontan-req-actions .driver-btn {
  min-height: 44px;
  padding: 10px var(--am-space-l);
  font-size: 0.9rem;
}

.driver-btn--success {
  background: var(--am-success, #22c55e);
  color: #fff;
  border-color: var(--am-success, #22c55e);
}

.driver-btn--success:hover:not(:disabled) { opacity: 0.9; }

/* ─── Standort-Teilen ────────────────────────────────────────────────── */
.location-share-section {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
  border-top: 1px solid var(--am-border);
  padding-top: var(--am-space-s);
  margin-top: var(--am-space-s);
}

.location-privacy-notice {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  color: var(--am-text-secondary);
}

.location-share-btns {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

.driver-btn--location {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
  border-color: var(--am-accent);
}

.driver-btn--location:hover:not(:disabled) { opacity: 0.9; }

.driver-btn--location-stop {
  background: var(--am-bg-raised);
  color: var(--am-text-secondary);
  border-color: var(--am-border-strong);
}

.location-share-active-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
  color: var(--am-success, #22c55e);
  font-weight: 600;
}

.location-pulse {
  font-size: 0.55rem;
  animation: location-blink 1.4s ease-in-out infinite;
}

@keyframes location-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}
</style>
