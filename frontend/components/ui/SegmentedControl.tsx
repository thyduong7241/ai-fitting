'use client';

import React from 'react';

export interface SegmentedControlOption<T extends string | number> {
  label: string;
  value: T;
  icon?: React.ReactNode;
  badge?: string;
}

export interface SegmentedControlProps<T extends string | number> {
  options: SegmentedControlOption<T>[];
  value: T;
  onChange: (value: T) => void;
  size?: 'sm' | 'md';
  className?: string;
  name?: string;
}

export function SegmentedControl<T extends string | number>({
  options,
  value,
  onChange,
  size = 'md',
  className = '',
  name = 'segmented-control',
}: SegmentedControlProps<T>) {
  const containerPadding = size === 'sm' ? 'p-1' : 'p-1.5';
  const itemPadding = size === 'sm' ? 'py-1 px-2.5 text-xs' : 'py-2 px-3 text-sm';

  return (
    <div
      role="radiogroup"
      aria-label={name}
      className={`relative flex items-center w-full rounded-16 bg-[#EEF4F6] border border-brand-border/60 ${containerPadding} ${className}`}
    >
      {options.map((option) => {
        const isSelected = option.value === value;
        return (
          <button
            key={String(option.value)}
            type="button"
            role="radio"
            aria-checked={isSelected}
            onClick={() => onChange(option.value)}
            className={`relative flex flex-1 items-center justify-center gap-1.5 font-medium rounded-14 transition-all duration-200 select-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal ${itemPadding} ${
              isSelected
                ? 'bg-white text-brand-navy shadow-sm font-semibold'
                : 'text-brand-slate hover:text-brand-navy'
            }`}
          >
            {option.icon && (
              <span className={`inline-flex shrink-0 ${isSelected ? 'text-brand-teal' : 'text-brand-muted'}`}>
                {option.icon}
              </span>
            )}
            <span>{option.label}</span>
            {option.badge && (
              <span className="ml-1 rounded-full bg-brand-teal px-1.5 py-0.2 text-[10px] font-bold text-white">
                {option.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
