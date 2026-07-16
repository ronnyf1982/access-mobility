<template>
  <div class="pta-page">
    <header class="pta-header">
      <div>
        <h1 class="pta-title">Website-Testzugänge</h1>
        <p class="pta-sub">Zugänge für die geschützte Vorschau-Website verwalten</p>
        <p class="pta-hint">
          <i class="pi pi-info-circle" aria-hidden="true"></i>
          Dieser Zugang öffnet nur die öffentliche Website. Er ist kein App-Benutzerkonto.
        </p>
      </div>
      <button class="am-btn am-btn-primary pta-create-btn" @click="openCreate">
        <i class="pi pi-plus" aria-hidden="true"></i>
        Zugang anlegen
      </button>
    </header>

    <!-- Filter-Zeile -->
    <div class="pta-filters" role="search" aria-label="Zugangliste filtern">
      <div class="pta-search-wrap">
        <i class="pi pi-search pta-search-icon" aria-hidden="true"></i>
        <input
          v-model="searchQuery"
          type="search"
          class="pta-search"
          placeholder="E-Mail, Name …"
          aria-label="Suche"
          @input="debouncedLoad"
        />
      </div>
      <select
        v-model="filterActive"
        class="pta-select"
        aria-label="Status filtern"
        @change="loadUsers"
      >
        <option value="">Aktiv &amp; Inaktiv</option>
        <option value="true">Nur Aktive</option>
        <option value="false">Nur Inaktive</option>
      </select>
    </div>

    <!-- Tabelle -->
    <div class="pta-table-wrap" role="region" aria-label="Zugangliste" aria-live="polite">
      <div v-if="loading" class="pta-loading" aria-busy="true" aria-label="Wird geladen">
        <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
        Wird geladen …
      </div>

      <div v-else-if="loadError" class="pta-load-error" role="alert">
        <i class="pi pi-exclamation-triangle" aria-hidden="true"></i>
        {{ loadError }}
        <button class="am-btn am-btn-sm pta-retry" @click="loadUsers">Erneut versuchen</button>
      </div>

      <div v-else-if="users.length === 0" class="pta-empty">
        <i class="pi pi-shield" aria-hidden="true"></i>
        <p>Keine Testzugänge gefunden.</p>
      </div>

      <table v-else class="pta-table" aria-label="Zugangliste">
        <thead>
          <tr>
            <th scope="col">E-Mail / Name</th>
            <th scope="col">Status</th>
            <th scope="col">Notiz</th>
            <th scope="col">Letzter Zugriff</th>
            <th scope="col">Erstellt</th>
            <th scope="col" class="pta-th-actions">
              <span class="sr-only">Aktionen</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" class="pta-row">
            <td class="pta-td-name">
              <div class="pta-avatar" aria-hidden="true">{{ initials(user) }}</div>
              <div>
                <div class="pta-email">{{ user.email }}</div>
                <div v-if="user.first_name || user.last_name" class="pta-name">
                  {{ [user.first_name, user.last_name].filter(Boolean).join(' ') }}
                </div>
              </div>
            </td>
            <td>
              <span
                class="pta-status-chip"
                :class="user.is_active ? 'pta-status--active' : 'pta-status--inactive'"
              >
                {{ user.is_active ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </td>
            <td class="pta-td-note">
              <span v-if="user.note" class="pta-note-text" :title="user.note">{{ user.note }}</span>
              <span v-else class="pta-empty-val">–</span>
            </td>
            <td class="pta-td-date">{{ formatDate(user.last_used_at) }}</td>
            <td class="pta-td-date">{{ formatDate(user.created_at) }}</td>
            <td class="pta-td-actions">
              <button
                class="pta-action-btn"
                :aria-label="`${user.email} bearbeiten`"
                @click="openEdit(user)"
              >
                <i class="pi pi-pencil" aria-hidden="true"></i>
              </button>
              <button
                class="pta-action-btn"
                :aria-label="`Passwort für ${user.email} zurücksetzen`"
                @click="openResetPassword(user)"
              >
                <i class="pi pi-key" aria-hidden="true"></i>
              </button>
              <button
                class="pta-action-btn"
                :class="user.is_active ? 'pta-action-btn--danger' : 'pta-action-btn--success'"
                :aria-label="user.is_active ? `${user.email} deaktivieren` : `${user.email} aktivieren`"
                @click="toggleActive(user)"
              >
                <i :class="['pi', user.is_active ? 'pi-ban' : 'pi-check-circle']" aria-hidden="true"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ─── Modal: Zugang anlegen ─────────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="modal === 'create'"
        class="pta-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-create-title"
        @click.self="closeModal"
      >
        <div class="pta-modal">
          <div class="pta-modal-header">
            <h2 id="modal-create-title" class="pta-modal-title">Testzugang anlegen</h2>
            <button class="pta-modal-close" aria-label="Schließen" @click="closeModal">
              <i class="pi pi-times" aria-hidden="true"></i>
            </button>
          </div>
          <div class="pta-modal-body">
            <div v-if="modalError" class="pta-modal-error" role="alert">
              <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
              {{ modalError }}
            </div>
            <div class="pta-form-grid">
              <div class="pta-field pta-field--full">
                <label class="pta-label" for="cf-email">E-Mail-Adresse *</label>
                <input
                  id="cf-email"
                  v-model="form.email"
                  type="email"
                  class="pta-input"
                  :class="{'pta-input--error': fe.email}"
                  autocomplete="off"
                />
                <span v-if="fe.email" class="pta-field-err">{{ fe.email }}</span>
              </div>
              <div class="pta-field">
                <label class="pta-label" for="cf-first">Vorname</label>
                <input id="cf-first" v-model="form.first_name" class="pta-input" />
              </div>
              <div class="pta-field">
                <label class="pta-label" for="cf-last">Nachname</label>
                <input id="cf-last" v-model="form.last_name" class="pta-input" />
              </div>
              <div class="pta-field pta-field--full">
                <label class="pta-label" for="cf-password">Passwort * (min. 10 Zeichen)</label>
                <div class="pta-input-group">
                  <input
                    id="cf-password"
                    v-model="form.password"
                    :type="showPw ? 'text' : 'password'"
                    class="pta-input pta-input--pw"
                    :class="{'pta-input--error': fe.password}"
                    autocomplete="new-password"
                  />
                  <button type="button" class="pta-pw-btn" :aria-label="showPw ? 'Verbergen' : 'Anzeigen'" @click="showPw = !showPw">
                    <i :class="['pi', showPw ? 'pi-eye-slash' : 'pi-eye']" aria-hidden="true"></i>
                  </button>
                </div>
                <span v-if="fe.password" class="pta-field-err">{{ fe.password }}</span>
              </div>
              <div class="pta-field pta-field--full">
                <label class="pta-label" for="cf-note">Notiz (intern)</label>
                <input id="cf-note" v-model="form.note" class="pta-input" placeholder="z. B. Name des Testers, Firma …" />
              </div>
              <div class="pta-field pta-field--full">
                <label class="pta-check-row">
                  <input v-model="form.is_active" type="checkbox" class="pta-check" />
                  <span>Zugang sofort aktivieren</span>
                </label>
              </div>
            </div>
          </div>
          <div class="pta-modal-footer">
            <button class="am-btn" @click="closeModal">Abbrechen</button>
            <button class="am-btn am-btn-primary" :disabled="saving" @click="submitCreate">
              <i v-if="saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
              Anlegen
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── Modal: Zugang bearbeiten ──────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="modal === 'edit' && selectedUser"
        class="pta-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-edit-title"
        @click.self="closeModal"
      >
        <div class="pta-modal">
          <div class="pta-modal-header">
            <h2 id="modal-edit-title" class="pta-modal-title">
              {{ selectedUser.email }} bearbeiten
            </h2>
            <button class="pta-modal-close" aria-label="Schließen" @click="closeModal">
              <i class="pi pi-times" aria-hidden="true"></i>
            </button>
          </div>
          <div class="pta-modal-body">
            <div v-if="modalError" class="pta-modal-error" role="alert">
              <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
              {{ modalError }}
            </div>
            <div class="pta-form-grid">
              <div class="pta-field">
                <label class="pta-label" for="ef-first">Vorname</label>
                <input id="ef-first" v-model="editForm.first_name" class="pta-input" />
              </div>
              <div class="pta-field">
                <label class="pta-label" for="ef-last">Nachname</label>
                <input id="ef-last" v-model="editForm.last_name" class="pta-input" />
              </div>
              <div class="pta-field pta-field--full">
                <label class="pta-label" for="ef-note">Notiz (intern)</label>
                <input id="ef-note" v-model="editForm.note" class="pta-input" />
              </div>
            </div>
          </div>
          <div class="pta-modal-footer">
            <button class="am-btn" @click="closeModal">Abbrechen</button>
            <button class="am-btn am-btn-primary" :disabled="saving" @click="submitEdit">
              <i v-if="saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
              Speichern
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── Modal: Passwort zurücksetzen ──────────────────────── -->
    <Teleport to="body">
      <div
        v-if="modal === 'reset-pw' && selectedUser"
        class="pta-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-pw-title"
        @click.self="closeModal"
      >
        <div class="pta-modal pta-modal--sm">
          <div class="pta-modal-header">
            <h2 id="modal-pw-title" class="pta-modal-title">Passwort zurücksetzen</h2>
            <button class="pta-modal-close" aria-label="Schließen" @click="closeModal">
              <i class="pi pi-times" aria-hidden="true"></i>
            </button>
          </div>
          <div class="pta-modal-body">
            <p class="pta-modal-hint">
              Zugang: <strong>{{ selectedUser.email }}</strong>
            </p>
            <div v-if="modalError" class="pta-modal-error" role="alert">
              <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
              {{ modalError }}
            </div>
            <div class="pta-form-grid">
              <div class="pta-field pta-field--full">
                <label class="pta-label" for="pw-new">Neues Passwort (min. 10 Zeichen) *</label>
                <div class="pta-input-group">
                  <input
                    id="pw-new"
                    v-model="pwForm.new_password"
                    :type="showPw ? 'text' : 'password'"
                    class="pta-input pta-input--pw"
                    :class="{'pta-input--error': fe.new_password}"
                    autocomplete="new-password"
                  />
                  <button type="button" class="pta-pw-btn" :aria-label="showPw ? 'Verbergen' : 'Anzeigen'" @click="showPw = !showPw">
                    <i :class="['pi', showPw ? 'pi-eye-slash' : 'pi-eye']" aria-hidden="true"></i>
                  </button>
                </div>
                <span v-if="fe.new_password" class="pta-field-err">{{ fe.new_password }}</span>
              </div>
              <div class="pta-field pta-field--full">
                <label class="pta-label" for="pw-confirm">Passwort bestätigen *</label>
                <input
                  id="pw-confirm"
                  v-model="pwForm.confirm_password"
                  :type="showPw ? 'text' : 'password'"
                  class="pta-input"
                  :class="{'pta-input--error': fe.confirm_password}"
                  autocomplete="new-password"
                />
                <span v-if="fe.confirm_password" class="pta-field-err">{{ fe.confirm_password }}</span>
              </div>
            </div>
          </div>
          <div class="pta-modal-footer">
            <button class="am-btn" @click="closeModal">Abbrechen</button>
            <button class="am-btn am-btn-primary" :disabled="saving" @click="submitResetPassword">
              <i v-if="saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
              Passwort setzen
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── Toast ──────────────────────────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="toast.show"
        class="pta-toast"
        :class="toast.type === 'success' ? 'pta-toast--success' : 'pta-toast--error'"
        role="status"
        aria-live="polite"
      >
        <i :class="['pi', toast.type === 'success' ? 'pi-check-circle' : 'pi-exclamation-circle']" aria-hidden="true"></i>
        {{ toast.msg }}
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { PreviewAccessUser, PreviewAccessUserCreate, PreviewAccessUserUpdate } from '@/api/previewAccess'
import * as api from '@/api/previewAccess'

// ── State ─────────────────────────────────────────────────────────
const users = ref<PreviewAccessUser[]>([])
const loading = ref(false)
const loadError = ref('')
const searchQuery = ref('')
const filterActive = ref('')

const modal = ref<'' | 'create' | 'edit' | 'reset-pw'>('')
const selectedUser = ref<PreviewAccessUser | null>(null)
const saving = ref(false)
const modalError = ref('')
const showPw = ref(false)

// Formular: Erstellen
const form = reactive<PreviewAccessUserCreate & { first_name: string; last_name: string; note: string }>({
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  is_active: true,
  note: '',
})

// Formular: Bearbeiten
const editForm = reactive<PreviewAccessUserUpdate>({
  first_name: '',
  last_name: '',
  note: '',
})

// Formular: Passwort
const pwForm = reactive({ new_password: '', confirm_password: '' })

// Feldvalidierungsfehler
const fe = reactive<Record<string, string>>({})

// Toast
const toast = reactive({ show: false, msg: '', type: 'success' as 'success' | 'error' })

// ── Debounce ──────────────────────────────────────────────────────
let debounceTimer: ReturnType<typeof setTimeout> | undefined
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadUsers, 320)
}

