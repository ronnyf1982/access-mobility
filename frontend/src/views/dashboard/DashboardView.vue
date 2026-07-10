<template>
  <div class="dashboard">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">Guten Morgen — Freitag, 10. Juli 2026</p>
      </div>
      <RouterLink to="/" class="am-btn am-btn-ghost page-header-back">
        <i class="pi pi-arrow-left" aria-hidden="true"></i>
        Zur Startseite
      </RouterLink>
    </div>

    <!-- Rollen-Kontext -->
    <div v-if="authStore.user" class="role-context" role="region" aria-label="Ihr Konto">
      <div class="role-context-inner">
        <div class="role-context-icon" aria-hidden="true">
          <i class="pi pi-user"></i>
        </div>
        <div class="role-context-text">
          <span class="role-context-name">
            Willkommen, <strong>{{ authStore.fullName }}</strong>
          </span>
          <span class="role-context-desc">
            <span class="am-badge am-badge-neutral role-badge">{{ currentRoleLabel }}</span>
            {{ currentRoleContext }}
          </span>
        </div>
      </div>
    </div>

    <!-- KPI Kacheln -->
    <div class="kpi-grid" role="region" aria-label="Kennzahlen">
      <component
        :is="kpi.to ? 'RouterLink' : 'div'"
        v-for="kpi in kpiCards"
        :key="kpi.label"
        class="kpi-card am-card"
        :class="{ 'kpi-card--link': !!kpi.to }"
        :to="kpi.to ?? undefined"
      >
        <div class="kpi-icon-box" :style="{ background: kpi.iconBg }" aria-hidden="true">
          <i :class="['pi', kpi.icon]"></i>
        </div>
        <div class="kpi-data">
          <span class="kpi-value">{{ kpi.value }}</span>
          <span class="kpi-label">{{ kpi.label }}</span>
          <span class="kpi-sub" :class="kpi.subClass">{{ kpi.sub }}</span>
        </div>
      </component>
    </div>

    <!-- Hauptbereich -->
    <div class="dashboard-body">
      <!-- Linke Spalte: Tabelle -->
      <section class="am-card rides-section" aria-labelledby="rides-heading">
        <div class="section-toolbar">
          <h2 id="rides-heading" class="section-title">Anstehende Fahrten</h2>
          <div class="section-actions">
            <button class="am-btn am-btn-ghost toolbar-btn">
              <i class="pi pi-filter" aria-hidden="true"></i>
              Filter
            </button>
            <button class="am-btn am-btn-primary toolbar-btn">
              <i class="pi pi-plus" aria-hidden="true"></i>
              Fahrt buchen
            </button>
          </div>
        </div>

        <div class="table-wrapper" role="region" aria-label="Fahrtenliste" tabindex="0">
          <table class="rides-table" aria-label="Anstehende Fahrten">
            <thead>
              <tr>
                <th scope="col">Datum</th>
                <th scope="col">Zeit</th>
                <th scope="col">Fahrgast</th>
                <th scope="col" class="am-hide-mobile">Von</th>
                <th scope="col" class="am-hide-mobile">Nach</th>
                <th scope="col" class="am-hide-mobile">Fahrzeug</th>
                <th scope="col">Fahrer:in</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ride in rides" :key="ride.id" class="rides-row">
                <td class="td-date">{{ ride.date }}</td>
                <td class="td-time">{{ ride.time }}</td>
                <td class="td-passenger">
                  <div class="passenger-cell">
                    <div class="passenger-avatar" aria-hidden="true">
                      {{ initials(ride.passenger) }}
                    </div>
                    <span>{{ ride.passenger }}</span>
                  </div>
                </td>
                <td class="td-addr am-hide-mobile">
                  <span class="addr-truncate" :title="ride.from">{{ ride.from }}</span>
                </td>
                <td class="td-addr am-hide-mobile">
                  <span class="addr-truncate" :title="ride.to">{{ ride.to }}</span>
                </td>
                <td class="am-hide-mobile">
                  <span class="vehicle-chip">{{ ride.vehicle }}</span>
                </td>
                <td>{{ ride.driver }}</td>
                <td>
                  <span
                    class="am-badge"
                    :class="statusClass(ride.status)"
                    :aria-label="`Status: ${statusLabel(ride.status)}`"
                  >
                    <i :class="['pi', statusIcon(ride.status)]" aria-hidden="true"></i>
                    {{ statusLabel(ride.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="table-footer">
          <span class="table-count">{{ rides.length }} Fahrten angezeigt</span>
          <button class="am-btn am-btn-ghost toolbar-btn">Alle Fahrten anzeigen</button>
        </div>
      </section>

      <!-- Rechte Spalte -->
      <aside class="dashboard-sidebar-right">
        <!-- Mobilitätsprofil-Status -->
        <section
          v-if="authStore.role === 'passenger' || authStore.role === 'trusted_person'"
          class="am-card profile-status-card"
          aria-labelledby="profile-status-heading"
        >
          <h3 id="profile-status-heading" class="widget-title">Mein Mobilitätsprofil</h3>
          <div v-if="profileStore.isProfileFilled" class="profile-status profile-status--filled">
            <i class="pi pi-check-circle" aria-hidden="true"></i>
            <div>
              <p class="profile-status-line">Profil hinterlegt</p>
              <p class="profile-status-sub">Ihre Angaben helfen, das richtige Fahrzeug zu finden.</p>
            </div>
          </div>
          <div v-else class="profile-status profile-status--empty">
            <i class="pi pi-exclamation-triangle" aria-hidden="true"></i>
            <div>
              <p class="profile-status-line">Noch kein Profil</p>
              <p class="profile-status-sub">Hinterlegen Sie Ihren Mobilitätsbedarf für bessere Fahrtenplanung.</p>
            </div>
          </div>
          <RouterLink to="/mobility-profile" class="am-btn am-btn-primary profile-status-btn">
            <i class="pi pi-pencil" aria-hidden="true"></i>
            {{ profileStore.isProfileFilled ? 'Profil bearbeiten' : 'Profil anlegen' }}
          </RouterLink>
        </section>

        <!-- Buchungsübersicht -->
        <section class="am-card" aria-labelledby="booking-overview-heading">
          <h3 id="booking-overview-heading" class="widget-title">Buchungsübersicht</h3>
          <p class="widget-sub">Heute, 10. Juli 2026</p>

          <div class="booking-stats">
            <div class="booking-stat-row" v-for="stat in bookingStats" :key="stat.label">
              <div class="booking-stat-label">
                <span class="booking-dot" :style="{ background: stat.color }"></span>
                {{ stat.label }}
              </div>
              <span class="booking-stat-value">{{ stat.value }}</span>
            </div>
          </div>

          <div class="booking-bar-group" aria-hidden="true">
            <div
              v-for="stat in bookingStats"
              :key="stat.label"
              class="booking-bar"
              :style="{ background: stat.color, flex: stat.value }"
            ></div>
          </div>

          <div class="booking-total">
            <span>Gesamt</span>
            <strong>{{ bookingTotal }} Buchungen</strong>
          </div>
        </section>

        <!-- Einsatzübersicht (Platzhalter) -->
        <section class="am-card map-placeholder" aria-label="Einsatzübersicht – Karte folgt">
          <h3 class="widget-title">Einsatzübersicht</h3>
          <div class="map-box" aria-hidden="true">
            <i class="pi pi-map-marker"></i>
            <span>Kartenansicht</span>
            <span class="map-sub">folgt in einem späteren Sprint</span>
          </div>
        </section>

        <!-- Fahrzeuge & Fahrer -->
        <section class="am-card fleet-stat-card" aria-labelledby="fleet-heading">
          <h3 id="fleet-heading" class="widget-title">Flotte &amp; Fahrer</h3>
          <div class="fleet-stats">
            <RouterLink to="/vehicles" class="fleet-stat-item">
              <div class="fleet-stat-icon" aria-hidden="true">
                <i class="pi pi-truck"></i>
              </div>
              <div class="fleet-stat-data">
                <span class="fleet-stat-value">{{ vehicleStore.activeCount }}</span>
                <span class="fleet-stat-label">Fahrzeuge aktiv</span>
              </div>
            </RouterLink>
            <RouterLink to="/drivers" class="fleet-stat-item">
              <div class="fleet-stat-icon" aria-hidden="true">
                <i class="pi pi-id-card"></i>
              </div>
              <div class="fleet-stat-data">
                <span class="fleet-stat-value">{{ driverStore.activeCount }}</span>
                <span class="fleet-stat-label">Fahrer aktiv</span>
              </div>
            </RouterLink>
          </div>
        </section>

        <!-- Schnellaktionen -->
        <section class="am-card" aria-labelledby="quick-actions-heading">
          <h3 id="quick-actions-heading" class="widget-title">Schnellaktionen</h3>
          <div class="quick-actions">
            <button
              v-for="action in quickActions"
              :key="action.label"
              class="quick-action-btn"
              :aria-label="action.label"
            >
              <div class="quick-action-icon" aria-hidden="true">
                <i :class="['pi', action.icon]"></i>
              </div>
              <span class="quick-action-label">{{ action.label }}</span>
            </button>
          </div>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMobilityProfileStore } from '@/stores/mobilityProfile'
import { useVehicleStore } from '@/stores/vehicle'
import { useDriverProfileStore } from '@/stores/driverProfile'
import { useTransportRequestStore } from '@/stores/transportRequests'
import { ROLE_LABELS, ROLE_CONTEXT } from '@/types'

const authStore = useAuthStore()
const profileStore = useMobilityProfileStore()
const vehicleStore = useVehicleStore()
const driverStore = useDriverProfileStore()
const transportStore = useTransportRequestStore()

onMounted(async () => {
  const role = authStore.role
  if ((role === 'passenger' || role === 'trusted_person') && !profileStore.profile) {
    await profileStore.load()
  }
  if (!vehicleStore.vehicles.length) vehicleStore.load()
  if (!driverStore.drivers.length) driverStore.load()
  transportStore.load().catch(() => {})
})
const currentRoleLabel = computed(() =>
  authStore.role ? ROLE_LABELS[authStore.role] : 'Unbekannte Rolle',
)
const currentRoleContext = computed(() =>
  authStore.role ? ROLE_CONTEXT[authStore.role] : '',
)

/* ── KPI-Kacheln ─────────────────────────────────────── */
const kpiCards = computed(() => [
  {
    label: 'Fahrten heute',
    value: '28',
    icon: 'pi-car',
    iconBg: 'var(--am-accent)',
    sub: '↑ 3 mehr als gestern',
    subClass: 'kpi-sub-positive',
    to: null,
  },
  {
    label: 'Transportanfragen',
    value: String(transportStore.totalCount),
    icon: 'pi-send',
    iconBg: 'rgba(99,102,241,0.2)',
    sub: transportStore.draftCount > 0
      ? `${transportStore.draftCount} Entwurf${transportStore.draftCount !== 1 ? 'e' : ''} offen`
      : transportStore.requestedCount > 0
        ? `${transportStore.requestedCount} gestellt`
        : 'Keine offenen Anfragen',
    subClass: transportStore.draftCount > 0 ? 'kpi-sub-warn' : 'kpi-sub-neutral',
    to: '/transport-requests',
  },
  {
    label: 'Aktive Fahrzeuge',
    value: '12',
    icon: 'pi-truck',
    iconBg: 'rgba(34,197,94,0.2)',
    sub: 'von 15 verfügbar',
    subClass: 'kpi-sub-neutral',
    to: '/vehicles',
  },
  {
    label: 'Pünktlichkeitsrate',
    value: '96 %',
    icon: 'pi-chart-line',
    iconBg: 'rgba(34,197,94,0.2)',
    sub: '↑ +2 % zur Vorwoche',
    subClass: 'kpi-sub-positive',
    to: null,
  },
])

/* ── Fahrtentabelle (Dummy-Daten) ────────────────────── */
interface Ride {
  id: number
  date: string
  time: string
  passenger: string
  from: string
  to: string
  vehicle: string
  driver: string
  status: 'confirmed' | 'in_progress' | 'pending'
}

const rides: Ride[] = [
  {
    id: 1,
    date: 'Fr, 10.07.',
    time: '08:15',
    passenger: 'Maria Schulz',
    from: 'Musterstr. 12, Berlin',
    to: 'Berliner Uniklinik',
    vehicle: 'VW Crafter WB-01',
    driver: 'Klaus Bauer',
    status: 'confirmed',
  },
  {
    id: 2,
    date: 'Fr, 10.07.',
    time: '09:30',
    passenger: 'Thomas Klein',
    from: 'Hauptbahnhof Berlin',
    to: 'Reha-Zentrum Nord',
    vehicle: 'Mercedes Vito WB-02',
    driver: 'Anna Meier',
    status: 'in_progress',
  },
  {
    id: 3,
    date: 'Fr, 10.07.',
    time: '11:00',
    passenger: 'Lisa Müller',
    from: 'Am Park 5, Berlin',
    to: 'Arztpraxis Dr. Wagner',
    vehicle: 'VW Crafter WB-03',
    driver: 'Peter Schulze',
    status: 'pending',
  },
  {
    id: 4,
    date: 'Fr, 10.07.',
    time: '13:45',
    passenger: 'Hans Werner',
    from: 'Schillerplatz 2, Berlin',
    to: 'Tagespflege Sonnenschein',
    vehicle: 'Mercedes Sprinter WB-04',
    driver: 'Sandra Koch',
    status: 'confirmed',
  },
  {
    id: 5,
    date: 'Fr, 10.07.',
    time: '15:20',
    passenger: 'Renate Braun',
    from: 'Lindenweg 8, Potsdam',
    to: 'Krankenhaus Potsdam',
    vehicle: 'VW Crafter WB-01',
    driver: 'Klaus Bauer',
    status: 'pending',
  },
]

function initials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

function statusLabel(s: Ride['status']): string {
  return { confirmed: 'Bestätigt', in_progress: 'Unterwegs', pending: 'Ausstehend' }[s]
}

function statusClass(s: Ride['status']): string {
  return {
    confirmed: 'am-badge-success',
    in_progress: 'am-badge-warning',
    pending: 'am-badge-neutral',
  }[s]
}

function statusIcon(s: Ride['status']): string {
  return {
    confirmed: 'pi-check',
    in_progress: 'pi-car',
    pending: 'pi-hourglass',
  }[s]
}

/* ── Buchungsübersicht ───────────────────────────────── */
const bookingStats = [
  { label: 'Bestätigt',       value: 18, color: 'var(--am-success)' },
  { label: 'In Bearbeitung',  value: 6,  color: 'var(--am-accent)' },
  { label: 'Ausstehend',      value: 4,  color: 'var(--am-text-muted)' },
]

const bookingTotal = computed(() =>
  bookingStats.reduce((sum, s) => sum + s.value, 0),
)

/* ── Schnellaktionen ─────────────────────────────────── */
const quickActions = [
  { label: 'Fahrt buchen',    icon: 'pi-plus' },
  { label: 'Fahrtenliste',    icon: 'pi-list' },
  { label: 'Fahrerbericht',   icon: 'pi-file-pdf' },
]
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

/* Page Header */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
}

.page-subtitle {
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  margin-top: 2px;
}

.page-header-back {
  font-size: 0.85rem;
  padding: 0.4rem 1rem;
  min-height: 38px;
}

/* ── KPI Grid ─────────────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--am-space-m);
}

@media (max-width: 1100px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 580px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
}

.kpi-icon-box {
  width: 44px;
  height: 44px;
  border-radius: var(--am-radius-s);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon-box .pi {
  font-size: 1.1rem;
  color: var(--am-text-on-accent);
}

.kpi-data {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.kpi-value {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--am-text-primary);
  line-height: 1;
}

.kpi-label {
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  font-weight: 500;
}

.kpi-sub {
  font-size: 0.7rem;
  color: var(--am-text-muted);
}

.kpi-sub-positive {
  color: var(--am-success);
}

.kpi-sub-neutral {
  color: var(--am-text-muted);
}

.kpi-sub-warn {
  color: var(--am-accent);
}

.kpi-card--link {
  text-decoration: none;
  cursor: pointer;
  transition: border-color var(--am-transition), transform var(--am-transition);
}

.kpi-card--link:hover {
  border-color: var(--am-accent);
  transform: translateY(-1px);
}

/* ── Dashboard Body ───────────────────────────────────── */
.dashboard-body {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: var(--am-space-l);
  align-items: start;
}

@media (max-width: 1100px) {
  .dashboard-body {
    grid-template-columns: 1fr;
  }
}

/* ── Rides Table ──────────────────────────────────────── */
.rides-section {
  padding: 0;
  overflow: hidden;
}

.section-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--am-space-m);
  padding: var(--am-space-m) var(--am-space-l);
  border-bottom: 1px solid var(--am-border);
  flex-wrap: wrap;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
}

