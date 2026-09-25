'use client';

import React from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { UserProfile } from '@/types/fitting';

export interface ProfileListScreenProps {
  profiles: UserProfile[];
  activeProfile: UserProfile;
  onSelectProfile: (id: string) => void;
  onViewDetail: (profile: UserProfile) => void;
  onAddNew: () => void;
  onDeleteProfile: (id: string) => void;
  onBack: () => void;
}

export function ProfileListScreen({
  profiles,
  activeProfile,
  onSelectProfile,
  onViewDetail,
  onAddNew,
  onDeleteProfile,
  onBack,
}: ProfileListScreenProps) {
  return (
    <div className="flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200">
      <StepHeader
        title="Danh Sách Hồ Sơ Đo"
        subtitle="Quản lý hồ sơ vóc dáng của bạn và người thân"
        onBack={onBack}
      />

      <div className="flex flex-1 flex-col justify-between p-5 overflow-y-auto no-scrollbar">
        <div className="flex flex-col gap-3">
          {profiles.map((profile) => {
            const isActive = profile.id === activeProfile?.id;
            const initial = profile.name.charAt(0).toUpperCase();

            return (
              <div
                key={profile.id}
                className={`flex flex-col gap-3 rounded-20 border p-4 transition-all ${
                  isActive
                    ? 'border-brand-teal bg-white shadow-card'
                    : 'border-brand-border/70 bg-white/80 hover:border-brand-border'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span
                      className={`flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold ${
                        isActive
                          ? 'bg-brand-teal text-white shadow-sm'
                          : 'bg-slate-200 text-brand-slate'
                      }`}
                    >
                      {initial}
                    </span>

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-brand-navy">
                          {profile.name}
                        </span>
                        {isActive && (
                          <Badge variant="brand" size="sm">
                            ĐANG CHỌN
                          </Badge>
                        )}
                        {profile.isDefault && (
                          <span className="rounded bg-slate-100 px-1.5 py-0.2 text-[10px] font-semibold text-brand-muted">
                            Mặc định
                          </span>
                        )}
                      </div>

                      <div className="text-xs text-brand-slate mt-0.5">
                        {profile.heightCm}cm • {profile.weightKg}kg •{' '}
                        {profile.gender === 'female' ? 'Nữ' : 'Nam'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Profile Action Buttons */}
                <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                  {profiles.length > 1 && (
                    <button
                      type="button"
                      onClick={() => onDeleteProfile(profile.id)}
                      className="px-2.5 py-1 text-xs font-semibold text-rose-500 hover:bg-rose-50 rounded-12 transition-all"
                    >
                      Xóa
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => onViewDetail(profile)}
                    className="px-2.5 py-1 text-xs font-semibold text-brand-slate hover:bg-slate-100 rounded-12 transition-all"
                  >
                    Xem Chi Tiết Số Đo
                  </button>
                  {!isActive && (
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => onSelectProfile(profile.id)}
                    >
                      Chọn Hồ Sơ Này
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Add New Profile Button */}
        <div className="pt-4 mt-auto">
          <Button
            variant="outline"
            size="lg"
            fullWidth
            onClick={onAddNew}
            leftIcon={
              <svg className="h-5 w-5 stroke-current stroke-2 fill-none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
            }
          >
            Thêm Hồ Sơ Mới
          </Button>
        </div>
      </div>
    </div>
  );
}
