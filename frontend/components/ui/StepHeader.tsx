'use client';

import React from 'react';

export interface StepHeaderProps {
  title: string;
  subtitle?: string;
  currentStep?: number;
  totalSteps?: number;
  onBack?: () => void;
  onClose?: () => void;
  rightAction?: React.ReactNode;
  className?: string;
}

export function StepHeader({
  title,
  subtitle,
  currentStep,
  totalSteps,
  onBack,
  onClose,
  rightAction,
  className = '',
}: StepHeaderProps) {
  return (
    <header className={`flex flex-col gap-2 px-5 py-3 border-b border-brand-border/60 bg-white ${className}`}>
      <div className="flex items-center justify-between">
        {/* Left Back Button or Placeholder */}
        <div className="flex items-center gap-2">
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="flex h-9 w-9 items-center justify-center rounded-full text-brand-slate hover:bg-slate-100 active:scale-95 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal"
              aria-label="Quay lại bước trước"
            >
              <svg className="h-5 w-5 stroke-current fill-none stroke-[2.2]" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          )}

          {currentStep !== undefined && totalSteps !== undefined && (
            <span className="inline-flex items-center rounded-full bg-brand-teal-subtle px-2.5 py-0.5 text-xs font-semibold text-brand-teal">
              Bước {currentStep}/{totalSteps}
            </span>
          )}
        </div>

        {/* Right Action or Close Button */}
        <div className="flex items-center gap-2">
          {rightAction}
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="flex h-9 w-9 items-center justify-center rounded-full text-brand-slate hover:bg-slate-100 active:scale-95 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal"
              aria-label="Đóng cửa sổ"
            >
              <svg className="h-5 w-5 stroke-current fill-none stroke-[2]" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Title & Subtitle */}
      <div>
        <h1 className="text-lg font-bold text-brand-navy tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-brand-muted mt-0.5">{subtitle}</p>}
      </div>
    </header>
  );
}
