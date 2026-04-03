import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value && !!user.value)

  async function login(username, password) {
    const response = await api.post('/api/token/', { username, password })
    const { access, refresh } = response.data

    token.value = access
    localStorage.setItem('token', access)
    localStorage.setItem('refresh_token', refresh)
    api.defaults.headers.common['Authorization'] = `Bearer ${access}`

    const userResponse = await api.get('/api/users/me/')
    user.value = userResponse.data
    localStorage.setItem('user', JSON.stringify(userResponse.data))

    return userResponse.data
  }

  async function refreshUser() {
    if (!token.value) return null
    const userResponse = await api.get('/api/users/me/')
    user.value = userResponse.data
    localStorage.setItem('user', JSON.stringify(userResponse.data))
    return userResponse.data
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    delete api.defaults.headers.common['Authorization']
  }

  function updateUser(userData) {
    user.value = { ...user.value, ...userData }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  async function initAuth() {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      try {
        await refreshUser()
      } catch {
        logout()
      }
    }
  }

  return { user, token, isLoggedIn, login, logout, updateUser, initAuth, refreshUser }
})
