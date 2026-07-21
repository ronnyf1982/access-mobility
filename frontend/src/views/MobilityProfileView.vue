<template>
  <div class="mp-page">
    <!-- Seitenheader -->
    <div class="mp-header">
      <div>
        <h1 class="mp-title">Mein Mobilitätsprofil</h1>
        <p class="mp-subtitle">
          Ihr Mobilitätsprofil hilft uns, später automatisch ein passendes Fahrzeug und die
          richtige Unterstützung auszuwählen.
        </p>
      </div>
    </div>

    <!-- Geführter Check CTA -->
    <div class="mp-assistant-cta am-card" role="region" aria-labelledby="assistant-cta-heading">
      <div class="mp-assistant-cta-icon" aria-hidden="true">
        <i class="pi pi-comments"></i>
      </div>
      <div class="mp-assistant-cta-text">
        <h2 id="assistant-cta-heading" class="mp-assistant-cta-title">Geführten Mobilitätscheck starten</h2>
        <p class="mp-assistant-cta-desc">
          Die App führt Sie Schritt für Schritt durch die wichtigsten Fragen.
          Sie können alles vor dem Speichern prüfen.
        </p>
      </div>
      <RouterLink
        to="/mobility-profile/assistant"
        class="am-btn am-btn-primary mp-assistant-cta-btn"
        aria-label="Geführten Mobilitätscheck starten"
      >
        <i class="pi pi-arrow-right" aria-hidden="true"></i>
        Geführten Check starten
      </RouterLink>
    </div>

    <div
      v-if="store.loading"
      class="mp-loading"
      role="status"
      aria-live="polite"
      aria-label="Profil wird geladen"
    >
      <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
      Profil wird geladen …
    </div>

    <form v-else class="mp-form" @submit.prevent="handleSave" novalidate>
      <!-- Hinweisbox -->
      <div class="mp-notice" role="note">
        <i class="pi pi-info-circle" aria-hidden="true"></i>
        Alle Angaben können jederzeit geändert werden.
        <strong>Medizinische Hinweise sind freiwillig</strong> und werden ausschließlich zur
        Fahrtplanung genutzt.
      </div>

      <!-- ── Schnellauswahl Transporttyp ──────────────────────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s0-heading">
        <h2 id="s0-heading" class="mp-section-title">
          <i class="pi pi-bolt" aria-hidden="true"></i>
          Schnellauswahl: Welche Art von Fahrt benötigen Sie?
        </h2>
        <p class="mp-section-desc">
          Wählen Sie den passenden Transporttyp — passende Felder werden vorausgefüllt.
          Sie können anschließend alles anpassen.
        </p>
        <div class="mp-transport-grid" role="group" aria-label="Transporttyp auswählen">
          <button
            v-for="tt in TRANSPORT_TYPES"
            :key="tt.id"
            type="button"
            class="mp-transport-card"
            :class="{ 'mp-transport-card--active': selectedTransportType === tt.id }"
            :aria-pressed="selectedTransportType === tt.id"
            :aria-label="tt.label + ': ' + tt.description"
            @click="applyTransportType(tt)"
          >
            <span class="mp-transport-label">{{ tt.label }}</span>
            <span class="mp-transport-desc">{{ tt.description }}</span>
            <span v-if="tt.warning" class="mp-transport-warning">
              <i class="pi pi-exclamation-triangle" aria-hidden="true"></i>
              {{ tt.warning }}
            </span>
          </button>
        </div>
        <p v-if="selectedTransportType" class="mp-transport-hint">
          <i class="pi pi-info-circle" aria-hidden="true"></i>
          Felder wurden vorausgefüllt — bitte prüfen und bei Bedarf anpassen.
          <button type="button" class="mp-link-btn" @click="selectedTransportType = null">Auswahl zurücksetzen</button>
        </p>
      </section>

      <!-- Erfolgsmeldung -->
      <div
        v-if="saveSuccess"
        class="mp-alert mp-alert--success"
        role="alert"
        aria-live="assertive"
      >
        <i class="pi pi-check-circle" aria-hidden="true"></i>
        Ihr Mobilitätsprofil wurde gespeichert.
      </div>

      <!-- Fehlermeldung -->
      <div
        v-if="saveError"
        class="mp-alert mp-alert--error"
        role="alert"
        aria-live="assertive"
      >
        <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
        {{ saveError }}
      </div>

      <!-- ── Abschnitt 1: Notfallkontakt ────────────────────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s1-heading">
        <h2 id="s1-heading" class="mp-section-title">
          <i class="pi pi-phone" aria-hidden="true"></i>
          Notfallkontakt
        </h2>
        <p class="mp-section-desc">
          Wer soll im Notfall kontaktiert werden? Die Angabe ist freiwillig.
        </p>
        <div class="mp-field-row">
          <div class="mp-field">
            <label for="ec-name" class="mp-label">Name der Kontaktperson</label>
            <input
              id="ec-name"
              v-model="form.emergency_contact_name"
              type="text"
              class="mp-input"
              autocomplete="off"
              aria-label="Name der Notfallkontaktperson"
              placeholder="Vorname Nachname"
            />
          </div>
          <div class="mp-field">
            <label for="ec-phone" class="mp-label">Telefonnummer</label>
            <input
              id="ec-phone"
              v-model="form.emergency_contact_phone"
              type="tel"
              class="mp-input"
              autocomplete="off"
              aria-label="Telefonnummer der Notfallkontaktperson"
              placeholder="+49 30 …"
            />
          </div>
        </div>
      </section>

      <!-- ── Abschnitt 2: Mobilitätsbedarf ──────────────────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s2-heading">
        <h2 id="s2-heading" class="mp-section-title">
          <i class="pi pi-heart" aria-hidden="true"></i>
          Mein Mobilitätsbedarf
        </h2>
        <p class="mp-section-desc">
          Wählen Sie alles aus, was auf Sie zutrifft. Mehrfachauswahl ist möglich.
        </p>

        <div class="mp-need-grid" role="group" aria-label="Mobilitätsbedarf auswählen">
          <button
            v-for="need in store.mobilityNeedItems"
            :key="String(need.key)"
            type="button"
            class="mp-need-card"
            :class="{ 'mp-need-card--active': form[need.key] as boolean }"
            role="checkbox"
            :aria-checked="!!(form[need.key] as boolean)"
            :aria-label="`${need.label}: ${need.description}`"
            @click="toggleNeed(need.key as NeedKey)"
          >
            <div class="mp-need-icon" aria-hidden="true">
              <i :class="['pi', need.icon]"></i>
            </div>
            <div class="mp-need-text">
              <span class="mp-need-label">{{ need.label }}</span>
              <span class="mp-need-desc">{{ need.description }}</span>
            </div>
            <div class="mp-need-check" aria-hidden="true">
              <i class="pi pi-check"></i>
            </div>
          </button>
        </div>

        <!-- Rollstuhl-Typ (nur wenn Rollstuhl aktiv) -->
        <div v-if="form.uses_wheelchair" class="mp-wheelchair-type" role="group" aria-labelledby="wct-heading">
          <p id="wct-heading" class="mp-label">Welche Art von Rollstuhl nutzen Sie?</p>
          <div class="mp-radio-group">
            <label v-for="opt in wheelchairTypeOptions" :key="opt.value" class="mp-radio-label">
              <input
                type="radio"
                class="mp-radio"
                :value="opt.value"
                v-model="form.wheelchair_type"
                :name="`wheelchair_type`"
              />
              <span>{{ opt.label }}</span>
            </label>
          </div>
        </div>
      </section>

      <!-- ── Abschnitt 3: Fahrzeug- / Service-Hinweise ──────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s3-heading">
        <h2 id="s3-heading" class="mp-section-title">
          <i class="pi pi-car" aria-hidden="true"></i>
          Fahrzeug- und Service-Hinweise
        </h2>
        <p class="mp-section-desc">
          Diese Angaben helfen dem Fahrdienst, das passende Fahrzeug bereit zu stellen.
        </p>

        <div class="mp-toggle-list">
          <!-- Rollstuhlplatz erforderlich -->
          <label class="mp-toggle-row">
            <span class="mp-toggle-label">
              Rollstuhlplatz im Fahrzeug erforderlich
              <span class="mp-toggle-sub">Das Fahrzeug muss einen gesicherten Rollstuhlplatz haben.</span>
            </span>
            <button
              type="button"
              class="mp-toggle-btn"
              :class="{ 'mp-toggle-btn--on': form.requires_wheelchair_space }"
              role="switch"
              :aria-checked="form.requires_wheelchair_space"
              aria-label="Rollstuhlplatz erforderlich"
              @click="form.requires_wheelchair_space = !form.requires_wheelchair_space"
            >
              <span class="mp-toggle-knob"></span>
            </button>
          </label>

          <!-- Zusätzliche Zeit -->
          <label class="mp-toggle-row">
            <span class="mp-toggle-label">
              Zusätzliche Zeit einplanen
              <span class="mp-toggle-sub">Für Ein- und Aussteigen wird mehr Zeit benötigt.</span>
            </span>
            <button
              type="button"
              class="mp-toggle-btn"
              :class="{ 'mp-toggle-btn--on': form.requires_extra_time }"
              role="switch"
              :aria-checked="form.requires_extra_time"
              aria-label="Zusätzliche Zeit einplanen"
              @click="form.requires_extra_time = !form.requires_extra_time"
            >
              <span class="mp-toggle-knob"></span>
            </button>
          </label>

          <!-- Auf Sitz wechseln -->
          <div class="mp-tristate-row">
            <span class="mp-toggle-label">
              Kann auf normalen Fahrzeugsitz wechseln
              <span class="mp-toggle-sub">Wenn ja, kann der Rollstuhl ggf. im Kofferraum transportiert werden.</span>
            </span>
            <div class="mp-tristate-btns" role="group" aria-label="Kann auf normalen Sitz wechseln">
              <button
                v-for="opt in tristateOptions"
                :key="String(opt.value)"
                type="button"
                class="mp-tristate-btn"
                :class="{ 'mp-tristate-btn--active': form.can_transfer_to_seat === opt.value }"
                :aria-pressed="form.can_transfer_to_seat === opt.value"
                @click="form.can_transfer_to_seat = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- Eigener Rollstuhl -->
          <div class="mp-tristate-row">
            <span class="mp-toggle-label">
              Eigener Rollstuhl vorhanden
              <span class="mp-toggle-sub">Falls ja, wird er im Fahrzeug mitgenommen.</span>
            </span>
            <div class="mp-tristate-btns" role="group" aria-label="Eigener Rollstuhl vorhanden">
              <button
                v-for="opt in tristateOptions"
                :key="String(opt.value)"
                type="button"
                class="mp-tristate-btn"
                :class="{ 'mp-tristate-btn--active': form.has_own_wheelchair === opt.value }"
                :aria-pressed="form.has_own_wheelchair === opt.value"
                @click="form.has_own_wheelchair = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Abschnitt 3b: Medizinische Detailangaben ──────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s3b-heading">
        <h2 id="s3b-heading" class="mp-section-title">
          <i class="pi pi-heart" aria-hidden="true"></i>
          Medizinische Detailangaben
          <span class="mp-optional-badge">freiwillig</span>
        </h2>
        <p class="mp-section-desc">
          Nur für qualifizierten Krankentransport relevant. Alle Angaben sind freiwillig
          und werden vertraulich behandelt.
        </p>

        <div class="mp-need-grid" role="group" aria-label="Medizinische Detailangaben">
          <button
            v-for="opt in MEDICAL_DETAIL_OPTIONS"
            :key="String(opt.key)"
            type="button"
            class="mp-need-card"
            :class="{ 'mp-need-card--active': form[opt.key] as boolean }"
            role="checkbox"
            :aria-checked="!!(form[opt.key] as boolean)"
            :aria-label="`${opt.label}: ${opt.description}`"
            @click="toggleMedDetail(opt.key)"
          >
            <div class="mp-need-icon" aria-hidden="true">
              <i :class="['pi', opt.icon]"></i>
            </div>
            <div class="mp-need-text">
              <span class="mp-need-label">{{ opt.label }}</span>
              <span class="mp-need-desc">{{ opt.description }}</span>
            </div>
            <div class="mp-need-check" aria-hidden="true">
              <i class="pi pi-check"></i>
            </div>
          </button>
        </div>

        <!-- Begleitperson Typ (nur wenn medizinische Begleitung aktiv) -->
        <div v-if="form.requires_medical_attendant" class="mp-wheelchair-type" role="group" aria-labelledby="att-heading">
          <p id="att-heading" class="mp-label">Welche Art von Begleitperson wird benötigt?</p>
          <div class="mp-radio-group">
            <label v-for="opt in ATTENDANT_TYPE_OPTIONS" :key="opt.value" class="mp-radio-label">
              <input
                type="radio"
                class="mp-radio"
                :value="opt.value"
                v-model="form.attendant_type_required"
                name="attendant_type_required"
              />
              <span>{{ opt.label }}</span>
            </label>
          </div>
        </div>

        <!-- Freitextfelder für medizinische Details -->
        <div class="mp-field">
          <label for="med-device-notes" class="mp-label">
            Hinweise zu mitgebrachten Medizingeräten
            <span class="mp-optional-badge">freiwillig</span>
          </label>
          <p class="mp-field-hint">z. B. „Beatmungsgerät Typ X, benötigt 230V-Anschluss"</p>
          <textarea
            id="med-device-notes"
            v-model="form.medical_device_notes"
            class="mp-textarea"
            rows="2"
            aria-label="Hinweise zu Medizingeräten"
          ></textarea>
        </div>

        <div class="mp-field">
          <label for="med-transport-notes" class="mp-label">
            Sonstige Transporthinweise (medizinisch)
            <span class="mp-optional-badge">freiwillig</span>
          </label>
          <p class="mp-field-hint">Weitere Informationen für das Transportpersonal</p>
          <textarea
            id="med-transport-notes"
            v-model="form.medical_transport_notes"
            class="mp-textarea"
            rows="2"
            aria-label="Sonstige medizinische Transporthinweise"
          ></textarea>
        </div>
      </section>

      <!-- ── Abschnitt 4: Hinweise ───────────────────────────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s4-heading">
        <h2 id="s4-heading" class="mp-section-title">
          <i class="pi pi-comment" aria-hidden="true"></i>
          Weitere Hinweise
        </h2>

        <div class="mp-field">
          <label for="comm-notes" class="mp-label">Kommunikationshinweise</label>
          <p class="mp-field-hint">
            Z. B. „Bitte laut und deutlich sprechen", „bevorzuge schriftliche Kommunikation"
          </p>
          <textarea
            id="comm-notes"
            v-model="form.communication_notes"
            class="mp-textarea"
            rows="3"
            aria-label="Kommunikationshinweise"
          ></textarea>
        </div>

        <div class="mp-field">
          <label for="med-notes" class="mp-label">
            Medizinische Hinweise
            <span class="mp-optional-badge">freiwillig</span>
          </label>
          <p class="mp-field-hint">
            Relevante Informationen für den Fahrdienst, z. B. Sauerstoffgerät, Medikamente im
            Notfall. Wird vertraulich behandelt.
          </p>
          <textarea
            id="med-notes"
            v-model="form.medical_notes"
            class="mp-textarea"
            rows="3"
            aria-label="Medizinische Hinweise — freiwillig"
          ></textarea>
        </div>

        <div class="mp-field">
          <label for="gen-notes" class="mp-label">Allgemeine Hinweise</label>
          <p class="mp-field-hint">
            Alles Weitere, das für den Fahrdienst wichtig sein könnte.
          </p>
          <textarea
            id="gen-notes"
            v-model="form.general_notes"
            class="mp-textarea"
            rows="3"
            aria-label="Allgemeine Hinweise"
          ></textarea>
        </div>
      </section>

      <!-- ── Abschnitt 5: Benachrichtigungseinstellungen ──────────────── -->
      <section class="mp-section am-card" aria-labelledby="s5-heading">
        <h2 id="s5-heading" class="mp-section-title">
          <i class="pi pi-bell" aria-hidden="true"></i>
          Benachrichtigungseinstellungen
        </h2>
        <p class="mp-section-desc">
          Legen Sie fest, über welche Fahrt-Ereignisse Ihre Vertrauenspersonen informiert werden sollen.
          <strong>Hinweis:</strong> Der Versand wird in einem späteren Sprint aktiviert.
        </p>

        <div v-if="notifLoading" class="mp-loading" role="status">
          <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
          Einstellungen werden geladen …
        </div>

        <div v-else class="notif-table" role="table" aria-label="Benachrichtigungseinstellungen">
          <!-- Kopfzeile -->
          <div class="notif-row notif-row--head" role="row">
            <div class="notif-cell notif-cell--event" role="columnheader">Ereignis</div>
            <div class="notif-cell notif-cell--chan" role="columnheader" title="Vertrauensperson informieren">Vertrauensperson</div>
            <div class="notif-cell notif-cell--chan" role="columnheader" title="In-App-Benachrichtigung">In-App</div>
            <div class="notif-cell notif-cell--chan" role="columnheader" title="E-Mail">E-Mail</div>
            <div class="notif-cell notif-cell--chan" role="columnheader" title="SMS">SMS</div>
          </div>

          <div
            v-for="pref in notifPrefs"
            :key="pref.event_type"
            class="notif-row"
            role="row"
          >
            <div class="notif-cell notif-cell--event" role="cell">
              {{ NOTIFICATION_EVENT_LABELS[pref.event_type] }}
            </div>
            <div class="notif-cell notif-cell--chan" role="cell">
              <input
                type="checkbox"
                class="notif-check"
                v-model="pref.notify_trusted_persons"
                :aria-label="`Vertrauensperson bei '${NOTIFICATION_EVENT_LABELS[pref.event_type]}' informieren`"
              />
            </div>
            <div class="notif-cell notif-cell--chan" role="cell">
              <input
                type="checkbox"
                class="notif-check"
                v-model="pref.channel_in_app"
                :aria-label="`In-App bei '${NOTIFICATION_EVENT_LABELS[pref.event_type]}'`"
              />
            </div>
            <div class="notif-cell notif-cell--chan" role="cell">
              <input
                type="checkbox"
                class="notif-check"
                v-model="pref.channel_email"
                :aria-label="`E-Mail bei '${NOTIFICATION_EVENT_LABELS[pref.event_type]}'`"
              />
            </div>
            <div class="notif-cell notif-cell--chan" role="cell">
              <input
                type="checkbox"
                class="notif-check"
                v-model="pref.channel_sms"
                :aria-label="`SMS bei '${NOTIFICATION_EVENT_LABELS[pref.event_type]}'`"
              />
            </div>
          </div>
        </div>

        <div v-if="notifSaveSuccess" class="mp-alert mp-alert--success" role="alert">
          <i class="pi pi-check-circle" aria-hidden="true"></i>
          Benachrichtigungseinstellungen gespeichert.
        </div>
        <div v-if="notifSaveError" class="mp-alert mp-alert--error" role="alert">
          <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
          {{ notifSaveError }}
        </div>

        <button
          type="button"
          class="am-btn am-btn-primary mp-save-btn"
          :disabled="notifSaving"
          :aria-busy="notifSaving"
          @click="handleNotifSave"
        >
          <i v-if="notifSaving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
          <i v-else class="pi pi-save" aria-hidden="true"></i>
          {{ notifSaving ? 'Wird gespeichert …' : 'Einstellungen speichern' }}
        </button>
      </section>

      <!-- ── Abschnitt 6: Wichtige Kontakte ────────────────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s6-heading">
        <h2 id="s6-heading" class="mp-section-title">
          <i class="pi pi-users" aria-hidden="true"></i>
          Wichtige Kontakte
        </h2>
        <p class="mp-section-desc">
          Verwalten Sie Ihre Kontakte und legen Sie fest, welche davon dem Fahrer oder im Notfall sichtbar sind.
        </p>

        <div v-if="contactsError" class="mp-alert mp-alert--error" role="alert">
          <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
          {{ contactsError }}
        </div>

        <div v-if="contactsLoading" class="mp-loading" role="status">
          <i class="pi pi-spin pi-spinner" aria-hidden="true"></i>
          Kontakte werden geladen …
        </div>

        <div v-else-if="contacts.length > 0" class="contact-list" role="list">
          <div v-for="c in contacts" :key="c.id" class="contact-item" role="listitem">
            <div class="contact-item-info">
              <span class="contact-item-name">{{ c.name || 'Unbenannter Kontakt' }}</span>
              <span v-if="c.role_label" class="contact-item-role">{{ c.role_label }}</span>
              <span class="contact-item-type">{{ CONTACT_TYPE_LABELS[c.contact_type] }}</span>
              <div class="contact-item-badges">
                <span v-if="c.is_emergency_contact" class="contact-badge contact-badge--emergency">Notfallkontakt</span>
                <span v-if="c.visible_to_driver" class="contact-badge contact-badge--driver">Fahrer sieht</span>
                <span v-if="c.visible_in_emergency" class="contact-badge contact-badge--emerg">Notfall sieht</span>
              </div>
            </div>
            <div class="contact-item-actions">
              <a v-if="c.phone_number" :href="`tel:${c.phone_number}`" class="contact-phone-link" :aria-label="`${c.name || 'Kontakt'} anrufen`">
                <i class="pi pi-phone" aria-hidden="true"></i>
                {{ c.phone_number }}
              </a>
              <span v-else class="contact-no-phone">Keine Telefonnummer</span>
              <button type="button" class="am-btn am-btn-secondary contact-action-btn" @click="openEditContact(c)" :aria-label="`${c.name} bearbeiten`">
                <i class="pi pi-pencil" aria-hidden="true"></i>
              </button>
              <button type="button" class="am-btn contact-action-btn contact-action-btn--delete" @click="handleContactDelete(c.id)" :aria-label="`${c.name} löschen`">
                <i class="pi pi-trash" aria-hidden="true"></i>
              </button>
            </div>
          </div>
        </div>

        <p v-else-if="!contactsLoading" class="mp-section-desc">Noch keine Kontakte angelegt.</p>

        <button v-if="!showContactForm" type="button" class="am-btn am-btn-secondary contact-add-btn" @click="openAddContact">
          <i class="pi pi-plus" aria-hidden="true"></i>
          Kontakt hinzufügen
        </button>

        <div v-if="showContactForm" class="contact-form" role="form" :aria-label="editingContactId ? 'Kontakt bearbeiten' : 'Neuen Kontakt anlegen'">
          <h3 class="contact-form-title">{{ editingContactId ? 'Kontakt bearbeiten' : 'Neuen Kontakt anlegen' }}</h3>

          <div v-if="contactFormError" class="mp-alert mp-alert--error" role="alert">
            <i class="pi pi-exclamation-circle" aria-hidden="true"></i>
            {{ contactFormError }}
          </div>

          <div class="mp-field-row">
            <div class="mp-field">
              <label for="cf-name" class="mp-label">Name <span style="color:var(--am-danger)">*</span></label>
              <input id="cf-name" v-model="contactForm.name" type="text" class="mp-input" placeholder="Vor- und Nachname" autocomplete="off" />
            </div>
            <div class="mp-field">
              <label for="cf-phone" class="mp-label">Telefonnummer</label>
              <input id="cf-phone" v-model="contactForm.phone_number" type="tel" class="mp-input" placeholder="+49 30 …" autocomplete="off" />
            </div>
          </div>

          <div class="mp-field-row">
            <div class="mp-field">
              <label for="cf-type" class="mp-label">Art des Kontakts</label>
              <select id="cf-type" v-model="contactForm.contact_type" class="mp-input mp-select">
                <option v-for="opt in CONTACT_TYPE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
            <div class="mp-field">
              <label for="cf-role" class="mp-label">Bezeichnung <span class="mp-optional-badge">freiwillig</span></label>
              <input id="cf-role" v-model="contactForm.role_label" type="text" class="mp-input" placeholder="z. B. Mutter, Hausarzt" autocomplete="off" />
            </div>
          </div>

          <div class="mp-field">
            <label for="cf-note" class="mp-label">Notiz <span class="mp-optional-badge">freiwillig</span></label>
            <textarea id="cf-note" v-model="contactForm.note" class="mp-textarea" rows="2" placeholder="Weitere Hinweise zu dieser Person"></textarea>
          </div>

          <div class="mp-field">
            <label for="cf-priority" class="mp-label">Priorität <span class="mp-optional-badge">0 = höchste</span></label>
            <input id="cf-priority" v-model.number="contactForm.priority" type="number" min="0" max="999" class="mp-input" style="max-width:120px" />
          </div>

          <div class="contact-flags">
            <label class="contact-flag">
              <input type="checkbox" v-model="contactForm.is_emergency_contact" class="contact-flag-check" />
              <span>Ist Notfallkontakt</span>
            </label>
            <label class="contact-flag">
              <input type="checkbox" v-model="contactForm.visible_to_driver" class="contact-flag-check" />
              <span>Für Fahrer sichtbar</span>
            </label>
            <label class="contact-flag">
              <input type="checkbox" v-model="contactForm.visible_in_emergency" class="contact-flag-check" />
              <span>Im Notfall sichtbar</span>
            </label>
            <label class="contact-flag">
              <input type="checkbox" v-model="contactForm.callable_in_emergency" class="contact-flag-check" />
              <span>Im Notfall anrufbar</span>
            </label>
          </div>

          <div class="contact-form-actions">
            <button
              type="button"
              class="am-btn am-btn-primary"
              :disabled="contactFormSaving || !contactForm.name.trim() || !contactForm.phone_number.trim()"
              :aria-disabled="contactFormSaving || !contactForm.name.trim() || !contactForm.phone_number.trim()"
              @click="handleContactSave"
            >
              <i v-if="contactFormSaving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
              <i v-else class="pi pi-save" aria-hidden="true"></i>
              {{ contactFormSaving ? 'Wird gespeichert …' : 'Speichern' }}
            </button>
            <button type="button" class="am-btn am-btn-secondary" @click="showContactForm = false; resetContactForm()">
              Abbrechen
            </button>
          </div>
        </div>
      </section>

      <!-- ── Abschnitt 7: Notfallinformationen ──────────────────────────── -->
      <section class="mp-section am-card" aria-labelledby="s7-heading">
        <h2 id="s7-heading" class="mp-section-title">
          <i class="pi pi-heart-fill" aria-hidden="true"></i>
          Notfallinformationen
          <span class="mp-optional-badge">freiwillig</span>
        </h2>
        <p class="mp-section-desc">
          Diese Angaben helfen im Notfall. Sie entscheiden, was Fahrer und Einsatzkräfte sehen dürfen.
        </p>

        <!-- Körperdaten -->
        <div class="efinfo-block">
          <div class="efinfo-block-header">
            <h3 class="efinfo-block-title">Körperdaten</h3>
            <div class="efinfo-vis-row" role="group" aria-label="Sichtbarkeit Körperdaten">
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_body_data_in_emergency" class="contact-flag-check" />
                Im Notfall anzeigen
              </label>
            </div>
          </div>
          <div class="mp-field-row">
            <div class="mp-field">
              <label for="ef-gender" class="mp-label">Geschlecht</label>
              <select id="ef-gender" v-model="form.gender" class="mp-input mp-select">
                <option value="">– keine Angabe –</option>
                <option v-for="opt in GENDER_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
            <div class="mp-field">
              <label for="ef-height" class="mp-label">Körpergröße (cm)</label>
              <input id="ef-height" v-model.number="form.body_height_cm" type="number" min="50" max="250" class="mp-input" placeholder="z. B. 172" />
            </div>
            <div class="mp-field">
              <label for="ef-weight" class="mp-label">Körpergewicht (kg)</label>
              <input id="ef-weight" v-model.number="form.body_weight_kg" type="number" min="10" max="300" class="mp-input" placeholder="z. B. 70" />
            </div>
          </div>
        </div>

        <!-- Erkrankungen & Behinderungen -->
        <div class="efinfo-block">
          <div class="efinfo-block-header">
            <h3 class="efinfo-block-title">Erkrankungen & Behinderungen</h3>
            <div class="efinfo-vis-row" role="group" aria-label="Sichtbarkeit Erkrankungen">
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_disabilities_to_driver" class="contact-flag-check" />
                Fahrer
              </label>
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_disabilities_in_emergency" class="contact-flag-check" />
                Notfall
              </label>
            </div>
          </div>
          <div class="mp-toggle-list">
            <label class="mp-toggle-row">
              <span class="mp-toggle-label">
                Epilepsie bekannt
                <span class="mp-toggle-sub">Aktiviert spezifische Erste-Hilfe-Hinweise im Notfall.</span>
              </span>
              <button type="button" class="mp-toggle-btn" :class="{ 'mp-toggle-btn--on': form.has_epilepsy }" role="switch" :aria-checked="form.has_epilepsy" @click="form.has_epilepsy = !form.has_epilepsy">
                <span class="mp-toggle-knob"></span>
              </button>
            </label>
            <label class="mp-toggle-row">
              <span class="mp-toggle-label">
                Sprechbehinderung / nicht sprechend
                <span class="mp-toggle-sub">Hinweis für Fahrer und Einsatzkräfte.</span>
              </span>
              <button type="button" class="mp-toggle-btn" :class="{ 'mp-toggle-btn--on': form.is_mute }" role="switch" :aria-checked="form.is_mute" @click="form.is_mute = !form.is_mute">
                <span class="mp-toggle-knob"></span>
              </button>
            </label>
          </div>
          <div class="mp-field">
            <label for="ef-conditions" class="mp-label">Bekannte Erkrankungen</label>
            <p class="mp-field-hint">z. B. Diabetes, Herzerkrankung, Demenz</p>
            <textarea id="ef-conditions" v-model="form.known_conditions" class="mp-textarea" rows="2"></textarea>
          </div>
          <div class="mp-field">
            <label for="ef-dis-notes" class="mp-label">Sonstige Behinderungshinweise</label>
            <textarea id="ef-dis-notes" v-model="form.other_disabilities_notes" class="mp-textarea" rows="2"></textarea>
          </div>
        </div>

        <!-- Medikation & Allergien -->
        <div class="efinfo-block">
          <div class="efinfo-block-header">
            <h3 class="efinfo-block-title">Medikation & Allergien</h3>
            <div class="efinfo-vis-row" role="group" aria-label="Sichtbarkeit Medikation">
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_medication_to_driver" class="contact-flag-check" />
                Fahrer
              </label>
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_medication_in_emergency" class="contact-flag-check" />
                Notfall
              </label>
            </div>
          </div>
          <div class="mp-field">
            <label for="ef-medication" class="mp-label">Dauermedikation</label>
            <p class="mp-field-hint">z. B. „Metformin 500 mg 2x täglich"</p>
            <textarea id="ef-medication" v-model="form.medication_notes" class="mp-textarea" rows="2"></textarea>
          </div>
          <div class="mp-field">
            <label for="ef-allergy" class="mp-label">Allergien / Unverträglichkeiten</label>
            <textarea id="ef-allergy" v-model="form.allergy_notes" class="mp-textarea" rows="2"></textarea>
          </div>
        </div>

        <!-- Notfallverhalten -->
        <div class="efinfo-block">
          <div class="efinfo-block-header">
            <h3 class="efinfo-block-title">Notfallverhalten</h3>
            <div class="efinfo-vis-row" role="group" aria-label="Sichtbarkeit Notfallhinweise">
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_emergency_notes_to_driver" class="contact-flag-check" />
                Fahrer
              </label>
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_emergency_notes_in_emergency" class="contact-flag-check" />
                Notfall
              </label>
            </div>
          </div>
          <div class="mp-field">
            <label for="ef-care" class="mp-label">Im Notfall bitte …</label>
            <p class="mp-field-hint">Was sollen Helfer tun?</p>
            <textarea id="ef-care" v-model="form.emergency_care_notes" class="mp-textarea" rows="2"></textarea>
          </div>
          <div class="mp-field">
            <label for="ef-helps" class="mp-label">Das hilft</label>
            <textarea id="ef-helps" v-model="form.what_helps_notes" class="mp-textarea" rows="2"></textarea>
          </div>
          <div class="mp-field">
            <label for="ef-avoid" class="mp-label">Das vermeiden</label>
            <textarea id="ef-avoid" v-model="form.what_to_avoid_notes" class="mp-textarea" rows="2"></textarea>
          </div>
          <div class="mp-field">
            <label for="ef-extra" class="mp-label">Weitere Notfallhinweise</label>
            <textarea id="ef-extra" v-model="form.additional_emergency_notes" class="mp-textarea" rows="2"></textarea>
          </div>
        </div>

        <!-- Kommunikationshinweise (Sichtbarkeit) -->
        <div class="efinfo-block">
          <div class="efinfo-block-header">
            <h3 class="efinfo-block-title">Sichtbarkeit: Kommunikationshinweise</h3>
            <div class="efinfo-vis-row" role="group" aria-label="Sichtbarkeit Kommunikationshinweise">
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_communication_notes_to_driver" class="contact-flag-check" />
                Fahrer
              </label>
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_communication_notes_in_emergency" class="contact-flag-check" />
                Notfall
              </label>
            </div>
          </div>
          <p class="mp-section-desc">Steuert, ob die Kommunikationshinweise aus Abschnitt 4 für Fahrer / im Notfall sichtbar sind.</p>
        </div>

        <!-- Kontaktsichtbarkeit (global) -->
        <div class="efinfo-block">
          <div class="efinfo-block-header">
            <h3 class="efinfo-block-title">Sichtbarkeit: Kontakte (global)</h3>
            <div class="efinfo-vis-row" role="group" aria-label="Sichtbarkeit Kontakte global">
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_contacts_to_driver" class="contact-flag-check" />
                Fahrer
              </label>
              <label class="efinfo-vis-label">
                <input type="checkbox" v-model="form.show_contacts_in_emergency" class="contact-flag-check" />
                Notfall
              </label>
            </div>
          </div>
          <p class="mp-section-desc">Globaler Schalter. Jeder Kontakt kann zusätzlich individuell konfiguriert werden (Abschnitt 6).</p>
        </div>
      </section>

      <!-- ── Abschnitt 8: Speichern ──────────────────────────────────────── -->
      <div class="mp-save-bar">
        <button
          type="submit"
          class="am-btn am-btn-primary mp-save-btn"
          :disabled="store.saving"
          :aria-busy="store.saving"
        >
          <i v-if="store.saving" class="pi pi-spin pi-spinner" aria-hidden="true"></i>
          <i v-else class="pi pi-save" aria-hidden="true"></i>
          {{ store.saving ? 'Wird gespeichert …' : 'Mobilitätsprofil speichern' }}
        </button>
        <span class="mp-save-hint">Ihre Daten werden sicher auf dem Server gespeichert.</span>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useMobilityProfileStore } from '@/stores/mobilityProfile'
