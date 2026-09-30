'use client';

import React, { useState } from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Button } from '@/components/ui/Button';
import { StepperInput } from '@/components/ui/StepperInput';
import { SegmentedControl } from '@/components/ui/SegmentedControl';
import { Gender, UserProfile } from '@/types/fitting';

export interface BodyMetricsInputScreenProps {
  initialProfile: UserProfile;
  onBack: () => void;
  onClose?: () => void;
  onSubmit: (data: {
    gender: Gender;
    heightCm: number;
    weightKg: number;
    age: number;
  }) => void;
}

export function BodyMetricsInputScreen({
  initialProfile,
  onBack,
  onClose,
  onSubmit,
}: BodyMetricsInputScreenProps) {
  const [gender, setGender] = useState<Gender>(initialProfile.gender || 'male');
  const [heightCm, setHeightCm] = useState<number>(initialProfile.heightCm || 170);
  const [weightKg, setWeightKg] = useState<number>(initialProfile.weightKg || 60);
  const [age, setAge] = useState<number>(initialProfile.age || 24);

  // Compute live BMI preview for user feedback
  const heightM = heightCm / 100.0;
  const bmi = heightM > 0 ? (weightKg / (heightM * heightM)).toFixed(1) : '21.0';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      gender,
      heightCm,
      weightKg,
      age,
    });
  };

  return (
    <div className="flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200">
      <StepHeader
        title="Thông Số Nhân Trắc Học"
        subtitle="Cung cấp chỉ số để AI hiệu chuẩn kích thước chính xác từ ảnh"
        onBack={onBack}
        onClose={onClose}
      />

      <form
        onSubmit={handleSubmit}
        className="flex flex-1 flex-col justify-between p-5 overflow-y-auto no-scrollbar"
      >
        <div className="flex flex-col gap-4">
          {/* Informative Hint Banner */}
          <div className="flex items-start gap-3 rounded-20 bg-gradient-to-r from-brand-teal/10 to-transparent p-3.5 border border-brand-teal/20">
            <span className="text-xl">📏</span>
            <div className="flex flex-col text-xs text-brand-slate">
              <span className="font-bold text-brand-navy">
                Mốc hiệu chuẩn kích thước (P2M Calibration)
              </span>
              <span className="mt-0.5 leading-relaxed text-[11px]">
                Chiều cao thực tế được dùng để chuyển đổi pixel ảnh thành centimet. Cân nặng và tuổi giúp AI hiệu chuẩn thể tích cơ thể và lọc sai số quần áo phồng.
              </span>
            </div>
          </div>

          {/* 1. Giới tính sinh học */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-brand-slate">
              Giới Tính Sinh Học
            </label>
            <SegmentedControl
              options={[
                { value: 'male', label: 'Nam' },
                { value: 'female', label: 'Nữ' },
              ]}
              value={gender}
              onChange={(val) => setGender(val as Gender)}
            />
          </div>

          {/* 2. Chiều cao & Cân nặng (2 cột) */}
          <div className="grid grid-cols-2 gap-3">
            <StepperInput
              label="Chiều cao"
              value={heightCm}
              unit="cm"
              min={120}
              max={230}
              step={1}
              onChange={setHeightCm}
            />
            <StepperInput
              label="Cân nặng"
              value={weightKg}
              unit="kg"
              min={30}
              max={160}
              step={0.5}
              onChange={setWeightKg}
            />
          </div>

          {/* 3. Độ tuổi & Chỉ số BMI tự động */}
          <div className="grid grid-cols-2 gap-3">
            <StepperInput
              label="Độ tuổi"
              value={age}
              unit="tuổi"
              min={14}
              max={90}
              step={1}
              onChange={setAge}
            />

            <div className="flex flex-col justify-center rounded-20 border border-slate-200/80 bg-white p-3 shadow-card text-center">
              <span className="text-[10px] uppercase font-bold text-brand-muted tracking-wider">
                Chỉ Số Khối (BMI)
              </span>
              <div className="flex items-baseline justify-center gap-1 mt-1">
                <span className="text-xl font-black text-brand-teal">
                  {bmi}
                </span>
                <span className="text-[10px] text-brand-slate font-medium">kg/m²</span>
              </div>
              <span className="text-[10px] text-emerald-600 font-semibold mt-0.5">
                {parseFloat(bmi) < 18.5 ? 'Gầy nhẹ' : parseFloat(bmi) <= 24.9 ? 'Cân đối chuẩn' : 'Hơi đầy đặn'}
              </span>
            </div>
          </div>
        </div>

        {/* Footer Submit CTA & Navigation Actions */}
        <div className="flex flex-col gap-2 pt-4 border-t border-brand-border/60">
          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
          >
            Tiếp Tục: Hướng Dẫn Chụp Ảnh AI →
          </Button>

          <div className="flex items-center justify-between px-1 pt-1 text-xs">
            <button
              type="button"
              onClick={onBack}
              className="flex items-center gap-1 font-semibold text-brand-slate hover:text-brand-navy active:scale-95 transition-all"
            >
              <span>←</span>
              <span>Quay lại</span>
            </button>
            {onClose && (
              <button
                type="button"
                onClick={onClose}
                className="flex items-center gap-1 font-semibold text-rose-500 hover:text-rose-600 active:scale-95 transition-all"
              >
                <span>✕</span>
                <span>Thoát quy trình</span>
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}
