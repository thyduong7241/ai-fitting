'use client';

import React, { useState } from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Button } from '@/components/ui/Button';
import { SegmentedControl } from '@/components/ui/SegmentedControl';
import { StepperInput } from '@/components/ui/StepperInput';
import { CreateFitProfileRequest, Gender, FitPreference, UserProfile } from '@/types/fitting';

export interface ProfileSetupScreenProps {
  initialProfile?: Partial<UserProfile>;
  onBack: () => void;
  onSubmit: (data: CreateFitProfileRequest) => void;
}

export function ProfileSetupScreen({
  initialProfile,
  onBack,
  onSubmit,
}: ProfileSetupScreenProps) {
  const [name, setName] = useState(initialProfile?.name || 'Tôi');
  const [gender, setGender] = useState<Gender>(initialProfile?.gender || 'female');
  const [fitPreference, setFitPreference] = useState<FitPreference>(initialProfile?.fitPreference || 'regular');
  const [heightCm, setHeightCm] = useState(initialProfile?.heightCm || 162);
  const [weightKg, setWeightKg] = useState(initialProfile?.weightKg || 50);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      name: name.trim() || 'Tôi',
      gender,
      fitPreference,
      heightCm,
      weightKg,
    });
  };

  return (
    <div className="flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200">
      <StepHeader
        title="Thiết Lập Vóc Dáng"
        subtitle="Thông số cơ bản giúp AI tính toán tỷ lệ nhân trắc học"
        currentStep={1}
        totalSteps={3}
        onBack={onBack}
      />

      <form onSubmit={handleSubmit} className="flex flex-1 flex-col justify-between p-5">
        <div className="flex flex-col gap-4">
          {/* Profile Name Input */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="profile-name" className="text-xs font-semibold uppercase tracking-wider text-brand-slate">
              Tên Hồ Sơ (Cho bạn hoặc người thân)
            </label>
            <input
              id="profile-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="VD: Trang, Minh, Em gái..."
              maxLength={30}
              required
              className="h-11 w-full rounded-16 border border-brand-border bg-white px-4 text-sm font-medium text-brand-navy placeholder:text-brand-muted/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal transition-all"
            />
          </div>

          {/* Gender Selection */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-brand-slate">
              Giới Tính
            </label>
            <SegmentedControl<Gender>
              name="gender-select"
              value={gender}
              onChange={setGender}
              options={[
                { label: 'Nữ', value: 'female' },
                { label: 'Nam', value: 'male' },
              ]}
            />
          </div>

          {/* Stepper Inputs for Height and Weight */}
          <div className="grid grid-cols-2 gap-3">
            <StepperInput
              label="Chiều cao"
              value={heightCm}
              unit="cm"
              min={100}
              max={230}
              step={1}
              onChange={setHeightCm}
            />
            <StepperInput
              label="Cân nặng"
              value={weightKg}
              unit="kg"
              min={30}
              max={180}
              step={0.5}
              onChange={setWeightKg}
            />
          </div>

          {/* Fit Preference Selection */}
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold uppercase tracking-wider text-brand-slate">
                Gu Mặc Thường Ngày
              </label>
              <span className="text-[11px] text-brand-muted">
                {fitPreference === 'slim' ? 'Ôm sát tôn dáng' : fitPreference === 'relaxed' ? 'Thoải mái che khuyết điểm' : 'Vừa vặn chuẩn thiết kế'}
              </span>
            </div>
            <SegmentedControl<FitPreference>
              name="fit-pref-select"
              value={fitPreference}
              onChange={setFitPreference}
              options={[
                { label: 'Ôm nhẹ', value: 'slim' },
                { label: 'Vừa vặn', value: 'regular' },
                { label: 'Rộng rãi', value: 'relaxed' },
              ]}
            />
          </div>
        </div>

        {/* Submit Action */}
        <div className="pt-4 mt-auto">
          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            rightIcon={
              <svg className="h-4 w-4 stroke-current stroke-2 fill-none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            }
          >
            Tiếp Tục Chọn Phương Thức Đo
          </Button>
        </div>
      </form>
    </div>
  );
}
