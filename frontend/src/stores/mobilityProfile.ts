import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { getMyProfile, updateMyProfile } from '@/api/mobilityProfile'
import type { MobilityProfile, MobilityProfileUpdate, MobilityNeedOption } from '@/types'

export const useMobilityProfileStore = defineStore('mobilityProfile', () => {
  const profile = ref<MobilityProfile | null>(null)
  const loading = ref(false)
  const saving = ref(false)

  const hasProfile = computed(() => profile.value !== null)

  const isProfileFilled = computed(() => {
    const p = profile.value
    if (!p) return false
    return (
      !!p.emergency_contact_name ||
      p.uses_wheelchair ||
      p.uses_rollator ||
      p.uses_crutches ||
      p.is_blind_or_visually_impaired ||
      p.is_deaf_or_hard_of_hearing ||
      p.needs_escort ||
      p.needs_entry_assistance ||
      p.needs_door_to_door_assistance ||
      p.needs_ramp ||
      p.needs_lift ||
      p.needs_stretcher_transport
    )
  })

  // Mobilitätsbedarfe als strukturierte Liste für die UI
  const mobilityNeedItems = computed((): Array<MobilityNeedOption & { active: boolean }> => {
    const p = profile.value
    return NEED_DEFINITIONS.map((def) => ({
      ...def,
      active: p ? !!(p[def.key] as boolean) : false,
    }))
  })

  async function load(): Promise<void> {
    loading.value = true
    try {
      profile.value = await getMyProfile()
    } finally {
      loading.value = false
    }
  }

  async function save(payload: MobilityProfileUpdate): Promise<void> {
    saving.value = true
    try {
      profile.value = await updateMyProfile(payload)
    } finally {
      saving.value = false
    }
  }

  return { profile, loading, saving, hasProfile, isProfileFilled, mobilityNeedItems, load, save }
})

// Statische Definitionen — spiegeln die Backend-Optionsliste wider
const NEED_DEFINITIONS: MobilityNeedOption[] = [
  {
    key: 'uses_wheelchair',
    label: 'Rollstuhl',
    icon: 'pi-circle-fill',
    description: 'Ich fahre mit einem Rollstuhl und benötige einen gesicherten Stellplatz im Fahrzeug.',
  },
  {
    key: 'uses_rollator',
    label: 'Rollator',
    icon: 'pi-arrows-h',
    description: 'Ich nutze einen Rollator. Er wird ggf. im Fahrzeug verstaut.',
  },
  {
    key: 'uses_crutches',
    label: 'Krücken / Gehstützen',
    icon: 'pi-arrow-up',
    description: 'Ich benutze Krücken oder Gehstützen.',
  },
  {
    key: 'is_blind_or_visually_impaired',
    label: 'Blind / sehbehindert',
    icon: 'pi-eye-slash',
    description: 'Der Fahrer holt mich an der Tür ab und führt mich verbal.',
  },
  {
    key: 'is_deaf_or_hard_of_hearing',
    label: 'Gehörlos / schwerhörig',
    icon: 'pi-volume-off',
    description: 'Bitte schriftlich oder per Geste kommunizieren.',
  },
  {
    key: 'needs_escort',
    label: 'Begleitperson',
    icon: 'pi-users',
    description: 'Eine Begleitperson fährt mit und benötigt einen zusätzlichen Sitzplatz.',
  },
  {
    key: 'needs_entry_assistance',
    label: 'Hilfe beim Ein- / Aussteigen',
    icon: 'pi-arrow-circle-up',
    description: 'Der Fahrer unterstützt mich beim Einsteigen und Aussteigen.',
  },
  {
    key: 'needs_door_to_door_assistance',
    label: 'Tür-zu-Tür-Begleitung',
    icon: 'pi-map-marker',
    description: 'Ich werde von Haustür zu Haustür begleitet.',
  },
  {
    key: 'needs_ramp',
    label: 'Rampe erforderlich',
    icon: 'pi-sort-amount-up-alt',
    description: 'Das Fahrzeug muss über eine Auffahrrampe verfügen.',
  },
  {
    key: 'needs_lift',
    label: 'Lift / Hebebühne',
    icon: 'pi-chevron-circle-up',
    description: 'Das Fahrzeug muss über eine elektrische Hebebühne verfügen.',
  },
  {
    key: 'needs_stretcher_transport',
    label: 'Liegendtransport',
    icon: 'pi-minus',
    description: 'Ich kann nicht sitzen. Der Transport muss liegend erfolgen.',
  },
]
