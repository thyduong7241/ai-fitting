'use client';

import React, { useState } from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Button } from '@/components/ui/Button';
import { StepperInput } from '@/components/ui/StepperInput';
import { UserProfile } from '@/types/fitting';

export interface ProfileDetailScreenProps {
  profile: UserProfile;
  onBack: () => void;
  onSave: (updates: Partial<UserProfile>) => void;
}

export function ProfileDetailScreen({
  profile,
  onBack,
  onSave,
}: ProfileDetailScreenProps) {
  const [name, setName] = useState(profile.name);
  const [heightCm, setHeightCm] = useState(profile.heightCm);
  const [weightKg, setWeightKg] = useState(profile.weightKg);
  const [chestCm, setChestCm] = useState(profile.chestCm || 84);
  const [waistCm, setWaistCm] = useState(profile.waistCm || 65);
  const [hipsCm, setHipsCm] = useState(profile.hipsCm || 90);
  const [shoulderCm, setShoulderCm] = useState(profile.shoulderCm || 38);
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      name,
      heightCm,
      weightKg,
      chestCm,
      waistCm,
      hipsCm,
      shoulderCm,
    });
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  return (
    <div className="flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200">
      <StepHeader
        title={`Chi Tiết: ${profile.name}`}
        subtitle="Xem và cập nhật số đo nhân trắc học"
        onBack={onBack}
      />

      <form onSubmit={handleSave} className="flex flex-1 flex-col justify-between p-5 overflow-y-auto no-scrollbar">
        <div className="flex flex-col gap-4">
          {/* Profile Name Edit */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-brand-slate">
              Tên Hồ Sơ
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="h-11 w-full rounded-16 border border-brand-border bg-white px-4 text-sm font-medium text-brand-navy focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal transition-all"
            />
          </div>

          {/* Measurements Stepper Grid */}
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
            <StepperInput
              label="Vòng Ngực"
              value={chestCm}
              unit="cm"
              min={60}
              max={150}
              step={0.5}
              onChange={setChestCm}
            />
            <StepperInput
              label="Vòng Eo"
              value={waistCm}
              unit="cm"
              min={50}
              max={140}
              step={0.5}
              onChange={setWaistCm}
            />
            <StepperInput
              label="Vòng Hông"
              value={hipsCm}
              unit="cm"
              min={65}
              max={160}
              step={0.5}
              onChange={setHipsCm}
            />
            <StepperInput
              label="Rộng Vai"
              value={shoulderCm}
              unit="cm"
              min={30}
              max={65}
              step={0.5}
              onChange={setShoulderCm}
            />
          </div>
        </div>

        {/* Save Button */}
        <div className="pt-4 mt-auto">
          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
          >
            {isSaved ? '✓ Đã Lưu Thành Công' : 'Lưu Thay Đổi Số Đo'}
          </Button>
        </div>
      </form>
    </div>
  );
}
