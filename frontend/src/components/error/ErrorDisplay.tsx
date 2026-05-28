'use client';

import { ReactNode } from 'react';

interface ErrorDisplayProps {
  error: string | null;
  onDismiss?: () => void;
  severity?: 'error' | 'warning' | 'info';
}

export function ErrorDisplay({ error, onDismiss, severity = 'error' }: ErrorDisplayProps) {
  if (!error) return null;

  const styles = {
    error: 'bg-red-900 border-red-700 text-red-200',
    warning: 'bg-yellow-900 border-yellow-700 text-yellow-200',
    info: 'bg-blue-900 border-blue-700 text-blue-200',
  };

  return (
    <div className={`border rounded-lg p-4 flex items-start justify-between gap-4 ${styles[severity]}`}>
      <div className="flex-1">
        <p className="text-sm font-medium">{error}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-lg font-semibold opacity-70 hover:opacity-100"
        >
          ×
        </button>
      )}
    </div>
  );
}

interface ErrorAlertProps {
  title: string;
  message: string;
  details?: ReactNode;
  onRetry?: () => void;
}

export function ErrorAlert({ title, message, details, onRetry }: ErrorAlertProps) {
  return (
    <div className="bg-red-900 border border-red-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-red-200 mb-2">{title}</h3>
      <p className="text-red-300 text-sm mb-3">{message}</p>
      {details && (
        <div className="bg-red-950 rounded p-3 mb-4 text-xs text-red-200 font-mono overflow-x-auto">
          {details}
        </div>
      )}
      <div className="flex gap-2">
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-4 py-2 bg-red-700 hover:bg-red-600 rounded font-medium text-sm"
          >
            Retry
          </button>
        )}
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-red-700 hover:bg-red-600 rounded font-medium text-sm"
        >
          Reload Page
        </button>
      </div>
    </div>
  );
}

interface SuccessAlertProps {
  message: string;
  onDismiss?: () => void;
}

export function SuccessAlert({ message, onDismiss }: SuccessAlertProps) {
  return (
    <div className="bg-green-900 border border-green-700 rounded-lg p-4 flex items-start justify-between gap-4">
      <p className="text-green-200 text-sm">{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-lg font-semibold text-green-200 opacity-70 hover:opacity-100"
        >
          ×
        </button>
      )}
    </div>
  );
}
