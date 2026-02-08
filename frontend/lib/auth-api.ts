import apiClient from './api-client'
import type { LoginRequest, RegisterRequest, AuthResponse, User } from '@/types/auth'

export const authApi = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', data)
    return response.data
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', data)
    return response.data
  },

  async logout(): Promise<void> {
    await apiClient.post('/auth/logout')
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },

  async updateProfile(data: { name?: string; email?: string }): Promise<User> {
    const response = await apiClient.patch<User>('/auth/me', data)
    return response.data
  },

  async changePassword(data: { currentPassword: string; newPassword: string }): Promise<void> {
    await apiClient.post('/auth/change-password', data)
  },

  async deleteAccount(): Promise<void> {
    await apiClient.delete('/auth/me')
  },
}