.section-actions {
  display: flex;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

.toolbar-btn {
  font-size: 0.8rem;
  padding: 0.35rem 0.9rem;
  min-height: 36px;
}

.table-wrapper {
  overflow-x: auto;
}

.rides-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.rides-table th {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--am-text-muted);
  padding: var(--am-space-s) var(--am-space-m);
  text-align: left;
  border-bottom: 1px solid var(--am-border);
  white-space: nowrap;
}

.rides-row td {
  padding: 10px var(--am-space-m);
  border-bottom: 1px solid var(--am-border);
  color: var(--am-text-primary);
  vertical-align: middle;
}

.rides-row:last-child td {
  border-bottom: none;
}

.rides-row:hover td {
  background: var(--am-bg-raised);
}

.td-date,
.td-time {
  color: var(--am-text-secondary);
  white-space: nowrap;
  font-size: 0.8rem;
}

.passenger-cell {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  white-space: nowrap;
}

.passenger-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.2);
  color: var(--am-accent);
  font-size: 0.65rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.addr-truncate {
  display: block;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--am-text-secondary);
  font-size: 0.8rem;
}

.vehicle-chip {
  font-size: 0.75rem;
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  padding: 2px 8px;
  color: var(--am-text-secondary);
  white-space: nowrap;
}

