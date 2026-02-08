'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/auth-store';
import { apiClient } from '@/lib/api-client';

interface APIKey {
  id: string;
  provider_name: string;
  api_key_masked: string;
  is_active: boolean;
}

/**
 * Hook to manage the API key setup wizard state
 * Shows wizard on first login if user has no API keys configured
 */
export function useAPIKeyWizard() {
  const { user, isAuthenticated } = useAuthStore();
  const [shouldShowWizard, setShouldShowWizard] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    checkWizardStatus();
  }, [user, isAuthenticated]);

  const checkWizardStatus = async () => {
    // Don't show wizard if not authenticated
    if (!isAuthenticated || !user) {
      setIsChecking(false);
      setShouldShowWizard(false);
      return;
    }

    // Check if wizard has been completed before
    const wizardCompleted = typeof window !== 'undefined' 
      ? localStorage.getItem('api_key_wizard_completed') === 'true'
      : false;

    if (wizardCompleted) {
      setIsChecking(false);
      setShouldShowWizard(false);
      return;
    }

    // Check if user has any API keys configured
    try {
      const response = await apiClient.get<{ api_keys: APIKey[]; total: number }>(
        '/api/v1/user/api-keys'
      );

      const hasApiKeys = response.data.api_keys.length > 0;

      // Show wizard if user has no API keys and hasn't completed wizard
      setShouldShowWizard(!hasApiKeys && !wizardCompleted);
    } catch (error) {
      console.error('Failed to check API keys:', error);
      // Don't show wizard if we can't check
      setShouldShowWizard(false);
    } finally {
      setIsChecking(false);
    }
  };

  const markWizardCompleted = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('api_key_wizard_completed', 'true');
    }
    setShouldShowWizard(false);
  };

  const resetWizard = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('api_key_wizard_completed');
    }
    checkWizardStatus();
  };

  return {
    shouldShowWizard,
    isChecking,
    markWizardCompleted,
    resetWizard,
  };
}