import { getTransportOptions } from '@/api/transportOptions'
import { getNotificationPreferences, saveNotificationPreferences } from '@/api/notificationPreferences'
import { listContacts, createContact, updateContact, deleteContact } from '@/api/passengerContacts'
import type { MobilityProfile, NotificationEventType, WheelchairType, AttendantType, TransportType, PassengerContact, PassengerContactCreate, ContactType } from '@/types'
import { NOTIFICATION_EVENT_LABELS, CONTACT_TYPE_LABELS } from '@/types'

type NeedKey =
  | 'uses_wheelchair'
  | 'uses_rollator'
  | 'uses_crutches'
  | 'is_blind_or_visually_impaired'
  | 'is_deaf_or_hard_of_hearing'
  | 'needs_escort'
  | 'needs_entry_assistance'
  | 'needs_door_to_door_assistance'
  | 'needs_ramp'
  | 'needs_lift'
  | 'needs_stretcher_transport'

type MedDetailKey =
  | 'requires_transport_chair'
  | 'requires_two_person_assistance'
  | 'requires_medical_transport'
  | 'brings_oxygen'
  | 'requires_oxygen_mount'
  | 'brings_medical_device'
  | 'requires_medical_equipment_storage'
  | 'requires_infusion_mount'
  | 'requires_special_positioning'
  | 'infection_or_hygiene_note'
  | 'requires_medical_attendant'

