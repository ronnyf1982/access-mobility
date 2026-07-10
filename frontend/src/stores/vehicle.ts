import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  getVehicles,
  createVehicle,
  updateVehicle,
  deactivateVehicle,
  permanentDeleteVehicle,
  getVehicleOptions,
  type VehicleOptions,
} from '@/api/vehicle'
import type { Vehicle, VehicleCreate, VehicleUpdate } from '@/types'

export const useVehicleStore = defineStore('vehicle', () => {
  const vehicles = ref<Vehicle[]>([])
  const options = ref<VehicleOptions | null>(null)
  const loading = ref(false)
  const saving = ref(false)

  const activeVehicles = computed(() => vehicles.value.filter((v) => v.is_active))
  const totalCount = computed(() => vehicles.value.length)
  const activeCount = computed(() => activeVehicles.value.length)

  async function load(): Promise<void> {
    loading.value = true
    try {
      vehicles.value = await getVehicles()
    } finally {
      loading.value = false
    }
  }

  async function loadOptions(): Promise<void> {
    if (options.value) return
    options.value = await getVehicleOptions()
  }

  async function create(payload: VehicleCreate): Promise<Vehicle> {
    saving.value = true
    try {
      const vehicle = await createVehicle(payload)
      vehicles.value.push(vehicle)
      return vehicle
    } finally {
      saving.value = false
    }
  }

  async function update(id: string, payload: VehicleUpdate): Promise<Vehicle> {
    saving.value = true
    try {
      const updated = await updateVehicle(id, payload)
      const idx = vehicles.value.findIndex((v) => v.id === id)
      if (idx >= 0) vehicles.value[idx] = updated
      return updated
    } finally {
      saving.value = false
    }
  }

  async function deactivate(id: string): Promise<Vehicle> {
    const updated = await deactivateVehicle(id)
    const idx = vehicles.value.findIndex((v) => v.id === id)
    if (idx >= 0) vehicles.value[idx] = updated
    return updated
  }

  async function reactivate(id: string): Promise<Vehicle> {
    return update(id, { is_active: true })
  }

  async function permanentDelete(id: string): Promise<void> {
    await permanentDeleteVehicle(id)
    vehicles.value = vehicles.value.filter((v) => v.id !== id)
  }

  return {
    vehicles,
    options,
    loading,
    saving,
    activeVehicles,
    totalCount,
    activeCount,
    load,
    loadOptions,
    create,
    update,
    deactivate,
    reactivate,
    permanentDelete,
  }
})
