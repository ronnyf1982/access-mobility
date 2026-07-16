<template>
  <div class="pau-page">
    <header class="pau-header">
      <div>
        <h1 class="pau-title">Benutzerverwaltung</h1>
        <p class="pau-sub">Alle Nutzer der Plattform verwalten</p>
      </div>
      <button class="am-btn am-btn-primary pau-create-btn" @click="openCreate">
        <i class="pi pi-plus" aria-hidden="true"></i>
        Nutzer anlegen
      </button>
    </header>

    <!-- Filter-Zeile -->
    <div class="pau-filters" role="search" aria-label="Nutzerliste filtern">
      <div class="pau-search-wrap">
        <i class="pi pi-search pau-search-icon" aria-hidden="true"></i>
        <input
          v-model="searchQuery"
          type="search"
          class="pau-search"
          placeholder="Name oder E-Mail …"
          aria-label="Suche"
          @input="debouncedLoad"
        />
      </div>
      <select
        v-model="filterRole"
        class="pau-select"
        aria-label="Rolle filtern"
        @change="loadUsers"
      >
        <option value="">Alle Rollen</option>
        <option v-for="r in ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
      </select>
      <select
        v-model="filterActive"
        class="pau-select"
        aria-label="Status filtern"
        @change="loadUsers"
      >
        <option value="">Aktiv &amp; Inaktiv</option>
        <option value="true">Nur Aktive</option>
        <option value="false">Nur Inaktive</option>
      </select>
    </div>

    <!-- Tabelle -->
    <div class="pau-table-wrap" role="region" aria-label="Nutzerliste" aria-live="polite">
      <!-- Ladezustand -->
      <div v-if="loading" class="pau-loading" aria-busy="true" aria-label="Wird geladen">
        <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
        Wird geladen …
      </div>

      <!-- Fehler -->
      <div v-else-if="loadError" class="pau-load-error" role="alert">
        <i class="pi pi-exclamation-triangle" aria-hidden="true"></i>
        {{ loadError }}
        <button class="am-btn am-btn-sm pau-retry" @click="loadUsers">Erneut versuchen</button>
      </div>

      <!-- Leer -->
      <div v-else-if="users.length === 0" class="pau-empty">
        <i class="pi pi-users" aria-hidden="true"></i>
        <p>Keine Nutzer gefunden.</p>
      </div>

      <!-- Tabelle -->
      <table v-else class="pau-table" aria-label="Nutzerliste">
        <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">E-Mail</th>
            <th scope="col">Rolle</th>
            <th scope="col">Status</th>
            <th scope="col">Erstellt</th>
            <th scope="col" class="pau-th-actions">
              <span class="sr-only">Aktionen</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" class="pau-row">
            <td class="pau-td-name">
              <div class="pau-avatar" aria-hidden="true">{{ initials(user) }}</div>
              <div>
                <div class="pau-name">{{ user.first_name }} {{ user.last_name }}</div>
                <div v-if="user.organization_name" class="pau-org">{{ user.organization_name }}</div>
              </div>
            </td>
            <td class="pau-td-email">{{ user.email }}</td>
            <td>
              <span class="pau-role-chip" :class="`pau-role--${user.role}`">
                {{ roleLabel(user.role) }}
              </span>
            </td>
            <td>
              <span class="pau-status-chip" :class="user.is_active ? 'pau-status--active' : 'pau-status--inactive'">
                {{ user.is_active ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </td>
            <td class="pau-td-date">{{ formatDate(user.created_at) }}</td>
            <td class="pau-td-actions">
              <button class="pau-action-btn" :aria-label="`${user.first_name} ${user.last_name} bearbeiten`" @click="openEdit(user)">
                <i class="pi pi-pencil" aria-hidden="true"></i>
              </button>
              <button class="pau-action-btn" :aria-label="`Passwort für ${user.first_name} ${user.last_name} zurücksetzen`" @click="openResetPassword(user)">
                <i class="pi pi-key" aria-hidden="true"></i>
              </button>
              <button
                class="pau-action-btn"
                :class="user.is_active ? 'pau-action-btn--danger' : 'pau-action-btn--success'"
                :aria-label="user.is_active ? `${user.first_name} ${user.last_name} deaktivieren` : `${user.first_name} ${user.last_name} aktivieren`"
                @click="toggleActive(user)"
              >
                <i :class="['pi', user.is_active ? 'pi-ban' : 'pi-check-circle']" aria-hidden="true"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ─── Modal: Nutzer anlegen ──────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="modal === 'create'"
        class="pau-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-create-title"
        @click.self="closeModal"
      >
        <div class="pau-modal">
          <div class="pau-modal-header">
            <h2 id="modal-create-title" class="pau-modal-title">Nutzer anlegen</h2>
            <button class="pau-modal-close" aria-label="Schließen" @click="closeModal">
              <i class="pi pi-times" aria-hidden="true"></i>
            </button>
          </div>
          <div class="pau-modal-body">
            <div v-if="modalError" class="pau-modal-error" role="alert">
              <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
              {{ modalError }}
            </div>
            <div class="pau-form-grid">
              <div class="pau-field">
                <label class="pau-label" for="cf-first">Vorname *</label>
                <input id="cf-first" v-model="form.first_name" class="pau-input" :class="{'pau-input--error': fe.first_name}" />
                <span v-if="fe.first_name" class="pau-field-err">{{ fe.first_name }}</span>
              </div>
              <div class="pau-field">
                <label class="pau-label" for="cf-last">Nachname *</label>
                <input id="cf-last" v-model="form.last_name" class="pau-input" :class="{'pau-input--error': fe.last_name}" />
                <span v-if="fe.last_name" class="pau-field-err">{{ fe.last_name }}</span>
              </div>
              <div class="pau-field pau-field--full">
                <label class="pau-label" for="cf-email">E-Mail *</label>
                <input id="cf-email" v-model="form.email" type="email" class="pau-input" :class="{'pau-input--error': fe.email}" />
                <span v-if="fe.email" class="pau-field-err">{{ fe.email }}</span>
              </div>
              <div class="pau-field pau-field--full">
                <label class="pau-label" for="cf-password">Passwort * (min. 10 Zeichen)</label>
                <div class="pau-input-group">
                  <input id="cf-password" v-model="form.password" :type="showPw ? 'text' : 'password'" class="pau-input pau-input--pw" :class="{'pau-input--error': fe.password}" autocomplete="new-password" />
                  <button type="button" class="pau-pw-btn" :aria-label="showPw ? 'Verbergen' : 'Anzeigen'" @click="showPw = !showPw">
                    <i :class="['pi', showPw ? 'pi-eye-slash' : 'pi-eye']" aria-hidden="true"></i>
                  </button>
                </div>
                <span v-if="fe.password" class="pau-field-err">{{ fe.password }}</span>
              </div>
              <div class="pau-field">
                <label class="pau-label" for="cf-role">Rolle *</label>
                <select id="cf-role" v-model="form.role" class="pau-input" :class="{'pau-input--error': fe.role}">
                  <option value="">Bitte wählen</option>
                  <option v-for="r in ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
                </select>
                <span v-if="fe.role" class="pau-field-err">{{ fe.role }}</span>
              </div>
              <div class="pau-field">
                <label class="pau-label" for="cf-phone">Telefon</label>
                <input id="cf-phone" v-model="form.phone" type="tel" class="pau-input" />
              </div>
              <div class="pau-field pau-field--full">
                <label class="pau-check-row">
                  <input v-model="form.is_active" type="checkbox" class="pau-check" />
                  <span>Konto sofort aktivieren</span>
                </label>
              </div>
            </div>
          </div>
          <div class="pau-modal-footer">
            <button class="am-btn" @click="closeModal">Abbrechen</button>
            <button class="am-btn am-btn-primary" :disabled="saving" @click="submitCreate">
              <i v-if="saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
              Anlegen
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── Modal: Nutzer bearbeiten ──────────────────────── -->
    <Teleport to="body">
      <div
        v-if="modal === 'edit' && selectedUser"
        class="pau-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-edit-title"
        @click.self="closeModal"
      >
        <div class="pau-modal">
          <div class="pau-modal-header">
            <h2 id="modal-edit-title" class="pau-modal-title">
              {{ selectedUser.first_name }} {{ selectedUser.last_name }} bearbeiten
            </h2>
            <button class="pau-modal-close" aria-label="Schließen" @click="closeModal">
              <i class="pi pi-times" aria-hidden="true"></i>
            </button>
          </div>
          <div class="pau-modal-body">
            <div v-if="modalError" class="pau-modal-error" role="alert">
              <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
              {{ modalError }}
            </div>
            <div class="pau-form-grid">
              <div class="pau-field">
                <label class="pau-label" for="ef-first">Vorname</label>
                <input id="ef-first" v-model="editForm.first_name" class="pau-input" />
              </div>
              <div class="pau-field">
                <label class="pau-label" for="ef-last">Nachname</label>
                <input id="ef-last" v-model="editForm.last_name" class="pau-input" />
              </div>
              <div class="pau-field pau-field--full">
                <label class="pau-label" for="ef-role">Rolle</label>
                <select id="ef-role" v-model="editForm.role" class="pau-input">
                  <option v-for="r in ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
                </select>
              </div>
              <div class="pau-field pau-field--full">
                <label class="pau-label" for="ef-phone">Telefon</label>
                <input id="ef-phone" v-model="editForm.phone" type="tel" class="pau-input" />
              </div>
            </div>
          </div>
          <div class="pau-modal-footer">
            <button class="am-btn" @click="closeModal">Abbrechen</button>
            <button class="am-btn am-btn-primary" :disabled="saving" @click="submitEdit">
              <i v-if="saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
              Speichern
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── Modal: Passwort zurücksetzen ──────────────────── -->
    <Teleport to="body">
      <div
        v-if="modal === 'reset-pw' && selectedUser"
        class="pau-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-pw-title"
        @click.self="closeModal"
      >
        <div class="pau-modal pau-modal--sm">
          <div class="pau-modal-header">
            <h2 id="modal-pw-title" class="pau-modal-title">Passwort zurücksetzen</h2>
            <button class="pau-modal-close" aria-label="Schließen" @click="closeModal">
              <i class="pi pi-times" aria-hidden="true"></i>
            </button>
          </div>
          <div class="pau-modal-body">
            <p class="pau-modal-hint">
              Nutzer: <strong>{{ selectedUser.first_name }} {{ selectedUser.last_name }}</strong>
            </p>
            <div v-if="modalError" class="pau-modal-error" role="alert">
              <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
              {{ modalError }}
            </div>
            <div class="pau-form-grid">
              <div class="pau-field pau-field--full">
                <label class="pau-label" for="pw-new">Neues Passwort (min. 10 Zeichen) *</label>
                <div class="pau-input-group">
                  <input id="pw-new" v-model="pwForm.new_password" :type="showPw ? 'text' : 'password'" class="pau-input pau-input--pw" :class="{'pau-input--error': fe.new_password}" autocomplete="new-password" />
                  <button type="button" class="pau-pw-btn" :aria-label="showPw ? 'Verbergen' : 'Anzeigen'" @click="showPw = !showPw">
                    <i :class="['pi', showPw ? 'pi-eye-slash' : 'pi-eye']" aria-hidden="true"></i>
                  </button>
                </div>
                <span v-if="fe.new_password" class="pau-field-err">{{ fe.new_password }}</span>
              </div>
              <div class="pau-field pau-field--full">
                <label class="pau-label" for="pw-confirm">Passwort bestätigen *</label>
                <input id="pw-confirm" v-model="pwForm.confirm_password" :type="showPw ? 'text' : 'password'" class="pau-input" :class="{'pau-input--error': fe.confirm_password}" autocomplete="new-password" />
                <span v-if="fe.confirm_password" class="pau-field-err">{{ fe.confirm_password }}</span>
              </div>
            </div>
          </div>
          <div class="pau-modal-footer">
            <button class="am-btn" @click="closeModal">Abbrechen</button>
            <button class="am-btn am-btn-primary" :disabled="saving" @click="submitResetPassword">
              <i v-if="saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
              Passwort setzen
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── Toast ──────────────────────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="toast.show"
        class="pau-toast"
        :class="toast.type === 'success' ? 'pau-toast--success' : 'pau-toast--error'"
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
import type { UserRole } from '@/types'
import type { PlatformAdminUser, PlatformAdminUserCreate, PlatformAdminUserUpdate } from '@/api/platformAdmin'
import * as api from '@/api/platformAdmin'

// ── Rollen ───────────────────────────────────────────────────────
const ROLES: { value: UserRole; label: string }[] = [
  { value: 'passenger', label: 'Fahrgast' },
  { value: 'trusted_person', label: 'Vertrauensperson' },
  { value: 'organization_admin', label: 'Organisations-Admin' },
  { value: 'organization_coordinator', label: 'Koordination' },
  { value: 'provider_admin', label: 'Anbieter-Admin' },
  { value: 'dispatcher', label: 'Disponent' },
  { value: 'driver', label: 'Fahrer' },
  { value: 'platform_admin', label: 'Platform-Admin' },
]

function roleLabel(role: string): string {
  return ROLES.find((r) => r.value === role)?.label ?? role
}

// ── State ────────────────────────────────────────────────────────
const users = ref<PlatformAdminUser[]>([])
const loading = ref(false)
const loadError = ref('')
const searchQuery = ref('')
const filterRole = ref('')
const filterActive = ref('')

const modal = ref<'' | 'create' | 'edit' | 'reset-pw'>('')
const selectedUser = ref<PlatformAdminUser | null>(null)
const saving = ref(false)
const modalError = ref('')
const showPw = ref(false)

// Formular: Erstellen
const form = reactive<PlatformAdminUserCreate & { phone: string }>({
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  role: '' as UserRole,
  phone: '',
  is_active: true,
  organization_id: null,
})

// Formular: Bearbeiten
const editForm = reactive<PlatformAdminUserUpdate & { first_name: string; last_name: string; phone: string }>({
  first_name: '',
  last_name: '',
  role: undefined,
  phone: '',
})

// Formular: Passwort
const pwForm = reactive({ new_password: '', confirm_password: '' })

// Feldvalidierungsfehler
const fe = reactive<Record<string, string>>({})

// Toast
const toast = reactive({ show: false, msg: '', type: 'success' as 'success' | 'error' })

// ── Debounce ─────────────────────────────────────────────────────
let debounceTimer: ReturnType<typeof setTimeout> | undefined
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadUsers, 320)
}