.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--am-space-s) var(--am-space-l);
  border-top: 1px solid var(--am-border);
}

.table-count {
  font-size: 0.75rem;
  color: var(--am-text-muted);
}

/* ── Right Sidebar ────────────────────────────────────── */
.dashboard-sidebar-right {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.widget-title {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.widget-sub {
  font-size: 0.75rem;
  color: var(--am-text-muted);
  margin-bottom: var(--am-space-m);
}

/* Booking stats */
.booking-stats {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
  margin-bottom: var(--am-space-m);
}

.booking-stat-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.85rem;
}

.booking-stat-label {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  color: var(--am-text-secondary);
}

.booking-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.booking-stat-value {
  font-weight: 600;
  color: var(--am-text-primary);
}

.booking-bar-group {
  display: flex;
  height: 6px;
  border-radius: 99px;
  overflow: hidden;
  gap: 2px;
  margin-bottom: var(--am-space-m);
}

.booking-bar {
  height: 100%;
  border-radius: 99px;
  min-width: 4px;
}

.booking-total {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--am-text-muted);
  padding-top: var(--am-space-s);
  border-top: 1px solid var(--am-border);
}

.booking-total strong {
  color: var(--am-text-primary);
}

/* Map placeholder */
.map-placeholder {
  padding: var(--am-space-m);
}

