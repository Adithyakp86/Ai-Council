'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import {
  Eye,
  EyeOff,
  Loader2,
  TestTube,
  CheckCircle,
  XCircle,
  ExternalLink,
  Info,
} from 'lucide-react';

export interface ProviderInfo {
  name: string;
  display_name: string;
  provider_type: 'free' | 'paid' | 'local';
  description: string;
  free_tier_info: string | null;
  signup_url: string;
  docs_url: string;
  capabilities?: string[];
  cost_info?: string;
}

interface APIKeyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  provider: ProviderInfo | null;
  existingKey?: string | null;
  onSuccess: () => void;
}

// Provider logos/icons mapping
const providerIcons: Record<string, string> = {
  ollama: '🦙',
  gemini: '✨',
  huggingface: '🤗',
  groq: '⚡',
  together: '🤝',
  openrouter: '🔀',
  openai: '🤖',
  qwen: '🐼',
};

// Provider capabilities mapping
const providerCapabilities: Record<string, string[]> = {
  ollama: ['Local execution', 'No API costs', 'Privacy-focused', 'Multiple models'],
  gemini: ['Fast inference', 'Large context window', 'Multimodal support', 'Free tier'],
  huggingface: ['Open-source models', 'Wide model selection', 'Free tier', 'Community-driven'],
  groq: ['Ultra-fast inference', 'Low latency', 'High throughput', 'Cost-effective'],
  together: ['Diverse models', 'Competitive pricing', 'Good reliability', 'API flexibility'],
  openrouter: ['Multi-provider access', 'Unified API', 'Fallback support', 'Model variety'],
  openai: ['GPT-4 access', 'High quality', 'Reliable', 'Advanced reasoning'],
  qwen: ['Multilingual support', 'Chinese language expertise', 'Competitive pricing', 'Good performance'],
};

// Provider cost information
const providerCostInfo: Record<string, string> = {
  ollama: 'Free - runs locally on your hardware',
  gemini: 'Free tier: 60 requests/min, then ~$0.0001/1K tokens',
  huggingface: 'Free tier: ~1000 requests/day, then pay-as-you-go',
  groq: 'Starting at $0.00027/1K tokens (very competitive)',
  together: 'Starting at $0.0002/1K tokens with $25 free credits',
  openrouter: 'Variable pricing by model, $1-5 free credits',
  openai: 'GPT-3.5: $0.0005/1K tokens, GPT-4: $0.03/1K tokens',
  qwen: 'Competitive pricing, free tier available in some regions',
};

export function APIKeyDialog({
  open,
  onOpenChange,
  provider,
  existingKey,
  onSuccess,
}: APIKeyDialogProps) {
  const { toast } = useToast();
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const handleClose = () => {
    setApiKey('');
    setShowApiKey(false);
    setTestResult(null);
    onOpenChange(false);
  };

  const handleTestKey = async () => {
    if (!provider || !apiKey.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter an API key to test',
        variant: 'destructive',
      });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      // First save the key temporarily or test directly
      // For now, we'll test by attempting to save and then test
      const response = await apiClient.post<{
        is_valid: boolean;
        error_message: string | null;
        provider_name: string;
      }>('/api/v1/user/api-keys/test-new', {
        provider_name: provider.name,
        api_key: apiKey.trim(),
      });

      if (response.data.is_valid) {
        setTestResult({
          success: true,
          message: `API key is valid! ${provider.display_name} is ready to use.`,
        });
      } else {
        setTestResult({
          success: false,
          message: response.data.error_message || 'API key validation failed',
        });
      }
    } catch (error: any) {
      setTestResult({
        success: false,
        message: error.response?.data?.detail || 'Failed to test API key',
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    if (!provider || !apiKey.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter an API key',
        variant: 'destructive',
      });
      return;
    }

    setSubmitting(true);

    try {
      await apiClient.post('/api/v1/user/api-keys', {
        provider_name: provider.name,
        api_key: apiKey.trim(),
      });

      toast({
        title: 'Success',
        description: `API key for ${provider.display_name} saved successfully`,
      });

      handleClose();
      onSuccess();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to save API key',
        variant: 'destructive',
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (!provider) return null;

  const capabilities = providerCapabilities[provider.name] || [];
  const costInfo = providerCostInfo[provider.name] || 'Pricing varies';
  const icon = providerIcons[provider.name] || '🔑';

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <span className="text-3xl">{icon}</span>
            <span>
              {existingKey ? 'Update' : 'Add'} {provider.display_name} API Key
            </span>
          </DialogTitle>
          <DialogDescription>{provider.description}</DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Get API Key Link */}
          <Alert variant="info">
            <Info className="h-4 w-4" />
            <AlertDescription>
              <div className="flex items-center justify-between">
                <span>Don't have an API key yet?</span>
                <Button
                  variant="link"
                  size="sm"
                  className="h-auto p-0"
                  onClick={() => window.open(provider.signup_url, '_blank')}
                >
                  Get your {provider.display_name} API key
                  <ExternalLink className="ml-1 h-3 w-3" />
                </Button>
              </div>
            </AlertDescription>
          </Alert>

          {/* API Key Input */}
          <div className="space-y-2">
            <Label htmlFor="api-key">API Key</Label>
            <div className="relative">
              <Input
                id="api-key"
                type={showApiKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => {
                  setApiKey(e.target.value);
                  setTestResult(null); // Clear test result when key changes
                }}
                placeholder={`Enter your ${provider.display_name} API key`}
                className="pr-10"
                autoComplete="off"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                onClick={() => setShowApiKey(!showApiKey)}
                tabIndex={-1}
              >
                {showApiKey ? (
                  <EyeOff className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <Eye className="h-4 w-4 text-muted-foreground" />
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Your API key will be encrypted and stored securely
            </p>
          </div>

          {/* Test Key Button */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleTestKey}
              disabled={!apiKey.trim() || testing || submitting}
              className="flex-1"
            >
              {testing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Testing...
                </>
              ) : (
                <>
                  <TestTube className="h-4 w-4 mr-2" />
                  Test Key
                </>
              )}
            </Button>
          </div>

          {/* Test Result */}
          {testResult && (
            <Alert variant={testResult.success ? 'success' : 'destructive'}>
              {testResult.success ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <XCircle className="h-4 w-4" />
              )}
              <AlertDescription>{testResult.message}</AlertDescription>
            </Alert>
          )}

          {/* Provider Benefits */}
          <div className="space-y-3 p-4 bg-muted rounded-lg">
            <h4 className="font-medium text-sm">Benefits of {provider.display_name}</h4>
            
            {/* Capabilities */}
            {capabilities.length > 0 && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">Capabilities:</p>
                <div className="flex flex-wrap gap-2">
                  {capabilities.map((capability) => (
                    <span
                      key={capability}
                      className="text-xs bg-background px-2 py-1 rounded border"
                    >
                      {capability}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Cost Information */}
            <div>
              <p className="text-xs text-muted-foreground mb-1">Cost:</p>
              <p className="text-sm">{costInfo}</p>
            </div>

            {/* Free Tier Info */}
            {provider.free_tier_info && (
              <div>
                <p className="text-xs text-muted-foreground mb-1">Free Tier:</p>
                <p className="text-sm">{provider.free_tier_info}</p>
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={submitting || testing}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={!apiKey.trim() || submitting || testing}
          >
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              'Save API Key'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