// ── Datenladen ────────────────────────────────────────────────────
async function loadUsers() {
  loading.value = true
  loadError.value = ''
  try {
    const params: { search?: string; is_active?: boolean } = {}
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (filterActive.value === 'true') params.is_active = true
    if (filterActive.value === 'false') params.is_active = false
    users.value = await api.listPreviewUsers(params)
  } catch {
    loadError.value = 'Zugangliste konnte nicht geladen werden.'
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)

// ── Hilfsfunktionen ───────────────────────────────────────────────
function initials(user: PreviewAccessUser): string {
  const f = user.first_name?.[0] ?? user.email[0] ?? ''
  const l = user.last_name?.[0] ?? ''
  return (f + l).toUpperCase()
}

function formatDate(iso: string | null): string {
  if (!iso) return '–'
  return new Date(iso).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function showToast(msg: string, type: 'success' | 'error' = 'success') {
  toast.msg = msg
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3500)
}

function clearFe() {
  for (const k in fe) delete fe[k]
}

// ── Modal-Steuerung ───────────────────────────────────────────────
function openCreate() {
  clearFe()
  modalError.value = ''
  showPw.value = false
  Object.assign(form, { email: '', password: '', first_name: '', last_name: '', is_active: true, note: '' })
  modal.value = 'create'
}

function openEdit(user: PreviewAccessUser) {
  clearFe()
  modalError.value = ''
  selectedUser.value = user
  Object.assign(editForm, {
    first_name: user.first_name ?? '',
    last_name: user.last_name ?? '',
    note: user.note ?? '',
  })
  modal.value = 'edit'
}

function openResetPassword(user: PreviewAccessUser) {
  clearFe()
  modalError.value = ''
  showPw.value = false
  selectedUser.value = user
  pwForm.new_password = ''
  pwForm.confirm_password = ''
  modal.value = 'reset-pw'
}

function closeModal() {
  modal.value = ''
  selectedUser.value = null
  saving.value = false
  modalError.value = ''
  clearFe()
}

// ── Validierung ───────────────────────────────────────────────────
function validateCreate(): boolean {
  clearFe()
  let ok = true
  if (!form.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    fe.email = 'Gültige E-Mail erforderlich'
    ok = false
  }
  if (!form.password || form.password.length < 10) {
    fe.password = 'Mindestens 10 Zeichen'
    ok = false
  }
  return ok
}

function validateResetPassword(): boolean {
  clearFe()
  let ok = true
  if (!pwForm.new_password || pwForm.new_password.length < 10) {
    fe.new_password = 'Mindestens 10 Zeichen'
    ok = false
  }
  if (!pwForm.confirm_password) {
    fe.confirm_password = 'Pflichtfeld'
    ok = false
  }
  if (pwForm.new_password && pwForm.confirm_password && pwForm.new_password !== pwForm.confirm_password) {
    fe.confirm_password = 'Passwörter stimmen nicht überein'
    ok = false
  }
  return ok
}

// ── Aktionen ──────────────────────────────────────────────────────
async function submitCreate() {
  if (!validateCreate() || saving.value) return
  saving.value = true
  modalError.value = ''
  try {
    await api.createPreviewUser({
      email: form.email.trim().toLowerCase(),
      password: form.password,
      first_name: form.first_name.trim() || null,
      last_name: form.last_name.trim() || null,
      is_active: form.is_active,
      note: form.note.trim() || null,
    })
    await loadUsers()
    closeModal()
    showToast('Testzugang wurde angelegt.')
  } catch (err: unknown) {
    const e = err as { status?: number; body?: { detail?: string } }
    if (e.status === 409) {
      modalError.value = 'Diese E-Mail-Adresse ist bereits vergeben.'
      fe.email = 'Bereits vergeben'
    } else if (e.status === 422) {
      modalError.value = 'Bitte alle Pflichtfelder prüfen.'
    } else {
      modalError.value = 'Fehler beim Anlegen. Bitte erneut versuchen.'
    }
  } finally {
    saving.value = false
  }
}

async function submitEdit() {
  if (saving.value || !selectedUser.value) return
  saving.value = true
  modalError.value = ''
  try {
    await api.updatePreviewUser(selectedUser.value.id, {
      first_name: editForm.first_name?.trim() || null,
      last_name: editForm.last_name?.trim() || null,
      note: editForm.note?.trim() || null,
    })
    await loadUsers()
    closeModal()
    showToast('Änderungen gespeichert.')
  } catch {
    modalError.value = 'Speichern fehlgeschlagen.'
  } finally {
    saving.value = false
  }
}

async function submitResetPassword() {
  if (!validateResetPassword() || saving.value || !selectedUser.value) return
  saving.value = true
  modalError.value = ''
  try {
    await api.resetPreviewUserPassword(selectedUser.value.id, {
      new_password: pwForm.new_password,
      confirm_password: pwForm.confirm_password,
    })
    closeModal()
    showToast('Passwort wurde zurückgesetzt.')
  } catch (err: unknown) {
    const e = err as { status?: number; body?: { detail?: string } }
    if (e.status === 400) {
      modalError.value = e.body?.detail ?? 'Passwörter stimmen nicht überein.'
      fe.confirm_password = 'Stimmen nicht überein'
    } else {
      modalError.value = 'Passwort-Reset fehlgeschlagen.'
    }
  } finally {
    saving.value = false
  }
}

async function toggleActive(user: PreviewAccessUser) {
  try {
    if (user.is_active) {
      await api.deactivatePreviewUser(user.id)
      showToast(`${user.email} deaktiviert.`)
    } else {
      await api.activatePreviewUser(user.id)
      showToast(`${user.email} aktiviert.`)
    }
    await loadUsers()
  } catch {
    showToast('Fehler beim Ändern des Status.', 'error')
  }
}
</script>

<style scoped>
/* ── Seite ──────────────────────────────────────────────────── */
.pta-page {
  padding: var(--am-space-xl) var(--am-space-l);
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

.pta-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--am-space-m);
}

