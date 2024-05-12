import { createRouter, createWebHistory } from 'vue-router'
import Ping from '../components/ping.vue'
import Bar from '../components/bar.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Bar
    },
    {
      path:'/ping',
      name: 'ping',
      component: Ping
    },
  ]
})

export default router