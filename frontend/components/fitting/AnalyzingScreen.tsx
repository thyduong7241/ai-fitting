'use client';

import React, { useEffect, useState } from 'react';

import { apiClient } from '@/services/apiClient';
import { BodyMeasurements, MeasurementResponse, UserProfile } from '@/types/fitting';

export interface AnalyzingScreenProps {
  frontImageUrl?: string;
  sideImageUrl?: string;
  activeProfile?: UserProfile;
  onBack?: () => void;
  onClose?: () => void;
  onComplete: (measureResponse?: MeasurementResponse) => void;
}

export function AnalyzingScreen({
  frontImageUrl,
  sideImageUrl,
  activeProfile,
  onBack,
  onClose,
  onComplete,
}: AnalyzingScreenProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isRetrying, setIsRetrying] = useState(0);

  const steps = [
    { title: 'Nhận diện nhân trắc học', desc: 'Trích xuất 33 mốc giải phẫu từ ảnh' },
    { title: 'Đối chiếu thông số phom áo', desc: 'So khớp kích thước vai, ngực, eo với size chart' },
    { title: 'Tính toán điểm Fit Score', desc: 'Tối ưu độ ôm theo gu mặc cá nhân' },
  ];

  useEffect(() => {
    let isCancelled = false;

    async function executeMeasurement() {
      setErrorMessage(null);
      setCurrentStepIndex(0);

      const t1 = setTimeout(() => {
        if (!isCancelled) setCurrentStepIndex(1);
      }, 700);

      const t2 = setTimeout(() => {
        if (!isCancelled) setCurrentStepIndex(2);
      }, 1400);

      try {
        if (!activeProfile) {
          throw new Error('Chưa có thông tin hồ sơ người dùng.');
        }

        const isFrontBase64 = frontImageUrl?.startsWith('data:');
        const isSideBase64 = sideImageUrl?.startsWith('data:');

        // Parallelize API call with minimum visual scan duration (1600ms) for smooth UX
        const [res] = await Promise.all([
          apiClient.estimateMeasurements({
            frontImageUrl: !isFrontBase64 ? (frontImageUrl || activeProfile.frontImageUrl) : undefined,
            frontImageBase64: isFrontBase64 ? frontImageUrl : undefined,
            sideImageUrl: !isSideBase64 ? (sideImageUrl || activeProfile.sideImageUrl) : undefined,
            sideImageBase64: isSideBase64 ? sideImageUrl : undefined,
            knownHeightCm: activeProfile.heightCm,
            weightKg: activeProfile.weightKg,
            age: activeProfile.age || 24,
            gender: activeProfile.gender,
          }),
          new Promise((resolve) => setTimeout(resolve, 1600)),
        ]);

        if (!isCancelled) {
          clearTimeout(t1);
          clearTimeout(t2);
          setCurrentStepIndex(3); // All complete

          setTimeout(() => {
            if (!isCancelled) {
              onComplete(res);
            }
          }, 350);
        }
      } catch (err: any) {
        if (!isCancelled) {
          clearTimeout(t1);
          clearTimeout(t2);
          const msg =
            err?.message ||
            'Không thể quét số đo từ ảnh. Vui lòng kiểm tra lại tư thế đứng hoặc chụp lại ảnh.';
          setErrorMessage(msg);
        }
      }
    }

    executeMeasurement();

    return () => {
      isCancelled = true;
    };
  }, [activeProfile, frontImageUrl, onComplete, sideImageUrl, isRetrying]);

  return (
    <div className="relative flex flex-1 flex-col items-center justify-center p-6 bg-brand-canvas text-center select-none animate-in fade-in duration-300">
      {/* Top Bar with Back and Exit (Close) Buttons */}
      <div className="absolute top-0 left-0 right-0 flex items-center justify-between p-4">
        {onBack ? (
          <button
            type="button"
            onClick={onBack}
            className="flex h-9 w-9 items-center justify-center rounded-full text-brand-slate hover:bg-slate-100 active:scale-95 transition-all focus-visible:outline-none"
            aria-label="Quay lại"
          >
            <svg className="h-5 w-5 stroke-current fill-none stroke-[2.2]" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        ) : (
          <div className="w-9" />
        )}

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-full text-brand-slate hover:bg-slate-100 active:scale-95 transition-all focus-visible:outline-none"
            aria-label="Hủy và thoát"
          >
            <svg className="h-5 w-5 stroke-current fill-none stroke-[2]" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {errorMessage ? (
        /* Error State Card */
        <div className="flex flex-col items-center max-w-[320px] rounded-24 border border-rose-200 bg-white p-5 shadow-card animate-in zoom-in-95">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600 mb-3">
            <svg className="h-6 w-6 stroke-current fill-none stroke-2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <h3 className="text-sm font-bold text-rose-950 mb-1">Không Thể Trích Xuất Số Đo</h3>
          <p className="text-xs text-rose-800/80 text-center mb-4 leading-relaxed">
            {errorMessage}
          </p>

          <div className="flex flex-col w-full gap-2">
            <button
              type="button"
              onClick={() => setIsRetrying((v) => v + 1)}
              className="w-full rounded-12 bg-brand-teal py-2.5 text-xs font-bold text-white hover:bg-brand-teal-dark active:scale-[0.98] transition-all"
            >
              Thử Lại Quét Ảnh
            </button>
            {onBack && (
              <button
                type="button"
                onClick={onBack}
                className="w-full rounded-12 border border-slate-200 bg-white py-2 text-xs font-semibold text-brand-slate hover:bg-slate-50 transition-all"
              >
                Chụp Hoặc Chọn Ảnh Khác
              </button>
            )}
            <button
              type="button"
              onClick={() => onComplete(undefined)}
              className="text-[11px] text-brand-muted hover:text-brand-slate underline py-1"
            >
              Tiếp tục với số đo ước lượng cơ bản
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Radar Pulse Animation Graphic */}
          <div className="relative mb-8 flex h-44 w-44 items-center justify-center">
            {/* Outer expanding ripple */}
            <div className="absolute inset-0 rounded-full border border-brand-teal/30 animate-ping opacity-75" />
            {/* Middle pulsing ring */}
            <div className="absolute inset-3 rounded-full border-2 border-brand-teal/40 animate-pulse bg-brand-teal-subtle/40" />
            {/* Inner rotating radar sweep */}
            <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-brand-teal shadow-widget text-white">
              <svg className="h-10 w-10 animate-spin fill-none stroke-current stroke-2 duration-1000" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" />
              </svg>
            </div>
          </div>

          <h2 className="text-lg font-bold text-brand-navy tracking-tight">
            AI Đang Quét Vóc Dáng...
          </h2>
          <p className="mt-1 text-xs text-brand-slate max-w-[260px]">
            Thuật toán phân tích nhân trắc học đang tìm kiếm kích cỡ hoàn hảo nhất cho bạn.
          </p>

          {/* 3 Sequential Progress Steps */}
          <div className="mt-8 flex w-full max-w-[320px] flex-col gap-2.5 text-left">
            {steps.map((step, idx) => {
              const isDone = idx < currentStepIndex;
              const isCurrent = idx === currentStepIndex;

              return (
                <div
                  key={step.title}
                  className={`flex items-center gap-3 rounded-16 border p-2.5 transition-all duration-300 ${
                    isCurrent
                      ? 'border-brand-teal bg-white shadow-card scale-[1.02]'
                      : isDone
                      ? 'border-emerald-200 bg-emerald-50/60 opacity-90'
                      : 'border-slate-200/60 bg-white/60 opacity-40'
                  }`}
                >
                  <div
                    className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold transition-colors ${
                      isDone
                        ? 'bg-emerald-500 text-white'
                        : isCurrent
                        ? 'bg-brand-teal text-white animate-pulse'
                        : 'bg-slate-200 text-brand-slate'
                    }`}
                  >
                    {isDone ? '✓' : idx + 1}
                  </div>

                  <div className="flex flex-col">
                    <span className={`text-xs font-bold ${isCurrent ? 'text-brand-navy' : isDone ? 'text-emerald-900' : 'text-brand-slate'}`}>
                      {step.title}
                    </span>
                    <span className="text-[10px] text-brand-muted line-clamp-1">
                      {step.desc}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