.pta-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--am-text-primary);
  margin: 0 0 4px;
}

.pta-sub {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 0 0 6px;
}

.pta-hint {
  font-size: 0.8rem;
  color: var(--am-text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
}

.pta-create-btn {
  min-height: 44px;
  white-space: nowrap;
}

/* Filter */
.pta-filters {
  display: flex;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.pta-search-wrap {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.pta-search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--am-text-secondary);
  font-size: 0.9rem;
  pointer-events: none;
}

.pta-search {
  width: 100%;
  height: 44px;
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.9rem;
  padding: 0 var(--am-space-m) 0 38px;
  outline: none;
  box-sizing: border-box;
  transition: border-color var(--am-transition), box-shadow var(--am-transition);
}

.pta-search:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.pta-select {
  height: 44px;
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.875rem;
  padding: 0 var(--am-space-m);
  outline: none;
  cursor: pointer;
  transition: border-color var(--am-transition);
}

.pta-select:focus {
  border-color: var(--am-accent);
}

/* Tabelle */
.pta-table-wrap {
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-m);
  overflow: hidden;
  overflow-x: auto;
}

.pta-loading,
.pta-empty,
.pta-load-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--am-space-m);
  padding: 60px 24px;
  color: var(--am-text-secondary);
  font-size: 0.9rem;
  flex-direction: column;
}

