'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { councilApi } from '@/lib/council-api';
import type { ExecutionMode, CostEstimate } from '@/types/council';
import { Loader2 } from 'lucide-react';

interface QueryInputProps {
  onSubmit: (query: string, mode: ExecutionMode) => void;
  isProcessing?: boolean;
}

export function QueryInput({ onSubmit, isProcessing = false }: QueryInputProps) {
  const [query, setQuery] = useState('');
  const [selectedMode, setSelectedMode] = useState<ExecutionMode>('balanced');
  const [costEstimate, setCostEstimate] = useState<CostEstimate | null>(null);
  const [isLoadingEstimate, setIsLoadingEstimate] = useState(false);

  const maxLength = 5000;
  const remainingChars = maxLength - query.length;

  // Fetch cost estimate when query changes (debounced)
  useEffect(() => {
    if (query.length < 10) {
      setCostEstimate(null);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoadingEstimate(true);
      try {
        const estimate = await councilApi.getCostEstimate(query);
        setCostEstimate(estimate);
      } catch (error) {
        console.error('Failed to fetch cost estimate:', error);
      } finally {
        setIsLoadingEstimate(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSubmit = () => {
    if (query.trim() && query.length <= maxLength) {
      onSubmit(query.trim(), selectedMode);
    }
  };

  const isValid = query.trim().length > 0 && query.length <= maxLength;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Submit Your Query</CardTitle>
        <CardDescription>
          Ask AI Council anything. Your query will be intelligently decomposed and processed by multiple specialized AI models.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Query Input */}
        <div className="space-y-2">
          <Textarea
            placeholder="Enter your query here... (e.g., 'Explain the pros and cons of renewable energy sources')"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="min-h-[150px] resize-y"
            maxLength={maxLength}
            disabled={isProcessing}
          />
          <div className="flex justify-between text-sm">
            <span className={remainingChars < 100 ? 'text-orange-500' : 'text-muted-foreground'}>
              {remainingChars} characters remaining
            </span>
            <span className="text-muted-foreground">
              {query.length} / {maxLength}
            </span>
          </div>
        </div>

        {/* Execution Mode Selector */}
        <div className="space-y-3">
          <label className="text-sm font-medium">Execution Mode</label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* Fast Mode */}
            <button
              type="button"
              onClick={() => setSelectedMode('fast')}
              disabled={isProcessing}
              className={`p-4 border rounded-lg text-left transition-all ${
                selectedMode === 'fast'
                  ? 'border-primary bg-primary/5 ring-2 ring-primary'
                  : 'border-border hover:border-primary/50'
              } ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="font-semibold mb-1">⚡ Fast</div>
              <div className="text-xs text-muted-foreground mb-2">
                Minimal decomposition, faster models
              </div>
              {costEstimate && (
                <div className="text-xs space-y-1">
                  <div className="font-medium">${costEstimate.fast.toFixed(4)}</div>
                  <div className="text-muted-foreground">
                    ~{costEstimate.estimatedTime.fast}s
                  </div>
                </div>
              )}
            </button>

            {/* Balanced Mode */}
            <button
              type="button"
              onClick={() => setSelectedMode('balanced')}
              disabled={isProcessing}
              className={`p-4 border rounded-lg text-left transition-all ${
                selectedMode === 'balanced'
                  ? 'border-primary bg-primary/5 ring-2 ring-primary'
                  : 'border-border hover:border-primary/50'
              } ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="font-semibold mb-1 flex items-center gap-2">
                ⚖️ Balanced
                <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                  Recommended
                </span>
              </div>
              <div className="text-xs text-muted-foreground mb-2">
                Moderate decomposition, mixed models
              </div>
              {costEstimate && (
                <div className="text-xs space-y-1">
                  <div className="font-medium">${costEstimate.balanced.toFixed(4)}</div>
                  <div className="text-muted-foreground">
                    ~{costEstimate.estimatedTime.balanced}s
                  </div>
                </div>
              )}
            </button>

            {/* Best Quality Mode */}
            <button
              type="button"
              onClick={() => setSelectedMode('best_quality')}
              disabled={isProcessing}
              className={`p-4 border rounded-lg text-left transition-all ${
                selectedMode === 'best_quality'
                  ? 'border-primary bg-primary/5 ring-2 ring-primary'
                  : 'border-border hover:border-primary/50'
              } ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="font-semibold mb-1">💎 Best Quality</div>
              <div className="text-xs text-muted-foreground mb-2">
                Maximum decomposition, premium models
              </div>
              {costEstimate && (
                <div className="text-xs space-y-1">
                  <div className="font-medium">${costEstimate.bestQuality.toFixed(4)}</div>
                  <div className="text-muted-foreground">
                    ~{costEstimate.estimatedTime.bestQuality}s
                  </div>
                </div>
              )}
            </button>
          </div>
        </div>

        {/* Cost Estimate Loading */}
        {isLoadingEstimate && query.length >= 10 && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Calculating cost estimates...</span>
          </div>
        )}

        {/* Submit Button */}
        <Button
          onClick={handleSubmit}
          disabled={!isValid || isProcessing}
          className="w-full"
          size="lg"
        >
          {isProcessing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processing...
            </>
          ) : (
            'Submit Query'
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
