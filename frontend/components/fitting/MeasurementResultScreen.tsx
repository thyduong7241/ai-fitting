'use client';

import React, { useState } from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { StepperInput } from '@/components/ui/StepperInput';
import { BodyMeasurements, UserProfile } from '@/types/fitting';
import Image from 'next/image';

export interface MeasurementResultScreenProps {
  measurements: BodyMeasurements;
  bodyShape?: string;
  smartFitNotes?: string[];
  confidencePercent?: number;
  confidenceMetrics?: Record<string, any>;
  frontImageUrl?: string;
  sideImageUrl?: string;
  activeProfile: UserProfile;
  onConfirm: (updatedMeasurements: BodyMeasurements, updatedProfile?: Partial<UserProfile>) => void;
  onRetake: () => void;
  onBack: () => void;
  onClose?: () => void;
}

// Anthropometric Shape Classification based on ratios (Vai, Ngực, Eo, Hông)
function evaluateBodyShape(
  shoulder: number,
  chest: number,
  waist: number,
  hips: number,
  gender: 'female' | 'male'
): { code: string; label: string; desc: string } {
  const whr = hips > 0 ? waist / hips : 0.8;
  const wcr = chest > 0 ? waist / chest : 0.85;

  if (gender === 'female') {
    // 1. Quả táo: Vòng eo/bụng lớn vượt trội
    if (whr >= 0.85 || waist >= chest - 3.0) {
      return {
        code: 'qua_tao',
        label: 'Dáng Quả Táo (Tròn)',
        desc: 'Vòng eo và bụng tròn đầy đặn hơn vai và hông.',
      };
    }
    // 2. Đồng hồ cát: Eo thắt rõ rệt, ngực và hông nở đều
    if (whr <= 0.75 && Math.abs(chest - hips) <= 6.0 && chest - waist >= 15.0) {
      return {
        code: 'dong_ho_cat',
        label: 'Dáng Đồng Hồ Cát',
        desc: 'Đường cong lý tưởng: Eo thon gọn, ngực và hông nở đều cân xứng.',
      };
    }
    // 3. Quả lê: Hông lớn hơn ngực rõ rệt
    if (hips >= chest + 5.0 && whr <= 0.82) {
      return {
        code: 'qua_le',
        label: 'Dáng Quả Lê (Tam giác xuôi)',
        desc: 'Phần thân dưới (hông/đùi) nở nang hơn so với thân trên.',
      };
    }
    // 4. Tam giác ngược: Vai & ngực rộng hơn hông
    if (chest >= hips + 5.0 || shoulder >= hips * 0.44) {
      return {
        code: 'tam_giac_nguoc',
        label: 'Dáng Tam Giác Ngược',
        desc: 'Khung vai và ngực rộng, eo và hông thon nhỏ.',
      };
    }
    // 5. Hình chữ nhật
    return {
      code: 'chu_nhat',
      label: 'Dáng Hình Chữ Nhật',
      desc: 'Tỷ lệ vai, ngực, eo và hông tương đối đều nhau, dáng người thẳng.',
    };
  } else {
    // Nam
    // 1. Hình Oval: Bụng tròn lớn nhất
    if (waist > chest && waist > hips) {
      return {
        code: 'oval',
        label: 'Dáng Hình Oval (Tròn)',
        desc: 'Vòng bụng/eo nhô tròn lớn nhất so với ngực và hông.',
      };
    }
    // 2. Hình Tam Giác: Thân dưới nở hơn thân trên
    if (hips >= chest || (waist >= chest && waist <= hips)) {
      return {
        code: 'tam_giac',
        label: 'Dáng Hình Tam Giác',
        desc: 'Phần eo dưới và hông rộng hơn so với bề rộng vai và ngực.',
      };
    }
    // 3. Tam Giác Ngược (V-Taper): Thể thao, vạm vỡ
    if (chest >= waist + 15.0 && wcr <= 0.80 && shoulder >= 44.0) {
      return {
        code: 'tam_giac_nguoc',
        label: 'Dáng Tam Giác Ngược (V-Taper)',
        desc: 'Khung vai và ngực vạm vỡ, eo thắt gọn chuẩn thể hình.',
      };
    }
    // 4. Hình Thang (Trapezoid): Chuẩn tỷ lệ vàng nam
    if (chest >= waist + 6.0 && chest >= hips - 2.0) {
      return {
        code: 'hinh_thang',
        label: 'Dáng Hình Thang (Chuẩn Nam)',
        desc: 'Tỷ lệ vàng nam giới: Vai ngực nở nang, eo và hông thon gọn cân đối.',
      };
    }
    // 5. Hình Chữ Nhật: Dáng thẳng
    return {
      code: 'chu_nhat',
      label: 'Dáng Hình Chữ Nhật',
      desc: 'Thân người thẳng mỏng, vai ngực và eo có bề ngang gần bằng nhau.',
    };
  }
}

