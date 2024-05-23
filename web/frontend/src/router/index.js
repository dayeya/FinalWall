import { createRouter, createWebHistory } from 'vue-router'
import RouterViewBind from '../views/RouterViewBind.vue'
import AdminPanel from '../views/AdminPanel.vue'
import Events from '../views/Events.vue'
import Rules from '../views/Rules.vue'
import Clusters from '../views/Clusters.vue'
import Configuration from '../views/Configuration.vue'
import Help from '../views/Help.vue'

const routes = [
  {
    path: '/', 
    name: 'Home', 
    component: AdminPanel // Change to HomeView.
  },
  {
    path: '/admin', 
    name: 'Admin',
    component: RouterViewBind,
    children: [
      {path: 'panel', name: 'Admin Panel', component: AdminPanel},
      {path: 'config', name: 'Configuration', component: Configuration},
      {path: 'clusters', name: 'Clusters', component: Clusters},
      {path: 'rules', name: 'Rules', component: Rules},
      {path: 'help', name: 'Help', component: Help},
      {
        path: 'events', 
        name: 'Events', 
        component: Events,
        children: [
          {path: 'access_logs', name: "Access Logs", component: Events},
          {path: 'security_logs', name: "Security Logs", component: Events},
        ]
      },
    ]
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes
});

export default router
