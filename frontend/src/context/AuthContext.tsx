'use client';

import React, { createContext, useCallback, useEffect, useState } from 'react';
import { User, AuthContextType, UserRole } from '@/types/auth';
import authService from '@/services/auth';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

// Role-based permissions mapping
const rolePermissions: Record<UserRole, string[]> = {
  admin: ['create_scan', 'read_scan', 'update_scan', 'delete_scan', 'manage_users', 'view_reports'],
  analyst: ['create_scan', 'read_scan', 'view_reports'],
  viewer: ['read_scan', 'view_reports'],
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      if (!authService.isAuthenticated()) {
        setUser(null);
        return;
      }

      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (err: any) {
      console.error('Auth check failed:', err);
      setUser(null);
      authService.logout();
      setError(err.message || 'Failed to authenticate');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.login({ email, password });
      setUser(response.user);
    } catch (err: any) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (email: string, username: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.register({ email, username, password });
      setUser(response.user);
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
    setError(null);
  }, []);

  const hasRole = useCallback((role: UserRole): boolean => {
    if (!user) return false;
    return user.role === role;
  }, [user]);

  const hasPermission = useCallback((action: string): boolean => {
    if (!user) return false;
    const permissions = rolePermissions[user.role] || [];
    return permissions.includes(action);
  }, [user]);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    logout,
    checkAuth,
    hasRole,
    hasPermission,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
