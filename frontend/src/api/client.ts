import axios, { AxiosError } from 'axios'

import { getToken } from '../services/authTokenStorage'
import { ApiError } from '../types/api'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
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