.pta-load-error {
  color: var(--am-danger);
}

.pta-retry {
  margin-top: 8px;
  font-size: 0.85rem;
  height: 36px;
  padding: 0 var(--am-space-m);
}

.pta-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.pta-table th {
  background: var(--am-bg-raised);
  color: var(--am-text-secondary);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--am-border);
  white-space: nowrap;
}

.pta-th-actions {
  width: 120px;
}

.pta-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--am-border);
  color: var(--am-text-primary);
  vertical-align: middle;
}

.pta-row:last-child td {
  border-bottom: none;
}

.pta-row:hover {
  background: var(--am-bg-raised);
}

/* Name-Zelle */
.pta-td-name {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  min-width: 200px;
}

.pta-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--am-accent);
  flex-shrink: 0;
}

.pta-email {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--am-text-primary);
}

.pta-name {
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  margin-top: 2px;
}

.pta-td-note {
  max-width: 180px;
}

.pta-note-text {
  font-size: 0.82rem;
  color: var(--am-text-secondary);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pta-empty-val {
  color: var(--am-text-muted);
}

.pta-td-date {
  color: var(--am-text-secondary);
  font-size: 0.82rem;
  white-space: nowrap;
}

.pta-td-actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
}

/* Status-Chips */
.pta-status-chip {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 0.72rem;
  font-weight: 700;
  white-space: nowrap;
}

