'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { MonitoringData } from '@/lib/admin-api'
import { Activity, AlertCircle, CheckCircle, XCircle } from 'lucide-react'

interface SystemMonitoringProps {
  monitoring: MonitoringData | null
}

export function SystemMonitoring({ monitoring }: SystemMonitoringProps) {
  if (!monitoring) {
    return null
  }

  const getHealthBadge = (status: 'healthy' | 'degraded' | 'down') => {
    switch (status) {
      case 'healthy':
        return (
          <Badge variant="default" className="bg-green-500">
            <CheckCircle className="h-3 w-3 mr-1" />
            Healthy
          </Badge>
        )
      case 'degraded':
        return (
          <Badge variant="default" className="bg-yellow-500">
            <AlertCircle className="h-3 w-3 mr-1" />
            Degraded
          </Badge>
        )
      case 'down':
        return (
          <Badge variant="destructive">
            <XCircle className="h-3 w-3 mr-1" />
            Down
          </Badge>
        )
    }
  }

  const getCircuitBreakerBadge = (state: 'open' | 'closed' | 'half-open') => {
    switch (state) {
      case 'closed':
        return (
          <Badge variant="default" className="bg-green-500">
            Closed
          </Badge>
        )
      case 'half-open':
        return (
          <Badge variant="default" className="bg-yellow-500">
            Half-Open
          </Badge>
        )
      case 'open':
        return (
          <Badge variant="destructive">
            Open
          </Badge>
        )
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Provider Health */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              AI Provider Health
            </CardTitle>
            <CardDescription>Status of cloud AI providers</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Groq</p>
                  <p className="text-sm text-gray-500">Ultra-fast inference</p>
                </div>
                {getHealthBadge(monitoring.providerHealth.groq)}
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Together.ai</p>
                  <p className="text-sm text-gray-500">Diverse model selection</p>
                </div>
                {getHealthBadge(monitoring.providerHealth.together)}
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">OpenRouter</p>
                  <p className="text-sm text-gray-500">Multi-provider access</p>
                </div>
                {getHealthBadge(monitoring.providerHealth.openrouter)}
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">HuggingFace</p>
                  <p className="text-sm text-gray-500">Open models</p>
                </div>
                {getHealthBadge(monitoring.providerHealth.huggingface)}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Circuit Breaker States */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertCircle className="h-5 w-5 mr-2" />
              Circuit Breaker States
            </CardTitle>
            <CardDescription>Failure protection status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Groq</p>
                  <p className="text-sm text-gray-500">Failure threshold: 5</p>
                </div>
                {getCircuitBreakerBadge(monitoring.circuitBreakers.groq)}
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Together.ai</p>
                  <p className="text-sm text-gray-500">Failure threshold: 5</p>
                </div>
                {getCircuitBreakerBadge(monitoring.circuitBreakers.together)}
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">OpenRouter</p>
                  <p className="text-sm text-gray-500">Failure threshold: 5</p>
                </div>
                {getCircuitBreakerBadge(monitoring.circuitBreakers.openrouter)}
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">HuggingFace</p>
                  <p className="text-sm text-gray-500">Failure threshold: 5</p>
                </div>
                {getCircuitBreakerBadge(monitoring.circuitBreakers.huggingface)}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Provider Cost Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Provider Cost Breakdown (Last 24h)</CardTitle>
          <CardDescription>
            Cost distribution across AI providers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-muted/50 p-4 rounded-lg">
                <p className="text-sm text-muted-foreground">Total Cost</p>
                <p className="text-2xl font-bold">
                  ${monitoring.providerCostBreakdown.totalCost.toFixed(4)}
                </p>
              </div>
              <div className="bg-muted/50 p-4 rounded-lg">
                <p className="text-sm text-muted-foreground">Total Requests</p>
                <p className="text-2xl font-bold">
                  {monitoring.providerCostBreakdown.totalRequests}
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-green-700">Estimated Savings</p>
                <p className="text-2xl font-bold text-green-600">
                  ${monitoring.providerCostBreakdown.estimatedSavings.toFixed(4)}
                </p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-blue-700">Free Provider Usage</p>
                <p className="text-2xl font-bold text-blue-600">
                  {monitoring.providerCostBreakdown.freeProviderUsagePercent.toFixed(0)}%
                </p>
              </div>
            </div>

            {/* Provider Breakdown */}
            <div className="space-y-4">
              {monitoring.providerCostBreakdown.byProvider.map((provider, index) => {
                const percentage = monitoring.providerCostBreakdown.totalCost > 0
                  ? (provider.totalCost / monitoring.providerCostBreakdown.totalCost) * 100
                  : 0;
                const isFree = ['ollama', 'huggingface', 'gemini'].includes(provider.providerName.toLowerCase());
                
                return (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-medium capitalize">{provider.providerName}</span>
                        {isFree && (
                          <Badge variant="default" className="bg-green-500">
                            Free
                          </Badge>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="font-medium">${provider.totalCost.toFixed(4)}</div>
                        <div className="text-sm text-muted-foreground">
                          {provider.requestCount} requests, {provider.totalSubtasks} subtasks
                        </div>
                      </div>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${isFree ? 'bg-green-500' : 'bg-primary'}`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>
                        {provider.totalInputTokens.toLocaleString()} input + {provider.totalOutputTokens.toLocaleString()} output tokens
                      </span>
                      <span>{percentage.toFixed(1)}% of total cost</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