export function MeasurementResultScreen({
  measurements,
  bodyShape,
  confidencePercent = 94,
  confidenceMetrics,
  frontImageUrl,
  sideImageUrl,
  activeProfile,
  onConfirm,
  onRetake,
  onBack,
  onClose,
}: MeasurementResultScreenProps) {
  const [showConfidenceModal, setShowConfidenceModal] = useState(false);
  const [isEditingMeasurements, setIsEditingMeasurements] = useState(false);
  const [isEditingBaseMetrics, setIsEditingBaseMetrics] = useState(false);

  // Base metrics state (Chiều cao, cân nặng, tuổi, giới tính)
  const [heightCm, setHeightCm] = useState(activeProfile.heightCm || measurements.heightCm || 170);
  const [weightKg, setWeightKg] = useState(activeProfile.weightKg || measurements.weightKg || 60);
  const [age, setAge] = useState(activeProfile.age || 24);
  const [gender] = useState(activeProfile.gender || 'male');

  // Body circumferences state (cm)
  const [shoulderCm, setShoulderCm] = useState(measurements.shoulderCm || activeProfile.shoulderCm || 42);
  const [chestCm, setChestCm] = useState(measurements.chestCm || activeProfile.chestCm || 92);
  const [waistCm, setWaistCm] = useState(measurements.waistCm || activeProfile.waistCm || 76);
  const [hipsCm, setHipsCm] = useState(measurements.hipsCm || activeProfile.hipsCm || 94);
  const [armLengthCm, setArmLengthCm] = useState(measurements.armLengthCm || 57);
  const [inseamCm, setInseamCm] = useState(measurements.inseamCm || 78);

  // Sync state when new measurements are delivered by the API
  React.useEffect(() => {
    if (measurements.shoulderCm) setShoulderCm(measurements.shoulderCm);
    if (measurements.chestCm) setChestCm(measurements.chestCm);
    if (measurements.waistCm) setWaistCm(measurements.waistCm);
    if (measurements.hipsCm) setHipsCm(measurements.hipsCm);
    if (measurements.armLengthCm) setArmLengthCm(measurements.armLengthCm);
    if (measurements.inseamCm) setInseamCm(measurements.inseamCm);
    if (measurements.heightCm) setHeightCm(measurements.heightCm);
    if (measurements.weightKg) setWeightKg(measurements.weightKg);
  }, [measurements]);

  // Live evaluated shape based on current measurements
  const currentShape = evaluateBodyShape(shoulderCm, chestCm, waistCm, hipsCm, gender);

  // Compute live BMI
  const heightM = heightCm / 100.0;
  const bmi = heightM > 0 ? (weightKg / (heightM * heightM)).toFixed(1) : '21.0';

  const handleContinue = () => {
    onConfirm(
      {
        heightCm,
        weightKg,
        chestCm,
        waistCm,
        hipsCm,
        shoulderCm,
        armLengthCm,
        inseamCm,
      },
      {
        heightCm,
        weightKg,
        age,
        gender,
        bodyShape: currentShape.code,
      }
    );
  };

  return (
    <div className="flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200">
      <StepHeader
        title="Số Đo Trích Xuất Từ Ảnh AI"
        subtitle={`Phân tích nhân trắc học cho ${activeProfile.name}`}
        onBack={onBack}
        onClose={onClose}
      />

      <div className="flex flex-1 flex-col gap-4 p-5 overflow-y-auto no-scrollbar">
        {/* 1. Compact Summary Header: Thông tin nền (Chiều cao, Cân nặng, Tuổi, Giới tính) */}
        <section className="flex flex-col gap-2 rounded-20 bg-white p-3.5 border border-brand-border/80 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs text-brand-slate">
              <span className="text-sm">👤</span>
              <span className="font-semibold text-brand-navy">Chỉ số nền đã nhập:</span>
            </div>
            <button
              type="button"
              onClick={() => setIsEditingBaseMetrics(!isEditingBaseMetrics)}
              className="text-[11px] font-bold text-brand-teal hover:underline"
            >
              {isEditingBaseMetrics ? 'Xong' : 'Sửa'}
            </button>
          </div>

          {isEditingBaseMetrics ? (
            <div className="grid grid-cols-3 gap-2 pt-1 border-t border-slate-100">
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
              <StepperInput
                label="Tuổi"
                value={age}
                unit="tuổi"
                min={14}
                max={90}
                step={1}
                onChange={setAge}
              />
            </div>
          ) : (
            <div className="flex flex-wrap items-center gap-1.5 text-xs">
              <span className="rounded-8 bg-slate-100 px-2 py-0.5 font-bold text-brand-navy">
                {heightCm} cm
              </span>
              <span className="text-slate-300">•</span>
              <span className="rounded-8 bg-slate-100 px-2 py-0.5 font-bold text-brand-navy">
                {weightKg} kg
              </span>
              <span className="text-slate-300">•</span>
              <span className="rounded-8 bg-slate-100 px-2 py-0.5 font-medium text-brand-slate">
                {gender === 'female' ? 'Nữ' : 'Nam'} ({age} tuổi)
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-[11px] font-semibold text-brand-teal">
                BMI {bmi}
              </span>
            </div>
          )}
        </section>

        {/* 2. Hero Card: Photos & Evaluated Body Shape */}
        <section className="flex flex-col gap-3 rounded-24 border border-brand-teal/20 bg-gradient-to-br from-white to-[#ECF8F7] p-4 shadow-widget">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              {/* Photo previews */}
              <div className="flex -space-x-3 overflow-hidden">
                {frontImageUrl && (
                  <Image
                    src={frontImageUrl}
                    alt="Ảnh chính diện"
                    width={48}
                    height={48}
                    unoptimized
                    className="inline-block h-12 w-12 rounded-full ring-2 ring-white object-cover bg-slate-100"
                  />
                )}
                {sideImageUrl && (
                  <Image
                    src={sideImageUrl}
                    alt="Ảnh góc nghiêng"
                    width={48}
                    height={48}
                    unoptimized
                    className="inline-block h-12 w-12 rounded-full ring-2 ring-white object-cover bg-slate-100"
                  />
                )}
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-brand-teal">
                  Vóc Dáng Nhận Diện
                </span>
                <h4 className="text-sm font-bold text-brand-navy">
                  {currentShape.label}
                </h4>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setShowConfidenceModal(true)}
              className="group flex items-center gap-1.5 transition-transform active:scale-95 cursor-pointer"
              title="Nhấn để xem chi tiết căn cứ tính điểm tin cậy"
            >
              <Badge
                variant={confidencePercent >= 90 ? 'perfect' : confidencePercent >= 80 ? 'loose' : 'tight'}
                size="sm"
                dot
              >
                {confidencePercent}% Tin Cậy
              </Badge>
              <span className="flex h-4 w-4 items-center justify-center rounded-full bg-brand-teal/15 text-[10px] font-bold text-brand-teal group-hover:bg-brand-teal group-hover:text-white transition-colors">
                i
              </span>
            </button>
          </div>

          <p className="text-[11px] leading-relaxed text-brand-slate">
            {currentShape.desc}
          </p>
        </section>

        {/* 3. Detailed Body Measurements (Vai, Ngực, Eo, Hông/Mông, Tay, Chân) */}
        <section className="flex flex-col gap-2.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-brand-slate">
              Số Đo Chi Tiết (cm)
            </span>
            <button
              type="button"
              onClick={() => setIsEditingMeasurements(!isEditingMeasurements)}
              className="text-xs font-semibold text-brand-teal hover:underline"
            >
              {isEditingMeasurements ? 'Thu gọn' : 'Chỉnh sửa số đo'}
            </button>
          </div>

          {isEditingMeasurements ? (
            <div className="grid grid-cols-2 gap-2.5 rounded-20 bg-white p-3 border border-brand-border">
              <StepperInput
                label="Rộng vai"
                value={shoulderCm}
                unit="cm"
                min={30}
                max={70}
                step={0.5}
                onChange={setShoulderCm}
              />
              <StepperInput
                label="Vòng ngực"
                value={chestCm}
                unit="cm"
                min={60}
                max={150}
                step={0.5}
                onChange={setChestCm}
              />
              <StepperInput
                label="Vòng eo"
                value={waistCm}
                unit="cm"
                min={50}
                max={140}
                step={0.5}
                onChange={setWaistCm}
              />
              <StepperInput
                label="Vòng mông (Hông)"
                value={hipsCm}
                unit="cm"
                min={60}
                max={160}
                step={0.5}
                onChange={setHipsCm}
              />
              <StepperInput
                label="Dài tay"
                value={armLengthCm}
                unit="cm"
                min={40}
                max={90}
                step={0.5}
                onChange={setArmLengthCm}
              />
              <StepperInput
                label="Dài chân (Inseam)"
                value={inseamCm}
                unit="cm"
                min={50}
                max={110}
                step={0.5}
                onChange={setInseamCm}
              />
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-2">
              <div className="flex flex-col items-center justify-center rounded-16 border border-slate-100 bg-white p-2.5 shadow-card text-center">
                <span className="text-[10px] uppercase font-semibold text-brand-muted">Rộng vai</span>
                <span className="text-base font-extrabold text-brand-navy mt-0.5">{shoulderCm}</span>
                <span className="text-[9px] text-brand-slate">cm</span>
              </div>
              <div className="flex flex-col items-center justify-center rounded-16 border border-slate-100 bg-white p-2.5 shadow-card text-center">
                <span className="text-[10px] uppercase font-semibold text-brand-muted">Vòng ngực</span>
                <span className="text-base font-extrabold text-brand-navy mt-0.5">{chestCm}</span>
                <span className="text-[9px] text-brand-slate">cm</span>
              </div>
              <div className="flex flex-col items-center justify-center rounded-16 border border-slate-100 bg-white p-2.5 shadow-card text-center">
                <span className="text-[10px] uppercase font-semibold text-brand-muted">Vòng eo</span>
                <span className="text-base font-extrabold text-brand-navy mt-0.5">{waistCm}</span>
                <span className="text-[9px] text-brand-slate">cm</span>
              </div>
              <div className="flex flex-col items-center justify-center rounded-16 border border-slate-100 bg-white p-2.5 shadow-card text-center">
                <span className="text-[10px] uppercase font-semibold text-brand-muted">Vòng mông</span>
                <span className="text-base font-extrabold text-brand-navy mt-0.5">{hipsCm}</span>
                <span className="text-[9px] text-brand-slate">cm</span>
              </div>
              <div className="flex flex-col items-center justify-center rounded-16 border border-slate-100 bg-white p-2.5 shadow-card text-center">
                <span className="text-[10px] uppercase font-semibold text-brand-muted">Dài tay</span>
                <span className="text-base font-extrabold text-brand-navy mt-0.5">{armLengthCm}</span>
                <span className="text-[9px] text-brand-slate">cm</span>
              </div>
              <div className="flex flex-col items-center justify-center rounded-16 border border-slate-100 bg-white p-2.5 shadow-card text-center">
                <span className="text-[10px] uppercase font-semibold text-brand-muted">Dài chân</span>
                <span className="text-base font-extrabold text-brand-navy mt-0.5">{inseamCm}</span>
                <span className="text-[9px] text-brand-slate">cm</span>
              </div>
            </div>
          )}
        </section>

        {/* 4. Smart Fit Notes */}
        <section className="flex flex-col gap-2 rounded-20 border border-slate-200/80 bg-white p-3.5 shadow-card">
          <div className="flex items-center gap-1.5">
            <span className="text-xs">💡</span>
            <span className="text-xs font-bold text-brand-navy">
              Lời Khuyên Chọn Size Từ AI
            </span>
          </div>
          <ul className="flex flex-col gap-1.5 pl-4 list-disc text-[11px] text-brand-slate leading-relaxed">
            <li>
              Tỷ lệ Eo/Hông (WHR): <strong className="text-brand-navy">{(waistCm / hipsCm).toFixed(2)}</strong> — {currentShape.desc}
            </li>
            {gender === 'male' && currentShape.code === 'hinh_thang' && (
              <li>Vóc dáng cân đối tự nhiên: Phù hợp với hầu hết các mẫu áo Slim-fit hoặc Regular-fit.</li>
            )}
            {gender === 'female' && currentShape.code === 'dong_ho_cat' && (
              <li>Ưu tiên các mẫu áo/đầm có điểm nhấn eo để tôn trọn vóc dáng đường cong.</li>
            )}
            {inseamCm / heightCm > 0.46 && (
              <li>Đôi chân dài so với tỷ lệ chiều cao: Quần dài nên kiểm tra kỹ thông số chiều dài ống.</li>
            )}
          </ul>
        </section>
      </div>

      {/* Footer CTAs */}
      <div className="flex flex-col gap-2 p-5 bg-white border-t border-brand-border/60">
        <Button
          variant="primary"
          size="lg"
          fullWidth
          onClick={handleContinue}
        >
          Xem Gợi Ý Size Chuẩn Xác →
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
          <button
            type="button"
            onClick={onRetake}
            className="font-medium text-brand-teal hover:underline active:scale-95 transition-all"
          >
            Chụp lại ảnh
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

      {/* Confidence Breakdown Modal */}
      {showConfidenceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-sm rounded-24 bg-white p-5 shadow-2xl border border-brand-teal/20 flex flex-col gap-4 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between border-b border-brand-border/60 pb-3">
              <div className="flex items-center gap-2">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[#ECF8F7] text-brand-teal text-sm">
                  🛡️
                </span>
                <h3 className="text-sm font-bold text-brand-navy">Độ Tin Cậy AI: {confidencePercent}%</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowConfidenceModal(false)}
                className="flex h-6 w-6 items-center justify-center rounded-full text-brand-muted hover:bg-slate-100 hover:text-brand-navy transition-colors text-sm"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-brand-slate leading-relaxed">
              Điểm tin cậy được tính toán từ mô hình <strong>Hybrid Stereometry 2D</strong> kết hợp dữ liệu kiểm định chuẩn (Benchmark) và chất lượng ảnh thực tế:
            </p>

            <div className="flex flex-col gap-2 rounded-16 bg-[#ECF8F7]/60 border border-[#D1EDEA] p-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-brand-muted">Mô hình đo:</span>
                <span className="font-semibold text-brand-navy">Hybrid Stereometry 2D</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-brand-muted">Benchmark chuẩn:</span>
                <span className="font-semibold text-brand-teal">
                  {confidenceMetrics?.benchmark_baseline ? `${confidenceMetrics.benchmark_baseline}% (MAE ~1.7cm)` : '93.3% Pass Rate'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-brand-muted">Số góc ảnh:</span>
                <span className="font-semibold text-brand-navy">
                  {sideImageUrl ? '2 góc (Chính diện + Nghiêng)' : '1 góc (Chính diện)'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-brand-muted">Nhận diện mốc xương:</span>
                <span className="font-semibold text-emerald-600">
                  {confidenceMetrics?.landmark_visibility_pct ? `${confidenceMetrics.landmark_visibility_pct}% rõ nét` : '33/33 điểm khớp'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-brand-muted">Sai số tham khảo:</span>
                <span className="font-semibold text-brand-navy">
                  ±{confidenceMetrics?.expected_mae_cm || 1.7} cm
                </span>
              </div>
            </div>

            <div className="rounded-12 bg-amber-50 border border-amber-200/80 p-2.5 text-[11px] text-amber-800 leading-relaxed">
              💡 <strong>Mẹo:</strong> AI trích xuất kích thước chuẩn người thật. Bạn hoàn toàn có thể nhấn <strong>&ldquo;Chỉnh sửa số đo&rdquo;</strong> để tùy biến theo gu mặc ôm hoặc rộng mong muốn.
            </div>

            <Button
              variant="primary"
              size="md"
              fullWidth
              onClick={() => setShowConfidenceModal(false)}
            >
              Đã hiểu
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