// ── Datenladen ───────────────────────────────────────────────────
async function loadUsers() {
  loading.value = true
  loadError.value = ''
  try {
    const params: { search?: string; role?: string; is_active?: boolean } = {}
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (filterRole.value) params.role = filterRole.value
    if (filterActive.value === 'true') params.is_active = true
    if (filterActive.value === 'false') params.is_active = false
    users.value = await api.listUsers(params)
  } catch {
    loadError.value = 'Nutzerliste konnte nicht geladen werden.'
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)

// ── Hilfsfunktionen ──────────────────────────────────────────────
function initials(user: PlatformAdminUser): string {
  return ((user.first_name[0] ?? '') + (user.last_name[0] ?? '')).toUpperCase()
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

// ── Modal-Steuerung ──────────────────────────────────────────────
function openCreate() {
  clearFe()
  modalError.value = ''
  showPw.value = false
  Object.assign(form, { email: '', password: '', first_name: '', last_name: '', role: '' as UserRole, phone: '', is_active: true, organization_id: null })
  modal.value = 'create'
}

function openEdit(user: PlatformAdminUser) {
  clearFe()
  modalError.value = ''
  selectedUser.value = user
  Object.assign(editForm, { first_name: user.first_name, last_name: user.last_name, role: user.role, phone: user.phone ?? '' })
  modal.value = 'edit'
}

function openResetPassword(user: PlatformAdminUser) {
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

// ── Validierung ──────────────────────────────────────────────────
function validateCreate(): boolean {
  clearFe()
  let ok = true
  if (!form.first_name.trim()) { fe.first_name = 'Pflichtfeld'; ok = false }
  if (!form.last_name.trim()) { fe.last_name = 'Pflichtfeld'; ok = false }
  if (!form.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { fe.email = 'Gültige E-Mail erforderlich'; ok = false }
  if (!form.password || form.password.length < 10) { fe.password = 'Mindestens 10 Zeichen'; ok = false }
  if (!form.role) { fe.role = 'Bitte Rolle wählen'; ok = false }
  return ok
}

function validateResetPassword(): boolean {
  clearFe()
  let ok = true
  if (!pwForm.new_password || pwForm.new_password.length < 10) { fe.new_password = 'Mindestens 10 Zeichen'; ok = false }
  if (!pwForm.confirm_password) { fe.confirm_password = 'Pflichtfeld'; ok = false }
  if (pwForm.new_password && pwForm.confirm_password && pwForm.new_password !== pwForm.confirm_password) { fe.confirm_password = 'Passwörter stimmen nicht überein'; ok = false }
  return ok
}

// ── Aktionen ─────────────────────────────────────────────────────
async function submitCreate() {
  if (!validateCreate() || saving.value) return
  saving.value = true
  modalError.value = ''
  try {
    await api.createUser({
      email: form.email.trim().toLowerCase(),
      password: form.password,
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      role: form.role,
      phone: form.phone.trim() || undefined,
      is_active: form.is_active,
      organization_id: form.organization_id ?? undefined,
    })
    await loadUsers()
    closeModal()
    showToast('Nutzer wurde angelegt.')
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
    const payload: PlatformAdminUserUpdate = {
      first_name: editForm.first_name.trim() || undefined,
      last_name: editForm.last_name.trim() || undefined,
      role: editForm.role,
      phone: editForm.phone.trim() || null,
    }
    await api.updateUser(selectedUser.value.id, payload)
    await loadUsers()
    closeModal()
    showToast('Änderungen gespeichert.')
  } catch (err: unknown) {
    const e = err as { status?: number; body?: { detail?: string } }
    if (e.status === 400) {
      modalError.value = e.body?.detail ?? 'Ungültige Änderung.'
    } else {
      modalError.value = 'Speichern fehlgeschlagen.'
    }
  } finally {
    saving.value = false
  }
}

async function submitResetPassword() {
  if (!validateResetPassword() || saving.value || !selectedUser.value) return
  saving.value = true
  modalError.value = ''
  try {
    await api.resetPassword(selectedUser.value.id, {
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

async function toggleActive(user: PlatformAdminUser) {
  try {
    if (user.is_active) {
      await api.deactivateUser(user.id)
      showToast(`${user.first_name} ${user.last_name} deaktiviert.`)
    } else {
      await api.activateUser(user.id)
      showToast(`${user.first_name} ${user.last_name} aktiviert.`)
    }
    await loadUsers()
  } catch (err: unknown) {
    const e = err as { status?: number; body?: { detail?: string } }
    if (e.status === 400) {
      showToast(e.body?.detail ?? 'Aktion nicht möglich.', 'error')
    } else {
      showToast('Fehler beim Ändern des Status.', 'error')
    }
  }
}
</script>

<style scoped>
/* ── Seite ────────────────────────────────────────────────── */
.pau-page {
  padding: var(--am-space-xl) var(--am-space-l);
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

/* Header */
.pau-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--am-space-m);
}

.pau-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--am-text-primary);
  margin: 0 0 4px;
}

.pau-sub {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 0;
}

.pau-create-btn {
  min-height: 44px;
  white-space: nowrap;
}

/* Filter */
.pau-filters {
  display: flex;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.pau-search-wrap {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.pau-search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--am-text-secondary);
  font-size: 0.9rem;
  pointer-events: none;
}

.pau-search {
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

.pau-search:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.pau-select {
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

.pau-select:focus {
  border-color: var(--am-accent);
}

/* Tabelle */
.pau-table-wrap {
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-m);
  overflow: hidden;
  overflow-x: auto;
}

.pau-loading,
.pau-empty,
.pau-load-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--am-space-m);
  padding: 60px 24px;
  color: var(--am-text-secondary);
  font-size: 0.9rem;
  flex-direction: column;
}

.pau-load-error {
  color: var(--am-danger);
}

.pau-retry {
  margin-top: 8px;
  font-size: 0.85rem;
  height: 36px;
  padding: 0 var(--am-space-m);
}

.pau-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.pau-table th {
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

.pau-th-actions {
  width: 120px;
}

.pau-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--am-border);
  color: var(--am-text-primary);
  vertical-align: middle;
}

.pau-row:last-child td {
  border-bottom: none;
}

.pau-row:hover {
  background: var(--am-bg-raised);
}

/* Name-Zelle */
.pau-td-name {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
}

.pau-avatar {
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

.pau-name {
  font-weight: 600;
  color: var(--am-text-primary);
  font-size: 0.875rem;
}

.pau-org {
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  margin-top: 2px;
}

.pau-td-email {
  color: var(--am-text-secondary);
  font-size: 0.85rem;
}

.pau-td-date {
  color: var(--am-text-secondary);
  font-size: 0.82rem;
  white-space: nowrap;
}

.pau-td-actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
}

/* Chips */
.pau-role-chip {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 0.72rem;
  font-weight: 700;
  background: var(--am-bg-raised);
  color: var(--am-text-secondary);
  border: 1px solid var(--am-border);
  white-space: nowrap;
}

.pau-role--platform_admin {
  background: var(--am-accent-bg);
  color: var(--am-accent);
  border-color: rgba(255, 214, 0, 0.25);
}

.pau-status-chip {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 0.72rem;
  font-weight: 700;
  white-space: nowrap;
}

.pau-status--active {
  background: var(--am-success-bg);
  color: var(--am-success);
  border: 1px solid rgba(34, 197, 94, 0.25);
}

.pau-status--inactive {
  background: var(--am-danger-bg);
  color: var(--am-danger);
  border: 1px solid rgba(239, 68, 68, 0.25);
}

/* Action-Buttons */
.pau-action-btn {
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

.pau-action-btn:hover {
  background: var(--am-bg-raised);
  color: var(--am-text-primary);
}

.pau-action-btn--danger:hover {
  color: var(--am-danger);
  border-color: var(--am-danger);
  background: var(--am-danger-bg);
}

.pau-action-btn--success:hover {
  color: var(--am-success);
  border-color: var(--am-success);
  background: var(--am-success-bg);
}

/* ── Modal ────────────────────────────────────────────────── */
.pau-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: var(--am-space-m);
}

.pau-modal {
  background: var(--am-bg-surface);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-l);
  width: 100%;
  max-width: 560px;
  max-height: 90dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pau-modal--sm {
  max-width: 420px;
}

.pau-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--am-border);
  flex-shrink: 0;
}

.pau-modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.pau-modal-close {
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

.pau-modal-close:hover {
  color: var(--am-text-primary);
  background: var(--am-bg-raised);
}

.pau-modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.pau-modal-hint {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 0;
}

.pau-modal-error {
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

.pau-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--am-space-m);
  padding: 16px 24px;
  border-top: 1px solid var(--am-border);
  flex-shrink: 0;
}

/* Formular */
.pau-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--am-space-m);
}

.pau-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pau-field--full {
  grid-column: 1 / -1;
}

.pau-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--am-text-primary);
}

.pau-input {
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

.pau-input:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.pau-input--error {
  border-color: var(--am-danger) !important;
}

.pau-input-group {
  position: relative;
}

.pau-input--pw {
  padding-right: 44px;
}

.pau-pw-btn {
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

.pau-pw-btn:hover {
  color: var(--am-text-primary);
}

.pau-field-err {
  font-size: 0.78rem;
  color: var(--am-danger);
}

.pau-check-row {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.875rem;
  color: var(--am-text-primary);
  cursor: pointer;
}

.pau-check {
  width: 18px;
  height: 18px;
  accent-color: var(--am-accent);
  cursor: pointer;
}

/* ── Toast ────────────────────────────────────────────────── */
.pau-toast {
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

.pau-toast--success {
  background: var(--am-success-bg);
  color: var(--am-success);
  border: 1px solid rgba(34, 197, 94, 0.35);
}

.pau-toast--error {
  background: var(--am-danger-bg);
  color: var(--am-danger);
  border: 1px solid rgba(239, 68, 68, 0.35);
}

@keyframes toastIn {
  from { transform: translateY(16px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

/* ── Accessibility ────────────────────────────────────────── */
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
