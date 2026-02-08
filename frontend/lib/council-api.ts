// API client for AI Council operations
import { apiClient } from './api-client';
import type { 
  CouncilRequest, 
  CouncilRequestResponse, 
  CouncilResponse,
  CostEstimate 
} from '@/types/council';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const councilApi = {
  /**
   * Submit a new request to AI Council
   */
  async submitRequest(request: CouncilRequest): Promise<CouncilRequestResponse> {
    const response = await apiClient.post<CouncilRequestResponse>(
      '/api/v1/council/process',
      request
    );
    return response.data;
  },

  /**
   * Get cost estimates for a request
   */
  async getCostEstimate(content: string): Promise<CostEstimate> {
    const response = await apiClient.post<CostEstimate>(
      '/api/v1/council/estimate',
      { content }
    );
    return response.data;
  },

  /**
   * Get request status
   */
  async getRequestStatus(requestId: string): Promise<{ 
    requestId: string; 
    status: string; 
    progress: number; 
    currentStage: string;
  }> {
    const response = await apiClient.get(`/api/v1/council/status/${requestId}`);
    return response.data;
  },

  /**
   * Get request result
   */
  async getRequestResult(requestId: string): Promise<CouncilResponse> {
    const response = await apiClient.get<CouncilResponse>(
      `/api/v1/council/result/${requestId}`
    );
    return response.data;
  },

  /**
   * Get request history
   */
  async getHistory(params?: {
    page?: number;
    limit?: number;
    search?: string;
    mode?: string;
    startDate?: string;
    endDate?: string;
  }): Promise<{
    items: any[];
    total: number;
    page: number;
    pages: number;
  }> {
    const response = await apiClient.get('/api/v1/council/history', { params });
    return response.data;
  },

  /**
   * Delete a request
   */
  async deleteRequest(requestId: string): Promise<void> {
    await apiClient.delete(`/api/v1/council/history/${requestId}`);
  },

  /**
   * Create WebSocket connection for real-time updates
   */
  createWebSocket(requestId: string, token: string): WebSocket {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    return new WebSocket(`${wsUrl}/ws/${requestId}?token=${token}`);
  }
};
