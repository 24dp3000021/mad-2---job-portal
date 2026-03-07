import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'

const routes = [
  { path: '/', component: LoginView },
  { path: '/admin', component: AdminDashboard },
  { path: '/student', component: StudentDashboard },
  { path: '/company', component: CompanyDashboard },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router