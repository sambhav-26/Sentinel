'use client';

import { ReactNode } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { UserRole } from '@/types/auth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredRole?: UserRole;
  requiredPermission?: string;
  fallback?: ReactNode;
}

/**
 * Component to protect routes based on authentication and authorization
 */
export function ProtectedRoute({
  children,
  requiredRole,
  requiredPermission,
  fallback,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user, hasRole, hasPermission } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
      return;
    }

    if (!isLoading && user) {
      // Check role-based access
      if (requiredRole && !hasRole(requiredRole)) {
        router.push('/unauthorized');
        return;
      }

      // Check permission-based access
      if (requiredPermission && !hasPermission(requiredPermission)) {
        router.push('/unauthorized');
        return;
      }
    }
  }, [isLoading, isAuthenticated, user, requiredRole, requiredPermission, hasRole, hasPermission, router]);

  if (isLoading) {
    return fallback || <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!isAuthenticated) {
    return fallback || <div className="flex items-center justify-center min-h-screen">Please log in</div>;
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return fallback || <div className="flex items-center justify-center min-h-screen">Insufficient permissions</div>;
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return fallback || <div className="flex items-center justify-center min-h-screen">Insufficient permissions</div>;
  }

  return children;
}
