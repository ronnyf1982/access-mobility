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
      meta: { public: true },
    },
    {
      path: '/datenschutz',
      name: 'datenschutz',
      component: DatenschutzView,
      meta: { public: true },
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
  const unlocked = !!sessionStorage.getItem('fahrando_unlocked')

  // Gate-Guard: / und seine Kinder erfordern Gate-Freigabe
  if (to.path === '/' && !unlocked) {
    return next('/gate')
  }

  // Bereits freigeschaltet: /gate → /
  if (to.path === '/gate' && unlocked) {
    return next('/')
  }

  // Öffentliche Routen (inkl. /gate, /login, /impressum, /datenschutz)
  if (to.meta.public || to.path === '/') {
    if (to.path === '/login' && auth.isAuthenticated) {
      return next('/dashboard')
    }
    return next()
  }

  // Auth-Prüfung für geschützte Routen
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
