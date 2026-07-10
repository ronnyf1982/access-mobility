import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PublicLayout from '@/layouts/PublicLayout.vue'
import PortalLayout from '@/layouts/PortalLayout.vue'
import LandingView from '@/views/LandingView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'
import MobilityProfileView from '@/views/MobilityProfileView.vue'

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
      path: '/dashboard',
      component: PortalLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: DashboardView },
        { path: '/mobility-profile', name: 'mobility-profile', component: MobilityProfileView },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
})

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

  next()
})

export default router
