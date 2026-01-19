import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

// Mock services
vi.mock('@/services/auth.service', () => ({
  authService: {
    signin: vi.fn(),
    signup: vi.fn(),
    saveAuth: vi.fn(),
    clearAuth: vi.fn(),
    isAuthenticated: vi.fn(() => false),
    getToken: vi.fn(() => null),
  },
}))

vi.mock('@/services/user.service', () => ({
  userService: {
    getCurrentUser: vi.fn(),
    updateProfile: vi.fn(),
  },
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should initialize with null user', () => {
    const store = useAuthStore()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('should set authenticated to true when user is set', () => {
    const store = useAuthStore()
    store.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    expect(store.isAuthenticated).toBe(true)
  })

  it('should clear user on logout', () => {
    const store = useAuthStore()
    store.user = {
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    store.logout()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })
})


