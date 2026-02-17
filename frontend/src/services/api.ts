import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { authService } from './auth.service'

// Create axios instance with default config
const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Track whether a refresh is already in progress to avoid concurrent refreshes
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (reason?: unknown) => void
  config: InternalAxiosRequestConfig
}> = []

function processQueue(error: unknown) {
  failedQueue.forEach(({ resolve, reject, config }) => {
    if (error) {
      reject(error)
    } else {
      // Retry with updated token
      config.headers.Authorization = `Bearer ${localStorage.getItem('access_token')}`
      resolve(api(config))
    }
  })
  failedQueue = []
}

// Response interceptor to handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Only attempt refresh for 401 errors, not on auth endpoints, and not already retried
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/')
    ) {
      if (isRefreshing) {
        // Queue this request until the refresh completes
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject, config: originalRequest })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const result = await authService.refreshToken()
        if (result) {
          // Refresh succeeded — retry original request and queued requests
          originalRequest.headers.Authorization = `Bearer ${result.access_token}`
          processQueue(null)
          return api(originalRequest)
        }
      } catch (refreshError) {
        processQueue(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Refresh failed or not applicable — clear auth and redirect to login
    if (error.response?.status === 401) {
      authService.clearAuth()
      if (window.location.pathname !== '/signin') {
        window.location.href = '/signin'
      }
    }

    return Promise.reject(error)
  }
)

export default api
