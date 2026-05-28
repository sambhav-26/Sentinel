'use client';

import { useContext } from 'react';
import { AuthContext } from '@/context/AuthContext';
import { AuthContextType } from '@/types/auth';

/**
 * Hook to use authentication context
 * Throws error if used outside of AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

export default useAuth;
