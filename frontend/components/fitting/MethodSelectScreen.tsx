'use client';

import React from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Badge } from '@/components/ui/Badge';
import { FitMethod } from '@/types/fitting';

export interface MethodSelectScreenProps {
  onBack: () => void;
  onSelectMethod: (method: FitMethod) => void;
}

export function MethodSelectScreen({
  onBack,
  onSelectMethod,
}: MethodSelectScreenProps) {
  return (
    <div className="flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200">
      <StepHeader
        title="Phương Thức Xác Định Vóc Dáng"
        subtitle="Chọn cách thuận tiện nhất để AI tính toán kích cỡ phù hợp"
        currentStep={2}
        totalSteps={3}
        onBack={onBack}
      />

      <div className="flex flex-1 flex-col justify-between p-5">
        <div className="flex flex-col gap-3.5">
          {/* Option 1: AI Vision Scan (Recommended) */}
          <button
            type="button"
            onClick={() => onSelectMethod('ai_photo')}
            className="group relative flex flex-col gap-2.5 rounded-20 border-2 border-brand-teal bg-white p-4 text-left shadow-card hover:shadow-widget active:scale-[0.99] transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal"
          >
            <div className="flex items-center justify-between">
              <span className="flex h-10 w-10 items-center justify-center rounded-14 bg-brand-teal text-white shadow-sm">
                <svg className="h-5 w-5 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </span>
              <Badge variant="brand" size="sm">
                ★ KHUYÊN DÙNG
              </Badge>
            </div>

            <div>
              <h2 className="text-base font-bold text-brand-navy group-hover:text-brand-teal transition-colors">
                AI Chụp Ảnh Toàn Thân
              </h2>
              <p className="mt-1 text-xs text-brand-slate leading-relaxed">
                Tải lên 2 ảnh (chính diện & nghiêng). AI tự động đo 33 mốc nhân trắc học và <strong className="text-brand-teal font-semibold">kích hoạt tính năng Mặc Thử Ảo (Try-On)</strong>.
              </p>
            </div>

            <div className="flex items-center gap-3 pt-2 border-t border-slate-100 text-[11px] text-brand-muted">
              <span className="flex items-center gap-1">
                <svg className="h-3.5 w-3.5 text-brand-teal-match" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Chính xác 98%
              </span>
              <span className="flex items-center gap-1">
                <svg className="h-3.5 w-3.5 text-brand-slate" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
                Chỉ mất 15 giây
              </span>
            </div>
          </button>

          {/* Option 2: Manual Measurements */}
          <button
            type="button"
            onClick={() => onSelectMethod('manual')}
            className="group relative flex flex-col gap-2.5 rounded-20 border border-brand-border bg-white p-4 text-left shadow-card hover:border-brand-teal/50 active:scale-[0.99] transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal"
          >
            <div className="flex items-center justify-between">
              <span className="flex h-10 w-10 items-center justify-center rounded-14 bg-slate-100 text-brand-slate">
                <svg className="h-5 w-5 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </span>
              <span className="text-[11px] font-medium text-brand-muted">
                Thủ công
              </span>
            </div>

            <div>
              <h2 className="text-base font-bold text-brand-navy group-hover:text-brand-teal transition-colors">
                Nhập Số Đo Bằng Thước Dây
              </h2>
              <p className="mt-1 text-xs text-brand-slate leading-relaxed">
                Nhập trực tiếp số đo các vòng: Ngực, Eo, Hông, Rộng vai nếu bạn đã nắm rõ kích thước cơ thể.
              </p>
            </div>

            <div className="flex items-center gap-3 pt-2 border-t border-slate-100 text-[11px] text-brand-muted">
              <span>Không cần chụp ảnh</span>
              <span>•</span>
              <span>Gợi ý size nhanh chóng</span>
            </div>
          </button>
        </div>

        {/* Security / Privacy reassurance note */}
        <div className="rounded-16 bg-[#EEF5F7] p-3 text-center text-[11px] text-brand-slate">
          🔒 Toàn bộ ảnh xử lý an toàn tại máy chủ nội bộ (on-premise), không gửi dữ liệu ra bên ngoài.
        </div>
      </div>
    </div>
  );
}
