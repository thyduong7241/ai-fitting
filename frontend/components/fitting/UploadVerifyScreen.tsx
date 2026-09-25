'use client';

import React, { useState } from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { QualityCheckResponse } from '@/types/fitting';

export interface UploadVerifyScreenProps {
  frontImageUrl: string;
  sideImageUrl?: string;
  onBack: () => void;
  onConfirm: (result: QualityCheckResponse) => void;
  onRetake: () => void;
}

export function UploadVerifyScreen({
  frontImageUrl,
  onBack,
  onConfirm,
  onRetake,
}: UploadVerifyScreenProps) {
  // Mode switcher for testing: valid (success) vs feet_cut_off (error simulation)
  const [simulateError, setSimulateError] = useState(false);

  const validResponse: QualityCheckResponse = {
    isValid: true,
    confidenceScore: 0.96,
    blurScore: 185.4,
    landmarksDetected: 33,
    issues: [],
  };

  const errorResponse: QualityCheckResponse = {
    isValid: false,
    confidenceScore: 0.42,
    blurScore: 160.0,
    landmarksDetected: 24,
    issues: [
      {
        code: 'feet_cut_off',
        severity: 'error',
        message: 'Bàn chân bị cắt khỏi khung hình. Vui lòng lùi xa camera khoảng 2-3 bước để thấy trọn vẹn từ đầu đến chân.',
        box: [0.85, 0.2, 1.0, 0.8],
      },
    ],
  };

  const currentResult = simulateError ? errorResponse : validResponse;

  return (
    <div className="flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200">
      <StepHeader
        title="Thẩm Định Chất Lượng Ảnh"
        subtitle="Hệ thống AI Quality Gate kiểm tra độ nét và khung hình"
        currentStep={2}
        totalSteps={3}
        onBack={onBack}
      />

      <div className="flex flex-1 flex-col justify-between p-5 overflow-y-auto no-scrollbar">
        <div className="flex flex-col gap-4">
          {/* Simulation Toggle for Reviewers / Dev Testing */}
          <div className="flex items-center justify-between rounded-16 border border-slate-200 bg-white p-2.5">
            <span className="text-xs font-semibold text-brand-slate">
              Chế độ thẩm định (Dev Demo):
            </span>
            <div className="flex gap-1">
              <button
                type="button"
                onClick={() => setSimulateError(false)}
                className={`rounded-12 px-2.5 py-1 text-xs font-semibold transition-all ${
                  !simulateError
                    ? 'bg-emerald-500 text-white shadow-sm'
                    : 'bg-slate-100 text-brand-slate hover:bg-slate-200'
                }`}
              >
                ✓ Đạt chuẩn
              </button>
              <button
                type="button"
                onClick={() => setSimulateError(true)}
                className={`rounded-12 px-2.5 py-1 text-xs font-semibold transition-all ${
                  simulateError
                    ? 'bg-rose-500 text-white shadow-sm'
                    : 'bg-slate-100 text-brand-slate hover:bg-slate-200'
                }`}
              >
                ✕ Lỗi cắt chân
              </button>
            </div>
          </div>

          {/* Photo Inspection Canvas Frame */}
          <div className="relative mx-auto flex h-72 w-52 overflow-hidden rounded-24 border-2 border-brand-border bg-slate-900 shadow-widget">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={frontImageUrl}
              alt="Ảnh đang kiểm định"
              className={`h-full w-full object-cover object-top transition-all ${
                simulateError ? 'translate-y-4 scale-105' : ''
              }`}
            />

            {/* Error Bounding Box Overlay if feet_cut_off */}
            {simulateError && (
              <div
                className="absolute inset-x-2 bottom-2 h-16 rounded-12 border-2 border-dashed border-rose-500 bg-rose-500/20 backdrop-blur-[1px] flex items-center justify-center animate-pulse"
                aria-hidden="true"
              >
                <span className="rounded bg-rose-600 px-2 py-0.5 text-[10px] font-bold text-white shadow">
                  Bàn chân bị cắt mép
                </span>
              </div>
            )}

            {/* AI Landmarks Detection Indicator */}
            <div className="absolute top-2.5 left-2.5 flex items-center gap-1.5 rounded-full bg-black/60 backdrop-blur-md px-2.5 py-1 text-[11px] font-semibold text-white">
              <span className={`h-2 w-2 rounded-full ${currentResult.isValid ? 'bg-emerald-400 animate-ping' : 'bg-rose-400'}`} />
              <span>{currentResult.landmarksDetected}/33 Landmarks</span>
            </div>
          </div>

          {/* Inspection Result Verdict Card */}
          {currentResult.isValid ? (
            <div className="rounded-20 border border-emerald-200 bg-emerald-50/70 p-3.5 shadow-card">
              <div className="flex items-center gap-2">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-500 text-white font-bold text-sm">
                  ✓
                </span>
                <div>
                  <h4 className="text-xs font-bold text-emerald-900">
                    Ảnh Đạt Tiêu Chuẩn Thẩm Định
                  </h4>
                  <p className="text-[11px] text-emerald-700">
                    Độ nét đạt {currentResult.blurScore} điểm • Nhận diện đủ 33 mốc cơ thể
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-20 border border-rose-200 bg-rose-50 p-3.5 shadow-card">
              <div className="flex items-start gap-2">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-rose-500 text-white font-bold text-sm">
                  ✕
                </span>
                <div>
                  <h4 className="text-xs font-bold text-rose-900">
                    Phát Hiện Lỗi Tư Thế Chụp
                  </h4>
                  <p className="mt-0.5 text-xs text-rose-700 leading-relaxed">
                    {currentResult.issues[0]?.message}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Bottom Actions */}
        <div className="flex flex-col gap-2 pt-4 mt-auto">
          {currentResult.isValid ? (
            <Button
              variant="primary"
              size="lg"
              fullWidth
              onClick={() => onConfirm(currentResult)}
              rightIcon={
                <svg className="h-4 w-4 stroke-current stroke-2 fill-none" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              }
            >
              Tiến Hành Quét Số Đo Cơ Thể
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="md"
                className="flex-1"
                onClick={onRetake}
              >
                Chụp Lại Ảnh
              </Button>
              <Button
                variant="primary"
                size="md"
                className="flex-1"
                onClick={() => setSimulateError(false)}
              >
                Dùng Ảnh Mẫu Chuẩn
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