const store = useMobilityProfileStore()
const toast = useToast()

const saveSuccess = ref(false)
const saveError = ref('')
const selectedTransportType = ref<string | null>(null)
const TRANSPORT_TYPES = ref<TransportType[]>([])

// ── Benachrichtigungseinstellungen ─────────────────────────────────────────

const ALL_NOTIFICATION_EVENTS: NotificationEventType[] = [
  'driver_on_way',
  'driver_arrived',
  'passenger_picked_up',
  'ride_started',
  'ride_completed',
  'ride_cancelled',
  'issue_reported',
]

interface EditableNotifPref {
  event_type: NotificationEventType
  notify_trusted_persons: boolean
  channel_in_app: boolean
  channel_email: boolean
  channel_sms: boolean
}

const notifPrefs = ref<EditableNotifPref[]>([])
const notifLoading = ref(false)
const notifSaving = ref(false)
const notifSaveSuccess = ref(false)
const notifSaveError = ref('')

function buildDefaultNotifPrefs(): EditableNotifPref[] {
  return ALL_NOTIFICATION_EVENTS.map((evt) => ({
    event_type: evt,
    notify_trusted_persons: true,
    channel_in_app: true,
    channel_email: false,
    channel_sms: false,
  }))
}

async function loadNotifPrefs() {
  notifLoading.value = true
  try {
    const saved = await getNotificationPreferences()
    if (saved.length === 0) {
      notifPrefs.value = buildDefaultNotifPrefs()
    } else {
      notifPrefs.value = ALL_NOTIFICATION_EVENTS.map((evt) => {
        const found = saved.find((p) => p.event_type === evt)
        return found
          ? {
              event_type: evt,
              notify_trusted_persons: found.notify_trusted_persons,
              channel_in_app: found.channel_in_app,
              channel_email: found.channel_email,
              channel_sms: found.channel_sms,
            }
          : {
              event_type: evt,
              notify_trusted_persons: true,
              channel_in_app: true,
              channel_email: false,
              channel_sms: false,
            }
      })
    }
  } catch {
    notifPrefs.value = buildDefaultNotifPrefs()
  } finally {
    notifLoading.value = false
  }
}

