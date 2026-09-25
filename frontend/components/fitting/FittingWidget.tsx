'use client';

import React, { useState } from 'react';
import { WidgetContainer } from '@/components/fitting/WidgetContainer';
import { WelcomeScreen } from '@/components/fitting/WelcomeScreen';
import { ProfileSetupScreen } from '@/components/fitting/ProfileSetupScreen';
import { MethodSelectScreen } from '@/components/fitting/MethodSelectScreen';
import { UploadGuideScreen } from '@/components/fitting/UploadGuideScreen';
import { UploadVerifyScreen } from '@/components/fitting/UploadVerifyScreen';
import { ManualInputScreen } from '@/components/fitting/ManualInputScreen';
import { AnalyzingScreen } from '@/components/fitting/AnalyzingScreen';
import { RecommendationScreen } from '@/components/fitting/RecommendationScreen';
import { ProfileListScreen } from '@/components/fitting/ProfileListScreen';
import { ProfileDetailScreen } from '@/components/fitting/ProfileDetailScreen';
import { VTOPreviewModal } from '@/components/fitting/VTOPreviewModal';

import { useFittingFlow } from '@/hooks/useFittingFlow';
import { useProfiles } from '@/hooks/useProfiles';
import { MOCK_GARMENTS, MOCK_SIZE_CHARTS } from '@/data/mockFittingData';
import { Garment, UserProfile, QualityCheckResponse, BodyMeasurements } from '@/types/fitting';

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

  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#E5EDF0]">
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
          onSelectMethod={(method) => {
            updateSessionData({ method });
            if (method === 'ai_photo') {
              goToStep('upload_guide');
            } else {
              goToStep('manual_input');
            }
          }}
        />
      )}

      {/* 4. Upload Guide Screen */}
      {currentStep === 'upload_guide' && (
        <UploadGuideScreen
          onBack={goBack}
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
          onSubmit={(measurements: BodyMeasurements) => {
            updateProfile(activeProfile.id, measurements);
            goToStep('analyzing');
          }}
        />
      )}

      {/* 7. Analyzing Screen */}
      {currentStep === 'analyzing' && (
        <AnalyzingScreen
          onComplete={() => {
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
