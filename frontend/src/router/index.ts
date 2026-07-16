import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PublicLayout from '@/layouts/PublicLayout.vue'
import PortalLayout from '@/layouts/PortalLayout.vue'
import LandingView from '@/views/LandingView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import OnboardingView from '@/views/OnboardingView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'
import MobilityProfileView from '@/views/MobilityProfileView.vue'
import MobilityAssistantView from '@/views/MobilityAssistantView.vue'
import VehiclesView from '@/views/VehiclesView.vue'
import DriversView from '@/views/DriversView.vue'
import TransportRequestView from '@/views/TransportRequestView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: PublicLayout,
      children: [
        { path: '', name: 'home', component: LandingView },
      ],
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true },
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: OnboardingView,
      meta: { requiresAuth: true },
    },
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
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
})

const ONBOARDING_BYPASS = new Set(['/onboarding', '/login', '/'])

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()

  if (to.meta.public || to.path === '/') {
    if (to.path === '/login' && auth.isAuthenticated) {
      return next('/dashboard')
    }
    return next()
  }

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

  // Redirect to onboarding if first login and not already there
  if (auth.user?.needs_onboarding && !ONBOARDING_BYPASS.has(to.path)) {
    return next('/onboarding')
  }

  next()
})

export default router