async function handleNotifSave() {
  notifSaving.value = true
  notifSaveSuccess.value = false
  notifSaveError.value = ''
  try {
    await saveNotificationPreferences(notifPrefs.value)
    notifSaveSuccess.value = true
    setTimeout(() => (notifSaveSuccess.value = false), 5000)
  } catch {
    notifSaveError.value = 'Speichern fehlgeschlagen. Bitte versuchen Sie es erneut.'
  } finally {
    notifSaving.value = false
  }
}

const wheelchairTypeOptions = [
  { value: 'manual' as WheelchairType, label: 'Manueller Rollstuhl' },
  { value: 'electric' as WheelchairType, label: 'Elektrorollstuhl' },
  { value: 'unknown' as WheelchairType, label: 'Ich weiß es nicht genau' },
]

const tristateOptions: Array<{ value: boolean | null; label: string }> = [
  { value: true, label: 'Ja' },
  { value: false, label: 'Nein' },
  { value: null, label: 'Unbekannt' },
]

const MEDICAL_DETAIL_OPTIONS: Array<{ key: MedDetailKey; label: string; icon: string; description: string }> = [
  { key: 'requires_transport_chair',          label: 'Tragestuhl erforderlich',         icon: 'pi-arrow-circle-up',    description: 'Ich benötige einen Tragestuhl für Zugänge ohne Aufzug.' },
  { key: 'requires_two_person_assistance',    label: 'Zweimann-Begleitung',             icon: 'pi-users',              description: 'Für Transfer oder Transport sind zwei Personen erforderlich.' },
  { key: 'requires_medical_transport',        label: 'Qual. Krankentransport',          icon: 'pi-shield',             description: 'Ich benötige qualifizierten Krankentransport (KTP) mit geschultem Personal.' },
  { key: 'brings_oxygen',                     label: 'Eigenes Sauerstoffgerät',         icon: 'pi-circle',             description: 'Ich bringe ein mobiles Sauerstoffgerät mit.' },
  { key: 'requires_oxygen_mount',             label: 'Sauerstoffhalterung benötigt',    icon: 'pi-sort-amount-up-alt', description: 'Das Fahrzeug muss eine Halterung für Sauerstoffgeräte haben.' },
  { key: 'brings_medical_device',             label: 'Eigenes Medizingerät',            icon: 'pi-inbox',              description: 'Ich transportiere ein medizinisches Gerät (Pumpe, Monitor o. ä.).' },
  { key: 'requires_medical_equipment_storage',label: 'Med. Stauraum benötigt',          icon: 'pi-inbox',              description: 'Das Fahrzeug muss Stauraum für medizinisches Equipment bieten.' },
  { key: 'requires_infusion_mount',           label: 'Infusionsständer benötigt',       icon: 'pi-sort-amount-up-alt', description: 'Während der Fahrt läuft eine Infusion — Halterung erforderlich.' },
  { key: 'requires_special_positioning',      label: 'Spezielle Lagerung',             icon: 'pi-minus',              description: 'Ich benötige eine besondere Lagerungsposition während der Fahrt.' },
  { key: 'infection_or_hygiene_note',         label: 'Hygiene- / Infektionshinweis',   icon: 'pi-shield',             description: 'Es liegt ein Hygiene- oder Infektionsschutzhinweis vor.' },
  { key: 'requires_medical_attendant',        label: 'Med. Begleitung erforderlich',   icon: 'pi-heart',              description: 'Eine medizinisch qualifizierte Begleitperson ist notwendig.' },
]

