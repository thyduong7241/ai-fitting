'use client';

import { useState, useCallback } from 'react';
import { FlowStep, FitMethod, BodyMeasurements, SizeLabel } from '@/types/fitting';

export interface FittingSessionData {
  profileId?: string;
  method?: FitMethod;
  frontImageUrl?: string;
  sideImageUrl?: string;
  measurements?: Partial<BodyMeasurements>;
  garmentId?: string;
  recommendedSize?: SizeLabel;
}

export interface UseFittingFlowReturn {
  currentStep: FlowStep;
  stepHistory: FlowStep[];
  canGoBack: boolean;
  sessionData: FittingSessionData;
  goToStep: (step: FlowStep) => void;
  goBack: () => void;
  updateSessionData: (data: Partial<FittingSessionData>) => void;
  resetFlow: (initialStep?: FlowStep) => void;
}

export function useFittingFlow(initialStep: FlowStep = 'welcome'): UseFittingFlowReturn {
  const [currentStep, setCurrentStep] = useState<FlowStep>(initialStep);
  const [stepHistory, setStepHistory] = useState<FlowStep[]>([initialStep]);
  const [sessionData, setSessionData] = useState<FittingSessionData>({
    method: 'ai_photo',
  });

  const goToStep = useCallback((nextStep: FlowStep) => {
    setCurrentStep(nextStep);
    setStepHistory((prev) => [...prev, nextStep]);
  }, []);

  const goBack = useCallback(() => {
    setStepHistory((prev) => {
      if (prev.length <= 1) return prev;
      const newHistory = [...prev];
      newHistory.pop(); // Remove current step
      const previousStep = newHistory[newHistory.length - 1];
      setCurrentStep(previousStep);
      return newHistory;
    });
  }, []);

  const updateSessionData = useCallback((data: Partial<FittingSessionData>) => {
    setSessionData((prev) => ({
      ...prev,
      ...data,
      measurements: {
        ...prev.measurements,
        ...data.measurements,
      },
    }));
  }, []);

  const resetFlow = useCallback((startStep: FlowStep = 'welcome') => {
    setCurrentStep(startStep);
    setStepHistory([startStep]);
    setSessionData({ method: 'ai_photo' });
  }, []);

  return {
    currentStep,
    stepHistory,
    canGoBack: stepHistory.length > 1,
    sessionData,
    goToStep,
    goBack,
    updateSessionData,
    resetFlow,
  };
}
