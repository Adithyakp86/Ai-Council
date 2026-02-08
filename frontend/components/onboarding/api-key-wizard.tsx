'use client';

import { useState, useEffect } from 'react';
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import {
  Eye,
  EyeOff,
  Loader2,
  CheckCircle,
  XCircle,
  ExternalLink,
  Info,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Key,
  Zap,
  Shield,
  DollarSign,
} from 'lucide-react';

interface ProviderInfo {
  name: string;
  display_name: string;
  provider_type: 'free' | 'paid' | 'local';
  description: string;
  free_tier_info: string | null;
  signup_url: string;
  docs_url: string;
  setup_steps: string[];
  benefits: string[];
  icon: string;
}

// Free providers recommended for new users
const RECOMMENDED_FREE_PROVIDERS: ProviderInfo[] = [
  {
    name: 'gemini',
    display_name: 'Google Gemini',
    provider_type: 'free',
    description: "Google's powerful Gemini AI models with a generous free tier.",
    free_tier_info: 'Free tier: 60 requests/minute, no billing required',
    signup_url: 'https://makersuite.google.com/app/apikey',
    docs_url: '/docs/gemini-setup',
    icon: '✨',
    setup_steps: [
      'Go to Google AI Studio (makersuite.google.com)',
      'Sign in with your Google account',
      'Click "Get API Key" button',
      'Create a new API key or use an existing one',
      'Copy the API key and paste it below',
    ],
    benefits: [
      'Completely free - no credit card required',
      '60 requests per minute',
      'Fast inference speed',
      'Large context window (32K tokens)',
      'Multimodal support (text + images)',
    ],
  },
  {
    name: 'huggingface',
    display_name: 'HuggingFace',
    provider_type: 'free',
    description: 'Access thousands of open-source AI models via HuggingFace Inference API.',
    free_tier_info: 'Free tier: ~1000 requests/day',
    signup_url: 'https://huggingface.co/settings/tokens',
    docs_url: '/docs/huggingface-setup',
    icon: '🤗',
    setup_steps: [
      'Go to HuggingFace (huggingface.co)',
      'Create a free account or sign in',
      'Go to Settings → Access Tokens',
      'Click "New token" and give it a name',
      'Copy the token and paste it below',
    ],
    benefits: [
      'Completely free - no credit card required',
      '~1000 requests per day',
      'Access to thousands of open-source models',
      'Community-driven and transparent',
      'Great for experimentation',
    ],
  },
];

interface APIKeyWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onComplete: () => void;
}

type WizardStep = 'welcome' | 'choose-provider' | 'setup-key' | 'complete';

