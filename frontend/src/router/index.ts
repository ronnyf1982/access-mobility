import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PublicLayout from '@/layouts/PublicLayout.vue'
import PortalLayout from '@/layouts/PortalLayout.vue'
import LandingView from '@/views/LandingView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import GateView from '@/views/GateView.vue'
import OnboardingView from '@/views/OnboardingView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'
import MobilityProfileView from '@/views/MobilityProfileView.vue'
import MobilityAssistantView from '@/views/MobilityAssistantView.vue'
import VehiclesView from '@/views/VehiclesView.vue'
import DriversView from '@/views/DriversView.vue'
import TransportRequestView from '@/views/TransportRequestView.vue'
import DriverDashboardView from '@/views/DriverDashboardView.vue'
import PlatformAdminUsersView from '@/views/platform_admin/PlatformAdminUsersView.vue'
import PlatformAdminTestAccessView from '@/views/platform_admin/PlatformAdminTestAccessView.vue'
import ImpressumView from '@/views/ImpressumView.vue'
import DatenschutzView from '@/views/DatenschutzView.vue'
import SpontaneousRideView from '@/views/SpontaneousRideView.vue'

const ONBOARDING_BYPASS = new Set(['/onboarding', '/login', '/'])

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // ── Schutzseite (immer erreichbar) ──────────────────
    {
      path: '/gate',
      name: 'gate',
      component: GateView,
      meta: { public: true },
    },
    // ── Öffentliche Website (nur nach Gate-Freigabe) ────
    {
      path: '/',
      component: PublicLayout,
      meta: { requiresPreviewAccess: true },
      children: [
        { path: '', name: 'home', component: LandingView },
      ],
    },
    // ── App-Login (unverändert) ──────────────────────────
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true },
    },
    // ── Rechtliches ─────────────────────────────────────
    {
      path: '/impressum',
      name: 'impressum',
      component: ImpressumView,
      meta: { gateExempt: true },
    },
    {
      path: '/datenschutz',
      name: 'datenschutz',
      component: DatenschutzView,
      meta: { gateExempt: true },
    },
    // ── Onboarding ──────────────────────────────────────
    {
      path: '/onboarding',
      name: 'onboarding',
      component: OnboardingView,
      meta: { requiresAuth: true },
    },
    // ── Portal (eingeloggt) ─────────────────────────────
    {
      path: '/dashboard',
      component: PortalLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: DashboardView },
        { path: '/mobility-profile', name: 'mobility-profile', component: MobilityProfileView },
        { path: '/mobility-profile/assistant', name: 'mobility-profile-assistant', component: MobilityAssistantView },
        { path: '/vehicles', name: 'vehicles', component: VehiclesView },
        { path: '/drivers', name: 'drivers', component: DriversView },
        { path: '/transport-requests', name: 'transport-requests', component: TransportRequestView },
        { path: '/spontaneous-ride', name: 'spontaneous-ride', component: SpontaneousRideView },
        { path: '/driver', name: 'driver-dashboard', component: DriverDashboardView },
      ],
    },
    // ── Platform-Admin ──────────────────────────────────
    {
      path: '/platform-admin',
      component: PortalLayout,
      meta: { requiresAuth: true, requiresPlatformAdmin: true },
      children: [
        {
          path: 'users',
          name: 'platform-admin-users',
          component: PlatformAdminUsersView,
        },
        {
          path: 'test-access',
          name: 'platform-admin-test-access',
          component: PlatformAdminTestAccessView,
        },
      ],
    },
    // ── Catch-all ───────────────────────────────────────
    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()
  const unlocked = !!sessionStorage.getItem('fahrando_preview_unlocked')

  // /gate selbst: immer erreichbar; bei bereits freigeschaltetem Gate zum Ziel weiterleiten
  if (to.path === '/gate') {
    if (unlocked) {
      const raw = to.query.redirect as string | undefined
      const target = raw && raw.startsWith('/') && !raw.startsWith('//') ? raw : '/'
      return next(target)
    }
    return next()
  }

  // Impressum & Datenschutz: immer frei, kein Gate erforderlich
  if (to.matched.some(r => r.meta.gateExempt)) {
    return next()
  }

  // Alles andere: Gate-Freischaltung erforderlich (Variante B)
  if (!unlocked) {
    return next({ path: '/gate', query: { redirect: to.fullPath } })
  }

  // ── Gate freigeschaltet — normale App-Auth-Logik ────────────

  // /login: eingeloggte Nutzer direkt zum Dashboard
  if (to.path === '/login') {
    return auth.isAuthenticated ? next('/dashboard') : next()
  }

  // Routen ohne App-Auth-Pflicht (/, öffentliche Website-Seiten)
  if (!to.matched.some(r => r.meta.requiresAuth)) {
    return next()
  }

  // App-Auth-Prüfung für geschützte Routen
  if (!auth.isAuthenticated) {
    return next('/login')
  }

  if (!auth.user) {
    try {
      await auth.loadUser()
    } catch {
      auth.logout()
      return next('/login')
    }
  }

  // Onboarding-Weiterleitung
  if (auth.user?.needs_onboarding && !ONBOARDING_BYPASS.has(to.path)) {
    return next('/onboarding')
  }

  // Platform-Admin-Guard
  if (to.meta.requiresPlatformAdmin && auth.user?.role !== 'platform_admin') {
    return next('/dashboard')
  }

  next()
})

export default router
