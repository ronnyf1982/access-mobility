<template>
  <div
    ref="mapEl"
    class="spontaneous-map"
    role="img"
    :aria-label="ariaLabel"
  ></div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { SpontaneousRideMatchResult } from '@/types'

import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'

L.Icon.Default.mergeOptions({ iconUrl, iconRetinaUrl, shadowUrl })

const props = withDefaults(defineProps<{
  pickupLat: number
  pickupLon: number
  matches?: SpontaneousRideMatchResult[]
  driverLat?: number | null
  driverLon?: number | null
}>(), {
  matches: () => [],
  driverLat: null,
  driverLon: null,
})

const ariaLabel = computed(() =>
  props.driverLat != null
    ? 'Karte mit Fahrerposition und Abholpunkt'
    : 'Karte mit verfügbaren Fahrzeugen in der Nähe',
)

const mapEl = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let dynamicLayer: L.LayerGroup | null = null

function buildPassengerIcon(): L.DivIcon {
  return L.divIcon({
    className: '',
    html: '<div class="smap-marker smap-marker--passenger" title="Mein Standort">📍</div>',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
  })
}

function buildVehicleIcon(): L.DivIcon {
  return L.divIcon({
    className: '',
    html: '<div class="smap-marker smap-marker--vehicle" title="Verfügbares Fahrzeug">🚐</div>',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
  })
}

function buildDriverIcon(): L.DivIcon {
  return L.divIcon({
    className: '',
    html: '<div class="smap-marker smap-marker--driver" title="Fahrer">🚗</div>',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
  })
}

function renderDynamic(): void {
  if (!map || !dynamicLayer) return
  dynamicLayer.clearLayers()

  if (props.driverLat != null && props.driverLon != null) {
    // Tracking-Modus: Fahrer-Marker
    L.marker([props.driverLat, props.driverLon], { icon: buildDriverIcon() })
      .bindTooltip('Fahrer', { permanent: true, direction: 'top' })
      .addTo(dynamicLayer!)

    // Karte auf beide Punkte anpassen
    const bounds = L.latLngBounds(
      [props.pickupLat, props.pickupLon],
      [props.driverLat, props.driverLon],
    )
    map.fitBounds(bounds, { padding: [40, 40] })
  } else {
    // Such-Modus: Fahrzeug-Marker
    for (const m of props.matches) {
      const popup = L.popup({ closeButton: false }).setContent(
        `<strong>${m.vehicle_label}</strong><br>` +
          `Entfernung: ${m.distance_km.toFixed(1)} km<br>` +
          `Ankunft ca. ${m.estimated_arrival_minutes} Min.<br>` +
          (m.matched_capabilities.length
            ? `Ausstattung: ${m.matched_capabilities.join(', ')}`
            : ''),
      )
      L.marker([m.vehicle_latitude, m.vehicle_longitude], { icon: buildVehicleIcon() })
        .bindPopup(popup)
        .addTo(dynamicLayer!)
    }
  }
}

onMounted(() => {
  if (!mapEl.value) return
  map = L.map(mapEl.value).setView([props.pickupLat, props.pickupLon], 13)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution:
      '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende',
    maxZoom: 19,
  }).addTo(map)

  L.marker([props.pickupLat, props.pickupLon], { icon: buildPassengerIcon() })
    .bindTooltip('Mein Standort', { permanent: true, direction: 'top' })
    .addTo(map)

  dynamicLayer = L.layerGroup().addTo(map)
  renderDynamic()
})

watch(() => [props.matches, props.driverLat, props.driverLon], renderDynamic, { deep: true })

onUnmounted(() => {
  map?.remove()
  map = null
})
</script>

<style scoped>
.spontaneous-map {
  width: 100%;
  height: 380px;
  border-radius: 8px;
  border: 1px solid var(--p-surface-border, #dee2e6);
}
</style>

<style>
.smap-marker {
  font-size: 28px;
  line-height: 1;
  cursor: default;
}
</style>
