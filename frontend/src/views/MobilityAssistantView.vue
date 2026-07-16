<template>
  <div class="assistant-page">
    <!-- Header -->
    <div class="assistant-header">
      <div class="assistant-header-text">
        <h1 class="assistant-title">Geführter Mobilitätscheck</h1>
        <p class="assistant-subtitle">
          Wir stellen Ihnen einige Fragen und bereiten Ihr Mobilitätsprofil vor.
          Sie können alles vor dem Speichern prüfen.
        </p>
      </div>
      <button
        type="button"
        class="am-btn am-btn-ghost assistant-cancel"
        aria-label="Check abbrechen und zurück zum Mobilitätsprofil"
        @click="handleCancel"
      >
        <i class="pi pi-times" aria-hidden="true"></i>
        Abbrechen
      </button>
    </div>

    <!-- Progress -->
    <div class="progress-bar-wrap" role="progressbar" :aria-valuenow="progressPercent" aria-valuemin="0" aria-valuemax="100" :aria-label="`Schritt ${currentIndex + 1} von ${total}`">
      <div class="progress-bar-track">
        <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <span class="progress-label">Schritt {{ currentIndex + 1 }} von {{ total }}</span>
    </div>

    <!-- ── Zusammenfassung ── -->
    <div v-if="showSummary" class="summary-card am-card" role="region" aria-labelledby="summary-heading">
      <h2 id="summary-heading" class="summary-title">
        <i class="pi pi-list-check" aria-hidden="true"></i>
        Zusammenfassung Ihrer Angaben
      </h2>
      <p class="summary-intro">
        Bitte prüfen Sie Ihre Antworten. Erst nach Ihrer Bestätigung werden die Angaben gespeichert.
      </p>

      <div
        v-if="statusMsg"
        class="assistant-status"
        :class="statusMsg.type === 'error' ? 'assistant-status--error' : 'assistant-status--success'"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <i :class="['pi', statusMsg.type === 'error' ? 'pi-exclamation-circle' : 'pi-check-circle']" aria-hidden="true"></i>
        {{ statusMsg.text }}
      </div>

      <ul class="summary-list" aria-label="Ihre Angaben">
        <li
          v-for="item in summaryItems"
          :key="item.questionId"
          class="summary-item"
          :class="`summary-item--${item.type}`"
        >
          <span class="summary-item-icon" aria-hidden="true">
            <i :class="['pi', item.type === 'yes' ? 'pi-check' : item.type === 'no' ? 'pi-minus' : 'pi-question']"></i>
          </span>
          <div class="summary-item-content">
            <span class="summary-question">{{ item.questionText }}</span>
            <span class="summary-answer">{{ item.answerLabel }}</span>
            <span v-if="item.fields.length" class="summary-fields">
              Setzt: {{ item.fields.join(' · ') }}
            </span>
            <span v-if="item.missingNote" class="summary-missing-note">
              <i class="pi pi-info-circle" aria-hidden="true"></i>
              {{ item.missingNote }}
            </span>
          </div>
        </li>
      </ul>

      <div class="summary-actions">
        <button
          type="button"
          class="am-btn am-btn-ghost"
          @click="showSummary = false"
        >
          <i class="pi pi-arrow-left" aria-hidden="true"></i>
          Zurück zu den Fragen
        </button>
        <button
          type="button"
          class="am-btn am-btn-primary"
          :disabled="saving"
          :aria-busy="saving"
          @click="handleSave"
        >
          <i v-if="saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
          <i v-else class="pi pi-save" aria-hidden="true"></i>
          {{ saving ? 'Wird gespeichert …' : 'Angaben speichern' }}
        </button>
      </div>
    </div>

    <!-- ── Fragenbereich ── -->
    <div v-else class="question-card am-card" role="region" :aria-labelledby="`q-heading-${currentQuestion.id}`">

      <!-- TTS-Leiste -->
      <div v-if="ttsAvailable" class="tts-bar">
        <button
          type="button"
          class="tts-btn"
          :aria-label="speaking ? 'Vorlesen stoppen' : 'Frage vorlesen'"
          @click="toggleSpeak"
        >
          <i :class="['pi', speaking ? 'pi-volume-off' : 'pi-volume-up']" aria-hidden="true"></i>
          {{ speaking ? 'Stopp' : 'Vorlesen' }}
        </button>
        <button
          v-if="authStore.user?.voice_mode_enabled"
          type="button"
          class="tts-toggle"
          :aria-pressed="autoSpeak"
          @click="autoSpeak = !autoSpeak"
        >
          <i class="pi pi-microphone" aria-hidden="true"></i>
          Auto {{ autoSpeak ? 'An' : 'Aus' }}
        </button>
      </div>

      <!-- Frage -->
      <div class="question-body">
        <p class="question-number" aria-hidden="true">Frage {{ currentIndex + 1 }}</p>
        <h2 :id="`q-heading-${currentQuestion.id}`" class="question-text">
          {{ currentQuestion.text }}
        </h2>
        <p v-if="currentQuestion.hint" class="question-hint">
          <i class="pi pi-info-circle" aria-hidden="true"></i>
          {{ currentQuestion.hint }}
        </p>
      </div>

      <!-- Antwort-Buttons -->
      <div class="answer-grid" role="group" :aria-label="`Antwort für: ${currentQuestion.text}`">
        <button
          v-for="opt in answerOptions"
          :key="opt.value"
          type="button"
          class="answer-btn"
          :class="{ 'answer-btn--selected': answers[currentQuestion.id] === opt.value }"
          :aria-pressed="answers[currentQuestion.id] === opt.value"
          @click="setAnswer(opt.value)"
        >
          <span class="answer-btn-icon" aria-hidden="true">
            <i :class="['pi', opt.icon]"></i>
          </span>
          <span class="answer-btn-label">{{ opt.label }}</span>
        </button>
      </div>

      <!-- Navigation -->
      <div class="question-nav">
        <button
          type="button"
          class="am-btn am-btn-ghost"
          :disabled="currentIndex === 0"
          :aria-disabled="currentIndex === 0"
          @click="goBack"
        >
          <i class="pi pi-arrow-left" aria-hidden="true"></i>
          Zurück
        </button>

        <div class="nav-spacer"></div>

        <button
          v-if="!isLastQuestion"
          type="button"
          class="am-btn am-btn-primary"
          :disabled="!hasAnswer"
          :aria-disabled="!hasAnswer"
          @click="goNext"
        >
          Weiter
          <i class="pi pi-arrow-right" aria-hidden="true"></i>
        </button>

        <button
          v-else
          type="button"
          class="am-btn am-btn-primary"
          :disabled="!hasAnswer"
          :aria-disabled="!hasAnswer"
          @click="finishQuestions"
        >
          <i class="pi pi-list-check" aria-hidden="true"></i>
          Zusammenfassung
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMobilityProfileStore } from '@/stores/mobilityProfile'
import { saveOnboardingPreferences } from '@/api/onboarding'
import {
  MOBILITY_ASSISTANT_QUESTIONS,
  FIELD_LABELS,
  type AnswerValue,
} from '@/data/mobilityAssistantQuestions'
import type { MobilityProfileUpdate } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const profileStore = useMobilityProfileStore()

