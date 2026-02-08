'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/auth-store';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { AuthenticatedLayout } from '@/components/layout/authenticated-layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import {
  Key,
  CheckCircle,
  AlertTriangle,
  Trash2,
  Plus,
  Loader2,
  TestTube,
} from 'lucide-react';
import { APIKeyDialog } from '@/components/settings/api-key-dialog';

interface APIKey {
  id: string;
  provider_name: string;
  api_key_masked: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_used_at: string | null;
}

interface ProviderInfo {
  name: string;
  display_name: string;
  provider_type: 'free' | 'paid' | 'local';
  description: string;
  free_tier_info: string | null;
  signup_url: string;
  docs_url: string;
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

// Supported providers list (should match backend)
const SUPPORTED_PROVIDERS: ProviderInfo[] = [
  {
    name: 'ollama',
    display_name: 'Ollama',
    provider_type: 'local',
    description: 'Local AI models running on your machine. 100% free, no API keys needed.',
    free_tier_info: 'Completely free - runs locally on your hardware',
    signup_url: 'https://ollama.ai',
    docs_url: '/docs/ollama-setup',
  },
  {
    name: 'gemini',
    display_name: 'Google Gemini',
    provider_type: 'free',
    description: "Google's Gemini AI models with generous free tier.",
    free_tier_info: 'Free tier: 60 requests/minute, no billing required',
    signup_url: 'https://makersuite.google.com/app/apikey',
    docs_url: '/docs/gemini-setup',
  },
  {
    name: 'huggingface',
    display_name: 'HuggingFace',
    provider_type: 'free',
    description: 'Open-source AI models via HuggingFace Inference API.',
    free_tier_info: 'Free tier: ~1000 requests/day',
    signup_url: 'https://huggingface.co/settings/tokens',
    docs_url: '/docs/huggingface-setup',
  },
  {
    name: 'groq',
    display_name: 'Groq',
    provider_type: 'paid',
    description: "Ultra-fast inference with Groq's LPU technology.",
    free_tier_info: 'Free credits available on signup',
    signup_url: 'https://console.groq.com',
    docs_url: '/docs/groq-setup',
  },
  {
    name: 'together',
    display_name: 'Together AI',
    provider_type: 'paid',
    description: 'Access to diverse open-source models.',
    free_tier_info: '$25 free credits on signup',
    signup_url: 'https://api.together.xyz',
    docs_url: '/docs/together-setup',
  },
  {
    name: 'openrouter',
    display_name: 'OpenRouter',
    provider_type: 'paid',
    description: 'Unified access to multiple AI providers.',
    free_tier_info: '$1-5 free credits on signup',
    signup_url: 'https://openrouter.ai',
    docs_url: '/docs/openrouter-setup',
  },
  {
    name: 'openai',
    display_name: 'OpenAI',
    provider_type: 'paid',
    description: 'GPT-3.5, GPT-4, and other OpenAI models.',
    free_tier_info: '$5 free trial (requires payment method)',
    signup_url: 'https://platform.openai.com',
    docs_url: '/docs/openai-setup',
  },
  {
    name: 'qwen',
    display_name: 'Qwen (Alibaba Cloud)',
    provider_type: 'paid',
    description: "Alibaba's Qwen AI models.",
    free_tier_info: 'Free tier available in some regions',
    signup_url: 'https://dashscope.aliyun.com',
    docs_url: '/docs/qwen-setup',
  },
];

function SettingsContent() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { toast } = useToast();
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<ProviderInfo | null>(null);
  const [testingProvider, setTestingProvider] = useState<string | null>(null);

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get<{ api_keys: APIKey[]; total: number }>(
        '/api/v1/user/api-keys'
      );
      setApiKeys(response.data.api_keys);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load API keys',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteApiKey = async (providerName: string) => {
    if (!confirm(`Are you sure you want to delete the API key for ${providerName}?`)) {
      return;
    }