export function APIKeyWizard({ open, onOpenChange, onComplete }: APIKeyWizardProps) {
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState<WizardStep>('welcome');
  const [selectedProvider, setSelectedProvider] = useState<ProviderInfo | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  // Reset state when dialog opens
  useEffect(() => {
    if (open) {
      setCurrentStep('welcome');
      setSelectedProvider(null);
      setApiKey('');
      setShowApiKey(false);
      setTestResult(null);
    }
  }, [open]);

  const handleClose = () => {
    onOpenChange(false);
  };

  const handleSkip = () => {
    // Mark wizard as completed even if skipped
    if (typeof window !== 'undefined') {
      localStorage.setItem('api_key_wizard_completed', 'true');
    }
    onComplete();
    handleClose();
  };

  const handleNext = () => {
    if (currentStep === 'welcome') {
      setCurrentStep('choose-provider');
    } else if (currentStep === 'choose-provider' && selectedProvider) {
      setCurrentStep('setup-key');
    }
  };

  const handleBack = () => {
    if (currentStep === 'setup-key') {
      setCurrentStep('choose-provider');
      setApiKey('');
      setTestResult(null);
    } else if (currentStep === 'choose-provider') {
      setCurrentStep('welcome');
      setSelectedProvider(null);
    }
  };

  const handleSelectProvider = (provider: ProviderInfo) => {
    setSelectedProvider(provider);
    setCurrentStep('setup-key');
  };

  const handleTestKey = async () => {
    if (!selectedProvider || !apiKey.trim()) {
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
      const response = await apiClient.post<{
        is_valid: boolean;
        error_message: string | null;
        provider_name: string;
      }>('/api/v1/user/api-keys/test-new', {
        provider_name: selectedProvider.name,
        api_key: apiKey.trim(),
      });

      if (response.data.is_valid) {
        setTestResult({
          success: true,
          message: `✓ API key is valid! ${selectedProvider.display_name} is ready to use.`,
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

  const handleSaveAndComplete = async () => {
    if (!selectedProvider || !apiKey.trim()) {
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
        provider_name: selectedProvider.name,
        api_key: apiKey.trim(),
      });

      // Mark wizard as completed
      if (typeof window !== 'undefined') {
        localStorage.setItem('api_key_wizard_completed', 'true');
      }

      setCurrentStep('complete');
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

  const handleFinish = () => {
    onComplete();
    handleClose();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        {/* Welcome Step */}
        {currentStep === 'welcome' && (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3 text-2xl">
                <Sparkles className="h-8 w-8 text-primary" />
                Welcome to AI Council!
              </DialogTitle>
              <DialogDescription className="text-base">
                Let's get you set up with your first AI provider
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 py-6">
              {/* Benefits of Adding Own Keys */}
              <div className="space-y-4">
                <h3 className="font-semibold text-lg">Why add your own API keys?</h3>
                
                <div className="grid gap-4 md:grid-cols-2">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <DollarSign className="h-4 w-4 text-green-600" />
                        Free Tier Benefits
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Many providers offer generous free tiers. Use your own keys to maximize free usage.
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Zap className="h-4 w-4 text-yellow-600" />
                        Better Performance
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Your own keys mean dedicated rate limits and faster response times.
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Shield className="h-4 w-4 text-blue-600" />
                        Privacy & Control
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Your API keys, your data. Full control over which providers you use.
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Key className="h-4 w-4 text-purple-600" />
                        No Shared Limits
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Avoid shared system rate limits. Your keys = your quota.
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* System Defaults Info */}
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Don't have API keys yet?</strong> No problem! You can skip this wizard and use our system default keys to get started. You can always add your own keys later in Settings.
                </AlertDescription>
              </Alert>
            </div>

            <DialogFooter className="flex justify-between">
              <Button variant="outline" onClick={handleSkip}>
                Skip for Now
              </Button>
              <Button onClick={handleNext}>
                Get Started
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </DialogFooter>
          </>
        )}

        {/* Choose Provider Step */}
        {currentStep === 'choose-provider' && (
          <>
            <DialogHeader>
              <DialogTitle className="text-xl">Choose a Free Provider</DialogTitle>
              <DialogDescription>
                Select one of these free providers to get started. Both are completely free with no credit card required.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-6">
              {RECOMMENDED_FREE_PROVIDERS.map((provider) => (
                <Card
                  key={provider.name}
                  className={`cursor-pointer transition-all hover:border-primary ${
                    selectedProvider?.name === provider.name ? 'border-primary border-2' : ''
                  }`}
                  onClick={() => handleSelectProvider(provider)}
                >
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                      <span className="text-3xl">{provider.icon}</span>
                      <div>
                        <div className="flex items-center gap-2">
                          {provider.display_name}
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">
                            Free
                          </span>
                        </div>
                        <p className="text-sm font-normal text-muted-foreground mt-1">
                          {provider.description}
                        </p>
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <p className="text-sm font-medium mb-2">Benefits:</p>
                        <ul className="text-sm text-muted-foreground space-y-1">
                          {provider.benefits.slice(0, 3).map((benefit, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                              <span>{benefit}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <DialogFooter className="flex justify-between">
              <Button variant="outline" onClick={handleBack}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Button>
              <Button variant="outline" onClick={handleSkip}>
                Skip for Now
              </Button>
            </DialogFooter>
          </>
        )}

        {/* Setup Key Step */}
        {currentStep === 'setup-key' && selectedProvider && (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3">
                <span className="text-3xl">{selectedProvider.icon}</span>
                Set up {selectedProvider.display_name}
              </DialogTitle>
              <DialogDescription>
                Follow these steps to get your free API key
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 py-4">
              {/* Setup Steps */}
              <div className="space-y-3">
                <h4 className="font-medium">Step-by-step instructions:</h4>
                <ol className="space-y-2">
                  {selectedProvider.setup_steps.map((step, idx) => (
                    <li key={idx} className="flex gap-3 text-sm">
                      <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-medium">
                        {idx + 1}
                      </span>
                      <span className="pt-0.5">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>

              {/* Get API Key Button */}
              <Alert>
                <ExternalLink className="h-4 w-4" />
                <AlertDescription>
                  <div className="flex items-center justify-between">
                    <span>Ready to get your API key?</span>
                    <Button
                      variant="link"
                      size="sm"
                      className="h-auto p-0"
                      onClick={() => window.open(selectedProvider.signup_url, '_blank')}
                    >
                      Open {selectedProvider.display_name}
                      <ExternalLink className="ml-1 h-3 w-3" />
                    </Button>
                  </div>
                </AlertDescription>
              </Alert>

              {/* API Key Input */}
              <div className="space-y-2">
                <Label htmlFor="api-key">Paste your API key here:</Label>
                <div className="relative">
                  <Input
                    id="api-key"
                    type={showApiKey ? 'text' : 'password'}
                    value={apiKey}
                    onChange={(e) => {
                      setApiKey(e.target.value);
                      setTestResult(null);
                    }}
                    placeholder={`Enter your ${selectedProvider.display_name} API key`}
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

              {/* Test Button */}
              <Button
                variant="outline"
                onClick={handleTestKey}
                disabled={!apiKey.trim() || testing || submitting}
                className="w-full"
              >
                {testing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Testing your API key...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Test API Key
                  </>
                )}
              </Button>

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
            </div>

            <DialogFooter className="flex justify-between">
              <Button variant="outline" onClick={handleBack}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Button>
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleSkip}>
                  Skip for Now
                </Button>
                <Button
                  onClick={handleSaveAndComplete}
                  disabled={!apiKey.trim() || submitting || testing || !testResult?.success}
                >
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      Save & Continue
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
              </div>
            </DialogFooter>
          </>
        )}

        {/* Complete Step */}
        {currentStep === 'complete' && selectedProvider && (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3 text-2xl">
                <CheckCircle className="h-8 w-8 text-green-600" />
                You're All Set!
              </DialogTitle>
              <DialogDescription className="text-base">
                {selectedProvider.display_name} has been configured successfully
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 py-6">
              <Alert variant="success">
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  <strong>Success!</strong> Your {selectedProvider.display_name} API key is now active and ready to use.
                </AlertDescription>
              </Alert>

              <div className="space-y-4">
                <h3 className="font-semibold">What's next?</h3>
                <ul className="space-y-3">
                  <li className="flex gap-3 text-sm">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-medium">
                      1
                    </span>
                    <span className="pt-0.5">
                      <strong>Start chatting:</strong> Submit your first query and watch AI Council orchestrate multiple models
                    </span>
                  </li>
                  <li className="flex gap-3 text-sm">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-medium">
                      2
                    </span>
                    <span className="pt-0.5">
                      <strong>Add more providers:</strong> Go to Settings to add more AI providers for better orchestration
                    </span>
                  </li>
                  <li className="flex gap-3 text-sm">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-medium">
                      3
                    </span>
                    <span className="pt-0.5">
                      <strong>Explore features:</strong> Check out your dashboard, history, and analytics
                    </span>
                  </li>
                </ul>
              </div>

              <Card className="bg-muted">
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground">
                    <strong>Tip:</strong> AI Council works best with multiple providers. Consider adding HuggingFace or other free providers in Settings for optimal orchestration and redundancy.
                  </p>
                </CardContent>
              </Card>
            </div>

            <DialogFooter>
              <Button onClick={handleFinish} className="w-full">
                Start Using AI Council
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
