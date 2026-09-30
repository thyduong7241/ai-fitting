'use client';

import React, { useState } from 'react';
import { WidgetContainer } from '@/components/fitting/WidgetContainer';
import { WelcomeScreen } from '@/components/fitting/WelcomeScreen';
import { ProfileSetupScreen } from '@/components/fitting/ProfileSetupScreen';
import { MethodSelectScreen } from '@/components/fitting/MethodSelectScreen';
import { BodyMetricsInputScreen } from '@/components/fitting/BodyMetricsInputScreen';
import { UploadGuideScreen } from '@/components/fitting/UploadGuideScreen';
import { UploadVerifyScreen } from '@/components/fitting/UploadVerifyScreen';
import { ManualInputScreen } from '@/components/fitting/ManualInputScreen';
import { AnalyzingScreen } from '@/components/fitting/AnalyzingScreen';
import { MeasurementResultScreen } from '@/components/fitting/MeasurementResultScreen';
import { RecommendationScreen } from '@/components/fitting/RecommendationScreen';
import { ProfileListScreen } from '@/components/fitting/ProfileListScreen';
import { ProfileDetailScreen } from '@/components/fitting/ProfileDetailScreen';
import { VTOPreviewModal } from '@/components/fitting/VTOPreviewModal';

import { useFittingFlow } from '@/hooks/useFittingFlow';
import { useProfiles } from '@/hooks/useProfiles';
import { MOCK_GARMENTS, MOCK_SIZE_CHARTS } from '@/data/mockFittingData';
import { Garment, UserProfile, QualityCheckResponse, BodyMeasurements, MeasurementResponse } from '@/types/fitting';
import { activeTheme } from '@/config/theme';

export interface FittingWidgetProps {
  initialGarment?: Garment;
  onClose?: () => void;
}

