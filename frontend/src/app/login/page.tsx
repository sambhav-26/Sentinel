'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useFormValidation, validators } from '@/lib/validation';
import { ErrorDisplay, SuccessAlert } from '@/components/error/ErrorDisplay';
import { getErrorMessage } from '@/lib/error-handler';

export default function LoginPage() {
  const { login, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const { values, touched, getFieldError, handleChange, handleBlur, validateAll } = useFormValidation(
    { email: '', password: '' },
    {
      email: [
        (v) => validators.required(v, 'Email'),
        (v) => validators.email(v, 'Email'),
      ],
      password: [
        (v) => validators.required(v, 'Password'),
        (v) => validators.minLength(v, 6, 'Password'),
      ],
    }
  );

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateAll()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await login(values.email, values.password);
      setSuccess('Login successful!');
      setTimeout(() => {
        router.push('/dashboard');
      }, 1500);
    } catch (err: any) {
      const message = getErrorMessage(err);
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-[var(--text-secondary)]">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-8 space-y-6">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-3xl font-bold mb-2">SentinelOS</h1>
            <p className="text-[var(--text-secondary)]">Security Intelligence Platform</p>
          </div>

          {/* Alerts */}
          {success && <SuccessAlert message={success} />}
          {error && <ErrorDisplay error={error} onDismiss={() => setError(null)} />}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium mb-2">Email Address</label>
              <input
                type="email"
                name="email"
                placeholder="admin@example.com"
                value={values.email}
                onChange={handleChange}
                onBlur={handleBlur}
                className={`w-full bg-[var(--bg-primary)] border rounded px-4 py-2 text-sm ${
                  touched.email && getFieldError('email')
                    ? 'border-red-500 focus:outline-red-500'
                    : 'border-[var(--border-color)] focus:outline-blue-500'
                }`}
                disabled={isSubmitting}
              />
              {touched.email && getFieldError('email') && (
                <p className="text-red-300 text-xs mt-1">{getFieldError('email')}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium mb-2">Password</label>
              <input
                type="password"
                name="password"
                placeholder="••••••••"
                value={values.password}
                onChange={handleChange}
                onBlur={handleBlur}
                className={`w-full bg-[var(--bg-primary)] border rounded px-4 py-2 text-sm ${
                  touched.password && getFieldError('password')
                    ? 'border-red-500 focus:outline-red-500'
                    : 'border-[var(--border-color)] focus:outline-blue-500'
                }`}
                disabled={isSubmitting}
              />
              {touched.password && getFieldError('password') && (
                <p className="text-red-300 text-xs mt-1">{getFieldError('password')}</p>
              )}
            </div>

            {/* Remember Me */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="remember"
                className="w-4 h-4 border-[var(--border-color)] rounded"
                disabled={isSubmitting}
              />
              <label htmlFor="remember" className="ml-2 text-sm text-[var(--text-secondary)]">
                Remember me
              </label>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded font-medium text-sm transition-colors"
            >
              {isSubmitting ? 'Logging in...' : 'Sign In'}
            </button>
          </form>

          {/* Footer */}
          <div className="border-t border-[var(--border-color)] pt-6 text-center text-sm text-[var(--text-secondary)]">
            <p>Demo credentials:</p>
            <p className="font-mono text-xs mt-2">admin@example.com / password123</p>
          </div>
        </div>
      </div>
    </div>
  );
}