const ATTENDANT_TYPE_OPTIONS = [
  { value: 'none' as AttendantType, label: 'Keine medizinische Begleitung' },
  { value: 'escort_person' as AttendantType, label: 'Begleitperson (keine med. Qualifikation)' },
  { value: 'second_assistant' as AttendantType, label: 'Zweite Hilfsperson (z. B. für Transfer)' },
  { value: 'paramedic' as AttendantType, label: 'Rettungssanitäter / -helfer' },
  { value: 'medical_professional' as AttendantType, label: 'Pflegefachkraft / Arzt' },
  { value: 'unknown' as AttendantType, label: 'Unbekannt / bitte klären' },
]

// ── Kontakte (Sprint 12E) ──────────────────────────────────────────────────────

const contacts = ref<PassengerContact[]>([])
const contactsLoading = ref(false)
const contactsError = ref('')
const showContactForm = ref(false)
const contactFormSaving = ref(false)
const contactFormError = ref('')
const editingContactId = ref<string | null>(null)

const CONTACT_TYPE_OPTIONS: Array<{ value: ContactType; label: string }> = [
  { value: 'emergency_contact', label: 'Notfallkontakt' },
  { value: 'parent',            label: 'Elternteil / Familie' },
  { value: 'trusted_person',    label: 'Vertrauensperson' },
  { value: 'caregiver',         label: 'Pflegeperson' },
  { value: 'doctor',            label: 'Arzt / Therapeut' },
  { value: 'nursing_service',   label: 'Pflegedienst' },
  { value: 'school',            label: 'Schule' },
  { value: 'workshop',          label: 'Werkstatt / Beschäftigung' },
  { value: 'daycare',           label: 'Tagesstätte' },
  { value: 'other',             label: 'Sonstige' },
]

