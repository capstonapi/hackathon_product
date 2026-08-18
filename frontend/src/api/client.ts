import axios, { AxiosError } from 'axios'

import { getToken } from '../services/authTokenStorage'
import { ApiError } from '../types/api'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

export const apiClient = axios.create({
  // Keep local development working even before a frontend `.env` has been created.
  baseURL: API_BASE_URL,
})

apiClient.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error?: string }>) => {
    const status = error.response?.status ?? null
    const message = error.response?.data?.error ?? error.message ?? 'Request failed'
    return Promise.reject(new ApiError(message, status))
  },
)
