import { apiClient } from './api'

export interface User {
  id: string
  email: string
  is_active: boolean
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export const authService = {
  async register(email: string, password: string): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/auth/register', { email, password })
    return res.data
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/auth/login', { email, password })
    return res.data
  },

  async getMe(): Promise<User> {
    const res = await apiClient.get<User>('/auth/me')
    return res.data
  },
}
