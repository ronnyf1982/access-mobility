import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  getTransportRequests,
  getTransportRequest,
  createTransportRequest,
  updateTransportRequest,
  submitTransportRequest,
  cancelTransportRequest,
} from '@/api/transportRequests'
import type {
  TransportRequestListItem,
  TransportRequestRead,
  TransportRequestCreate,
  TransportRequestUpdate,
} from '@/types'

export const useTransportRequestStore = defineStore('transportRequests', () => {
  const requests = ref<TransportRequestListItem[]>([])
  const current = ref<TransportRequestRead | null>(null)
  const loading = ref(false)
  const saving = ref(false)

  const draftCount = computed(
    () => requests.value.filter((r) => r.status === 'draft').length,
  )
  const requestedCount = computed(
    () => requests.value.filter((r) => r.status === 'requested').length,
  )
  const totalCount = computed(() => requests.value.length)

  async function load(): Promise<void> {
    loading.value = true
    try {
      requests.value = await getTransportRequests()
    } finally {
      loading.value = false
    }
  }

  async function loadOne(id: string): Promise<TransportRequestRead> {
    current.value = await getTransportRequest(id)
    return current.value
  }

  async function create(payload: TransportRequestCreate): Promise<TransportRequestRead> {
    saving.value = true
    try {
      const req = await createTransportRequest(payload)
      requests.value.unshift(req as unknown as TransportRequestListItem)
      current.value = req
      return req
    } finally {
      saving.value = false
    }
  }

  async function update(id: string, payload: TransportRequestUpdate): Promise<TransportRequestRead> {
    saving.value = true
    try {
      const req = await updateTransportRequest(id, payload)
      _replaceInList(req)
      current.value = req
      return req
    } finally {
      saving.value = false
    }
  }

  async function submit(id: string): Promise<TransportRequestRead> {
    saving.value = true
    try {
      const req = await submitTransportRequest(id)
      _replaceInList(req)
      if (current.value?.id === id) current.value = req
      return req
    } finally {
      saving.value = false
    }
  }

  async function cancel(id: string): Promise<TransportRequestRead> {
    saving.value = true
    try {
      const req = await cancelTransportRequest(id)
      _replaceInList(req)
      if (current.value?.id === id) current.value = req
      return req
    } finally {
      saving.value = false
    }
  }

  function _replaceInList(req: TransportRequestRead) {
    const idx = requests.value.findIndex((r) => r.id === req.id)
    if (idx >= 0) requests.value[idx] = req as unknown as TransportRequestListItem
  }

  return {
    requests,
    current,
    loading,
    saving,
    draftCount,
    requestedCount,
    totalCount,
    load,
    loadOne,
    create,
    update,
    submit,
    cancel,
  }
})
