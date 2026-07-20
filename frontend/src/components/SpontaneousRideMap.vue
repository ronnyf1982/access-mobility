<template>
  <div
    ref="mapEl"
    class="spontaneous-map"
    role="img"
    aria-label="Karte mit verfügbaren Fahrzeugen in der Nähe"
  ></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { SpontaneousRideMatchResult } from '@/types'

// Fix Leaflet default icon paths for Vite builds (icons are imported as assets)
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'

L.Icon.Default.mergeOptions({ iconUrl, iconRetinaUrl, shadowUrl })

const props = defineProps<{
  pickupLat: number
  pickupLon: number
  matches: SpontaneousRideMatchResult[]
}>()

const mapEl = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let vehicleLayer: L.LayerGroup | null = null

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

function renderVehicles(): void {
  if (!map || !vehicleLayer) return
  vehicleLayer.clearLayers()
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
      .addTo(vehicleLayer!)
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

  vehicleLayer = L.layerGroup().addTo(map)
  renderVehicles()
})

watch(() => props.matches, renderVehicles, { deep: true })

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