.map-box {
  height: 120px;
  border-radius: var(--am-radius-s);
  border: 1px dashed var(--am-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--am-text-muted);
}

.map-box .pi {
  font-size: 1.5rem;
}

.map-box span {
  font-size: 0.8rem;
}

.map-sub {
  font-size: 0.7rem !important;
  color: var(--am-text-muted) !important;
}

/* Role context */
.role-context {
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-m);
  padding: var(--am-space-m) var(--am-space-l);
}

.role-context-inner {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-m);
}

.role-context-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--am-accent);
  font-size: 1rem;
}

.role-context-text {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.role-context-name {
  font-size: 0.9rem;
  color: var(--am-text-primary);
}

.role-context-desc {
  font-size: 0.82rem;
  color: var(--am-text-secondary);
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  flex-wrap: wrap;
}

.role-badge {
  font-size: 0.7rem;
  flex-shrink: 0;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  padding: var(--am-space-s) var(--am-space-m);
  border-radius: var(--am-radius-s);
  border: 1px solid var(--am-border);
  background: var(--am-bg-raised);
  cursor: pointer;
  transition: background var(--am-transition), border-color var(--am-transition);
  min-height: 44px;
}

.quick-action-btn:hover {
  background: var(--am-bg-surface);
  border-color: var(--am-accent);
}

.quick-action-icon {
  width: 30px;
  height: 30px;
  border-radius: var(--am-radius-s);
  background: var(--am-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-action-icon .pi {
  color: var(--am-text-on-accent);
  font-size: 0.85rem;
}

.quick-action-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--am-text-primary);
}

/* Profile Status Card */
.profile-status-card {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}

.profile-status {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s);
  border-radius: var(--am-radius-s);
  font-size: 0.82rem;
}

