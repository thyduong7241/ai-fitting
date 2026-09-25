'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Garment, UserProfile } from '@/types/fitting';

export type VTOState =
  | 'ready'
  | 'queued'
  | 'processing'
  | 'completed'
  | 'bad_quality'
  | 'service_unavailable'
  | 'out_of_vram'
  | 'garment_mismatch';

export interface VTOPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  garment: Garment;
  profile: UserProfile;
}

export function VTOPreviewModal({
  isOpen,
  onClose,
  garment,
  profile,
}: VTOPreviewModalProps) {
  const [vtoState, setVtoState] = useState<VTOState>('ready');
  const [showOriginal, setShowOriginal] = useState(false);
  const [progress, setProgress] = useState(0);

  // Simulated VTO generation cycle
  const handleStartTryOn = () => {
    setVtoState('queued');
    setProgress(10);

    setTimeout(() => {
      setVtoState('processing');
      setProgress(40);
    }, 1500);

    setTimeout(() => {
      setProgress(75);
    }, 3000);

    setTimeout(() => {
      setProgress(100);
      setVtoState('completed');
    }, 4500);
  };

  useEffect(() => {
    if (!isOpen) {
      setVtoState('ready');
      setShowOriginal(false);
      setProgress(0);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="vto-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200"
    >
      <div className="relative flex h-full max-h-[750px] w-full max-w-[390px] flex-col overflow-hidden rounded-[28px] border border-brand-border bg-white shadow-modal">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-brand-border/60 px-5 py-3 bg-white">
          <div className="flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-brand-teal text-white">
              <svg className="h-3.5 w-3.5 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </span>
            <h3 id="vto-modal-title" className="text-sm font-bold text-brand-navy">
              Thử Đồ Ảo (Virtual Try-On)
            </h3>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full text-brand-slate hover:bg-slate-100 active:scale-95 transition-all"
            aria-label="Đóng cửa sổ thử đồ"
          >
            <svg className="h-4 w-4 stroke-current stroke-2 fill-none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* State Simulator Bar for Testing / Demos */}
        <div className="flex items-center gap-1 overflow-x-auto no-scrollbar border-b border-slate-100 bg-slate-50 px-3 py-1.5 text-[10px]">
          <span className="font-semibold text-brand-muted shrink-0">Demo:</span>
          {(['ready', 'queued', 'processing', 'completed', 'bad_quality', 'service_unavailable'] as VTOState[]).map(
            (st) => (
              <button
                key={st}
                type="button"
                onClick={() => setVtoState(st)}
                className={`rounded-full px-2 py-0.5 font-medium shrink-0 transition-all ${
                  vtoState === st
                    ? 'bg-brand-teal text-white font-bold'
                    : 'bg-white text-brand-slate border border-slate-200 hover:bg-slate-100'
                }`}
              >
                {st}
              </button>
            )
          )}
        </div>

        {/* Body Area with 8 Distinct State Views */}
        <div className="flex flex-1 flex-col items-center justify-center p-5 overflow-y-auto no-scrollbar">
          {/* STATE 1: READY / EMPTY */}
          {vtoState === 'ready' && (
            <div className="flex flex-col items-center text-center my-auto">
              <div className="relative mb-4 flex h-60 w-44 overflow-hidden rounded-20 border-2 border-brand-teal/40 bg-slate-100 shadow-card">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={profile.frontImageUrl || '/mock/profile_trang_front.png'}
                  alt={profile.name}
                  className="h-full w-full object-cover object-top"
                />
                <Badge
                  variant="brand"
                  size="sm"
                  className="absolute bottom-2 left-2"
                >
                  {profile.name} • {profile.heightCm}cm
                </Badge>
              </div>

              <h4 className="text-base font-bold text-brand-navy">
                Sẵn Sàng Mặc Thử Áo Lên Người
              </h4>
              <p className="mt-1 text-xs text-brand-slate max-w-[280px]">
                Mô hình CatVTON sẽ mô phỏng chiếc <strong className="text-brand-navy font-semibold">{garment.name}</strong> lên vóc dáng thực tế của bạn.
              </p>
            </div>
          )}

          {/* STATE 2: QUEUED */}
          {vtoState === 'queued' && (
            <div className="flex flex-col items-center text-center my-auto animate-pulse">
              <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-amber-50 border-2 border-amber-200 text-amber-600">
                <svg className="h-10 w-10 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <Badge variant="tight" size="md">Vị trí #1 trong hàng đợi</Badge>
              <h4 className="mt-3 text-base font-bold text-brand-navy">
                Đang Xếp Hàng Xử Lý...
              </h4>
              <p className="mt-1 text-xs text-brand-slate max-w-[260px]">
                Máy chủ GPU đang chuẩn bị tài nguyên. Thời gian chờ ước tính: ~12 giây.
              </p>
            </div>
          )}

          {/* STATE 3: PROCESSING */}
          {vtoState === 'processing' && (
            <div className="flex flex-col items-center text-center my-auto">
              <div className="relative mb-5 flex h-24 w-24 items-center justify-center">
                <div className="absolute inset-0 rounded-full border-4 border-brand-teal/20" />
                <div className="absolute inset-0 rounded-full border-4 border-brand-teal border-t-transparent animate-spin" />
                <span className="text-lg font-extrabold text-brand-teal">{progress}%</span>
              </div>
              <h4 className="text-base font-bold text-brand-navy">
                AI Đang Mặc Thử Áo...
              </h4>
              <p className="mt-1 text-xs text-brand-slate max-w-[260px]">
                Đang căn chỉnh tỷ lệ vai, độ rủ của nếp vải và tạo ánh sáng chân thực.
              </p>
            </div>
          )}

          {/* STATE 4: COMPLETED (SUCCESS) */}
          {vtoState === 'completed' && (
            <div className="flex flex-col items-center w-full my-auto">
              {/* Canvas Preview Container */}
              <div className="relative mx-auto flex h-72 w-56 overflow-hidden rounded-24 border-2 border-brand-teal shadow-widget">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={
                    showOriginal
                      ? profile.frontImageUrl || '/mock/profile_trang_front.png'
                      : garment.imageUrl
                  }
                  alt="Kết quả mặc thử"
                  className="h-full w-full object-cover object-top"
                />

                {/* Before / After Toggle Pill */}
                <button
                  type="button"
                  onMouseDown={() => setShowOriginal(true)}
                  onMouseUp={() => setShowOriginal(false)}
                  onTouchStart={() => setShowOriginal(true)}
                  onTouchEnd={() => setShowOriginal(false)}
                  className="absolute bottom-3 left-1/2 -translate-x-1/2 flex items-center gap-1.5 rounded-full bg-black/70 backdrop-blur-md px-3 py-1 text-xs font-semibold text-white shadow-lg active:scale-95 transition-all select-none"
                >
                  <svg className="h-3.5 w-3.5 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span>{showOriginal ? 'Đang xem ảnh gốc' : 'Giữ để xem ảnh gốc'}</span>
                </button>
              </div>

              <div className="mt-3 flex items-center justify-between w-full px-2 text-xs">
                <span className="font-semibold text-emerald-700">✓ Thử đồ thành công</span>
                <span className="text-brand-muted">Độ phân giải: 1024x1024</span>
              </div>
            </div>
          )}

          {/* STATE 5: BAD QUALITY */}
          {vtoState === 'bad_quality' && (
            <div className="flex flex-col items-center text-center my-auto">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-rose-50 text-rose-500">
                <svg className="h-8 w-8 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h4 className="text-base font-bold text-rose-900">
                Chất Lượng Ảnh Chưa Đạt
              </h4>
              <p className="mt-1 text-xs text-rose-700 max-w-[260px]">
                Ảnh chụp bị mờ hoặc không đủ ánh sáng để AI phân tách trang phục.
              </p>
            </div>
          )}

          {/* STATE 6: SERVICE UNAVAILABLE */}
          {vtoState === 'service_unavailable' && (
            <div className="flex flex-col items-center text-center my-auto">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 text-brand-slate">
                <svg className="h-8 w-8 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 4.243a9 9 0 01-12.728 0m0 0l2.829-2.829m-2.829 2.829L3 21m5.657-12.536a5 5 0 000 7.072m0 0l2.829-2.829" />
                </svg>
              </div>
              <h4 className="text-base font-bold text-brand-navy">
                Máy Chủ Thử Đồ Đang Nghỉ
              </h4>
              <p className="mt-1 text-xs text-brand-slate max-w-[260px]">
                Microservice CatVTON GPU hiện chưa online. Bạn vẫn có thể sử dụng bảng thông số đo kích cỡ bình thường.
              </p>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="border-t border-brand-border/60 bg-white p-4">
          {vtoState === 'ready' && (
            <Button
              variant="primary"
              size="lg"
              fullWidth
              onClick={handleStartTryOn}
              leftIcon={
                <svg className="h-5 w-5 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              }
            >
              Bắt Đầu Tạo Ảnh Mặc Thử (AI Inference)
            </Button>
          )}

          {vtoState === 'completed' && (
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="md"
                className="flex-1"
                onClick={() => setVtoState('ready')}
              >
                Thử Lại
              </Button>
              <Button
                variant="primary"
                size="md"
                className="flex-1"
                onClick={onClose}
              >
                Hoàn Tất
              </Button>
            </div>
          )}

          {(vtoState === 'bad_quality' || vtoState === 'service_unavailable') && (
            <Button
              variant="outline"
              size="md"
              fullWidth
              onClick={() => setVtoState('ready')}
            >
              Quay Lại
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
