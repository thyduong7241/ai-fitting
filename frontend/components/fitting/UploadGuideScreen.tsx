'use client';

import React, { useState, useRef } from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Button } from '@/components/ui/Button';
import { fitApiClient } from '@/services/apiClient';
import { QualityCheckResponse } from '@/types/fitting';

export interface UploadGuideScreenProps {
  onBack: () => void;
  onClose?: () => void;
  onContinue: (frontImage: string, sideImage?: string) => void;
}

export function UploadGuideScreen({
  onBack,
  onClose,
  onContinue,
}: UploadGuideScreenProps) {
  const [frontImage, setFrontImage] = useState<string>('/mock/profile_trang_front.png');
  const [sideImage, setSideImage] = useState<string>('/mock/profile_trang_side.png');
  const [showGuideModal, setShowGuideModal] = useState<boolean>(false);

  // Instant Quality Check states per image slot
  const [frontChecking, setFrontChecking] = useState<boolean>(false);
  const [sideChecking, setSideChecking] = useState<boolean>(false);
  const [frontQcResult, setFrontQcResult] = useState<QualityCheckResponse | null>(null);
  const [sideQcResult, setSideQcResult] = useState<QualityCheckResponse | null>(null);

  const frontInputRef = useRef<HTMLInputElement>(null);
  const sideInputRef = useRef<HTMLInputElement>(null);

  const handleInstantQualityCheck = async (base64Data: string, isSide: boolean) => {
    if (isSide) {
      setSideChecking(true);
      setSideQcResult(null);
      try {
        const res = await fitApiClient.checkQuality({
          imageBase64: base64Data,
          imageType: 'side',
        });
        setSideQcResult(res);
      } catch (err) {
        console.warn('Instant QC side check failed:', err);
      } finally {
        setSideChecking(false);
      }
    } else {
      setFrontChecking(true);
      setFrontQcResult(null);
      try {
        const res = await fitApiClient.checkQuality({
          imageBase64: base64Data,
          imageType: 'front',
        });
        setFrontQcResult(res);
      } catch (err) {
        console.warn('Instant QC front check failed:', err);
      } finally {
        setFrontChecking(false);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, isSide = false) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const base64Data = event.target?.result as string;
        if (base64Data) {
          if (isSide) {
            setSideImage(base64Data);
            handleInstantQualityCheck(base64Data, true);
          } else {
            setFrontImage(base64Data);
            handleInstantQualityCheck(base64Data, false);
          }
        }
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="relative flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200">
      <StepHeader
        title="Hướng Dẫn Chụp Ảnh"
        subtitle="Để AI nhận diện chính xác 33 mốc giải phẫu cơ thể"
        currentStep={2}
        totalSteps={3}
        onBack={onBack}
        onClose={onClose}
      />

      <div className="flex flex-1 flex-col justify-between p-5 overflow-y-auto no-scrollbar">
        <div className="flex flex-col gap-4">
          {/* 4 Tiêu Chí Chụp Ảnh Đạt Chuẩn AI (100% Pass Quality Gate) */}
          <div className="rounded-20 border border-brand-teal/25 bg-white p-3.5 shadow-card">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-1.5">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-teal text-white text-[10px] font-bold">
                  ✓
                </span>
                <h3 className="text-xs font-bold uppercase tracking-wider text-brand-navy">
                  Tiêu Chí Ảnh Chuẩn AI (100% Pass)
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowGuideModal(true)}
                className="text-[11px] font-bold text-brand-teal hover:underline flex items-center gap-0.5 bg-brand-teal-subtle px-2 py-0.5 rounded-full"
              >
                Chi tiết
                <svg className="h-3 w-3 stroke-current fill-none stroke-[2.5]" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            <p className="text-[11px] text-brand-slate mb-2">
              Khi tự chụp hoặc chọn ảnh từ điện thoại để kiểm thử:
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs">
              {/* 1. Tư thế đứng */}
              <div className="flex flex-col rounded-14 bg-slate-50/80 p-2 border border-slate-100/80">
                <div className="flex items-center gap-1 mb-1">
                  <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-800 text-[9px] font-bold">1</span>
                  <span className="text-[11px] font-bold text-brand-navy leading-none">Tư thế đứng</span>
                </div>
                <p className="text-[10px] text-brand-slate leading-tight">
                  Đứng thẳng, nhìn camera. <strong className="text-brand-navy font-semibold">2 tay mở nhẹ 15°-20° (chữ A)</strong> không che eo & hông.
                </p>
              </div>

              {/* 2. Khung hình (Full-body) */}
              <div className="flex flex-col rounded-14 bg-slate-50/80 p-2 border border-slate-100/80">
                <div className="flex items-center gap-1 mb-1">
                  <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-800 text-[9px] font-bold">2</span>
                  <span className="text-[11px] font-bold text-brand-navy leading-none">Khung hình</span>
                </div>
                <p className="text-[10px] text-brand-slate leading-tight">
                  Thấy <strong className="text-brand-navy font-semibold">trọn vẹn từ đỉnh đầu đến bàn chân</strong>. Đặt máy ngang ngực/thắt lưng.
                </p>
              </div>

              {/* 3. Trang phục */}
              <div className="flex flex-col rounded-14 bg-slate-50/80 p-2 border border-slate-100/80">
                <div className="flex items-center gap-1 mb-1">
                  <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-800 text-[9px] font-bold">3</span>
                  <span className="text-[11px] font-bold text-brand-navy leading-none">Trang phục</span>
                </div>
                <p className="text-[10px] text-brand-slate leading-tight">
                  Đồ <strong className="text-brand-navy font-semibold">gọn gàng, ôm vừa người</strong> (áo thun + quần gọn). Tránh áo phao to, váy xù.
                </p>
              </div>

              {/* 4. Nền & Ánh sáng */}
              <div className="flex flex-col rounded-14 bg-slate-50/80 p-2 border border-slate-100/80">
                <div className="flex items-center gap-1 mb-1">
                  <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-800 text-[9px] font-bold">4</span>
                  <span className="text-[11px] font-bold text-brand-navy leading-none">Nền & Ánh sáng</span>
                </div>
                <p className="text-[10px] text-brand-slate leading-tight">
                  Tường trơn, <strong className="text-brand-navy font-semibold">tương phản với màu áo</strong>. Ánh sáng đều, không ngược sáng.
                </p>
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
                  className={`group relative flex h-48 w-full cursor-pointer flex-col items-center justify-center overflow-hidden rounded-20 border-2 border-dashed bg-white p-2 transition-all shadow-card ${
                    frontQcResult?.isValid === false
                      ? 'border-rose-400 bg-rose-50/20'
                      : frontQcResult?.isValid === true
                      ? 'border-emerald-500 bg-emerald-50/10'
                      : 'border-brand-teal/70 hover:border-brand-teal'
                  }`}
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

                      {/* Instant QC Status Badge */}
                      {frontChecking ? (
                        <div className="absolute top-2 left-2 flex items-center gap-1 rounded-full bg-slate-900/80 px-2 py-0.5 text-[10px] font-semibold text-white shadow-sm backdrop-blur-sm animate-pulse">
                          <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-ping" />
                          <span>Đang kiểm định...</span>
                        </div>
                      ) : frontQcResult ? (
                        <div
                          className={`absolute top-2 left-2 flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold text-white shadow-sm backdrop-blur-sm ${
                            frontQcResult.isValid ? 'bg-emerald-600/90' : 'bg-rose-600/90'
                          }`}
                        >
                          <span>{frontQcResult.isValid ? '✓ Đạt chuẩn' : '✕ Lỗi ảnh'}</span>
                        </div>
                      ) : null}
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

                {/* Instant Feedback Message for Front */}
                {frontQcResult && !frontQcResult.isValid && frontQcResult.issues.length > 0 && (
                  <div className="rounded-10 bg-rose-50 border border-rose-200/80 p-1.5 text-[10px] text-rose-700 font-medium leading-tight animate-in fade-in duration-200">
                    ⚠️ {frontQcResult.issues[0].message}
                  </div>
                )}

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
                  className={`group relative flex h-48 w-full cursor-pointer flex-col items-center justify-center overflow-hidden rounded-20 border-2 border-dashed bg-white p-2 transition-all shadow-card ${
                    sideQcResult?.isValid === false
                      ? 'border-rose-400 bg-rose-50/20'
                      : sideQcResult?.isValid === true
                      ? 'border-emerald-500 bg-emerald-50/10'
                      : 'border-slate-200 hover:border-brand-teal'
                  }`}
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

                      {/* Instant QC Status Badge */}
                      {sideChecking ? (
                        <div className="absolute top-2 left-2 flex items-center gap-1 rounded-full bg-slate-900/80 px-2 py-0.5 text-[10px] font-semibold text-white shadow-sm backdrop-blur-sm animate-pulse">
                          <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-ping" />
                          <span>Đang kiểm định...</span>
                        </div>
                      ) : sideQcResult ? (
                        <div
                          className={`absolute top-2 left-2 flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold text-white shadow-sm backdrop-blur-sm ${
                            sideQcResult.isValid ? 'bg-emerald-600/90' : 'bg-rose-600/90'
                          }`}
                        >
                          <span>{sideQcResult.isValid ? '✓ Đạt chuẩn' : '✕ Lỗi ảnh'}</span>
                        </div>
                      ) : null}
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

                {/* Instant Feedback Message for Side */}
                {sideQcResult && !sideQcResult.isValid && sideQcResult.issues.length > 0 && (
                  <div className="rounded-10 bg-rose-50 border border-rose-200/80 p-1.5 text-[10px] text-rose-700 font-medium leading-tight animate-in fade-in duration-200">
                    ⚠️ {sideQcResult.issues[0].message}
                  </div>
                )}

                <input
                  ref={sideInputRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleFileChange(e, true)}
                  className="hidden"
                />
              </div>
            </div>

            {/* Quick Demo Test Images Switcher */}
            <div className="flex items-center justify-between pt-1">
              <span className="text-[11px] text-brand-muted">Bộ ảnh kiểm thử:</span>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => {
                    setFrontImage('/demo/front.jpg');
                    setSideImage('/demo/side.jpg');
                  }}
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold border transition-colors ${
                    frontImage.includes('demo')
                      ? 'bg-brand-teal text-white border-brand-teal'
                      : 'bg-white text-brand-slate border-slate-200 hover:border-brand-teal'
                  }`}
                >
                  Ảnh test áo khoác
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setFrontImage('/mock/profile_trang_front.png');
                    setSideImage('/mock/profile_trang_side.png');
                  }}
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold border transition-colors ${
                    frontImage.includes('profile_trang')
                      ? 'bg-brand-teal text-white border-brand-teal'
                      : 'bg-white text-brand-slate border-slate-200 hover:border-brand-teal'
                  }`}
                >
                  Ảnh mẫu chuẩn
                </button>
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

          <div className="flex items-center justify-between px-1 pt-2 text-xs">
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
                <span>Thoát</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Pop-up Modal: Tiêu Chuẩn 4 Tiêu Chí Chi Tiết */}
      {showGuideModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="relative flex w-full max-w-sm flex-col rounded-24 bg-white p-5 shadow-widget animate-in zoom-in-95 duration-200 max-h-[88vh] overflow-y-auto no-scrollbar">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-teal-subtle text-brand-teal">
                  <svg className="h-4 w-4 stroke-current fill-none stroke-2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-xs font-bold text-brand-navy uppercase tracking-wider">Tiêu Chuẩn Chụp Ảnh AI</h3>
                  <span className="text-[10px] text-brand-teal font-semibold">100% Pass Quality Gate</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowGuideModal(false)}
                className="flex h-7 w-7 items-center justify-center rounded-full text-brand-slate hover:bg-slate-100 active:scale-95 transition-all"
              >
                ✕
              </button>
            </div>

            <p className="text-[11px] text-brand-slate py-2.5 leading-relaxed">
              Để thuật toán AI nhận diện chuẩn xác 33 mốc giải phẫu và trích xuất số đo chính xác, vui lòng tuân thủ 4 tiêu chí sau:
            </p>

            <div className="flex flex-col gap-2.5 text-xs">
              {/* Item 1 */}
              <div className="rounded-16 bg-slate-50 p-3 border border-slate-100/80">
                <div className="flex items-center gap-2 font-bold text-brand-navy mb-1.5 text-xs">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-teal text-white text-[10px]">1</span>
                  Tư Thế Đứng
                </div>
                <ul className="list-disc list-inside text-[11px] text-brand-slate space-y-1 pl-1 leading-relaxed">
                  <li>Đứng thẳng tự nhiên, mắt nhìn thẳng vào ống kính máy ảnh.</li>
                  <li>
                    <strong className="text-brand-navy font-semibold">2 tay khép hờ hoặc mở nhẹ sang hai bên 15° - 20° (hình chữ A nhỏ):</strong> Điều này rất quan trọng để cánh tay không che khuất đường cong eo và hông.
                  </li>
                </ul>
              </div>

              {/* Item 2 */}
              <div className="rounded-16 bg-slate-50 p-3 border border-slate-100/80">
                <div className="flex items-center gap-2 font-bold text-brand-navy mb-1.5 text-xs">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-teal text-white text-[10px]">2</span>
                  Khung Hình (Full-body)
                </div>
                <ul className="list-disc list-inside text-[11px] text-brand-slate space-y-1 pl-1 leading-relaxed">
                  <li>Phải nhìn thấy <strong className="text-brand-navy font-semibold">trọn vẹn từ đỉnh đầu tới hết bàn chân</strong> (tránh để chân chạm sát mép đáy màn hình).</li>
                  <li>Điện thoại để cao ngang tầm ngực hoặc thắt lưng (tránh góc chụp từ trên dốc xuống làm chân bị ngắn và sai tỷ lệ P2M).</li>
                </ul>
              </div>

              {/* Item 3 */}
              <div className="rounded-16 bg-slate-50 p-3 border border-slate-100/80">
                <div className="flex items-center gap-2 font-bold text-brand-navy mb-1.5 text-xs">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-teal text-white text-[10px]">3</span>
                  Trang Phục
                </div>
                <ul className="list-disc list-inside text-[11px] text-brand-slate space-y-1 pl-1 leading-relaxed">
                  <li>Nên mặc đồ <strong className="text-brand-navy font-semibold">gọn gàng, ôm vừa người</strong> (áo phông/croptop + quần jean/legging/short).</li>
                  <li>Tránh áo phao to xù hoặc váy rộng thùng thình che mất đường cong eo.</li>
                </ul>
              </div>

              {/* Item 4 */}
              <div className="rounded-16 bg-slate-50 p-3 border border-slate-100/80">
                <div className="flex items-center gap-2 font-bold text-brand-navy mb-1.5 text-xs">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-teal text-white text-[10px]">4</span>
                  Nền & Ánh Sáng
                </div>
                <ul className="list-disc list-inside text-[11px] text-brand-slate space-y-1 pl-1 leading-relaxed">
                  <li>Đứng trước <strong className="text-brand-navy font-semibold">tường trơn hoặc phông nền đơn sắc</strong> có độ tương phản với màu áo.</li>
                  <li>Ánh sáng đều, không ngược sáng để tránh mất chi tiết đường biên cơ thể.</li>
                </ul>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setShowGuideModal(false)}
              className="mt-4 w-full rounded-14 bg-brand-teal py-2.5 text-xs font-bold text-white hover:bg-brand-teal-dark active:scale-[0.98] transition-all shadow-sm"
            >
              Đã Hiểu, Tiếp Tục Chọn Ảnh
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