// ── State ──────────────────────────────────────────────────────────────
const questions = MOBILITY_ASSISTANT_QUESTIONS
const total = questions.length
const currentIndex = ref(0)
const answers = ref<Record<string, AnswerValue>>({})
const showSummary = ref(false)
const saving = ref(false)
const statusMsg = ref<{ type: 'error' | 'success'; text: string } | null>(null)

// TTS
const ttsAvailable = ref(typeof window !== 'undefined' && 'speechSynthesis' in window)
const speaking = ref(false)
const autoSpeak = ref(authStore.user?.voice_mode_enabled === true)

// ── Computed ───────────────────────────────────────────────────────────
const currentQuestion = computed(() => questions[currentIndex.value])
const isLastQuestion = computed(() => currentIndex.value === total - 1)
const hasAnswer = computed(() => !!answers.value[currentQuestion.value.id])
const progressPercent = computed(() =>
  showSummary.value ? 100 : Math.round((currentIndex.value / total) * 100),
)

const answerOptions = [
  { value: 'yes' as AnswerValue, label: 'Ja', icon: 'pi-check' },
  { value: 'no' as AnswerValue, label: 'Nein', icon: 'pi-times' },
  { value: 'unknown' as AnswerValue, label: 'Weiß ich nicht', icon: 'pi-question' },
  { value: 'skip' as AnswerValue, label: 'Überspringen', icon: 'pi-forward' },
]

const ANSWER_LABELS: Record<AnswerValue, string> = {
  yes: 'Ja',
  no: 'Nein',
  unknown: 'Weiß ich nicht',
  skip: 'Übersprungen',
}

