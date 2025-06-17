import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
}

export function LoadingSpinner({ size = 'medium', color = 'currentColor' }: LoadingSpinnerProps) {
  const sizeMap = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  return (
    <div className="flex justify-center items-center">
      <div
        className={`${sizeMap[size]} animate-spin rounded-full border-4 border-gray-200 border-t-blue-600`}
        style={{ borderTopColor: color }}
        role="status"
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  );
} 