const GENDER_OPTIONS = [
  { value: 'weiblich',    label: 'Weiblich' },
  { value: 'männlich',    label: 'Männlich' },
  { value: 'divers',      label: 'Divers' },
  { value: 'keine Angabe', label: 'Keine Angabe' },
]

const contactForm = reactive<PassengerContactCreate>({
  name: '',
  phone_number: '',
  role_label: null,
  contact_type: 'other',
  note: null,
  is_emergency_contact: false,
  visible_to_driver: false,
  visible_in_emergency: false,
  callable_in_emergency: false,
  priority: 1,
})

function resetContactForm() {
  contactForm.name = ''
  contactForm.phone_number = ''
  contactForm.role_label = null
  contactForm.contact_type = 'other'
  contactForm.note = null
  contactForm.is_emergency_contact = false
  contactForm.visible_to_driver = false
  contactForm.visible_in_emergency = false
  contactForm.callable_in_emergency = false
  contactForm.priority = 1
  editingContactId.value = null
  contactFormError.value = ''
}

function openAddContact() {
  resetContactForm()
  showContactForm.value = true
}

function openEditContact(c: PassengerContact) {
  contactForm.name = c.name
  contactForm.phone_number = c.phone_number ?? ''
  contactForm.role_label = c.role_label
  contactForm.contact_type = c.contact_type
  contactForm.note = c.note
  contactForm.is_emergency_contact = c.is_emergency_contact
  contactForm.visible_to_driver = c.visible_to_driver
  contactForm.visible_in_emergency = c.visible_in_emergency
  contactForm.callable_in_emergency = c.callable_in_emergency
  contactForm.priority = c.priority
  editingContactId.value = c.id
  showContactForm.value = true
}

async function loadContacts() {
  contactsLoading.value = true
  contactsError.value = ''
  try {
    contacts.value = await listContacts()
  } catch {
    contactsError.value = 'Kontakte konnten nicht geladen werden.'
  } finally {
    contactsLoading.value = false
  }
}

async function handleContactSave() {
  if (!contactForm.name.trim() || !contactForm.phone_number.trim()) {
    contactFormError.value = 'Bitte Name und Telefonnummer eintragen.'
    return
  }
  contactFormSaving.value = true
  contactFormError.value = ''
  try {
    if (editingContactId.value) {
      await updateContact(editingContactId.value, { ...contactForm })
    } else {
      await createContact({ ...contactForm })
    }
    showContactForm.value = false
    resetContactForm()
    await loadContacts()
  } catch {
    contactFormError.value = 'Speichern fehlgeschlagen. Bitte versuchen Sie es erneut.'
  } finally {
    contactFormSaving.value = false
  }
}

async function handleContactDelete(id: string) {
  try {
    await deleteContact(id)
    await loadContacts()
  } catch {
    contactsError.value = 'Löschen fehlgeschlagen.'
  }
}

// Lokales Formular-State — wird beim Laden aus dem Store befüllt
const form = reactive<Partial<MobilityProfile>>({
  emergency_contact_name: null,
  emergency_contact_phone: null,
  uses_wheelchair: false,
  wheelchair_type: null,
  uses_rollator: false,
  uses_crutches: false,
  is_blind_or_visually_impaired: false,
  is_deaf_or_hard_of_hearing: false,
  needs_escort: false,
  needs_entry_assistance: false,
  needs_door_to_door_assistance: false,
  needs_ramp: false,
  needs_lift: false,
  needs_stretcher_transport: false,
  can_transfer_to_seat: null,
  has_own_wheelchair: null,
  requires_wheelchair_space: false,
  requires_extra_time: false,
  requires_transport_chair: false,
  requires_two_person_assistance: false,
  requires_medical_transport: false,
  brings_oxygen: false,
  requires_oxygen_mount: false,
  brings_medical_device: false,
  requires_medical_equipment_storage: false,
  requires_infusion_mount: false,
  requires_special_positioning: false,
  infection_or_hygiene_note: false,
  requires_medical_attendant: false,
  attendant_type_required: 'none',
  medical_device_notes: null,
  medical_transport_notes: null,
  communication_notes: null,
  medical_notes: null,
  general_notes: null,
  // Sprint 12E
  has_epilepsy: false,
  is_mute: false,
  other_disabilities_notes: null,
  known_conditions: null,
  medication_notes: null,
  allergy_notes: null,
  emergency_care_notes: null,
  what_helps_notes: null,
  what_to_avoid_notes: null,
  additional_emergency_notes: null,
  body_height_cm: null,
  body_weight_kg: null,
  gender: null,
  show_disabilities_to_driver: false,
  show_disabilities_in_emergency: false,
  show_medication_to_driver: false,
  show_medication_in_emergency: false,
  show_emergency_notes_to_driver: false,
  show_emergency_notes_in_emergency: false,
  show_communication_notes_to_driver: false,
  show_communication_notes_in_emergency: false,
  show_body_data_in_emergency: false,
  show_contacts_to_driver: false,
  show_contacts_in_emergency: false,
})

function syncFormFromStore() {
  const p = store.profile
  if (!p) return
  Object.assign(form, {
    emergency_contact_name: p.emergency_contact_name,
    emergency_contact_phone: p.emergency_contact_phone,
    uses_wheelchair: p.uses_wheelchair,
    wheelchair_type: p.wheelchair_type,
    uses_rollator: p.uses_rollator,
    uses_crutches: p.uses_crutches,
    is_blind_or_visually_impaired: p.is_blind_or_visually_impaired,
    is_deaf_or_hard_of_hearing: p.is_deaf_or_hard_of_hearing,
    needs_escort: p.needs_escort,
    needs_entry_assistance: p.needs_entry_assistance,
    needs_door_to_door_assistance: p.needs_door_to_door_assistance,
    needs_ramp: p.needs_ramp,
    needs_lift: p.needs_lift,
    needs_stretcher_transport: p.needs_stretcher_transport,
    can_transfer_to_seat: p.can_transfer_to_seat,
    has_own_wheelchair: p.has_own_wheelchair,
    requires_wheelchair_space: p.requires_wheelchair_space,
    requires_extra_time: p.requires_extra_time,
    requires_transport_chair: p.requires_transport_chair,
    requires_two_person_assistance: p.requires_two_person_assistance,
    requires_medical_transport: p.requires_medical_transport,
    brings_oxygen: p.brings_oxygen,
    requires_oxygen_mount: p.requires_oxygen_mount,
    brings_medical_device: p.brings_medical_device,
    requires_medical_equipment_storage: p.requires_medical_equipment_storage,
    requires_infusion_mount: p.requires_infusion_mount,
    requires_special_positioning: p.requires_special_positioning,
    infection_or_hygiene_note: p.infection_or_hygiene_note,
    requires_medical_attendant: p.requires_medical_attendant,
    attendant_type_required: p.attendant_type_required ?? 'none',
    medical_device_notes: p.medical_device_notes,
    medical_transport_notes: p.medical_transport_notes,
    communication_notes: p.communication_notes,
    medical_notes: p.medical_notes,
    general_notes: p.general_notes,
    // Sprint 12E
    has_epilepsy: p.has_epilepsy ?? false,
    is_mute: p.is_mute ?? false,
    other_disabilities_notes: p.other_disabilities_notes ?? null,
    known_conditions: p.known_conditions ?? null,
    medication_notes: p.medication_notes ?? null,
    allergy_notes: p.allergy_notes ?? null,
    emergency_care_notes: p.emergency_care_notes ?? null,
    what_helps_notes: p.what_helps_notes ?? null,
    what_to_avoid_notes: p.what_to_avoid_notes ?? null,
    additional_emergency_notes: p.additional_emergency_notes ?? null,
    body_height_cm: p.body_height_cm ?? null,
    body_weight_kg: p.body_weight_kg ?? null,
    gender: p.gender ?? null,
    show_disabilities_to_driver: p.show_disabilities_to_driver ?? false,
    show_disabilities_in_emergency: p.show_disabilities_in_emergency ?? false,
    show_medication_to_driver: p.show_medication_to_driver ?? false,
    show_medication_in_emergency: p.show_medication_in_emergency ?? false,
    show_emergency_notes_to_driver: p.show_emergency_notes_to_driver ?? false,
    show_emergency_notes_in_emergency: p.show_emergency_notes_in_emergency ?? false,
    show_communication_notes_to_driver: p.show_communication_notes_to_driver ?? false,
    show_communication_notes_in_emergency: p.show_communication_notes_in_emergency ?? false,
    show_body_data_in_emergency: p.show_body_data_in_emergency ?? false,
    show_contacts_to_driver: p.show_contacts_to_driver ?? false,
    show_contacts_in_emergency: p.show_contacts_in_emergency ?? false,
  })
}

