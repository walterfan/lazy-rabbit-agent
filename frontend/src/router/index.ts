import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PlanView from '../views/PlanView.vue'
import DoView from '../views/DoView.vue'
import CheckView from '../views/CheckView.vue'
import AdjustView from '../views/AdjustView.vue'
import PromptView from '../views/PromptView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/prompt',
      name: 'prompt',
      component: PromptView
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue')
    },
    {
      path: '/plan',
      name: 'plan',
      component: PlanView
    },
    {
      path: '/do',
      name: 'do',
      component: DoView
    },
    {
      path: '/check',
      name: 'check',
      component: CheckView
    },
    {
      path: '/adjust',
      name: 'adjust',
      component: AdjustView
    },
    // Redirect to plan by default
    {
      path: '/:pathMatch(.*)*',
      redirect: '/plan'
    }
  ]
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  authStore.checkAuth() // Check auth state on each route change
  
  // Define routes that don't require authentication
  const publicRoutes = ['/login']
  
  // If not authenticated and trying to access a protected route
  if (!authStore.isAuthenticated && !publicRoutes.includes(to.path)) {
    return '/login'
  }
  
  // If authenticated and trying to access login page
  if (authStore.isAuthenticated && to.path === '/login') {
    return '/' // Redirect to home if already logged in
  }
})

export default router