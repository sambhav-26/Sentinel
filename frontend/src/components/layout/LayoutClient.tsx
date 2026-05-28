'use client';

import { ReactNode } from 'react';
import { AuthProvider } from '@/context/AuthContext';
import ErrorBoundary from '@/components/error/ErrorBoundary';
import AppShell from '@/components/layout/AppShell';

interface LayoutClientProps {
  children: ReactNode;
}

export function LayoutClient({ children }: LayoutClientProps) {
  return (
    <AuthProvider>
      <ErrorBoundary>
        <AppShell>{children}</AppShell>
      </ErrorBoundary>
    </AuthProvider>
  );
}