    try {
      await apiClient.delete(`/api/v1/user/api-keys/${providerName}`);

      toast({
        title: 'Success',
        description: 'API key deleted successfully',
      });

      fetchApiKeys();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete API key',
        variant: 'destructive',
      });
    }
  };

  const handleTestApiKey = async (providerName: string) => {
    setTestingProvider(providerName);
    try {
      const response = await apiClient.post<{
        is_valid: boolean;
        error_message: string | null;
        provider_name: string;
      }>(`/api/v1/user/api-keys/${providerName}/test`);

      if (response.data.is_valid) {
        toast({
          title: 'Success',
          description: `API key for ${providerName} is valid`,
        });
      } else {
        toast({
          title: 'Invalid API Key',
          description: response.data.error_message || 'API key validation failed',
          variant: 'destructive',
        });
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to test API key',
        variant: 'destructive',
      });
    } finally {
      setTestingProvider(null);
    }
  };

  const openAddDialog = (providerName: string) => {
    const providerInfo = getProviderInfo(providerName);
    if (providerInfo) {
      setSelectedProvider(providerInfo);
      setAddDialogOpen(true);
    }
  };

  const getProviderStatus = (providerName: string) => {
    const userKey = apiKeys.find((key) => key.provider_name === providerName);
    if (userKey) {
      return { type: 'configured', icon: CheckCircle, color: 'text-green-600' };
    }
    return { type: 'system', icon: AlertTriangle, color: 'text-yellow-600' };
  };

  const getProviderInfo = (providerName: string) => {
    return SUPPORTED_PROVIDERS.find((p) => p.name === providerName);
  };

  return (
    <div className="min-h-screen bg-background py-8 px-4">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Settings</h1>
            <p className="text-muted-foreground">Manage your API keys and preferences</p>
          </div>
        </div>

        {/* API Keys Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5" />
              API Keys
            </CardTitle>
            <CardDescription>
              Configure your own API keys for AI providers. Keys are encrypted and stored securely.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-24 bg-muted rounded" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {SUPPORTED_PROVIDERS.map((provider) => {
                  const status = getProviderStatus(provider.name);
                  const userKey = apiKeys.find((key) => key.provider_name === provider.name);
                  const StatusIcon = status.icon;

                  return (
                    <Card key={provider.name} className="border-2">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-4">
                          {/* Provider Info */}
                          <div className="flex items-start gap-3 flex-1">
                            <div className="text-3xl">{providerIcons[provider.name] || '🔑'}</div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold">{provider.display_name}</h3>
                                <StatusIcon className={`h-4 w-4 ${status.color}`} />
                                {provider.provider_type === 'free' && (
                                  <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">
                                    Free
                                  </span>
                                )}
                                {provider.provider_type === 'local' && (
                                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                                    Local
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-muted-foreground mb-2">
                                {provider.description}
                              </p>
                              {provider.free_tier_info && (
                                <p className="text-xs text-muted-foreground italic">
                                  {provider.free_tier_info}
                                </p>
                              )}
                              {userKey && (
                                <div className="mt-2 space-y-1">
                                  <p className="text-xs text-muted-foreground">
                                    Key: <code className="bg-muted px-1 py-0.5 rounded">{userKey.api_key_masked}</code>
                                  </p>
                                  {userKey.last_used_at && (
                                    <p className="text-xs text-muted-foreground">
                                      Last used: {new Date(userKey.last_used_at).toLocaleDateString()}
                                    </p>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex flex-col gap-2">
                            {userKey ? (
                              <>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleTestApiKey(provider.name)}
                                  disabled={testingProvider === provider.name}
                                >
                                  {testingProvider === provider.name ? (
                                    <>
                                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                      Testing...
                                    </>
                                  ) : (
                                    <>
                                      <TestTube className="h-4 w-4 mr-2" />
                                      Test
                                    </>
                                  )}
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => openAddDialog(provider.name)}
                                >
                                  <Key className="h-4 w-4 mr-2" />
                                  Update
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => handleDeleteApiKey(provider.name)}
                                >
                                  <Trash2 className="h-4 w-4 mr-2" />
                                  Delete
                                </Button>
                              </>
                            ) : (
                              <Button
                                size="sm"
                                onClick={() => openAddDialog(provider.name)}
                              >
                                <Plus className="h-4 w-4 mr-2" />
                                Add Key
                              </Button>
                            )}
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => window.open(provider.signup_url, '_blank')}
                            >
                              Get API Key
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}

            <div className="mt-6 p-4 bg-muted rounded-lg">
              <h4 className="font-medium mb-2 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-yellow-600" />
                About API Keys
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Your API keys are encrypted and stored securely</li>
                <li>Keys with a green checkmark are configured by you</li>
                <li>Keys with a yellow warning are using system defaults (if available)</li>
                <li>Free tier providers are great for getting started</li>
                <li>You can test your keys to verify they work correctly</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Add/Update API Key Dialog */}
      <APIKeyDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
        provider={selectedProvider}
        existingKey={
          selectedProvider
            ? apiKeys.find((k) => k.provider_name === selectedProvider.name)?.api_key_masked
            : null
        }
        onSuccess={fetchApiKeys}
      />
    </div>
  );
}

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <AuthenticatedLayout>
        <SettingsContent />
      </AuthenticatedLayout>
    </ProtectedRoute>
  );
}
