import api from './api'
import type { LoginRequest, LoginResponse, SignupRequest, SignupResponse } from '@/types/user'

export const authService = {
  /**
   * Sign up a new user
   */
  async signup(data: SignupRequest): Promise<SignupResponse> {
    const response = await api.post<SignupResponse>('/auth/signup', data)
    return response.data
  },

  /**
   * Sign in with email and password
   */
  async signin(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/signin', data)
    return response.data
  },

  /**
   * Save authentication data to localStorage
   */
  saveAuth(token: string, user: LoginResponse['user']): void {
    localStorage.setItem('access_token', token)
    localStorage.setItem('user', JSON.stringify(user))
  },

  /**
   * Clear authentication data from localStorage
   */
  clearAuth(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  },

  /**
   * Get stored token
   */
  getToken(): string | null {
    return localStorage.getItem('access_token')
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken()
  },
}


