import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  getDrivers,
  createDriver,
  updateDriver,
  deactivateDriver,
  permanentDeleteDriver,
  getDriverOptions,
  type DriverOptions,
} from '@/api/driverProfile'
import type { DriverProfile, DriverProfileCreate, DriverProfileUpdate } from '@/types'

export const useDriverProfileStore = defineStore('driverProfile', () => {
  const drivers = ref<DriverProfile[]>([])
  const options = ref<DriverOptions | null>(null)
  const loading = ref(false)
  const saving = ref(false)

  const activeDrivers = computed(() => drivers.value.filter((d) => d.is_active))
  const totalCount = computed(() => drivers.value.length)
  const activeCount = computed(() => activeDrivers.value.length)

  async function load(): Promise<void> {
    loading.value = true
    try {
      drivers.value = await getDrivers()
    } finally {
      loading.value = false
    }
  }

  async function loadOptions(): Promise<void> {
    if (options.value) return
    options.value = await getDriverOptions()
  }

  async function create(payload: DriverProfileCreate): Promise<DriverProfile> {
    saving.value = true
    try {
      const driver = await createDriver(payload)
      drivers.value.push(driver)
      return driver
    } finally {
      saving.value = false
    }
  }

  async function update(id: string, payload: DriverProfileUpdate): Promise<DriverProfile> {
    saving.value = true
    try {
      const updated = await updateDriver(id, payload)
      const idx = drivers.value.findIndex((d) => d.id === id)
      if (idx >= 0) drivers.value[idx] = updated
      return updated
    } finally {
      saving.value = false
    }
  }

  async function deactivate(id: string): Promise<DriverProfile> {
    const updated = await deactivateDriver(id)
    const idx = drivers.value.findIndex((d) => d.id === id)
    if (idx >= 0) drivers.value[idx] = updated
    return updated
  }

  async function reactivate(id: string): Promise<DriverProfile> {
    return update(id, { is_active: true })
  }

  async function permanentDelete(id: string): Promise<void> {
    await permanentDeleteDriver(id)
    drivers.value = drivers.value.filter((d) => d.id !== id)
  }

  return {
    drivers,
    options,
    loading,
    saving,
    activeDrivers,
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
