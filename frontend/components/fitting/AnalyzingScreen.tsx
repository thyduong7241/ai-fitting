'use client';

import React, { useEffect, useState } from 'react';

export interface AnalyzingScreenProps {
  onComplete: () => void;
}

export function AnalyzingScreen({ onComplete }: AnalyzingScreenProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  const steps = [
    { title: 'Nhận diện nhân trắc học', desc: 'Trích xuất 33 mốc giải phẫu từ ảnh' },
    { title: 'Đối chiếu thông số phom áo', desc: 'So khớp kích thước vai, ngực, eo với size chart' },
    { title: 'Tính toán điểm Fit Score', desc: 'Tối ưu độ ôm theo gu mặc cá nhân' },
  ];

  useEffect(() => {
    // Timer 1: Advance to step 1
    const t1 = setTimeout(() => {
      setCurrentStepIndex(1);
    }, 800);

    // Timer 2: Advance to step 2
    const t2 = setTimeout(() => {
      setCurrentStepIndex(2);
    }, 1600);

    // Timer 3: Complete analysis
    const t3 = setTimeout(() => {
      onComplete();
    }, 2500);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [onComplete]);

  return (
    <div className="flex flex-1 flex-col items-center justify-center p-6 bg-brand-canvas text-center select-none animate-in fade-in duration-300">
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
    </div>
  );
}
