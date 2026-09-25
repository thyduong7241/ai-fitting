'use client';

import React, { useState } from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Button } from '@/components/ui/Button';
import { StepperInput } from '@/components/ui/StepperInput';
import { BodyMeasurements, UserProfile } from '@/types/fitting';

export interface ManualInputScreenProps {
  activeProfile: UserProfile;
  onBack: () => void;
  onSubmit: (measurements: BodyMeasurements) => void;
}

export function ManualInputScreen({
  activeProfile,
  onBack,
  onSubmit,
}: ManualInputScreenProps) {
  const [unit, setUnit] = useState<'cm' | 'inch'>('cm');

  // Stored internally in cm
  const [heightCm, setHeightCm] = useState(activeProfile.heightCm || 162);
  const [weightKg, setWeightKg] = useState(activeProfile.weightKg || 50);
  const [chestCm, setChestCm] = useState(activeProfile.chestCm || 84);
  const [waistCm, setWaistCm] = useState(activeProfile.waistCm || 65);
  const [hipsCm, setHipsCm] = useState(activeProfile.hipsCm || 90);
  const [shoulderCm, setShoulderCm] = useState(activeProfile.shoulderCm || 38);

  const displayFactor = unit === 'inch' ? 0.3937 : 1;
  const toDisplay = (cm: number) => Number((cm * displayFactor).toFixed(1));
  const fromDisplay = (val: number) => unit === 'inch' ? Number((val / displayFactor).toFixed(1)) : val;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      heightCm,
      weightKg,
      chestCm,
      waistCm,
      hipsCm,
      shoulderCm,
    });
  };

  return (
    <div className="flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200">
      <StepHeader
        title="Nhập Số Đo Cơ Thể"
        subtitle="Dùng thước dây đo các vòng để nhận gợi ý chuẩn xác nhất"
        currentStep={2}
        totalSteps={3}
        onBack={onBack}
      />

      <form onSubmit={handleSubmit} className="flex flex-1 flex-col justify-between p-5 overflow-y-auto no-scrollbar">
        <div className="flex flex-col gap-4">
          {/* Unit Toggle cm vs inch */}
          <div className="flex items-center justify-between rounded-16 border border-slate-200 bg-white p-2">
            <span className="text-xs font-semibold text-brand-slate">Đơn vị đo:</span>
            <div className="flex gap-1">
              <button
                type="button"
                onClick={() => setUnit('cm')}
                className={`rounded-12 px-3 py-1 text-xs font-semibold transition-all ${
                  unit === 'cm'
                    ? 'bg-brand-teal text-white shadow-sm'
                    : 'bg-slate-100 text-brand-slate hover:bg-slate-200'
                }`}
              >
                Centimet (cm)
              </button>
              <button
                type="button"
                onClick={() => setUnit('inch')}
                className={`rounded-12 px-3 py-1 text-xs font-semibold transition-all ${
                  unit === 'inch'
                    ? 'bg-brand-teal text-white shadow-sm'
                    : 'bg-slate-100 text-brand-slate hover:bg-slate-200'
                }`}
              >
                Inches (in)
              </button>
            </div>
          </div>

          {/* Stepper Inputs for 6 Body Dimensions */}
          <div className="grid grid-cols-2 gap-3">
            <StepperInput
              label="Chiều cao"
              value={toDisplay(heightCm)}
              unit={unit}
              min={unit === 'cm' ? 100 : 40}
              max={unit === 'cm' ? 240 : 95}
              step={1}
              onChange={(val) => setHeightCm(fromDisplay(val))}
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
              value={toDisplay(chestCm)}
              unit={unit}
              min={unit === 'cm' ? 60 : 24}
              max={unit === 'cm' ? 150 : 60}
              step={0.5}
              onChange={(val) => setChestCm(fromDisplay(val))}
            />
            <StepperInput
              label="Vòng Eo"
              value={toDisplay(waistCm)}
              unit={unit}
              min={unit === 'cm' ? 50 : 20}
              max={unit === 'cm' ? 140 : 55}
              step={0.5}
              onChange={(val) => setWaistCm(fromDisplay(val))}
            />
            <StepperInput
              label="Vòng Hông"
              value={toDisplay(hipsCm)}
              unit={unit}
              min={unit === 'cm' ? 65 : 26}
              max={unit === 'cm' ? 160 : 65}
              step={0.5}
              onChange={(val) => setHipsCm(fromDisplay(val))}
            />
            <StepperInput
              label="Rộng Vai"
              value={toDisplay(shoulderCm)}
              unit={unit}
              min={unit === 'cm' ? 30 : 12}
              max={unit === 'cm' ? 65 : 26}
              step={0.5}
              onChange={(val) => setShoulderCm(fromDisplay(val))}
            />
          </div>

          <div className="rounded-16 bg-[#EEF5F7] p-3 text-center text-[11px] text-brand-slate">
            💡 <strong>Mẹo:</strong> Đo ngực tại điểm nhô cao nhất, eo tại điểm hẹp nhất và hông tại điểm nở nhất.
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
            Tính Toán Độ Vừa Vặn & Gợi Ý Size
          </Button>
        </div>
      </form>
    </div>
  );
}
