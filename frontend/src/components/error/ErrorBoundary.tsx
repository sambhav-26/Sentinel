'use client';

import React, { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="bg-red-900 border border-red-700 rounded-lg p-6 m-4">
            <h2 className="text-lg font-semibold text-red-200 mb-2">Something went wrong</h2>
            <p className="text-red-300 text-sm mb-3">{this.state.error?.message}</p>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              className="px-4 py-2 bg-red-700 hover:bg-red-600 rounded text-sm font-medium text-red-100"
            >
              Try Again
            </button>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
