'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { OrchestrationState, Subtask } from '@/types/council';
import { CheckCircle2, Circle, Loader2, AlertCircle } from 'lucide-react';

interface OrchestrationVisualizationProps {
  state: OrchestrationState;
}

const stageConfig = {
  analysis: { label: 'Analysis', icon: '🔍', order: 1 },
  routing: { label: 'Routing', icon: '🎯', order: 2 },
  execution: { label: 'Execution', icon: '⚡', order: 3 },
  arbitration: { label: 'Arbitration', icon: '⚖️', order: 4 },
  synthesis: { label: 'Synthesis', icon: '🔄', order: 5 },
  complete: { label: 'Complete', icon: '✅', order: 6 },
};

export function OrchestrationVisualization({ state }: OrchestrationVisualizationProps) {
  const currentStageOrder = stageConfig[state.stage]?.order || 0;

  const getStageStatus = (stageOrder: number): 'complete' | 'active' | 'pending' => {
    if (stageOrder < currentStageOrder) return 'complete';
    if (stageOrder === currentStageOrder) return 'active';
    return 'pending';
  };

  const getSubtaskIcon = (subtask: Subtask) => {
    if (subtask.status === 'completed') {
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    }
    if (subtask.status === 'processing') {
      return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
    }
    if (subtask.status === 'failed') {
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
    return <Circle className="h-4 w-4 text-gray-400" />;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Orchestration Progress</span>
          <span className="text-sm font-normal text-muted-foreground">
            {state.completedSubtasks} / {state.totalSubtasks} subtasks completed
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Stage Progress */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Processing Stages</h3>
          <div className="relative">
            {/* Progress Line */}
            <div className="absolute top-5 left-0 right-0 h-0.5 bg-border" />
            <div
              className="absolute top-5 left-0 h-0.5 bg-primary transition-all duration-500"
              style={{
                width: `${((currentStageOrder - 1) / (Object.keys(stageConfig).length - 1)) * 100}%`,
              }}
            />

            {/* Stage Nodes */}
            <div className="relative flex justify-between">
              {Object.entries(stageConfig).map(([key, config]) => {
                const status = getStageStatus(config.order);
                return (
                  <div key={key} className="flex flex-col items-center gap-2">
                    <div
                      className={`
                        w-10 h-10 rounded-full flex items-center justify-center text-lg
                        transition-all duration-300 border-2
                        ${
                          status === 'complete'
                            ? 'bg-primary border-primary text-primary-foreground'
                            : status === 'active'
                            ? 'bg-primary/10 border-primary text-primary animate-pulse'
                            : 'bg-background border-border text-muted-foreground'
                        }
                      `}
                    >
                      {config.icon}
                    </div>
                    <span
                      className={`
                        text-xs font-medium
                        ${status === 'active' ? 'text-primary' : 'text-muted-foreground'}
                      `}
                    >
                      {config.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Current Stage Info */}
        {state.stage !== 'complete' && (
          <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Loader2 className="h-4 w-4 text-primary animate-spin" />
              <span className="font-medium text-primary">
                {stageConfig[state.stage]?.label} in progress...
              </span>
            </div>
            {state.intent && (
              <p className="text-sm text-muted-foreground">
                Detected intent: <span className="font-medium">{state.intent}</span>
              </p>
            )}
            {state.complexity && (
              <p className="text-sm text-muted-foreground">
                Complexity: <span className="font-medium">{state.complexity}</span>
              </p>
            )}
          </div>
        )}

        {/* Subtasks Grid */}
        {state.subtasks.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-medium">Subtasks</h3>
            <div className="grid grid-cols-1 gap-2">
              {state.subtasks.map((subtask) => (
                <div
                  key={subtask.id}
                  className={`
                    p-3 rounded-lg border transition-all
                    ${
                      subtask.status === 'completed'
                        ? 'bg-green-50 border-green-200 dark:bg-green-950/20 dark:border-green-900'
                        : subtask.status === 'processing'
                        ? 'bg-blue-50 border-blue-200 dark:bg-blue-950/20 dark:border-blue-900'
                        : subtask.status === 'failed'
                        ? 'bg-red-50 border-red-200 dark:bg-red-950/20 dark:border-red-900'
                        : 'bg-muted/50 border-border'
                    }
                  `}
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">{getSubtaskIcon(subtask)}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium text-muted-foreground">
                          {subtask.taskType}
                        </span>
                        {subtask.priority && (
                          <span className="text-xs px-1.5 py-0.5 rounded bg-background border">
                            {subtask.priority}
                          </span>
                        )}
                      </div>
                      <p className="text-sm">{subtask.content}</p>
                      {subtask.assignedModel && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Model: {subtask.assignedModel}
                        </p>
                      )}
                      {subtask.status === 'completed' && subtask.confidence && (
                        <div className="flex items-center gap-3 mt-2 text-xs">
                          <span className="text-muted-foreground">
                            Confidence: <span className="font-medium">{(subtask.confidence * 100).toFixed(0)}%</span>
                          </span>
                          {subtask.cost && (
                            <span className="text-muted-foreground">
                              Cost: <span className="font-medium">${subtask.cost.toFixed(4)}</span>
                            </span>
                          )}
                          {subtask.executionTime && (
                            <span className="text-muted-foreground">
                              Time: <span className="font-medium">{subtask.executionTime.toFixed(1)}s</span>
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Active Executions */}
        {state.activeExecutions.length > 0 && (
          <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
              <span className="font-medium text-blue-700 dark:text-blue-300">
                {state.activeExecutions.length} subtask{state.activeExecutions.length > 1 ? 's' : ''} executing in parallel
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Multiple AI models are working simultaneously to process your request faster.
            </p>
          </div>
        )}

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Overall Progress</span>
            <span className="font-medium">
              {state.totalSubtasks > 0
                ? Math.round((state.completedSubtasks / state.totalSubtasks) * 100)
                : 0}%
            </span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-500"
              style={{
                width: `${
                  state.totalSubtasks > 0
                    ? (state.completedSubtasks / state.totalSubtasks) * 100
                    : 0
                }%`,
              }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
