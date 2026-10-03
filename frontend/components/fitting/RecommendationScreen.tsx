'use client';

import React, { useState, useEffect } from 'react';
import { StepHeader } from '@/components/ui/StepHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { SegmentedControl } from '@/components/ui/SegmentedControl';
import { ProfileSwitcher } from '@/components/ui/ProfileSwitcher';
import {
  Garment,
  GarmentSizeChart,
  UserProfile,
  FitPreference,
  SizeRecommendResponse,
  FitIntelligenceResponse,
} from '@/types/fitting';
import { calculateFitRecommendation } from '@/services/fitEngine';
import { apiClient } from '@/services/apiClient';

export interface RecommendationScreenProps {
  garment: Garment;
  sizeCharts: GarmentSizeChart[];
  profiles: UserProfile[];
  activeProfile: UserProfile;
  onSelectProfile: (id: string) => void;
  onBack: () => void;
  onClose?: () => void;
  onOpenTryOn: () => void;
}

export function RecommendationScreen({
  garment,
  sizeCharts,
  profiles,
  activeProfile,
  onSelectProfile,
  onBack,
  onClose,
  onOpenTryOn,
}: RecommendationScreenProps) {
  const [preferenceOverride, setPreferenceOverride] = useState<FitPreference>(activeProfile.fitPreference || 'regular');
  const [show3DModal, setShow3DModal] = useState(false);
  const [backendFit, setBackendFit] = useState<FitIntelligenceResponse | null>(null);

  // Recalculate recommendation based on active profile and preference override (Client baseline fallback)
  const clientRecommendation: SizeRecommendResponse = calculateFitRecommendation(
    garment,
    sizeCharts,
    activeProfile,
    preferenceOverride
  );

  // Fetch advanced ML recommendation & copywriting from backend /api/v1/fit-intelligence/recommend
  useEffect(() => {
    let isMounted = true;
    apiClient
      .getFitIntelligence({
        productId: garment.id,
        measurements: {
          height: activeProfile.heightCm,
          weight: activeProfile.weightKg,
          shoulder: activeProfile.shoulderCm || 39.0,
          bust: activeProfile.chestCm || 86.0,
          waist: activeProfile.waistCm || 70.0,
          hip: activeProfile.hipsCm || 92.0,
        },
        fitPreference: preferenceOverride,
      })
      .then((data) => {
        if (isMounted) setBackendFit(data);
      })
      .catch((err) => {
        console.warn('Backend Fit Intelligence fallback to local client engine:', err);
      });

    return () => {
      isMounted = false;
    };
  }, [garment.id, activeProfile, preferenceOverride]);

  const recommendedSize = backendFit?.recommendedSize || clientRecommendation.recommendedSize;
  const confidencePercent = backendFit?.confidence || clientRecommendation.confidencePercent;
  const headline = backendFit?.headline;
  const whyText = backendFit?.whyText || clientRecommendation.summaryExplanation;

  return (
    <div className="flex flex-1 flex-col justify-between bg-brand-canvas animate-in fade-in duration-200 relative">
      {/* Top Header with Profile Switcher */}
      <div className="flex items-center justify-between px-5 py-2.5 bg-white border-b border-brand-border/60">
        <span className="text-[11px] font-bold uppercase tracking-wider text-brand-teal">
          Kết Quả Phân Tích
        </span>
        <ProfileSwitcher
          profiles={profiles}
          activeProfile={activeProfile}
          onSelectProfile={onSelectProfile}
        />
      </div>

      <StepHeader
        title={`Gợi Ý Size: ${recommendedSize}`}
        subtitle={`Tính toán cho ${activeProfile.name} • ${activeProfile.heightCm}cm`}
        onBack={onBack}
        onClose={onClose}
      />

      <div className="flex flex-1 flex-col gap-4 p-5 overflow-y-auto no-scrollbar">
        {/* Main Recommendation Hero Card */}
        <section
          className="flex flex-col gap-3 rounded-24 border-2 border-brand-teal/30 bg-gradient-to-br from-white to-[#ECF8F7] p-4 shadow-widget"
          aria-label="Khuyến nghị kích thước chính"
        >
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-brand-slate uppercase tracking-wider">
                Kích Cỡ Khuyên Dùng
              </span>
              <div className="flex items-baseline gap-2 mt-0.5">
                <span className="text-4xl font-black text-brand-teal tracking-tight">
                  Size {recommendedSize}
                </span>
                <span className="text-xs font-bold text-brand-teal-match">
                  ({confidencePercent}% phù hợp)
                </span>
              </div>
            </div>

            <Badge variant="perfect" size="md" dot>
              {backendFit?.confidenceLabel || clientRecommendation.fitPreferenceLabel}
            </Badge>
          </div>

          {headline && (
            <h4 className="text-sm font-bold text-brand-navy">
              {headline}
            </h4>
          )}

          <p className="text-xs leading-relaxed text-brand-slate">
            {whyText}
          </p>

          {/* 4 Vùng cơ thể chi tiết nếu có từ Backend Fit Engine */}
          {backendFit?.zones && backendFit.zones.length > 0 ? (
            <div className="flex flex-wrap gap-1.5 pt-2 border-t border-brand-border/60">
              {backendFit.zones.map((zone) => (
                <Badge
                  key={zone.zone}
                  variant={
                    zone.status === 'optimal'
                      ? 'perfect'
                      : zone.status.includes('tight')
                      ? 'tight'
                      : 'loose'
                  }
                  size="sm"
                >
                  {zone.zoneVn}: {zone.badge}
                </Badge>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-1.5 pt-2 border-t border-brand-border/60">
              {clientRecommendation.breakdown.map((part) => (
                <Badge
                  key={part.part}
                  variant={
                    part.status === 'perfect'
                      ? 'perfect'
                      : part.status.includes('tight')
                      ? 'tight'
                      : 'loose'
                  }
                  size="sm"
                >
                  {part.partLabel}: {part.statusLabel}
                </Badge>
              ))}
            </div>
          )}
        </section>

        {/* 3D Body Shape Showcase Card */}
        <div className="flex items-center justify-between rounded-16 border border-brand-teal/40 bg-white p-3.5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-12 bg-brand-teal/10 text-brand-teal text-xl">
              🧍
            </div>
            <div>
              <div className="text-xs font-bold text-brand-navy">
                Mô Hình Vóc Dáng 3D Của Bạn
              </div>
              <div className="text-[11px] text-brand-muted">
                Xoay 360°, đối chiếu tỷ lệ thực tế & số đo
              </div>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShow3DModal(true)}
          >
            Mở 3D Studio
          </Button>
        </div>

        {/* Dynamic Preference Override Filter */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold uppercase tracking-wider text-brand-slate">
            Thử Đổi Gu Mặc (Xem Độ Ôm Thay Đổi)
          </label>
          <SegmentedControl<FitPreference>
            name="preference-override"
            value={preferenceOverride}
            onChange={setPreferenceOverride}
            options={[
              { label: 'Ôm nhẹ', value: 'slim' },
              { label: 'Vừa vặn', value: 'regular' },
              { label: 'Rộng rãi', value: 'relaxed' },
            ]}
          />
        </div>

        {/* Hotspot Comparison Across Sizes */}
        <section className="flex flex-col gap-2" aria-label="So sánh các size">
          <h3 className="text-xs font-bold uppercase tracking-wider text-brand-slate">
            Chi Tiết So Sánh Các Size Khác
          </h3>

          <div className="flex flex-col gap-2">
            {Object.keys(clientRecommendation.sizeComparisons).map((sizeKey) => {
              const comp = clientRecommendation.sizeComparisons[sizeKey];
              const isBest = sizeKey === recommendedSize;

              return (
                <div
                  key={sizeKey}
                  className={`flex items-center justify-between rounded-16 border p-3 transition-all ${
                    isBest
                      ? 'border-brand-teal bg-white shadow-card'
                      : 'border-brand-border/70 bg-white/70'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`flex h-9 w-9 items-center justify-center rounded-12 text-sm font-bold ${
                        isBest
                          ? 'bg-brand-teal text-white shadow-sm'
                          : 'bg-slate-100 text-brand-navy'
                      }`}
                    >
                      {sizeKey}
                    </span>

                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-brand-navy">
                          Phù hợp: {Math.round(comp.fitScore * 100)}%
                        </span>
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.2 rounded-full ${
                            isBest
                              ? 'bg-emerald-100 text-emerald-800'
                              : comp.badgeLabel.includes('chật')
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {comp.badgeLabel}
                        </span>
                      </div>
                      <p className="text-[11px] text-brand-muted line-clamp-1 mt-0.5">
                        {comp.description}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>

      {/* 3D Studio Iframe Modal */}
      {show3DModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="relative flex h-[85vh] w-full max-w-lg flex-col rounded-24 bg-slate-900 border border-slate-700 shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3 bg-slate-950 text-white">
              <div className="flex items-center gap-2">
                <span className="text-lg">🧍</span>
                <span className="text-sm font-bold">3D Body Studio — {activeProfile.name}</span>
              </div>
              <button
                type="button"
                onClick={() => setShow3DModal(false)}
                className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-800 text-slate-300 hover:bg-slate-700"
              >
                ✕
              </button>
            </div>
            <iframe
              src="http://localhost:8000/api/v1/body-shape/studio"
              className="flex-1 w-full border-none bg-slate-950"
              title="3D Body Studio"
            />
          </div>
        </div>
      )}

      {/* Sticky Bottom Actions */}
      <footer className="sticky bottom-0 flex flex-col gap-2 border-t border-brand-border/60 bg-white/95 backdrop-blur-sm p-4">
        <Button
          variant="primary"
          size="lg"
          fullWidth
          onClick={onOpenTryOn}
          leftIcon={
            <svg className="h-5 w-5 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          }
        >
          Mặc Thử Ảo Với AI (Virtual Try-On)
        </Button>
      </footer>
    </div>
  );
}
