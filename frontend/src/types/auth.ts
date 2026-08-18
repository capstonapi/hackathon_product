export interface AuthResponse {
  token: string
}

export interface RegisterPayload {
  username: string
  password: string
  email?: string
}

export interface LoginPayload {
  username: string
  password: string
}
