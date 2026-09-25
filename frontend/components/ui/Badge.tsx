'use client';

import React from 'react';

export type BadgeVariant = 'perfect' | 'tight' | 'loose' | 'extreme' | 'neutral' | 'brand';
export type BadgeSize = 'sm' | 'md';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: BadgeSize;
  dot?: boolean;
}

export function Badge({
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
  className = '',
  ...props
}: BadgeProps) {
  const variantStyles: Record<BadgeVariant, { container: string; dot: string }> = {
    perfect: {
      container: 'bg-[#E8F8F4] text-brand-teal-match border border-[#C2EFE4]',
      dot: 'bg-brand-teal-match',
    },
    tight: {
      container: 'bg-amber-50 text-amber-800 border border-amber-200',
      dot: 'bg-amber-500',
    },
    loose: {
      container: 'bg-sky-50 text-sky-800 border border-sky-200',
      dot: 'bg-sky-500',
    },
    extreme: {
      container: 'bg-rose-50 text-rose-800 border border-rose-200',
      dot: 'bg-rose-500',
    },
    neutral: {
      container: 'bg-slate-100 text-brand-slate border border-slate-200',
      dot: 'bg-slate-400',
    },
    brand: {
      container: 'bg-brand-teal-subtle text-brand-teal border border-teal-200 font-semibold',
      dot: 'bg-brand-teal',
    },
  };

  const sizeStyles: Record<BadgeSize, string> = {
    sm: 'px-2 py-0.5 text-[11px] gap-1',
    md: 'px-2.5 py-1 text-xs gap-1.5',
  };

  const { container, dot: dotColor } = variantStyles[variant];

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full select-none ${container} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {dot && <span className={`h-1.5 w-1.5 rounded-full ${dotColor}`} aria-hidden="true" />}
      {children}
    </span>
  );
}