.pta-status--active {
  background: var(--am-success-bg);
  color: var(--am-success);
  border: 1px solid rgba(34, 197, 94, 0.25);
}

.pta-status--inactive {
  background: var(--am-danger-bg);
  color: var(--am-danger);
  border: 1px solid rgba(239, 68, 68, 0.25);
}

/* Action-Buttons */
.pta-action-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--am-radius-s);
  background: none;
  border: 1px solid var(--am-border);
  color: var(--am-text-secondary);
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--am-transition), background var(--am-transition), border-color var(--am-transition);
}

.pta-action-btn:hover {
  background: var(--am-bg-raised);
  color: var(--am-text-primary);
}

.pta-action-btn--danger:hover {
  color: var(--am-danger);
  border-color: var(--am-danger);
  background: var(--am-danger-bg);
}

.pta-action-btn--success:hover {
  color: var(--am-success);
  border-color: var(--am-success);
  background: var(--am-success-bg);
}

/* ── Modal ──────────────────────────────────────────────────── */
.pta-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: var(--am-space-m);
}

.pta-modal {
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-l);
  width: 100%;
  max-width: 520px;
  max-height: 90dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pta-modal--sm {
  max-width: 420px;
}

.pta-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--am-border);
  flex-shrink: 0;
}

.pta-modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.pta-modal-close {
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  color: var(--am-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--am-radius-s);
  transition: color var(--am-transition), background var(--am-transition);
}

