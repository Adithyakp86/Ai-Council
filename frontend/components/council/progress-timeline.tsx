'use client';

import { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { TimelineEvent } from '@/types/council';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface ProgressTimelineProps {
  events: TimelineEvent[];
  autoScroll?: boolean;
}

export function ProgressTimeline({ events, autoScroll = true }: ProgressTimelineProps) {
  const timelineEndRef = useRef<HTMLDivElement>(null);
  const [expandedEvents, setExpandedEvents] = useState<Set<number>>(new Set());

  // Auto-scroll to latest event
  useEffect(() => {
    if (autoScroll && timelineEndRef.current) {
      timelineEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [events, autoScroll]);

  const toggleEventExpansion = (index: number) => {
    setExpandedEvents((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  const getStageIcon = (stage: string) => {
    const icons: Record<string, string> = {
      analysis_started: '🔍',
      analysis_complete: '✅',
      decomposition_complete: '📋',
      routing_complete: '🎯',
      execution_progress: '⚡',
      arbitration_decision: '⚖️',
      synthesis_progress: '🔄',
      final_response: '🎉',
      error: '❌',
    };
    return icons[stage] || '📌';
  };

  const getStageColor = (stage: string) => {
    if (stage.includes('error')) return 'text-red-500';
    if (stage.includes('complete') || stage.includes('final')) return 'text-green-500';
    if (stage.includes('progress')) return 'text-blue-500';
    return 'text-primary';
  };

  if (events.length === 0) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Progress Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <p>No events yet. Submit a query to see real-time progress.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Progress Timeline</span>
          <span className="text-sm font-normal text-muted-foreground">
            {events.length} event{events.length !== 1 ? 's' : ''}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="max-h-[600px] overflow-y-auto pr-2 space-y-3">
          {events.map((event, index) => {
            const isExpanded = expandedEvents.has(index);
            const hasMetadata = event.metadata && Object.keys(event.metadata).length > 0;

            return (
              <div key={index} className="relative">
                {/* Timeline Line */}
                {index < events.length - 1 && (
                  <div className="absolute left-4 top-10 bottom-0 w-0.5 bg-border" />
                )}

                {/* Event Card */}
                <div className="flex gap-3">
                  {/* Icon */}
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-background border-2 border-primary flex items-center justify-center text-lg">
                      {getStageIcon(event.stage)}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div
                      className={`
                        p-3 rounded-lg border transition-all
                        ${isExpanded ? 'bg-accent/50' : 'bg-background'}
                        hover:bg-accent/30
                      `}
                    >
                      {/* Header */}
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className={`text-sm font-medium ${getStageColor(event.stage)}`}>
                              {event.stage.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {formatTime(event.timestamp)}
                            </span>
                          </div>
                          <p className="text-sm text-foreground mt-1">{event.message}</p>
                        </div>

                        {/* Expand Button */}
                        {hasMetadata && (
                          <button
                            onClick={() => toggleEventExpansion(index)}
                            className="flex-shrink-0 p-1 hover:bg-accent rounded transition-colors"
                            aria-label={isExpanded ? 'Collapse details' : 'Expand details'}
                          >
                            {isExpanded ? (
                              <ChevronDown className="h-4 w-4" />
                            ) : (
                              <ChevronRight className="h-4 w-4" />
                            )}
                          </button>
                        )}
                      </div>

                      {/* Expanded Metadata */}
                      {isExpanded && hasMetadata && (
                        <div className="mt-3 pt-3 border-t space-y-2">
                          <div className="text-xs font-medium text-muted-foreground mb-2">
                            Event Details:
                          </div>
                          <div className="bg-muted/50 rounded p-2 space-y-1">
                            {Object.entries(event.metadata!).map(([key, value]) => (
                              <div key={key} className="flex gap-2 text-xs">
                                <span className="font-medium text-muted-foreground min-w-[100px]">
                                  {key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}:
                                </span>
                                <span className="text-foreground break-all">
                                  {typeof value === 'object'
                                    ? JSON.stringify(value, null, 2)
                                    : String(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}

          {/* Auto-scroll anchor */}
          <div ref={timelineEndRef} />
        </div>
      </CardContent>
    </Card>
  );
}
