<template>
  <div class="fahrando-logo" :style="{ width: size, height: 'auto' }">
    <!-- Dekoratives SVG-Symbol, aria-hidden -->
    <svg
      :width="iconSize"
      :height="iconSize"
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
      class="fahrando-logo__icon"
    >
      <!-- Bewegungslinien links -->
      <line x1="1" y1="15" x2="13" y2="15" stroke="#FFD600" stroke-width="2.2" stroke-linecap="round"/>
      <line x1="4"  y1="21" x2="13" y2="21" stroke="#FFD600" stroke-width="2.2" stroke-linecap="round"/>
      <line x1="7"  y1="27" x2="13" y2="27" stroke="#FFD600" stroke-width="2.2" stroke-linecap="round"/>

      <!-- Rollstuhl-Silhouette (stilisiert) -->
      <!-- Kopf -->
      <circle cx="30" cy="10" r="3.5" fill="#FFD600"/>
      <!-- Oberkörper -->
      <path
        d="M30 14 L30 24 L37 24"
        stroke="#FFD600"
        stroke-width="2.2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <!-- Armlehne -->
      <path
        d="M24 19 L30 19"
        stroke="#FFD600"
        stroke-width="2.2"
        stroke-linecap="round"
      />
      <!-- Großes Rad -->
      <circle cx="27" cy="33" r="7.5" stroke="#FFD600" stroke-width="2.2"/>
      <!-- Kleines Vorderrad -->
      <circle cx="39" cy="33" r="3.5" stroke="#FFD600" stroke-width="2.2"/>
      <!-- Fußstütze -->
      <path
        d="M30 24 L33 29"
        stroke="#FFD600"
        stroke-width="2"
        stroke-linecap="round"
      />
      <!-- Routenlinie / Bodenlinie -->
      <path
        d="M14 42 Q24 46 36 42"
        stroke="#FFD600"
        stroke-width="1.4"
        stroke-linecap="round"
        opacity="0.4"
      />
    </svg>

    <!-- Markenname als echter Text — kein svg-Text, immer lesbar -->
    <span class="fahrando-logo__name" :style="{ fontSize: textSize }">Fahrando</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    size?: string
    variant?: 'default' | 'small' | 'large'
  }>(),
  {
    size: 'auto',
    variant: 'default',
  },
)

const iconSize = computed(() => {
  if (props.variant === 'small') return 28
  if (props.variant === 'large') return 56
  return 40
})

const textSize = computed(() => {
  if (props.variant === 'small') return '1.05rem'
  if (props.variant === 'large') return '2rem'
  return '1.4rem'
})
</script>

<style scoped>
.fahrando-logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.fahrando-logo__icon {
  flex-shrink: 0;
}

.fahrando-logo__name {
  font-weight: 800;
  color: #F0F0F0;
  letter-spacing: -0.01em;
  line-height: 1;
  white-space: nowrap;
}
</style>