export function FittingWidget({
  initialGarment = MOCK_GARMENTS[0],
  onClose,
}: FittingWidgetProps) {
  const { currentStep, goToStep, goBack, updateSessionData } = useFittingFlow('welcome');
  const { profiles, activeProfile, setActiveProfile, addProfile, updateProfile, deleteProfile, isLoaded } = useProfiles();

  const [garment] = useState<Garment>(initialGarment);
  const sizeCharts = MOCK_SIZE_CHARTS[garment.id] || MOCK_SIZE_CHARTS['zara_jk_01'] || [];

  const [selectedProfileForDetail, setSelectedProfileForDetail] = useState<UserProfile>(activeProfile);
  const [isVTOModalOpen, setIsVTOModalOpen] = useState(false);
  const [uploadedFrontImage, setUploadedFrontImage] = useState<string>('/mock/profile_trang_front.png');
  const [uploadedSideImage, setUploadedSideImage] = useState<string | undefined>('/mock/profile_trang_side.png');
  const [measurementResult, setMeasurementResult] = useState<MeasurementResponse | null>(null);

  const handleExit = () => {
    if (onClose) {
      onClose();
    } else {
      goToStep('welcome');
    }
  };

  if (!isLoaded) {
    return (
      <div className={`flex min-h-screen items-center justify-center bg-gradient-to-br ${activeTheme.backdropGradient}`}>
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-teal border-t-transparent" />
      </div>
    );
  }

  return (
    <WidgetContainer>
      {/* 1. Welcome Screen */}
      {currentStep === 'welcome' && (
        <WelcomeScreen
          garment={garment}
          activeProfile={activeProfile}
          onStart={() => goToStep('method_select')}
          onViewProfiles={() => goToStep('profile_list')}
          onClose={onClose}
        />
      )}

      {/* 2. Profile Setup Screen */}
      {currentStep === 'profile_setup' && (
        <ProfileSetupScreen
          initialProfile={activeProfile}
          onBack={goBack}
          onClose={handleExit}
          onSubmit={(data) => {
            const newProfile = addProfile(data);
            setActiveProfile(newProfile.id);
            goToStep('method_select');
          }}
        />
      )}

      {/* 3. Method Select Screen */}
      {currentStep === 'method_select' && (
        <MethodSelectScreen
          onBack={goBack}
          onClose={handleExit}
          onSelectMethod={(method) => {
            updateSessionData({ method });
            if (method === 'ai_photo') {
              goToStep('body_metrics_input');
            } else {
              goToStep('manual_input');
            }
          }}
        />
      )}

      {/* 3b. Body Metrics Input Screen (Chiều cao, cân nặng, tuổi, giới tính) */}
      {currentStep === 'body_metrics_input' && (
        <BodyMetricsInputScreen
          initialProfile={activeProfile}
          onBack={goBack}
          onClose={handleExit}
          onSubmit={(metrics) => {
            updateProfile(activeProfile.id, {
              gender: metrics.gender,
              heightCm: metrics.heightCm,
              weightKg: metrics.weightKg,
              age: metrics.age,
            });
            goToStep('upload_guide');
          }}
        />
      )}

      {/* 4. Upload Guide Screen */}
      {currentStep === 'upload_guide' && (
        <UploadGuideScreen
          onBack={goBack}
          onClose={handleExit}
          onContinue={(front, side) => {
            setUploadedFrontImage(front);
            setUploadedSideImage(side);
            goToStep('upload_verify');
          }}
        />
      )}

      {/* 5. Upload Verify Screen (Quality Gate) */}
      {currentStep === 'upload_verify' && (
        <UploadVerifyScreen
          frontImageUrl={uploadedFrontImage}
          sideImageUrl={uploadedSideImage}
          onBack={goBack}
          onClose={handleExit}
          onConfirm={(_res: QualityCheckResponse) => {
            goToStep('analyzing');
          }}
          onRetake={() => goToStep('upload_guide')}
        />
      )}

      {/* 6. Manual Input Screen */}
      {currentStep === 'manual_input' && (
        <ManualInputScreen
          activeProfile={activeProfile}
          onBack={goBack}
          onClose={handleExit}
          onSubmit={(measurements: BodyMeasurements) => {
            updateProfile(activeProfile.id, measurements);
            goToStep('analyzing');
          }}
        />
      )}

      {/* 7. Analyzing Screen */}
      {currentStep === 'analyzing' && (
        <AnalyzingScreen
          frontImageUrl={uploadedFrontImage}
          sideImageUrl={uploadedSideImage}
          activeProfile={activeProfile}
          onBack={goBack}
          onClose={handleExit}
          onComplete={(res) => {
            if (res) {
              setMeasurementResult(res);
              updateProfile(activeProfile.id, {
                ...res.measurements,
                bodyShape: res.bodyShape,
                smartFitNotes: res.smartFitNotes,
                frontImageUrl: uploadedFrontImage,
                sideImageUrl: uploadedSideImage,
                isVerified: true,
              });
            }
            goToStep('measurement_result');
          }}
        />
      )}

      {/* 7b. Measurement Result Screen (Hiển thị số đo AI trích xuất từ ảnh) */}
      {currentStep === 'measurement_result' && (
        <MeasurementResultScreen
          measurements={
            measurementResult?.measurements || {
              heightCm: activeProfile.heightCm,
              weightKg: activeProfile.weightKg,
              chestCm: activeProfile.chestCm || 88,
              waistCm: activeProfile.waistCm || 70,
              hipsCm: activeProfile.hipsCm || 92,
              shoulderCm: activeProfile.shoulderCm || 40,
              armLengthCm: activeProfile.armLengthCm || 56,
              inseamCm: activeProfile.inseamCm || 76,
            }
          }
          bodyShape={measurementResult?.bodyShape || activeProfile.bodyShape || 'chu_nhat'}
          smartFitNotes={measurementResult?.smartFitNotes || activeProfile.smartFitNotes}
          confidencePercent={measurementResult?.confidencePercent || 94}
          confidenceMetrics={measurementResult?.metrics}
          frontImageUrl={uploadedFrontImage}
          sideImageUrl={uploadedSideImage}
          activeProfile={activeProfile}
          onBack={goBack}
          onClose={handleExit}
          onRetake={() => goToStep('upload_guide')}
          onConfirm={(updatedMeasurements, updatedProfile) => {
            updateProfile(activeProfile.id, {
              ...updatedMeasurements,
              ...(updatedProfile || {}),
            });
            goToStep('recommendation');
          }}
        />
      )}

      {/* 8. Recommendation Screen */}
      {currentStep === 'recommendation' && (
        <RecommendationScreen
          garment={garment}
          sizeCharts={sizeCharts}
          profiles={profiles}
          activeProfile={activeProfile}
          onSelectProfile={setActiveProfile}
          onBack={() => goToStep('welcome')}
          onClose={handleExit}
          onOpenTryOn={() => setIsVTOModalOpen(true)}
        />
      )}

      {/* 9. Profile List Screen */}
      {currentStep === 'profile_list' && (
        <ProfileListScreen
          profiles={profiles}
          activeProfile={activeProfile}
          onSelectProfile={(id) => {
            setActiveProfile(id);
            goToStep('recommendation');
          }}
          onViewDetail={(prof) => {
            setSelectedProfileForDetail(prof);
            goToStep('profile_detail');
          }}
          onAddNew={() => goToStep('profile_setup')}
          onDeleteProfile={(id) => deleteProfile(id)}
          onBack={goBack}
        />
      )}

      {/* 10. Profile Detail Screen */}
      {currentStep === 'profile_detail' && (
        <ProfileDetailScreen
          profile={selectedProfileForDetail}
          onBack={goBack}
          onSave={(updates) => {
            updateProfile(selectedProfileForDetail.id, updates);
            goBack();
          }}
        />
      )}

      {/* Virtual Try-On Modal */}
      <VTOPreviewModal
        isOpen={isVTOModalOpen}
        onClose={() => setIsVTOModalOpen(false)}
        garment={garment}
        profile={activeProfile}
      />
    </WidgetContainer>
  );
}
