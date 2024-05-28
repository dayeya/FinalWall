import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  {
    path: '/', 
    name: 'Home',
    component: Dashboard
  },
  {
    path: '/admin', 
    name: 'Admin',
    component: () => import('../views/RouterViewBind.vue'),
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => Dashboard },
      { path: 'config', name: 'Configuration', component: () => import('../views/Configuration.vue') },
      { path: 'events', name: 'Events', component: () => import('../views/Events.vue') },
      { path: 'cluster', name: 'Cluster', component: () => import('../views/Cluster.vue') },
      { path: 'rules', name: 'Rules', component: () => import('../views/Rules.vue') },
      { path: 'help', name: 'Help', component: () => import('../views/Help.vue') }
    ]
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes
});

export default router
