import { createRouter, createWebHistory } from 'vue-router'
import PublicLayout from '@/layouts/PublicLayout.vue'
import PortalLayout from '@/layouts/PortalLayout.vue'
import LandingView from '@/views/LandingView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: PublicLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: LandingView,
        },
      ],
    },
    {
      path: '/dashboard',
      component: PortalLayout,
      children: [
        {
          path: '',
          name: 'dashboard',
          component: DashboardView,
        },
      ],
    },
    // Catch-all: Weiterleitung zu /dashboard (noch nicht implementierte Portal-Routen)
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard',
    },
  ],
})

export default router