// Wenn Rollstuhl deaktiviert wird, Rollstuhl-Typ zurücksetzen
watch(
  () => form.uses_wheelchair,
  (val) => {
    if (!val) form.wheelchair_type = null
  },
)

// Wenn medizinische Begleitung deaktiviert wird, Typ zurücksetzen
watch(
  () => form.requires_medical_attendant,
  (val) => {
    if (!val) form.attendant_type_required = 'none'
  },
)

function toggleNeed(key: NeedKey) {
  ;(form[key] as boolean) = !(form[key] as boolean)
}

function toggleMedDetail(key: MedDetailKey) {
  ;(form[key] as boolean) = !(form[key] as boolean)
}

// All boolean form fields that presets may set — reset before every preset change.
const PRESET_RESET: Partial<MobilityProfile> = {
  needs_stretcher_transport: false,
  requires_transport_chair: false,
  requires_two_person_assistance: false,
  requires_medical_transport: false,
  brings_oxygen: false,
  requires_oxygen_mount: false,
  brings_medical_device: false,
  requires_medical_equipment_storage: false,
  requires_infusion_mount: false,
  requires_special_positioning: false,
  infection_or_hygiene_note: false,
  requires_medical_attendant: false,
  attendant_type_required: 'none' as AttendantType,
}

function applyTransportType(tt: TransportType) {
  if (selectedTransportType.value === tt.id) {
    Object.assign(form, PRESET_RESET)
    selectedTransportType.value = null
    return
  }
  // Reset: use backend's controlled-field list; fall back to local PRESET_RESET keys.
  const boolFieldsToReset = tt.preset_controlled_profile_fields.length > 0
    ? tt.preset_controlled_profile_fields
    : (Object.keys(PRESET_RESET) as string[]).filter(k => k !== 'attendant_type_required')
  const resetPatch: Record<string, unknown> = { attendant_type_required: 'none' as AttendantType }
  for (const f of boolFieldsToReset) {
    if (f in form) resetPatch[f] = false
  }
  // Preset: suggested boolean fields → true, then non-boolean value overrides.
  const presetPatch: Record<string, unknown> = {}
  for (const f of tt.suggested_profile_fields) {
    if (f in form) presetPatch[f] = true
  }
  if (tt.suggested_field_values) {
    for (const [k, v] of Object.entries(tt.suggested_field_values)) {
      if (k in form) presetPatch[k] = v
    }
  }
  Object.assign(form, resetPatch, presetPatch)
  selectedTransportType.value = tt.id
}

async function handleSave() {
  saveSuccess.value = false
  saveError.value = ''
  try {
    await store.save({ ...form })
    saveSuccess.value = true
    toast.add({
      severity: 'success',
      summary: 'Gespeichert',
      detail: 'Ihr Mobilitätsprofil wurde erfolgreich gespeichert.',
      life: 4000,
    })
    // Erfolgsmeldung nach 6 Sek. ausblenden
    setTimeout(() => (saveSuccess.value = false), 6000)
  } catch {
    saveError.value =
      'Das Speichern ist fehlgeschlagen. Bitte prüfen Sie Ihre Verbindung und versuchen Sie es erneut.'
  }
}

onMounted(async () => {
  const [, typesResult] = await Promise.allSettled([
    store.profile ? Promise.resolve() : store.load(),
    getTransportOptions(),
  ])
  TRANSPORT_TYPES.value = typesResult.status === 'fulfilled' ? typesResult.value : []
  syncFormFromStore()
  await loadNotifPrefs()
  await loadContacts()
})

// Store-Profil-Änderungen ins Formular übernehmen (z. B. nach erstem Load)
watch(() => store.profile, syncFormFromStore)
</script>

<style scoped>
.mp-page {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
  max-width: 820px;
}

/* Header */
.mp-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--am-space-m);
}

.mp-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.mp-subtitle {
  font-size: 0.875rem;
  color: var(--am-text-secondary);
  margin: 4px 0 0;
  line-height: 1.5;
}

/* Loading */
.mp-loading {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  color: var(--am-text-secondary);
  font-size: 0.9rem;
  padding: var(--am-space-xl);
  justify-content: center;
}

/* Notice */
.mp-notice {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  background: var(--am-accent-bg);
  border: 1px solid rgba(255, 214, 0, 0.3);
  border-radius: var(--am-radius-s);
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  line-height: 1.5;
}

.mp-notice .pi {
  color: var(--am-accent);
  flex-shrink: 0;
  margin-top: 2px;
}

/* Alerts */
.mp-alert {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-s);
  padding: var(--am-space-s) var(--am-space-m);
  border-radius: var(--am-radius-s);
  font-size: 0.875rem;
  line-height: 1.5;
}

.mp-alert--success {
  background: var(--am-success-bg);
  border: 1px solid var(--am-success);
  color: var(--am-success);
}

.mp-alert--error {
  background: var(--am-danger-bg);
  border: 1px solid var(--am-danger);
  color: var(--am-danger);
}

/* Form */
.mp-form {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-l);
}

/* Section */
.mp-section {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.mp-section-title {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 1rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.mp-section-title .pi {
  color: var(--am-accent);
  font-size: 1rem;
}

.mp-section-desc {
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* Fields */
.mp-field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--am-space-m);
}

@media (max-width: 600px) {
  .mp-field-row {
    grid-template-columns: 1fr;
  }
}

.mp-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mp-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
}

.mp-field-hint {
  font-size: 0.78rem;
  color: var(--am-text-secondary);
  margin: 0;
  line-height: 1.4;
}

.mp-optional-badge {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 99px;
  background: var(--am-bg-raised);
  color: var(--am-text-secondary);
  border: 1px solid var(--am-border);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.mp-input {
  height: 44px;
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.9rem;
  padding: 0 var(--am-space-m);
  outline: none;
  transition: border-color var(--am-transition);
  box-sizing: border-box;
  width: 100%;
}

.mp-input:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

.mp-textarea {
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border-strong);
  border-radius: var(--am-radius-s);
  color: var(--am-text-primary);
  font-size: 0.9rem;
  padding: var(--am-space-s) var(--am-space-m);
  outline: none;
  resize: vertical;
  transition: border-color var(--am-transition);
  width: 100%;
  min-height: 80px;
  box-sizing: border-box;
  font-family: inherit;
}

.mp-textarea:focus {
  border-color: var(--am-accent);
  box-shadow: 0 0 0 3px rgba(255, 214, 0, 0.18);
}

/* Need cards grid */
.mp-need-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--am-space-s);
}

@media (max-width: 520px) {
  .mp-need-grid {
    grid-template-columns: 1fr;
  }
}

.mp-need-card {
  display: flex;
  align-items: flex-start;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 2px solid var(--am-border);
  border-radius: var(--am-radius-m);
  cursor: pointer;
  text-align: left;
  transition: border-color var(--am-transition), background var(--am-transition);
  min-height: 80px;
  position: relative;
}

.mp-need-card:hover {
  border-color: var(--am-border-strong);
  background: var(--am-bg-surface);
}

.mp-need-card--active {
  border-color: var(--am-accent);
  background: var(--am-accent-bg);
}

.mp-need-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--am-radius-s);
  background: var(--am-bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--am-text-secondary);
  font-size: 1.1rem;
  transition: color var(--am-transition), background var(--am-transition);
}

.mp-need-card--active .mp-need-icon {
  background: var(--am-accent);
  color: var(--am-text-on-accent);
}

.mp-need-text {
  flex: 1;
  min-width: 0;
}

.mp-need-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin-bottom: 2px;
}

.mp-need-desc {
  display: block;
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  line-height: 1.4;
}

.mp-need-check {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--am-border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: transparent;
  font-size: 0.65rem;
  transition: all var(--am-transition);
}

.mp-need-card--active .mp-need-check {
  background: var(--am-accent);
  border-color: var(--am-accent);
  color: var(--am-text-on-accent);
}

/* Wheelchair type radio */
.mp-wheelchair-type {
  background: var(--am-bg-base);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  padding: var(--am-space-m);
}

