/**
 * Authentication service - API operations for auth
 */

import apiClient from './api-client';
import { LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, User } from '@/types/auth';

export class AuthService {
  /**
   * Login with email and password
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', data);
    if (response.access_token) {
      apiClient.setAuthToken(response.access_token);
    }
    return response;
  }

  /**
   * Register a new account
   */
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await apiClient.post<RegisterResponse>('/auth/register', data);
    if (response.access_token) {
      apiClient.setAuthToken(response.access_token);
    }
    return response;
  }

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me');
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/refresh');
    if (response.access_token) {
      apiClient.setAuthToken(response.access_token);
    }
    return response;
  }

  /**
   * Logout (clear token)
   */
  logout(): void {
    apiClient.clearAuthToken();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    const token = localStorage.getItem('auth_token');
    return !!token;
  }

  /**
   * Get auth token
   */
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
  }
}

export default new AuthService();
