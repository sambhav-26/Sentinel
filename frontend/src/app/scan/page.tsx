'use client';

import { useEffect, useState } from 'react';
import { useScans } from '@/hooks/useScans';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Scan, ScanCreateRequest } from '@/types';
import { ErrorDisplay, SuccessAlert } from '@/components/error/ErrorDisplay';
import { ScanListSkeleton } from '@/components/loading/SkeletonLoaders';
import { useFormValidation, validators } from '@/lib/validation';
import { getErrorMessage } from '@/lib/error-handler';

function ScanContent() {
  const { scans, loading, error: apiError, createScan, listScans, waitForCompletion } = useScans();
  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedScan, setSelectedScan] = useState<string | null>(null);

  const { values, errors, touched, getFieldError, handleChange, handleBlur, validateAll, reset } = useFormValidation(
    { repository_url: '' },
    {
      repository_url: [
        (v) => validators.required(v, 'Repository URL'),
        (v) => validators.url(v, 'Repository URL'),
      ],
    }
  );

  useEffect(() => {
    listScans(0, 20);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateAll()) {
      return;
    }

    setCreating(true);
    try {
      const scan = await createScan(values as ScanCreateRequest);
      setSuccess('Scan created successfully!');
      reset();
      setShowForm(false);
      await listScans(0, 20);
      setTimeout(() => setSuccess(null), 5000);
      
      // Optionally wait for completion in background
      waitForCompletion(scan.id).catch(console.error);
    } catch (err) {
      console.error('Failed to create scan:', err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-semibold">Security Scans</h1>
          <p className="text-[var(--text-secondary)] mt-1">
            Manage and monitor code security scans
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-medium text-sm"
        >
          New Scan
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Repository URL</label>
            <input
              type="text"
              name="repository_url"
              placeholder="https://github.com/user/repo"
              value={values.repository_url}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`w-full bg-[var(--bg-primary)] border rounded px-3 py-2 text-sm ${touched.repository_url && getFieldError('repository_url') ? 'border-red-500 focus:outline-red-500' : 'border-[var(--border-color)] focus:outline-blue-500'}`}
            />
            {touched.repository_url && getFieldError('repository_url') && (
              <p className="text-red-300 text-xs mt-1">{getFieldError('repository_url')}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Repository Name (Optional)</label>
            <input
              type="text"
              name="repository_name"
              placeholder="My Project"
              value={values.repository_name || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              className="w-full bg-[var(--bg-primary)] border border-[var(--border-color)] rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Description (Optional)</label>
            <textarea
              name="description"
              placeholder="Scan description..."
              value={values.description || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              className="w-full bg-[var(--bg-primary)] border border-[var(--border-color)] rounded px-3 py-2 text-sm"
              rows={3}
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={creating}
              className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded font-medium text-sm"
            >
              {creating ? 'Creating...' : 'Start Scan'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                reset();
              }}
              className="flex-1 px-4 py-2 bg-[var(--bg-primary)] border border-[var(--border-color)] hover:border-[var(--text-secondary)] rounded font-medium text-sm"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {success && <SuccessAlert message={success} onDismiss={() => setSuccess(null)} />}
      {apiError && <ErrorDisplay error={apiError} />}

      {loading ? (
        <ScanListSkeleton />
      ) : (
        <div className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-[var(--bg-primary)] border-b border-[var(--border-color)]">
              <tr>
                <th className="px-4 py-3 text-left font-medium">ID</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
                <th className="px-4 py-3 text-left font-medium">Progress</th>
                <th className="px-4 py-3 text-left font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={4} className="px-4 py-3 text-center text-[var(--text-secondary)]">
                    Loading scans...
                  </td>
                </tr>
              ) : scans.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-3 text-center text-[var(--text-secondary)]">
                    No scans yet
                  </td>
                </tr>
              ) : (
                scans.map((scan) => (
                  <tr
                    key={scan.id}
                    onClick={() => setSelectedScan(scan.id)}
                    className="border-b border-[var(--border-color)] hover:bg-[var(--bg-primary)] cursor-pointer"
                  >
                    <td className="px-4 py-3 font-mono text-xs">{scan.id.substring(0, 8)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        scan.status === 'completed' ? 'bg-green-900 text-green-200' :
                        scan.status === 'failed' ? 'bg-red-900 text-red-200' :
                        scan.status === 'running' ? 'bg-blue-900 text-blue-200' :
                        'bg-gray-900 text-gray-200'
                      }`}>
                        {scan.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="w-32 bg-[var(--border-color)] rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full transition-all"
                          style={{ width: `${scan.progress}%` }}
                        />
                      </div>
                    </td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">
                      {new Date(scan.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
      )}
    </div>
  );
}

export default function ScanPage() {
  return (
    <ProtectedRoute requiredPermission="create_scan">
      <ScanContent />
    </ProtectedRoute>
  );
}