const summaryItems = computed(() =>
  questions.map((q) => {
    const answer = answers.value[q.id] ?? 'skip'
    const fields =
      answer === 'yes'
        ? q.yesFields
            .map((f) => FIELD_LABELS[f.field] ?? f.field)
            .filter(Boolean) as string[]
        : []
    return {
      questionId: q.id,
      questionText: q.text,
      answer,
      answerLabel: ANSWER_LABELS[answer],
      type: answer === 'yes' ? 'yes' : answer === 'no' ? 'no' : 'neutral',
      fields,
      missingNote: answer === 'yes' ? q.missingFieldNote : undefined,
    }
  }),
)

// ── TTS ────────────────────────────────────────────────────────────────
function speak(text: string) {
  if (!ttsAvailable.value) return
  window.speechSynthesis.cancel()
  speaking.value = true
  const utter = new SpeechSynthesisUtterance(text)
  utter.lang = 'de-DE'
  utter.onend = () => { speaking.value = false }
  utter.onerror = () => { speaking.value = false }
  window.speechSynthesis.speak(utter)
}

function stopSpeak() {
  if (!ttsAvailable.value) return
  window.speechSynthesis.cancel()
  speaking.value = false
}

function toggleSpeak() {
  if (speaking.value) {
    stopSpeak()
  } else {
    const q = currentQuestion.value
    speak(q.text + (q.hint ? '. Hinweis: ' + q.hint : ''))
  }
}

// Auto-speak when question changes
watch(currentIndex, () => {
  stopSpeak()
  if (autoSpeak.value && ttsAvailable.value) {
    // Small delay to let Vue render the new question text
    setTimeout(() => speak(currentQuestion.value.text), 150)
  }
})

onMounted(() => {
  profileStore.load().catch(() => {})
  if (autoSpeak.value && ttsAvailable.value) {
    setTimeout(() => speak(currentQuestion.value.text), 300)
  }
})

onUnmounted(() => {
  stopSpeak()
})

// ── Navigation ─────────────────────────────────────────────────────────
function setAnswer(value: AnswerValue) {
  answers.value = { ...answers.value, [currentQuestion.value.id]: value }
}

function goNext() {
  if (currentIndex.value < total - 1) {
    currentIndex.value++
  }
}

function goBack() {
  if (showSummary.value) {
    showSummary.value = false
    return
  }
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

function finishQuestions() {
  stopSpeak()
  showSummary.value = true
  statusMsg.value = null
}

function handleCancel() {
  stopSpeak()
  router.push('/mobility-profile')
}

// ── Save ───────────────────────────────────────────────────────────────
async function handleSave() {
  saving.value = true
  statusMsg.value = null
  try {
    // 1. Collect User-model changes (voice_mode_enabled)
    const voiceQuestion = answers.value['voice_mode_mode']
    const voiceAnswer = answers.value['voice_mode']
    const newVoiceMode = voiceAnswer === 'yes'
    const voiceChanged = authStore.user?.voice_mode_enabled !== newVoiceMode && voiceAnswer !== 'skip' && voiceAnswer !== 'unknown'

    if (voiceChanged) {
      const updatedUser = await saveOnboardingPreferences(newVoiceMode)
      authStore.user = updatedUser
    }

    // 2. Collect MobilityProfile changes
    const profilePatch: MobilityProfileUpdate = {}
    for (const q of questions) {
      const answer = answers.value[q.id]
      if (answer !== 'yes') continue
      for (const mapping of q.yesFields) {
        if (mapping.model === 'mobilityProfile') {
          ;(profilePatch as Record<string, boolean>)[mapping.field as string] = mapping.value
        }
      }
    }

    const hasProfileChanges = Object.keys(profilePatch).length > 0
    if (hasProfileChanges) {
      await profileStore.save(profilePatch)
    }

    statusMsg.value = { type: 'success', text: 'Ihr Mobilitätsprofil wurde gespeichert.' }
    setTimeout(() => router.push('/mobility-profile'), 1800)
  } catch {
    statusMsg.value = { type: 'error', text: 'Beim Speichern ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.' }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.assistant-page {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
  max-width: 680px;
  margin: 0 auto;
}

/* Header */
.assistant-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.assistant-header-text {
  flex: 1;
}

.assistant-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0 0 4px;
}

.assistant-subtitle {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.assistant-cancel {
  font-size: 0.85rem;
  min-height: 36px;
  padding: 0 var(--am-space-m);
  flex-shrink: 0;
}

/* Progress */
.progress-bar-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-bar-track {
  height: 6px;
  background: var(--am-bg-raised);
  border-radius: 99px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--am-accent);
  border-radius: 99px;
  transition: width 0.3s ease;
}

.progress-label {
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  font-weight: 500;
}

/* Status */
.assistant-status {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  border-radius: var(--am-radius-s);
  font-size: 0.875rem;
  margin-bottom: var(--am-space-m);
}

.assistant-status--error {
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  color: var(--am-danger);
}

.assistant-status--success {
  background: color-mix(in srgb, var(--am-success) 12%, transparent);
  border: 1px solid var(--am-success);
  color: var(--am-success);
}

/* TTS bar */
.tts-bar {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  padding-bottom: var(--am-space-m);
  border-bottom: 1px solid var(--am-border);
  margin-bottom: var(--am-space-m);
}

.tts-btn,
.tts-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px var(--am-space-m);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  color: var(--am-text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  min-height: 36px;
  transition: background var(--am-transition), color var(--am-transition);
}

.tts-btn:hover,
.tts-toggle:hover {
  background: var(--am-bg-surface);
  color: var(--am-text-primary);
}

.tts-toggle[aria-pressed='true'] {
  background: color-mix(in srgb, var(--am-accent) 15%, var(--am-bg-raised));
  border-color: var(--am-accent);
  color: var(--am-accent);
}

/* Question */
.question-card {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.question-body {
  margin-bottom: var(--am-space-l);
}

.question-number {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--am-accent);
  margin: 0 0 var(--am-space-s);
}

.question-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0 0 var(--am-space-s);
  line-height: 1.3;
}

.question-hint {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* Answer buttons */
.answer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--am-space-m);
  margin-bottom: var(--am-space-l);
}

