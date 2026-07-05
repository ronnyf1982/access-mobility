import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ApiStatus = 'idle' | 'loading' | 'ok' | 'error'

export const useAppStore = defineStore('app', () => {
  const apiStatus = ref<ApiStatus>('idle')

  function setApiStatus(status: ApiStatus) {
    apiStatus.value = status
  }

  return { apiStatus, setApiStatus }
})
