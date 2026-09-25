'use client';

import React, { useState, useMemo } from 'react';
import { MOCK_GARMENTS } from '@/data/mockFittingData';
import { Garment, Brand, Category } from '@/types/fitting';
import { useProfiles } from '@/hooks/useProfiles';
import { ProfileSwitcher } from '@/components/ui/ProfileSwitcher';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { FittingWidget } from '@/components/fitting/FittingWidget';

type BrandFilter = 'all' | Brand;
type CategoryFilter = 'all' | Category;

export default function CatalogPage() {
  const { profiles, activeProfile, setActiveProfile, addProfile, isLoaded } = useProfiles();

  const [selectedBrand, setSelectedBrand] = useState<BrandFilter>('all');
  const [selectedCategory, setSelectedCategory] = useState<CategoryFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [fittingGarment, setFittingGarment] = useState<Garment | null>(null);

  // Brand filter tabs configuration
  const brandTabs: { label: string; value: BrandFilter }[] = [
    { label: 'Tất cả (50)', value: 'all' },
    { label: 'Zara (10)', value: 'zara' },
    { label: 'Uniqlo (10)', value: 'uniqlo' },
    { label: 'H&M (10)', value: 'hm' },
    { label: 'Pull&Bear (10)', value: 'pullandbear' },
    { label: 'Stradivarius (10)', value: 'stradivarius' },
  ];

  // Category filter tabs
  const categoryTabs: { label: string; value: CategoryFilter }[] = [
    { label: 'Tất cả danh mục', value: 'all' },
    { label: 'Áo khoác', value: 'jacket' },
    { label: 'Áo dạ & Măng tô', value: 'coat' },
    { label: 'Áo phao', value: 'puffer' },
    { label: 'Blazer', value: 'blazer' },
  ];

  // Filtered garments calculation
  const filteredGarments = useMemo(() => {
    return MOCK_GARMENTS.filter((g) => {
      const matchBrand = selectedBrand === 'all' || g.brand === selectedBrand;
      const matchCategory = selectedCategory === 'all' || g.category === selectedCategory;
      const query = searchQuery.trim().toLowerCase();
      const matchSearch =
        !query ||
        g.name.toLowerCase().includes(query) ||
        g.sku.toLowerCase().includes(query);

      return matchBrand && matchCategory && matchSearch;
    });
  }, [selectedBrand, selectedCategory, searchQuery]);

  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-brand-canvas">
        <div className="h-10 w-10 animate-spin rounded-full border-3 border-brand-teal border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F6FBFA] text-brand-navy">
      {/* Top E-Commerce Header */}
      <header className="sticky top-0 z-30 border-b border-brand-border/70 bg-white/95 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          {/* Logo & Brand Identity */}
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-14 bg-brand-teal text-white shadow-sm font-bold">
              AI
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-extrabold tracking-tight text-brand-navy">
                  AI Precision Fit
                </span>
                <span className="hidden sm:inline-flex rounded-full bg-brand-teal-subtle px-2 py-0.5 text-[10px] font-bold text-brand-teal">
                  DEMO STORE
                </span>
              </div>
              <p className="hidden md:block text-[11px] text-brand-muted">
                Trợ lý AI thử đồ & chọn size thông minh cho thời trang Outerwear
              </p>
            </div>
          </div>

          {/* Active Profile Switcher on Header */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex flex-col text-right">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-brand-slate">
                Người thử đồ:
              </span>
              <span className="text-xs font-bold text-brand-teal">
                {activeProfile.name} ({activeProfile.heightCm}cm • {activeProfile.weightKg}kg)
              </span>
            </div>
            <ProfileSwitcher
              profiles={profiles}
              activeProfile={activeProfile}
              onSelectProfile={setActiveProfile}
              onAddProfile={() => {
                const newProf = addProfile({
                  name: 'Người thân mới',
                  gender: 'female',
                  fitPreference: 'regular',
                  heightCm: 160,
                  weightKg: 48,
                });
                setActiveProfile(newProf.id);
              }}
            />
          </div>
        </div>

        {/* Search & Filter Subbar */}
        <div className="mx-auto max-w-7xl border-t border-brand-border/40 px-4 py-2.5 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            {/* Brand Filter Pills */}
            <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5">
              {brandTabs.map((tab) => (
                <button
                  key={tab.value}
                  type="button"
                  onClick={() => setSelectedBrand(tab.value)}
                  className={`rounded-full px-3 py-1 text-xs font-medium shrink-0 transition-all ${
                    selectedBrand === tab.value
                      ? 'bg-brand-teal text-white shadow-sm font-semibold'
                      : 'bg-white text-brand-slate border border-brand-border hover:border-brand-teal/40 hover:bg-slate-50'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Search Input Box */}
            <div className="relative w-full md:w-64">
              <input
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm áo, SKU hoặc kiểu dáng..."
                className="h-9 w-full rounded-full border border-brand-border bg-white pl-8 pr-4 text-xs text-brand-navy placeholder:text-brand-muted/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-teal transition-all"
              />
              <svg
                className="absolute left-2.5 top-2.5 h-4 w-4 text-brand-muted fill-none stroke-current stroke-2"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
      </header>

      {/* Main Catalog Body */}
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Banner Section */}
        <div className="relative mb-6 overflow-hidden rounded-24 bg-gradient-to-r from-brand-navy via-[#1F3D55] to-brand-teal p-6 text-white shadow-widget">
          <div className="relative z-10 max-w-2xl">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-white/20 backdrop-blur-md px-3 py-0.5 text-xs font-semibold text-teal-200 mb-2">
              ✨ 50 MẪU SẢN PHẨM OUTERWEAR THỰC TẾ
            </span>
            <h1 className="text-xl font-extrabold tracking-tight sm:text-2xl lg:text-3xl text-white">
              Chọn Chiếc Áo Ưa Thích & Trải Nghiệm AI Fitting
            </h1>
            <p className="mt-1.5 text-xs sm:text-sm text-slate-200 leading-relaxed">
              Bấm nút <strong>&quot;Thử Đồ & Chọn Size AI&quot;</strong> trên bất kỳ sản phẩm nào để kích hoạt công nghệ
              so khớp nhân trắc học và mô phỏng Virtual Try-On cho <strong className="text-white underline">{activeProfile.name}</strong>.
            </p>
          </div>
        </div>

        {/* Results Counter & Category Bar */}
        <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-xs font-semibold text-brand-slate">
            Hiển thị <span className="font-bold text-brand-teal">{filteredGarments.length}</span> sản phẩm phù hợp
          </div>

          <div className="flex items-center gap-1 overflow-x-auto no-scrollbar">
            {categoryTabs.map((cat) => (
              <button
                key={cat.value}
                type="button"
                onClick={() => setSelectedCategory(cat.value)}
                className={`rounded-12 px-2.5 py-1 text-[11px] font-medium transition-all ${
                  selectedCategory === cat.value
                    ? 'bg-brand-navy text-white font-semibold'
                    : 'text-brand-slate hover:bg-slate-200/60'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Garment Grid */}
        {filteredGarments.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-24 border border-dashed border-brand-border bg-white py-16 text-center">
            <svg className="h-12 w-12 text-brand-muted/60 stroke-current stroke-1.5 fill-none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-bold text-brand-navy">Không tìm thấy sản phẩm phù hợp</h3>
            <p className="mt-1 text-xs text-brand-muted">Vui lòng thử đổi từ khóa tìm kiếm hoặc chọn thương hiệu khác.</p>
            <button
              type="button"
              onClick={() => {
                setSelectedBrand('all');
                setSelectedCategory('all');
                setSearchQuery('');
              }}
              className="mt-4 rounded-full bg-brand-teal-subtle px-4 py-1.5 text-xs font-semibold text-brand-teal hover:bg-teal-100 transition-all"
            >
              Đặt lại toàn bộ bộ lọc
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {filteredGarments.map((garment) => (
              <article
                key={garment.id}
                className="group relative flex flex-col overflow-hidden rounded-20 border border-brand-border bg-white shadow-card hover:shadow-widget hover:border-brand-teal/40 transition-all duration-200"
              >
                {/* Product Image Box */}
                <div className="relative aspect-[3/4] w-full overflow-hidden bg-slate-100">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={garment.imageUrl}
                    alt={garment.name}
                    loading="lazy"
                    className="h-full w-full object-cover object-top group-hover:scale-105 transition-transform duration-300"
                  />

                  {/* Brand Tag Overlay */}
                  <span className="absolute top-2.5 left-2.5 rounded-full bg-black/60 backdrop-blur-md px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white">
                    {garment.brand}
                  </span>

                  {/* Stretch Badge */}
                  <span className="absolute bottom-2.5 left-2.5 rounded bg-white/90 backdrop-blur-md px-1.5 py-0.5 text-[10px] font-semibold text-brand-slate shadow-sm">
                    Độ co giãn: {garment.fabricStretch}
                  </span>
                </div>

                {/* Info Container */}
                <div className="flex flex-1 flex-col justify-between p-3.5">
                  <div>
                    <div className="flex items-center justify-between text-[11px] text-brand-muted">
                      <span>{garment.sku}</span>
                      <span className="capitalize">{garment.category}</span>
                    </div>

                    <h2 className="mt-1 text-xs font-bold text-brand-navy line-clamp-2 leading-snug group-hover:text-brand-teal transition-colors">
                      {garment.name}
                    </h2>
                  </div>

                  <div className="mt-3 flex flex-col gap-2.5 pt-2.5 border-t border-brand-border/60">
                    <div className="flex items-baseline justify-between">
                      <span className="text-sm font-extrabold text-brand-navy">
                        {garment.price?.toLocaleString('vi-VN')} đ
                      </span>
                      <div className="flex gap-1">
                        {garment.availableSizes?.slice(0, 4).map((s) => (
                          <span
                            key={s}
                            className="rounded bg-slate-100 px-1 py-0.2 text-[10px] font-medium text-brand-slate"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Action Button: Trigger Fitting Widget */}
                    <Button
                      variant="primary"
                      size="sm"
                      fullWidth
                      onClick={() => setFittingGarment(garment)}
                      leftIcon={
                        <svg className="h-3.5 w-3.5 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      }
                    >
                      Thử Đồ & Chọn Size AI
                    </Button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-brand-border/70 bg-white py-6 text-center text-xs text-brand-muted">
        <p>© 2026 AI Precision Fit — On-Premise Virtual Fitting MVP. Base on Humanstack Vibe Coding.</p>
      </footer>

      {/* Fitting Widget Modal Overlay when a product is clicked */}
      {fittingGarment && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-0 sm:p-4 animate-in fade-in duration-200"
        >
          <div className="relative flex h-full w-full max-w-[430px] items-center justify-center">
            <FittingWidget
              initialGarment={fittingGarment}
              onClose={() => setFittingGarment(null)}
            />
          </div>
        </div>
      )}
    </div>
  );
}