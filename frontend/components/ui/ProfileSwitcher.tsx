'use client';

import React, { useState, useRef, useEffect } from 'react';
import { UserProfile } from '@/types/fitting';

export interface ProfileSwitcherProps {
  profiles: UserProfile[];
  activeProfile: UserProfile;
  onSelectProfile: (id: string) => void;
  onAddProfile?: () => void;
  className?: string;
}

export function ProfileSwitcher({
  profiles,
  activeProfile,
  onSelectProfile,
  onAddProfile,
  className = '',
}: ProfileSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const initialLetter = activeProfile?.name?.charAt(0).toUpperCase() || 'U';

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Active Profile Pill Button */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={`Hồ sơ hiện tại: ${activeProfile?.name}. Bấm để đổi hồ sơ.`}
        className="flex items-center gap-2 rounded-full border border-brand-border bg-white px-2.5 py-1 text-xs font-medium text-brand-navy shadow-sm hover:border-brand-teal/50 hover:bg-slate-50 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal"
      >
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-teal text-[10px] font-bold text-white uppercase">
          {initialLetter}
        </span>
        <span className="font-semibold text-brand-navy">{activeProfile?.name || 'Chưa chọn'}</span>
        <span className="text-brand-muted">• {activeProfile?.heightCm}cm</span>
        <svg
          className={`h-3.5 w-3.5 text-brand-slate transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          role="listbox"
          className="absolute left-0 mt-1.5 w-60 rounded-16 border border-brand-border bg-white p-1.5 shadow-modal z-50 animate-in fade-in zoom-in-95 duration-100"
        >
          <div className="px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider text-brand-muted">
            Chọn Hồ Sơ Đo
          </div>

          <div className="flex flex-col gap-0.5 max-h-48 overflow-y-auto no-scrollbar">
            {profiles.map((profile) => {
              const isSelected = profile.id === activeProfile?.id;
              const letter = profile.name.charAt(0).toUpperCase();

              return (
                <button
                  key={profile.id}
                  type="button"
                  role="option"
                  aria-selected={isSelected}
                  onClick={() => {
                    onSelectProfile(profile.id);
                    setIsOpen(false);
                  }}
                  className={`flex w-full items-center justify-between rounded-12 px-2.5 py-2 text-xs transition-all text-left ${
                    isSelected
                      ? 'bg-brand-teal-subtle text-brand-navy font-semibold'
                      : 'text-brand-navy hover:bg-slate-50 font-medium'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={`flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-bold ${
                        isSelected ? 'bg-brand-teal text-white' : 'bg-slate-200 text-brand-slate'
                      }`}
                    >
                      {letter}
                    </span>
                    <div>
                      <div className="text-brand-navy">{profile.name}</div>
                      <div className="text-[10px] text-brand-muted">
                        {profile.heightCm}cm • {profile.weightKg}kg •{' '}
                        {profile.fitPreference === 'slim'
                          ? 'Ôm nhẹ'
                          : profile.fitPreference === 'relaxed'
                          ? 'Rộng rãi'
                          : 'Vừa vặn'}
                      </div>
                    </div>
                  </div>

                  {isSelected && (
                    <svg className="h-4 w-4 text-brand-teal" viewBox="0 0 20 20" fill="currentColor">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </button>
              );
            })}
          </div>

          {onAddProfile && (
            <div className="mt-1 border-t border-brand-border/60 pt-1">
              <button
                type="button"
                onClick={() => {
                  setIsOpen(false);
                  onAddProfile();
                }}
                className="flex w-full items-center gap-2 rounded-12 px-2.5 py-2 text-xs font-medium text-brand-teal hover:bg-brand-teal-subtle transition-all"
              >
                <svg className="h-4 w-4 stroke-current stroke-2 fill-none" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                <span>Thêm hồ sơ người thân...</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