.mp-radio-group {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
  margin-top: var(--am-space-s);
}

.mp-radio-label {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.875rem;
  color: var(--am-text-primary);
  cursor: pointer;
  min-height: 36px;
}

.mp-radio {
  width: 18px;
  height: 18px;
  accent-color: var(--am-accent);
  cursor: pointer;
  flex-shrink: 0;
}

/* Toggle list */
.mp-toggle-list {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
}

.mp-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  cursor: pointer;
  min-height: 64px;
}

.mp-toggle-label {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--am-text-primary);
  flex: 1;
}

.mp-toggle-sub {
  font-size: 0.78rem;
  font-weight: 400;
  color: var(--am-text-secondary);
}

.mp-toggle-btn {
  position: relative;
  width: 44px;
  height: 24px;
  border-radius: 99px;
  background: var(--am-border-strong);
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  transition: background var(--am-transition);
  padding: 0;
}

.mp-toggle-btn--on {
  background: var(--am-accent);
}

.mp-toggle-knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  transition: transform var(--am-transition);
  display: block;
}

.mp-toggle-btn--on .mp-toggle-knob {
  transform: translateX(20px);
}

/* Tristate */
.mp-tristate-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  min-height: 64px;
  flex-wrap: wrap;
}

.mp-tristate-btns {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.mp-tristate-btn {
  padding: 6px 14px;
  border-radius: var(--am-radius-s);
  border: 1px solid var(--am-border-strong);
  background: var(--am-bg-base);
  color: var(--am-text-secondary);
  font-size: 0.82rem;
  cursor: pointer;
  transition: all var(--am-transition);
  min-height: 36px;
  min-width: 60px;
}

.mp-tristate-btn:hover {
  border-color: var(--am-accent);
  color: var(--am-text-primary);
}

.mp-tristate-btn--active {
  background: var(--am-accent);
  border-color: var(--am-accent);
  color: var(--am-text-on-accent);
  font-weight: 700;
}

/* Save bar */
.mp-save-bar {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  flex-wrap: wrap;
  padding: var(--am-space-m) 0;
}

.mp-save-btn {
  min-height: 48px;
  font-size: 0.95rem;
  padding: 0 var(--am-space-xl);
}

.mp-save-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.mp-save-hint {
  font-size: 0.78rem;
  color: var(--am-text-secondary);
}

/* Transport-type Schnellauswahl */
.mp-transport-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--am-space-s);
}

.mp-transport-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 2px solid var(--am-border);
  border-radius: var(--am-radius-m);
  cursor: pointer;
  text-align: left;
  transition: border-color var(--am-transition), background var(--am-transition);
  min-height: 90px;
}

.mp-transport-card:hover {
  border-color: var(--am-border-strong);
}

.mp-transport-card--active {
  border-color: var(--am-accent);
  background: var(--am-accent-bg);
}

.mp-transport-label {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--am-text-primary);
}

.mp-transport-desc {
  font-size: 0.75rem;
  color: var(--am-text-secondary);
  line-height: 1.4;
}

.mp-transport-warning {
  font-size: 0.7rem;
  color: var(--am-danger);
  display: flex;
  align-items: flex-start;
  gap: 4px;
  margin-top: 4px;
  line-height: 1.3;
}

.mp-transport-hint {
  font-size: 0.82rem;
  color: var(--am-text-secondary);
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  flex-wrap: wrap;
  margin: 0;
}

.mp-link-btn {
  background: none;
  border: none;
  color: var(--am-accent);
  font-size: 0.82rem;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  font-weight: 600;
}

/* ── Guided Check CTA ─────────────────────────────────────────────────── */
.mp-assistant-cta {
  display: flex;
  align-items: center;
  gap: var(--am-space-l);
  flex-wrap: wrap;
}

.mp-assistant-cta-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--am-radius-m);
  background: color-mix(in srgb, var(--am-accent) 15%, var(--am-bg-raised));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.4rem;
  color: var(--am-accent);
}

.mp-assistant-cta-text {
  flex: 1;
  min-width: 200px;
}

.mp-assistant-cta-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0 0 4px;
}

.mp-assistant-cta-desc {
  font-size: 0.85rem;
  color: var(--am-text-secondary);
  margin: 0;
}

.mp-assistant-cta-btn {
  text-decoration: none;
  min-height: 44px;
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  white-space: nowrap;
  flex-shrink: 0;
}

/* ── Benachrichtigungseinstellungen ──────────────────────────────────────── */
.notif-table {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
  overflow-x: auto;
}

.notif-row {
  display: grid;
  grid-template-columns: 1fr 100px 80px 80px 80px;
  align-items: center;
  gap: var(--am-space-s);
  padding: 8px var(--am-space-s);
  border-radius: var(--am-radius-s);
}

.notif-row:nth-child(even) {
  background: var(--am-bg-raised);
}

.notif-row--head {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--am-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--am-border);
  padding-bottom: var(--am-space-s);
}

.notif-cell--event {
  font-size: 0.875rem;
  color: var(--am-text-primary);
}

.notif-cell--chan {
  display: flex;
  align-items: center;
  justify-content: center;
}

.notif-check {
  width: 18px;
  height: 18px;
  accent-color: var(--am-accent);
  cursor: pointer;
}

@media (max-width: 540px) {
  .notif-row {
    grid-template-columns: 1fr 72px 60px 60px 60px;
    font-size: 0.8rem;
  }
}

/* ── Sprint 12E: Kontaktverwaltung ──────────────────────────────────── */
.contact-list {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-s);
}

.contact-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
  flex-wrap: wrap;
}

.contact-item-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
  min-width: 0;
}

.contact-item-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--am-text-primary);
}

.contact-item-role,
.contact-item-type {
  font-size: 0.78rem;
  color: var(--am-text-secondary);
}

.contact-item-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.contact-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 1px 8px;
  border-radius: 99px;
  border: 1px solid var(--am-border);
  background: var(--am-bg-card);
  color: var(--am-text-secondary);
}

.contact-badge--emergency {
  background: rgba(220, 38, 38, 0.1);
  border-color: var(--am-danger, #dc2626);
  color: var(--am-danger, #dc2626);
}

.contact-badge--driver {
  background: rgba(255, 214, 0, 0.1);
  border-color: var(--am-accent);
  color: var(--am-accent);
}

.contact-badge--emerg {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
  color: #3b82f6;
}

.contact-item-actions {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  flex-wrap: wrap;
  flex-shrink: 0;
}

.contact-phone-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--am-success, #16a34a);
  text-decoration: none;
  border: 1px solid currentColor;
  padding: 4px 10px;
  border-radius: var(--am-radius-s);
  background: rgba(34, 197, 94, 0.07);
  white-space: nowrap;
}

.contact-no-phone {
  font-size: 0.78rem;
  color: var(--am-text-secondary);
  font-style: italic;
}

.contact-action-btn {
  width: 36px;
  height: 36px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.contact-action-btn--delete {
  background: transparent;
  border: 1px solid var(--am-danger, #dc2626);
  color: var(--am-danger, #dc2626);
  border-radius: var(--am-radius-s);
  cursor: pointer;
  transition: background var(--am-transition);
}

.contact-action-btn--delete:hover {
  background: rgba(220, 38, 38, 0.1);
}

.contact-add-btn {
  align-self: flex-start;
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
}

.contact-form {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-base);
  border: 1px solid var(--am-accent);
  border-radius: var(--am-radius-m);
}

.contact-form-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.contact-flags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--am-space-m);
}

.contact-flag {
  display: flex;
  align-items: center;
  gap: var(--am-space-s);
  font-size: 0.875rem;
  color: var(--am-text-primary);
  cursor: pointer;
}

.contact-flag-check {
  width: 18px;
  height: 18px;
  accent-color: var(--am-accent);
  cursor: pointer;
  flex-shrink: 0;
}

.contact-form-actions {
  display: flex;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

/* ── Sprint 12E: Notfallinformationen ───────────────────────────────── */
.efinfo-block {
  display: flex;
  flex-direction: column;
  gap: var(--am-space-m);
  padding: var(--am-space-m);
  background: var(--am-bg-raised);
  border: 1px solid var(--am-border);
  border-radius: var(--am-radius-s);
}

.efinfo-block-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--am-space-m);
  flex-wrap: wrap;
}

.efinfo-block-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--am-text-primary);
  margin: 0;
}

.efinfo-vis-row {
  display: flex;
  align-items: center;
  gap: var(--am-space-m);
  flex-wrap: wrap;
  flex-shrink: 0;
}

.efinfo-vis-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  color: var(--am-text-secondary);
  cursor: pointer;
  white-space: nowrap;
}

.mp-select {
  appearance: none;
  cursor: pointer;
}
</style>