.profile-status--filled {
  background: var(--am-success-bg);
  border: 1px solid var(--am-success);
  color: var(--am-success);
}

.profile-status--empty {
  background: rgba(255, 214, 0, 0.06);
  border: 1px solid rgba(255, 214, 0, 0.3);
  color: var(--am-accent);
}

.profile-status .pi {
  font-size: 1rem;
  flex-shrink: 0;
  margin-top: 1px;
}

.profile-status-line {
  font-weight: 700;
  margin: 0 0 2px;
  color: inherit;
}

.profile-status-sub {
  margin: 0;
  font-size: 0.76rem;
  color: var(--am-text-secondary);
}

.profile-status-btn {
  font-size: 0.82rem;
  min-height: 36px;
  padding: 0 var(--am-space-m);
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--am-space-s);
}

/* Fleet stat card */
.fleet-stat-card {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}

.fleet-stats {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}

.fleet-stat-item {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  padding: var(--am-space-s) var(--am-space-s);
  border-radius: var(--am-radius-s);
  text-decoration: none;
  transition: background var(--am-transition);
  min-height: 44px;
}

.fleet-stat-item:hover {
  background: var(--am-bg-raised);
}

.fleet-stat-icon {
  width: 34px;
  height: 34px;
  border-radius: var(--am-radius-s);
  background: var(--am-accent-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--am-accent);
  font-size: 0.9rem;
}

.fleet-stat-data {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.fleet-stat-value {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--am-text-primary);
  line-height: 1;
}

.fleet-stat-label {
  font-size: 0.72rem;
  color: var(--am-text-secondary);
}
</style>
