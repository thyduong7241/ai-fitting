'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { UserProfile, Garment } from '@/types/fitting';

export interface WelcomeScreenProps {
  garment: Garment;
  activeProfile: UserProfile;
  onStart: () => void;
  onViewProfiles?: () => void;
  onClose?: () => void;
}

export function WelcomeScreen({
  garment,
  activeProfile,
  onStart,
  onViewProfiles,
  onClose,
}: WelcomeScreenProps) {
  return (
    <div className="flex flex-1 flex-col justify-between p-5 bg-brand-canvas animate-in fade-in duration-200">
      {/* Top Bar with Brand and Close */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-brand-teal animate-pulse" />
          <span className="text-[11px] font-bold uppercase tracking-wider text-brand-teal">
            AI Precision Fit
          </span>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full text-brand-slate hover:bg-slate-200/60 active:scale-95 transition-all"
            aria-label="Đóng widget"
          >
            <svg className="h-5 w-5 stroke-current stroke-2 fill-none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Hero Visual Card */}
      <div className="my-auto flex flex-col items-center text-center">
        {/* Garment Preview Thumbnail with Glow */}
        <div className="relative mb-5 flex h-36 w-28 items-center justify-center rounded-20 bg-white p-2 border border-brand-border shadow-widget">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={garment.imageUrl}
            alt={garment.name}
            className="h-full w-full rounded-14 object-cover object-center"
          />
          <Badge
            variant="brand"
            size="sm"
            className="absolute -bottom-2.5 shadow-sm"
          >
            {garment.brand.toUpperCase()}
          </Badge>
        </div>

        <h1 className="text-xl font-extrabold text-brand-navy tracking-tight max-w-[280px]">
          Trợ Lý Thử Đồ & Chọn Size Chuẩn Xác
        </h1>
        <p className="mt-2 text-xs leading-relaxed text-brand-slate max-w-[300px]">
          Công nghệ AI phân tích nhân trắc học đối chiếu số đo cơ thể bạn với từng cm phom áo thực tế.
        </p>

        {/* Feature Highlights */}
        <div className="mt-5 flex w-full flex-col gap-2 rounded-16 border border-brand-border/80 bg-white p-3.5 text-left shadow-card">
          <div className="flex items-center gap-2.5">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-teal-subtle text-brand-teal">
              <svg className="h-4 w-4 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
            <div className="text-xs">
              <span className="font-bold text-brand-navy">Gợi ý kích thước 98% chuẩn xác</span>
              <p className="text-[11px] text-brand-muted">Độ lệch sai số vai, ngực dưới 1.5cm</p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-amber-50 text-amber-600">
              <svg className="h-4 w-4 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </span>
            <div className="text-xs">
              <span className="font-bold text-brand-navy">Phân tích độ ôm 5 vùng cơ thể</span>
              <p className="text-[11px] text-brand-muted">Vai, ngực, eo, hông và chiều dài áo</p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-teal-50 text-teal-700">
              <svg className="h-4 w-4 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </span>
            <div className="text-xs">
              <span className="font-bold text-brand-navy">Thử đồ ảo AI (Virtual Try-On)</span>
              <p className="text-[11px] text-brand-muted">Mô phỏng mặc áo lên ảnh người thật</p>
            </div>
          </div>
        </div>

        {/* Current Profile Preview */}
        {activeProfile && (
          <div className="mt-4 flex items-center justify-between w-full px-1 text-xs text-brand-slate">
            <span>
              Hồ sơ: <strong className="text-brand-navy font-semibold">{activeProfile.name}</strong> ({activeProfile.heightCm}cm)
            </span>
            {onViewProfiles && (
              <button
                type="button"
                onClick={onViewProfiles}
                className="text-xs font-semibold text-brand-teal hover:underline"
              >
                Đổi hồ sơ
              </button>
            )}
          </div>
        )}
      </div>

      {/* Bottom Action */}
      <div className="pt-4">
        <Button
          variant="primary"
          size="lg"
          fullWidth
          onClick={onStart}
          rightIcon={
            <svg className="h-4 w-4 stroke-current stroke-2 fill-none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          }
        >
          Bắt Đầu Chọn Size
        </Button>
      </div>
    </div>
  );
}
