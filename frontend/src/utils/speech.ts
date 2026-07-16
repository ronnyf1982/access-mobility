// ────────────────────────────────────────────────────────────────────────────
// Browser Speech API type declarations (not yet in all TS DOM lib versions)
// ────────────────────────────────────────────────────────────────────────────

interface SpeechRecognitionResult {
  readonly length: number
  item(index: number): SpeechRecognitionAlternative
  [index: number]: SpeechRecognitionAlternative
}
interface SpeechRecognitionAlternative {
  readonly transcript: string
  readonly confidence: number
}
interface SpeechRecognitionResultList {
  readonly length: number
  item(index: number): SpeechRecognitionResult
  [index: number]: SpeechRecognitionResult
}
interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number
  readonly results: SpeechRecognitionResultList
}
interface SpeechRecognitionErrorEvent extends Event {
  readonly error: string
  readonly message: string
}
interface SpeechRecognition extends EventTarget {
  lang: string
  continuous: boolean
  interimResults: boolean
  maxAlternatives: number
  onstart: ((this: SpeechRecognition, ev: Event) => void) | null
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => void) | null
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => void) | null
  onend: ((this: SpeechRecognition, ev: Event) => void) | null
  start(): void
  stop(): void
  abort(): void
}

// ────────────────────────────────────────────────────────────────────────────
// Text-to-Speech (Browser Web Speech API)
// ────────────────────────────────────────────────────────────────────────────

export function isTTSSupported(): boolean {
  return typeof window !== 'undefined' && 'speechSynthesis' in window
}

export function speak(text: string, onEnd?: () => void): void {
  if (!isTTSSupported()) {
    onEnd?.()
    return
  }
  window.speechSynthesis.cancel()
  const utter = new SpeechSynthesisUtterance(text)
  utter.lang = 'de-DE'
  utter.rate = 0.95
  if (onEnd) {
    utter.onend = () => onEnd()
    utter.onerror = () => onEnd()
  }
  window.speechSynthesis.speak(utter)
}

export function stopSpeaking(): void {
  if (isTTSSupported()) {
    window.speechSynthesis.cancel()
  }
}

// ────────────────────────────────────────────────────────────────────────────
// Speech Recognition (STT — Browser Web Speech API)
// ────────────────────────────────────────────────────────────────────────────

type SpeechRecognitionCtor = new () => SpeechRecognition

function getSRCtor(): SpeechRecognitionCtor | null {
  if (typeof window === 'undefined') return null
  const w = window as unknown as Record<string, unknown>
  const SR =
    (w['SpeechRecognition'] as SpeechRecognitionCtor | undefined) ??
    (w['webkitSpeechRecognition'] as SpeechRecognitionCtor | undefined) ??
    null
  return SR
}

export function isSTTSupported(): boolean {
  return getSRCtor() !== null
}

let _activeRec: SpeechRecognition | null = null

export function stopRecognition(): void {
  if (_activeRec) {
    _activeRec.abort()
    _activeRec = null
  }
}

export function startRecognition(
  onResult: (transcript: string) => void,
  onError?: (errorType: string) => void,
  onStart?: () => void,
): void {
  const SR = getSRCtor()
  if (!SR) {
    onError?.('not_supported')
    return
  }
  stopRecognition()

  const rec = new SR()
  rec.lang = 'de-DE'
  rec.continuous = false
  rec.interimResults = false
  rec.maxAlternatives = 3

  rec.onstart = () => onStart?.()

  rec.onresult = (event: SpeechRecognitionEvent) => {
    const alternatives: string[] = []
    for (let i = 0; i < event.results.length; i++) {
      const result = event.results[i]
      for (let j = 0; j < result.length; j++) {
        alternatives.push(result[j].transcript.toLowerCase().trim())
      }
    }
    onResult(alternatives.join(' | '))
    _activeRec = null
  }

  rec.onerror = (event: SpeechRecognitionErrorEvent) => {
    onError?.(event.error)
    _activeRec = null
  }

  rec.onend = () => {
    _activeRec = null
  }

  rec.start()
  _activeRec = rec
}

// ────────────────────────────────────────────────────────────────────────────
// Command normalization
// ────────────────────────────────────────────────────────────────────────────

export type AnswerCommand = 'yes' | 'no' | 'unknown' | 'skip'

export type RecognizedCommand =
  | { type: 'answer'; value: AnswerCommand }
  | { type: 'read_options' }
  | { type: 'repeat_question' }
  | { type: 'go_back' }
  | { type: 'cancel' }
  | null

export function normalizeSpokenInput(raw: string): RecognizedCommand {
  // Test each alternative (separated by ' | ')
  const alternatives = raw.split(' | ').map((s) => s.trim())

  for (const t of alternatives) {
    const cmd = _matchSingle(t)
    if (cmd) return cmd
  }
  return null
}

function _matchSingle(t: string): RecognizedCommand {
  // Priority: navigation > meta > answer
  if (/\b(abbrech|beend)\w*/.test(t)) return { type: 'cancel' }
  if (/\b(zurück|vorherige frage)\b/.test(t)) return { type: 'go_back' }
  if (/\b(wiederhole?n?|nochmal|frage wiederhol)\w*/.test(t)) return { type: 'repeat_question' }
  if (
    /\b(antwort\w*|möglichkeit\w*|option\w*)\s*(vorlesen|lesen)\b/.test(t) ||
    /\b(welche antwort\w*|hilfe)\b/.test(t) ||
    /\boptionen?\b/.test(t)
  )
    return { type: 'read_options' }

  if (/\b(ja|genau|richtig|stimmt)\b/.test(t)) return { type: 'answer', value: 'yes' }
  if (/\b(nein|nicht\b|brauche ich nicht|möchte ich nicht)\b/.test(t))
    return { type: 'answer', value: 'no' }
  if (/\b(weiß ich nicht|unklar|keine ahnung|unsicher)\b/.test(t))
    return { type: 'answer', value: 'unknown' }
  if (/\b(überspringen|weiter\b|später)\b/.test(t)) return { type: 'answer', value: 'skip' }

  return null
}

export const ANSWER_SPOKEN_LABELS: Record<AnswerCommand, string> = {
  yes: 'Ja',
  no: 'Nein',
  unknown: 'Weiß ich nicht',
  skip: 'Überspringen',
}
