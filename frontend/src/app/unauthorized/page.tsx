'use client';

import Link from 'next/link';

export default function UnauthorizedPage() {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center px-4">
      <div className="text-center space-y-6">
        <div>
          <p className="text-6xl font-bold text-red-500 mb-2">403</p>
          <h1 className="text-3xl font-bold">Access Denied</h1>
        </div>

        <p className="text-[var(--text-secondary)] max-w-md">
          You do not have permission to access this resource. Contact your administrator if you believe this is a mistake.
        </p>

        <div className="flex gap-4 justify-center">
          <Link
            href="/dashboard"
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium transition-colors"
          >
            Go to Dashboard
          </Link>
          <Link
            href="/login"
            className="px-6 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] hover:border-blue-500 rounded font-medium transition-colors"
          >
            Log in Again
          </Link>
        </div>
      </div>
    </div>
  );
}