@media (max-width: 480px) {
  .answer-grid {
    grid-template-columns: 1fr;
  }
}

.answer-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--am-space-s);
  padding: var(--am-space-l) var(--am-space-m);
  background: var(--am-bg-raised);
  border: 2px solid var(--am-border);
  border-radius: var(--am-radius-m);
  cursor: pointer;
  min-height: 88px;
  transition: border-color var(--am-transition), background var(--am-transition);
}

.answer-btn:hover {
  border-color: var(--am-border-strong);
  background: var(--am-bg-surface);
}

.answer-btn:focus-visible {
  outline: 2px solid var(--am-accent);
  outline-offset: 2px;
}

.answer-btn--selected {
  border-color: var(--am-accent);
  background: color-mix(in srgb, var(--am-accent) 10%, var(--am-bg-raised));
}

.answer-btn-icon {
  font-size: 1.4rem;
  color: var(--am-text-secondary);
}

.answer-btn--selected .answer-btn-icon {
  color: var(--am-accent);
}

.answer-btn-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--am-text-primary);
}

/* Navigation */
.question-nav {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  padding-top: var(--am-space-m);
  border-top: 1px solid var(--am-border);
}

.nav-spacer {
  flex: 1;
}

.question-nav .am-btn {
  min-height: 44px;
}

.question-nav .am-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Summary */
.summary-card {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.summary-title {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.summary-intro {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 0;
}

.summary-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}

.summary-item {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-m);
  padding: var(--am-space-s) var(--am-space-m);
  border-radius: var(--am-radius-s);
  border: 1px solid var(--am-border);
  background: var(--am-bg-raised);
}

.summary-item--yes {
  border-color: rgba(34, 197, 94, 0.3);
  background: color-mix(in srgb, var(--am-success) 6%, var(--am-bg-raised));
}

.summary-item--no {
  opacity: 0.6;
}

.summary-item-icon {
  font-size: 1rem;
  width: 24px;
  flex-shrink: 0;
  padding-top: 2px;
}

.summary-item--yes .summary-item-icon { color: var(--am-success); }
.summary-item--no .summary-item-icon { color: var(--am-text-muted); }
.summary-item--neutral .summary-item-icon { color: var(--am-text-muted); }

.summary-item-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.summary-question {
  font-size: 0.85rem;
  color: var(--am-text-secondary);
}

.summary-answer {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--am-text-primary);
}

.summary-fields {
  font-size: 0.75rem;
  color: var(--am-accent);
  font-weight: 600;
}

.summary-missing-note {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  font-size: 0.72rem;
  color: var(--am-text-muted);
  font-style: italic;
}

.summary-actions {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  flex-wrap: wrap;
  padding-top: var(--am-space-m);
  border-top: 1px solid var(--am-border);
}

.summary-actions .am-btn {
  min-height: 48px;
}

.summary-actions .am-btn-primary {
  flex: 1;
  justify-content: center;
  min-width: 200px;
}

.summary-actions .am-btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
