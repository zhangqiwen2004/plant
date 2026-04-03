import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
  { path: '/plants', name: 'Plants', component: () => import('../views/Plants.vue') },
  { path: '/plants/:id', name: 'PlantDetail', component: () => import('../views/PlantDetail.vue') },
  { path: '/community', name: 'Community', component: () => import('../views/Community.vue') },
  { path: '/posts/:id', name: 'PostDetail', component: () => import('../views/PostDetail.vue') },
  { path: '/questions', name: 'Questions', component: () => import('../views/Questions.vue') },
  { path: '/questions/:id', name: 'QuestionDetail', component: () => import('../views/QuestionDetail.vue') },
  { path: '/matching', name: 'Matching', component: () => import('../views/Matching.vue'), meta: { requiresAuth: true } },
  { path: '/matching/consultations/:id', name: 'ConsultationDetail', component: () => import('../views/ConsultationDetail.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue'), meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: () => import('../views/admin/Dashboard.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/plants', name: 'AdminPlants', component: () => import('../views/admin/Plants.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/topics', name: 'AdminTopics', component: () => import('../views/admin/Topics.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/posts', name: 'AdminPosts', component: () => import('../views/admin/Posts.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/moderation', name: 'AdminModeration', component: () => import('../views/admin/Moderation.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/experts', name: 'AdminExperts', component: () => import('../views/admin/Experts.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/users', name: 'AdminUsers', component: () => import('../views/admin/Users.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/matching', name: 'AdminMatching', component: () => import('../views/admin/Matching.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/analytics', name: 'AdminAnalytics', component: () => import('../views/admin/Analytics.vue'), meta: { requiresAuth: true, requiresAdmin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  
  if ((to.path === '/login' || to.path === '/register') && token) {
    next(user?.role === 'admin' ? '/admin' : '/')
  } else if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresAdmin && user?.role !== 'admin') {
    next('/')
  } else {
    next()
  }
})

export default router
