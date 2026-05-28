'use client';

export function ScanListSkeleton() {
  return (
    <div className="space-y-2">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="bg-[var(--bg-primary)] border border-[var(--border-color)] rounded p-4 animate-pulse">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="h-4 bg-[var(--border-color)] rounded w-24 mb-2"></div>
              <div className="h-3 bg-[var(--border-color)] rounded w-32"></div>
            </div>
            <div className="w-32 h-2 bg-[var(--border-color)] rounded-full"></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function FindingListSkeleton() {
  return (
    <div className="space-y-3">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-4 animate-pulse">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="h-5 bg-[var(--border-color)] rounded w-40 mb-2"></div>
              <div className="h-4 bg-[var(--border-color)] rounded w-full mb-3"></div>
              <div className="grid grid-cols-2 gap-2">
                <div className="h-3 bg-[var(--border-color)] rounded w-32"></div>
                <div className="h-3 bg-[var(--border-color)] rounded w-32"></div>
              </div>
            </div>
            <div className="w-16 h-8 bg-[var(--border-color)] rounded ml-4"></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function StatsCardSkeleton() {
  return (
    <div className="grid grid-cols-4 gap-3">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-4 animate-pulse">
          <div className="h-4 bg-[var(--border-color)] rounded w-20 mb-3"></div>
          <div className="h-8 bg-[var(--border-color)] rounded w-12"></div>
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton() {
  return (
    <div className="border border-[var(--border-color)] rounded-lg overflow-hidden">
      <div className="bg-[var(--bg-primary)] border-b border-[var(--border-color)] p-4 animate-pulse">
        <div className="flex gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-4 bg-[var(--border-color)] rounded flex-1"></div>
          ))}
        </div>
      </div>
      <div className="space-y-0">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="border-b border-[var(--border-color)] p-4 animate-pulse">
            <div className="flex gap-4">
              {[...Array(4)].map((_, j) => (
                <div key={j} className="h-4 bg-[var(--border-color)] rounded flex-1"></div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg p-6 animate-pulse">
      <div className="h-6 bg-[var(--border-color)] rounded w-40 mb-4"></div>
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-4 bg-[var(--border-color)] rounded w-full"></div>
        ))}
      </div>
    </div>
  );
}

export function FormInputSkeleton() {
  return (
    <div className="space-y-2">
      <div className="h-4 bg-[var(--border-color)] rounded w-24 animate-pulse"></div>
      <div className="h-10 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded animate-pulse"></div>
    </div>
  );
}
