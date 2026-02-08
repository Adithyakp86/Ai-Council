import apiClient from './api-client'

export interface AdminUser {
  id: string
  email: string
  name: string
  role: 'user' | 'admin'
  isActive: boolean
  totalRequests: number
  createdAt: string
}

export interface AdminUsersResponse {
  users: AdminUser[]
  total: number
  page: number
  pages: number
}

export interface UpdateUserRequest {
  isActive?: boolean
  role?: 'user' | 'admin'
}

export interface ProviderHealth {
  groq: 'healthy' | 'degraded' | 'down'
  together: 'healthy' | 'degraded' | 'down'
  openrouter: 'healthy' | 'degraded' | 'down'
  huggingface: 'healthy' | 'degraded' | 'down'
}

export interface CircuitBreakerStates {
  groq: 'open' | 'closed' | 'half-open'
  together: 'open' | 'closed' | 'half-open'
  openrouter: 'open' | 'closed' | 'half-open'
  huggingface: 'open' | 'closed' | 'half-open'
}

export interface ProviderCostBreakdown {
  providerName: string
  requestCount: number
  totalSubtasks: number
  totalCost: number
  totalInputTokens: number
  totalOutputTokens: number
}

export interface ProviderCostData {
  byProvider: ProviderCostBreakdown[]
  totalCost: number
  totalRequests: number
  estimatedSavings: number
  freeProviderUsagePercent: number
}

export interface MonitoringData {
  totalUsers: number
  requestsLast24h: number
  averageResponseTime: number
  totalCostLast24h: number
  successRate: number
  activeWebsockets: number
  providerHealth: ProviderHealth
  circuitBreakers: CircuitBreakerStates
  providerCostBreakdown: ProviderCostData
}

export interface UserDetails extends AdminUser {
  requestHistory: Array<{
    id: string
    content: string
    executionMode: string
    status: string
    createdAt: string
    cost?: number
  }>
  statistics: {
    totalRequests: number
    totalCost: number
    averageConfidence: number
  }
}

export const adminApi = {
  // Get all users with pagination
  async getUsers(page: number = 1, limit: number = 50): Promise<AdminUsersResponse> {
    const response = await apiClient.get('/admin/users', {
      params: { page, limit },
    })
    return response.data
  },

  // Update user (enable/disable, promote to admin)
  async updateUser(userId: string, data: UpdateUserRequest): Promise<void> {
    await apiClient.patch(`/admin/users/${userId}`, data)
  },

  // Get user details
  async getUserDetails(userId: string): Promise<UserDetails> {
    const response = await apiClient.get(`/admin/users/${userId}`)
    return response.data
  },

  // Get system monitoring data
  async getMonitoring(): Promise<MonitoringData> {
    const response = await apiClient.get('/admin/monitoring')
    return response.data
  },
}
