import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PortalLayout from '@/layouts/PortalLayout.vue'
import LandingView from '@/views/LandingView.vue'
import OnboardingView from '@/views/OnboardingView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'
import MobilityProfileView from '@/views/MobilityProfileView.vue'
import MobilityAssistantView from '@/views/MobilityAssistantView.vue'
import VehiclesView from '@/views/VehiclesView.vue'
import DriversView from '@/views/DriversView.vue'
import TransportRequestView from '@/views/TransportRequestView.vue'
import DriverDashboardView from '@/views/DriverDashboardView.vue'
import PlatformAdminUsersView from '@/views/platform_admin/PlatformAdminUsersView.vue'
import ImpressumView from '@/views/ImpressumView.vue'
import DatenschutzView from '@/views/DatenschutzView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Coming-Soon / Login — standalone, keine PublicLayout
    {
      path: '/',
      name: 'home',
      component: LandingView,
      meta: { public: true },
    },
    // /login → Weiterleitung zu /
    {
      path: '/login',
      redirect: '/',
    },
    // Rechtliches
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
    // Onboarding
    {
      path: '/onboarding',
      name: 'onboarding',
      component: OnboardingView,
      meta: { requiresAuth: true },
    },
    // Portal (eingeloggt)
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
    // Platform-Admin
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
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

const ONBOARDING_BYPASS = new Set(['/onboarding', '/', '/impressum', '/datenschutz'])

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()

  // Öffentliche Routen
  if (to.meta.public) {
    return next()
  }

  // Auth-Prüfung
  if (!auth.isAuthenticated) {
    return next('/')
  }

  if (!auth.user) {
    try {
      await auth.loadUser()
    } catch {
      auth.logout()
      return next('/')
    }
  }

  // Onboarding-Weiterleitung
  if (auth.user?.needs_onboarding && !ONBOARDING_BYPASS.has(to.path)) {
    return next('/onboarding')
  }

  // Platform-Admin-Guard: 403 → /dashboard
  if (to.meta.requiresPlatformAdmin && auth.user?.role !== 'platform_admin') {
    return next('/dashboard')
  }

  next()
})

export default router
