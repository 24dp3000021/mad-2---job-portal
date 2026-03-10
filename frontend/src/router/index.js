import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'

const routes = [
  { 
    path: '/', 
    name: 'Login', 
    component: LoginView 
  },
  { 
    path: '/admin', 
    name: 'Admin', 
    component: AdminDashboard, 
    meta: { requiresAuth: true, role: 'admin' } 
  },
  { 
    path: '/student', 
    name: 'Student', 
    component: StudentDashboard, 
    meta: { requiresAuth: true, role: 'student' } 
  },
  { 
    path: '/company', 
    name: 'Company', 
    component: CompanyDashboard, 
    meta: { requiresAuth: true, role: 'company' } 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// SECURITY GUARD: This runs before every single page change
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('role')

  // 1. If page requires authentication
  if (to.meta.requiresAuth) {
    if (!token) {

      next('/') 
    } else if (to.meta.role && to.meta.role !== userRole) {
      // Logged in but wrong role? (e.g. Student trying to access /admin)

      if (userRole === 'admin') next('/admin')
      else if (userRole === 'student') next('/student')
      else if (userRole === 'company') next('/company')
      else next('/')
    } else {
      next() // Authorized: Let them pass
    }
  } else {
    // 2. If user is already logged in and tries to go to Login page
    if (to.path === '/' && token) {
      if (userRole === 'admin') next('/admin')
      else if (userRole === 'student') next('/student')
      else if (userRole === 'company') next('/company')
    } else {
      next() // Page doesn't require auth (Login page)
    }
  }
})

export default router