'use client';

import type { ExecutionMode, CostEstimate } from '@/types/council';

interface ExecutionModeSelectorProps {
  selectedMode: ExecutionMode;
  onModeChange: (mode: ExecutionMode) => void;
  costEstimate?: CostEstimate | null;
  disabled?: boolean;
}

interface ModeConfig {
  value: ExecutionMode;
  icon: string;
  label: string;
  description: string;
  recommended?: boolean;
}

const modes: ModeConfig[] = [
  {
    value: 'fast',
    icon: '⚡',
    label: 'Fast',
    description: 'Minimal decomposition, faster models for quick results',
  },
  {
    value: 'balanced',
    icon: '⚖️',
    label: 'Balanced',
    description: 'Moderate decomposition with mixed models for optimal balance',
    recommended: true,
  },
  {
    value: 'best_quality',
    icon: '💎',
    label: 'Best Quality',
    description: 'Maximum decomposition with premium models for highest quality',
  },
];

export function ExecutionModeSelector({
  selectedMode,
  onModeChange,
  costEstimate,
  disabled = false,
}: ExecutionModeSelectorProps) {
  const getCostForMode = (mode: ExecutionMode): number | null => {
    if (!costEstimate) return null;
    switch (mode) {
      case 'fast':
        return costEstimate.fast;
      case 'balanced':
        return costEstimate.balanced;
      case 'best_quality':
        return costEstimate.bestQuality;
    }
  };

  const getTimeForMode = (mode: ExecutionMode): number | null => {
    if (!costEstimate) return null;
    switch (mode) {
      case 'fast':
        return costEstimate.estimatedTime.fast;
      case 'balanced':
        return costEstimate.estimatedTime.balanced;
      case 'best_quality':
        return costEstimate.estimatedTime.bestQuality;
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">Execution Mode</label>
        <span className="text-xs text-muted-foreground">
          Choose your speed/cost/quality trade-off
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {modes.map((mode) => {
          const isSelected = selectedMode === mode.value;
          const cost = getCostForMode(mode.value);
          const time = getTimeForMode(mode.value);

          return (
            <button
              key={mode.value}
              type="button"
              onClick={() => onModeChange(mode.value)}
              disabled={disabled}
              className={`
                relative p-4 border rounded-lg text-left transition-all
                ${
                  isSelected
                    ? 'border-primary bg-primary/5 ring-2 ring-primary shadow-sm'
                    : 'border-border hover:border-primary/50 hover:bg-accent/50'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              {/* Recommended Badge */}
              {mode.recommended && (
                <div className="absolute -top-2 -right-2">
                  <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-primary text-primary-foreground rounded-full shadow-sm">
                    Recommended
                  </span>
                </div>
              )}

              {/* Mode Header */}
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">{mode.icon}</span>
                <span className="font-semibold">{mode.label}</span>
              </div>

              {/* Description */}
              <p className="text-xs text-muted-foreground mb-3 min-h-[2.5rem]">
                {mode.description}
              </p>

              {/* Cost and Time Estimates */}
              {cost !== null && time !== null ? (
                <div className="space-y-1 pt-2 border-t">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Estimated Cost:</span>
                    <span className="font-medium">${cost.toFixed(4)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Estimated Time:</span>
                    <span className="font-medium">~{time}s</span>
                  </div>
                </div>
              ) : (
                <div className="pt-2 border-t">
                  <div className="text-xs text-muted-foreground italic">
                    Enter a query to see estimates
                  </div>
                </div>
              )}

              {/* Selection Indicator */}
              {isSelected && (
                <div className="absolute top-2 right-2">
                  <div className="h-5 w-5 rounded-full bg-primary flex items-center justify-center">
                    <svg
                      className="h-3 w-3 text-primary-foreground"
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Additional Info */}
      <div className="text-xs text-muted-foreground bg-muted/50 p-3 rounded-md">
        <strong>💡 Tip:</strong> Balanced mode is recommended for most queries. Use Fast for simple questions, 
        and Best Quality for complex analysis requiring maximum accuracy.
      </div>
    </div>
  );
}
