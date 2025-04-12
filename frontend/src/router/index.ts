import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PlanView from '../views/PlanView.vue'
import DoView from '../views/DoView.vue'
import CheckView from '../views/CheckView.vue'
import AdjustView from '../views/AdjustView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
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

export default router