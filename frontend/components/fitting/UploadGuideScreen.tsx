'use client';

import React, { useState, useRef } from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Button } from '@/components/ui/Button';

export interface UploadGuideScreenProps {
  onBack: () => void;
  onContinue: (frontImage: string, sideImage?: string) => void;
}

export function UploadGuideScreen({
  onBack,
  onContinue,
}: UploadGuideScreenProps) {
  const [frontImage, setFrontImage] = useState<string>('/mock/profile_trang_front.png');
  const [sideImage, setSideImage] = useState<string>('/mock/profile_trang_side.png');
  const frontInputRef = useRef<HTMLInputElement>(null);
  const sideInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, isSide = false) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      if (isSide) {
        setSideImage(url);
      } else {
        setFrontImage(url);
      }
    }
  };

  return (
    <div className="flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200">
      <StepHeader
        title="Hướng Dẫn Chụp Ảnh"
        subtitle="Để AI nhận diện chính xác 33 mốc giải phẫu cơ thể"
        currentStep={2}
        totalSteps={3}
        onBack={onBack}
      />

      <div className="flex flex-1 flex-col justify-between p-5 overflow-y-auto no-scrollbar">
        <div className="flex flex-col gap-4">
          {/* Pose Checklist Card */}
          <div className="rounded-20 border border-brand-border bg-white p-3.5 shadow-card">
            <h3 className="text-xs font-bold uppercase tracking-wider text-brand-navy mb-2.5">
              Chuẩn Tư Thế Đo Của AI
            </h3>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex items-start gap-1.5 rounded-12 bg-emerald-50/80 p-2 text-emerald-900 border border-emerald-100">
                <span className="text-emerald-600 font-bold shrink-0">✓</span>
                <span className="text-[11px] leading-snug">Đứng thẳng tự nhiên, nhìn vào camera</span>
              </div>
              <div className="flex items-start gap-1.5 rounded-12 bg-emerald-50/80 p-2 text-emerald-900 border border-emerald-100">
                <span className="text-emerald-600 font-bold shrink-0">✓</span>
                <span className="text-[11px] leading-snug">Lộ rõ toàn bộ đầu và bàn chân</span>
              </div>
              <div className="flex items-start gap-1.5 rounded-12 bg-rose-50/80 p-2 text-rose-900 border border-rose-100">
                <span className="text-rose-600 font-bold shrink-0">✕</span>
                <span className="text-[11px] leading-snug">Tránh áo quần quá rộng thùng thình</span>
              </div>
              <div className="flex items-start gap-1.5 rounded-12 bg-rose-50/80 p-2 text-rose-900 border border-rose-100">
                <span className="text-rose-600 font-bold shrink-0">✕</span>
                <span className="text-[11px] leading-snug">Tránh góc chụp nghiêng từ trên xuống</span>
              </div>
            </div>
          </div>

          {/* Photo Upload Slots */}
          <div className="flex flex-col gap-2.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-brand-slate">
              Tải Ảnh Toàn Thân (Mẫu có sẵn hoặc ảnh của bạn)
            </span>

            <div className="grid grid-cols-2 gap-3">
              {/* Front Photo Slot */}
              <div className="flex flex-col gap-1.5">
                <div
                  onClick={() => frontInputRef.current?.click()}
                  className="group relative flex h-48 w-full cursor-pointer flex-col items-center justify-center overflow-hidden rounded-20 border-2 border-dashed border-brand-teal/70 bg-white p-2 hover:border-brand-teal transition-all shadow-card"
                >
                  {frontImage ? (
                    <>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={frontImage}
                        alt="Ảnh chính diện"
                        className="h-full w-full rounded-14 object-cover object-top"
                      />
                      <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity rounded-20">
                        <span className="text-[11px] font-semibold text-white bg-black/50 px-2 py-1 rounded-full">
                          Đổi ảnh khác
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="flex flex-col items-center text-center p-2 text-brand-muted">
                      <svg className="h-8 w-8 stroke-current stroke-1.5 fill-none" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                      </svg>
                      <span className="mt-1 text-xs font-medium">Tải ảnh chính diện</span>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between px-1">
                  <span className="text-xs font-semibold text-brand-navy">Ảnh Chính Diện</span>
                  <span className="rounded bg-brand-teal-subtle px-1 text-[10px] font-bold text-brand-teal">
                    BẮT BUỘC
                  </span>
                </div>
                <input
                  ref={frontInputRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleFileChange(e, false)}
                  className="hidden"
                />
              </div>

              {/* Side Photo Slot */}
              <div className="flex flex-col gap-1.5">
                <div
                  onClick={() => sideInputRef.current?.click()}
                  className="group relative flex h-48 w-full cursor-pointer flex-col items-center justify-center overflow-hidden rounded-20 border-2 border-dashed border-slate-200 bg-white p-2 hover:border-brand-teal transition-all shadow-card"
                >
                  {sideImage ? (
                    <>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={sideImage}
                        alt="Ảnh góc nghiêng"
                        className="h-full w-full rounded-14 object-cover object-top"
                      />
                      <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity rounded-20">
                        <span className="text-[11px] font-semibold text-white bg-black/50 px-2 py-1 rounded-full">
                          Đổi ảnh khác
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="flex flex-col items-center text-center p-2 text-brand-muted">
                      <svg className="h-8 w-8 stroke-current stroke-1.5 fill-none" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                      </svg>
                      <span className="mt-1 text-xs font-medium">Tải ảnh góc nghiêng</span>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between px-1">
                  <span className="text-xs font-semibold text-brand-navy">Ảnh Góc Nghiêng</span>
                  <span className="text-[10px] text-brand-muted">Khuyến khích</span>
                </div>
                <input
                  ref={sideInputRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleFileChange(e, true)}
                  className="hidden"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Next Button */}
        <div className="pt-4 mt-auto">
          <Button
            variant="primary"
            size="lg"
            fullWidth
            onClick={() => onContinue(frontImage, sideImage)}
            disabled={!frontImage}
            rightIcon={
              <svg className="h-4 w-4 stroke-current stroke-2 fill-none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            }
          >
            Kiểm Định Chất Lượng Ảnh (AI Quality Gate)
          </Button>
        </div>
      </div>
    </div>
  );
}
