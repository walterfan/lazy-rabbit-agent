// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref(null)
  const accessToken = ref<string | null>(null)

  const login = (token: string) => {
    isAuthenticated.value = true
    accessToken.value = token
    // Store both auth state and token
    localStorage.setItem('isAuthenticated', 'true')
    localStorage.setItem('access_token', token)
  }

  const logout = () => {
    isAuthenticated.value = false
    accessToken.value = null
    // Clear all auth-related storage
    localStorage.removeItem('isAuthenticated')
    localStorage.removeItem('access_token')
  }

  // Check auth state on initialization
  const checkAuth = () => {
    const token = localStorage.getItem('access_token')
    isAuthenticated.value = !!token && localStorage.getItem('isAuthenticated') === 'true'
    if (isAuthenticated.value) {
      accessToken.value = token
    }
  }

  return { 
    isAuthenticated, 
    user, 
    accessToken,
    login, 
    logout, 
    checkAuth 
  }
})