.pta-modal-close:hover {
  color: var(--am-text-primary);
  background: var(--am-bg-raised);
}

.pta-modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.pta-modal-hint {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 0;
}

.pta-modal-error {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  border-radius: var(--am-radius-s);
  color: var(--am-danger);
  font-size: 0.85rem;
}

.pta-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--am-space-m);
  padding: 16px 24px;
  border-top: 1px solid var(--am-border);
  flex-shrink: 0;
}

/* Formular */
.pta-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--am-space-m);
}

.pta-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pta-field--full {
  grid-column: 1 / -1;
}

.pta-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--am-text-primary);
}

.pta-input {
  height: 44px;
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.875rem;
  padding: 0 var(--am-space-m);
  outline: none;
  width: 100%;
  box-sizing: border-box;
  transition: border-color var(--am-transition), box-shadow var(--am-transition);
}

.pta-input:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.pta-input--error {
  border-color: var(--am-danger) !important;
}

.pta-input-group {
  position: relative;
}

.pta-input--pw {
  padding-right: 44px;
}

.pta-pw-btn {
  position: absolute;
  right: 0;
  top: 0;
  width: 44px;
  height: 44px;
  background: none;
  border: none;
  color: var(--am-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--am-transition);
}

.pta-pw-btn:hover {
  color: var(--am-text-primary);
}

.pta-field-err {
  font-size: 0.78rem;
  color: var(--am-danger);
}

.pta-check-row {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.875rem;
  color: var(--am-text-primary);
  cursor: pointer;
}

.pta-check {
  width: 18px;
  height: 18px;
  accent-color: var(--am-accent);
  cursor: pointer;
}

/* ── Toast ──────────────────────────────────────────────────── */
.pta-toast {
  position: fixed;
  bottom: 32px;
  right: 32px;
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  padding: 12px 20px;
  border-radius: var(--am-radius-m);
  font-size: 0.9rem;
  font-weight: 600;
  z-index: 300;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  animation: toastIn 0.25s ease;
}

.pta-toast--success {
  background: var(--am-success-bg);
  color: var(--am-success);
  border: 1px solid rgba(34, 197, 94, 0.35);
}

.pta-toast--error {
  background: var(--am-danger-bg);
  color: var(--am-danger);
  border: 1px solid rgba(239, 68, 68, 0.35);
}

@keyframes toastIn {
  from { transform: translateY(16px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

/* ── Accessibility ──────────────────────────────────────────── */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

:focus-visible {
  outline: 2px solid var(--am-accent);
  outline-offset: 2px;
  border-radius: var(--am-radius-s);
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
</style>
