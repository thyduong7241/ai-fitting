'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { UserProfile, CreateFitProfileRequest } from '@/types/fitting';
import { DEFAULT_PROFILES } from '@/data/mockFittingData';

const STORAGE_KEY_PROFILES = 'ai_precision_fit_profiles';
const STORAGE_KEY_ACTIVE_ID = 'ai_precision_fit_active_id';
const STORAGE_KEY_SESSION_ID = 'ai_fitting_session_id';

export interface UseProfilesReturn {
  profiles: UserProfile[];
  activeProfile: UserProfile;
  activeId: string;
  isLoaded: boolean;
  setActiveProfile: (id: string) => void;
  addProfile: (data: CreateFitProfileRequest | Omit<UserProfile, 'id' | 'createdAt' | 'updatedAt'>) => UserProfile;
  updateProfile: (id: string, updates: Partial<UserProfile>) => void;
  deleteProfile: (id: string) => void;
  resetProfiles: () => void;
}

export function useProfiles(): UseProfilesReturn {
  const [profiles, setProfiles] = useState<UserProfile[]>(DEFAULT_PROFILES);
  const [activeId, setActiveId] = useState<string>(DEFAULT_PROFILES[0].id);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  // Hydration-safe initial load from LocalStorage
  useEffect(() => {
    try {
      const storedProfiles = localStorage.getItem(STORAGE_KEY_PROFILES);
      const storedActiveId = localStorage.getItem(STORAGE_KEY_ACTIVE_ID);

      let loadedProfiles = DEFAULT_PROFILES;
      if (storedProfiles) {
        const parsed = JSON.parse(storedProfiles);
        if (Array.isArray(parsed) && parsed.length > 0) {
          loadedProfiles = parsed;
          setProfiles(parsed);
        } else {
          localStorage.setItem(STORAGE_KEY_PROFILES, JSON.stringify(DEFAULT_PROFILES));
        }
      } else {
        localStorage.setItem(STORAGE_KEY_PROFILES, JSON.stringify(DEFAULT_PROFILES));
      }

      if (storedActiveId && loadedProfiles.some((p) => p.id === storedActiveId)) {
        setActiveId(storedActiveId);
        localStorage.setItem(STORAGE_KEY_SESSION_ID, storedActiveId);
      } else {
        const fallbackId = loadedProfiles[0]?.id || DEFAULT_PROFILES[0].id;
        setActiveId(fallbackId);
        localStorage.setItem(STORAGE_KEY_ACTIVE_ID, fallbackId);
        localStorage.setItem(STORAGE_KEY_SESSION_ID, fallbackId);
      }
    } catch (err) {
      console.error('Failed to load fit profiles from localStorage:', err);
      setProfiles(DEFAULT_PROFILES);
      setActiveId(DEFAULT_PROFILES[0].id);
    } finally {
      setIsLoaded(true);
    }
  }, []);

  // Persist state to LocalStorage whenever profiles change
  useEffect(() => {
    if (!isLoaded) return;
    try {
      localStorage.setItem(STORAGE_KEY_PROFILES, JSON.stringify(profiles));
    } catch (err) {
      console.error('Failed to save profiles to localStorage:', err);
    }
  }, [profiles, isLoaded]);

  // Persist active ID and sync with session ID header key
  useEffect(() => {
    if (!isLoaded) return;
    try {
      localStorage.setItem(STORAGE_KEY_ACTIVE_ID, activeId);
      localStorage.setItem(STORAGE_KEY_SESSION_ID, activeId);
    } catch (err) {
      console.error('Failed to save active profile ID to localStorage:', err);
    }
  }, [activeId, isLoaded]);

  const setActiveProfile = useCallback((id: string) => {
    setActiveId(id);
  }, []);

  const addProfile = useCallback(
    (data: CreateFitProfileRequest | Omit<UserProfile, 'id' | 'createdAt' | 'updatedAt'>): UserProfile => {
      const newId = `p-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 6)}`;
      const nowIso = new Date().toISOString();

      const newProfile: UserProfile = {
        ...data,
        id: newId,
        isVerified: data.frontImageUrl ? true : false,
        isDefault: profiles.length === 0,
        createdAt: nowIso,
        updatedAt: 'Vừa xong',
      };

      setProfiles((prev) => [...prev, newProfile]);
      setActiveId(newId);
      return newProfile;
    },
    [profiles.length]
  );

  const updateProfile = useCallback((id: string, updates: Partial<UserProfile>) => {
    setProfiles((prev) =>
      prev.map((p) => {
        if (p.id !== id) return p;
        return {
          ...p,
          ...updates,
          updatedAt: 'Vừa xong',
        };
      })
    );
  }, []);

  const deleteProfile = useCallback(
    (id: string) => {
      setProfiles((prev) => {
        const filtered = prev.filter((p) => p.id !== id);
        if (filtered.length === 0) {
          // Keep at least one default profile
          return DEFAULT_PROFILES;
        }
        return filtered;
      });

      // If active profile was deleted, switch to first available
      setActiveId((currentActiveId) => {
        if (currentActiveId === id) {
          const remaining = profiles.filter((p) => p.id !== id);
          return remaining[0]?.id || DEFAULT_PROFILES[0].id;
        }
        return currentActiveId;
      });
    },
    [profiles]
  );

  const resetProfiles = useCallback(() => {
    setProfiles(DEFAULT_PROFILES);
    setActiveId(DEFAULT_PROFILES[0].id);
    try {
      localStorage.setItem(STORAGE_KEY_PROFILES, JSON.stringify(DEFAULT_PROFILES));
      localStorage.setItem(STORAGE_KEY_ACTIVE_ID, DEFAULT_PROFILES[0].id);
      localStorage.setItem(STORAGE_KEY_SESSION_ID, DEFAULT_PROFILES[0].id);
    } catch (err) {
      console.error('Failed to reset profiles in localStorage:', err);
    }
  }, []);

  const activeProfile = useMemo(() => {
    return profiles.find((p) => p.id === activeId) || profiles[0] || DEFAULT_PROFILES[0];
  }, [profiles, activeId]);

  return {
    profiles,
    activeProfile,
    activeId,
    isLoaded,
    setActiveProfile,
    addProfile,
    updateProfile,
    deleteProfile,
    resetProfiles,
  };
}
