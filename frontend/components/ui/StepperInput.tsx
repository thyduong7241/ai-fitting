'use client';

import React from 'react';

export interface StepperInputProps {
  label: string;
  value: number;
  unit: string;
  min?: number;
  max?: number;
  step?: number;
  onChange: (value: number) => void;
  helperText?: string;
  className?: string;
}

export function StepperInput({
  label,
  value,
  unit,
  min = 0,
  max = 300,
  step = 1,
  onChange,
  helperText,
  className = '',
}: StepperInputProps) {
  const canDecrement = value - step >= min;
  const canIncrement = value + step <= max;

  const handleDecrement = () => {
    if (canDecrement) {
      onChange(Number((value - step).toFixed(1)));
    }
  };

  const handleIncrement = () => {
    if (canIncrement) {
      onChange(Number((value + step).toFixed(1)));
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
      e.preventDefault();
      handleIncrement();
    } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
      e.preventDefault();
      handleDecrement();
    }
  };

  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold uppercase tracking-wider text-brand-slate">
          {label}
        </label>
        {helperText && <span className="text-xs text-brand-muted">{helperText}</span>}
      </div>

      <div
        role="spinbutton"
        tabIndex={0}
        aria-label={label}
        aria-valuenow={value}
        aria-valuemin={min}
        aria-valuemax={max}
        onKeyDown={handleKeyDown}
        className="flex h-12 w-full items-center justify-between rounded-16 border border-brand-border bg-white px-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal select-none"
      >
        {/* Decrement Button */}
        <button
          type="button"
          onClick={handleDecrement}
          disabled={!canDecrement}
          aria-label={`Giảm ${label}`}
          className="flex h-9 w-9 items-center justify-center rounded-12 text-brand-navy hover:bg-slate-100 active:scale-95 disabled:opacity-30 disabled:hover:bg-transparent transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal"
        >
          <svg className="h-4 w-4 stroke-current stroke-[2.5]" viewBox="0 0 24 24" fill="none">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 12H5" />
          </svg>
        </button>

        {/* Value Display */}
        <div className="flex items-baseline gap-1">
          <span className="text-lg font-bold text-brand-navy tracking-tight">{value}</span>
          <span className="text-xs font-medium text-brand-muted">{unit}</span>
        </div>

        {/* Increment Button */}
        <button
          type="button"
          onClick={handleIncrement}
          disabled={!canIncrement}
          aria-label={`Tăng ${label}`}
          className="flex h-9 w-9 items-center justify-center rounded-12 text-brand-navy hover:bg-slate-100 active:scale-95 disabled:opacity-30 disabled:hover:bg-transparent transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal"
        >
          <svg className="h-4 w-4 stroke-current stroke-[2.5]" viewBox="0 0 24 24" fill="none">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 5v14m-7-7h14" />
          </svg>
        </button>
      </div>
    </div>
  );
}
