'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { CouncilResponse, SubtaskResult, ModelContribution } from '@/types/council';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface OrchestrationBreakdownProps {
  response: CouncilResponse;
}

export function OrchestrationBreakdown({ response }: OrchestrationBreakdownProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  // Calculate model contributions
  const modelContributions: ModelContribution[] = response.modelsUsed.map((modelId) => {
    const subtasksForModel = response.subtaskResults.filter((st) => st.modelId === modelId);
    return {
      modelId,
      subtasksHandled: subtasksForModel.length,
      totalCost: subtasksForModel.reduce((sum, st) => sum + st.cost, 0),
      averageConfidence: subtasksForModel.length > 0
        ? subtasksForModel.reduce((sum, st) => sum + st.confidence, 0) / subtasksForModel.length
        : 0,
    };
  });

  // Calculate parallel efficiency
  const totalSequentialTime = response.subtaskResults.reduce((sum, st) => sum + st.executionTime, 0);
  const parallelEfficiency = totalSequentialTime > 0
    ? ((totalSequentialTime - response.executionTime) / totalSequentialTime) * 100
    : 0;

  const SectionHeader = ({ id, title, icon }: { id: string; title: string; icon: string }) => {
    const isExpanded = expandedSections.has(id);
    return (
      <button
        onClick={() => toggleSection(id)}
        className="w-full flex items-center justify-between p-3 hover:bg-accent/50 rounded-lg transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{icon}</span>
          <span className="font-medium">{title}</span>
        </div>
        {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>
    );
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Orchestration Breakdown</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Overview Section */}
        <div className="border rounded-lg">
          <SectionHeader id="overview" title="Overview" icon="📊" />
          {expandedSections.has('overview') && (
            <div className="p-4 space-y-4 border-t">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-muted/50 rounded-lg">
                  <div className="text-2xl font-bold text-primary">
                    {response.orchestrationMetadata.totalSubtasks}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">Total Subtasks</div>
                </div>
                <div className="text-center p-3 bg-muted/50 rounded-lg">
                  <div className="text-2xl font-bold text-primary">
                    {response.modelsUsed.length}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">Models Used</div>
                </div>
                <div className="text-center p-3 bg-muted/50 rounded-lg">
                  <div className="text-2xl font-bold text-primary">
                    {response.orchestrationMetadata.parallelExecutions}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">Parallel Executions</div>
                </div>
                <div className="text-center p-3 bg-muted/50 rounded-lg">
                  <div className="text-2xl font-bold text-primary">
                    {parallelEfficiency.toFixed(0)}%
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">Time Saved</div>
                </div>
              </div>

              <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="text-2xl">💡</div>
                  <div className="flex-1">
                    <div className="font-medium text-sm mb-1">Parallel Processing Efficiency</div>
                    <p className="text-sm text-muted-foreground">
                      By processing {response.orchestrationMetadata.parallelExecutions} subtasks in parallel, 
                      we saved approximately {(totalSequentialTime - response.executionTime).toFixed(1)}s 
                      compared to sequential execution.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Model Contributions Section */}
        <div className="border rounded-lg">
          <SectionHeader id="models" title="Model Contributions" icon="🤖" />
          {expandedSections.has('models') && (
            <div className="p-4 border-t">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2 font-medium">Model</th>
                      <th className="text-center p-2 font-medium">Subtasks</th>
                      <th className="text-center p-2 font-medium">Avg Confidence</th>
                      <th className="text-right p-2 font-medium">Total Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {modelContributions.map((contribution, index) => (
                      <tr key={index} className="border-b last:border-0 hover:bg-accent/50">
                        <td className="p-2">
                          <div className="font-medium">{contribution.modelId}</div>
                        </td>
                        <td className="text-center p-2">
                          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-medium">
                            {contribution.subtasksHandled}
                          </span>
                        </td>
                        <td className="text-center p-2">
                          <div className="flex items-center justify-center gap-2">
                            <span className="font-medium">
                              {(contribution.averageConfidence * 100).toFixed(0)}%
                            </span>
                            <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                              <div
                                className="h-full bg-primary"
                                style={{ width: `${contribution.averageConfidence * 100}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="text-right p-2 font-medium">
                          ${contribution.totalCost.toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="border-t-2 font-medium">
                      <td className="p-2">Total</td>
                      <td className="text-center p-2">
                        {response.orchestrationMetadata.totalSubtasks}
                      </td>
                      <td className="text-center p-2">
                        {(response.confidence * 100).toFixed(0)}%
                      </td>
                      <td className="text-right p-2">
                        ${response.totalCost.toFixed(4)}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Cost Breakdown Section */}
        <div className="border rounded-lg">
          <SectionHeader id="costs" title="Cost Breakdown" icon="💰" />
          {expandedSections.has('costs') && (
            <div className="p-4 space-y-4 border-t">
              {/* Cost by Model */}
              <div>
                <h4 className="text-sm font-medium mb-3">Cost by Model</h4>
                <div className="space-y-2">
                  {modelContributions.map((contribution, index) => {
                    const percentage = (contribution.totalCost / response.totalCost) * 100;
                    return (
                      <div key={index}>
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="text-muted-foreground">{contribution.modelId}</span>
                          <span className="font-medium">
                            ${contribution.totalCost.toFixed(4)} ({percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Cost by Subtask */}
              <div>
                <h4 className="text-sm font-medium mb-3">Cost by Subtask</h4>
                <div className="space-y-2 max-h-[300px] overflow-y-auto">
                  {response.subtaskResults.map((subtask, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-muted/50 rounded text-sm"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="font-medium truncate">Subtask {index + 1}</div>
                        <div className="text-xs text-muted-foreground">{subtask.modelId}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">${subtask.cost.toFixed(4)}</div>
                        <div className="text-xs text-muted-foreground">
                          {subtask.executionTime.toFixed(1)}s
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Subtask Details Section */}
        <div className="border rounded-lg">
          <SectionHeader id="subtasks" title="Subtask Details" icon="📋" />
          {expandedSections.has('subtasks') && (
            <div className="p-4 space-y-3 border-t max-h-[400px] overflow-y-auto">
              {response.subtaskResults.map((subtask, index) => (
                <div key={index} className="p-3 bg-muted/50 rounded-lg border">
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-medium">Subtask {index + 1}</div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded">
                        {subtask.modelId}
                      </span>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-sm">
                    <div>
                      <div className="text-xs text-muted-foreground">Confidence</div>
                      <div className="font-medium">{(subtask.confidence * 100).toFixed(0)}%</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Cost</div>
                      <div className="font-medium">${subtask.cost.toFixed(4)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Time</div>
                      <div className="font-medium">{subtask.executionTime.toFixed(1)}s</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Parallel Execution Metrics */}
        <div className="border rounded-lg">
          <SectionHeader id="parallel" title="Parallel Execution Metrics" icon="⚡" />
          {expandedSections.has('parallel') && (
            <div className="p-4 space-y-4 border-t">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">Sequential Time</div>
                  <div className="text-2xl font-bold">{totalSequentialTime.toFixed(1)}s</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    If processed one by one
                  </div>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">Actual Time</div>
                  <div className="text-2xl font-bold text-primary">
                    {response.executionTime.toFixed(1)}s
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    With parallel processing
                  </div>
                </div>
              </div>

              <div className="bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-900 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="text-3xl">🚀</div>
                  <div>
                    <div className="font-medium text-sm mb-1">
                      {(totalSequentialTime / response.executionTime).toFixed(1)}x Faster
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Parallel execution saved {(totalSequentialTime - response.executionTime).toFixed(1)}s 
                      ({parallelEfficiency.toFixed(0)}% efficiency gain)
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
