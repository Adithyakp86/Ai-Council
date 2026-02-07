'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { CouncilResponse } from '@/types/council';
import { Copy, Download, Check } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface ResponseViewerProps {
  response: CouncilResponse;
}

export function ResponseViewer({ response }: ResponseViewerProps) {
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(response.content);
      setCopied(true);
      toast({
        title: 'Copied!',
        description: 'Response copied to clipboard',
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast({
        title: 'Failed to copy',
        description: 'Could not copy to clipboard',
        variant: 'destructive',
      });
    }
  };

  const handleDownloadJSON = () => {
    const dataStr = JSON.stringify(response, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `council-response-${response.requestId}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    toast({
      title: 'Downloaded!',
      description: 'Response saved as JSON file',
    });
  };

  // Simple syntax highlighting for code blocks
  const renderContent = (content: string) => {
    const parts = content.split(/(```[\s\S]*?```)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('```')) {
        const lines = part.split('\n');
        const language = lines[0].replace('```', '').trim() || 'text';
        const code = lines.slice(1, -1).join('\n');
        
        return (
          <div key={index} className="my-4">
            <div className="bg-muted px-3 py-1 text-xs font-mono text-muted-foreground border-b">
              {language}
            </div>
            <pre className="bg-muted p-4 rounded-b-lg overflow-x-auto">
              <code className="text-sm font-mono">{code}</code>
            </pre>
          </div>
        );
      }
      
      return (
        <div key={index} className="whitespace-pre-wrap">
          {part}
        </div>
      );
    });
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Final Response</CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyToClipboard}
              className="gap-2"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  Copy
                </>
              )}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownloadJSON}
              className="gap-2"
            >
              <Download className="h-4 w-4" />
              Download JSON
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Response Content */}
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <div className="p-4 bg-accent/50 rounded-lg border">
            {renderContent(response.content)}
          </div>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Confidence Score */}
          <div className="p-4 bg-muted/50 rounded-lg border">
            <div className="text-xs text-muted-foreground mb-1">Confidence Score</div>
            <div className="text-2xl font-bold">
              {(response.confidence * 100).toFixed(0)}%
            </div>
            <div className="mt-2 h-2 bg-background rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${response.confidence * 100}%` }}
              />
            </div>
          </div>

          {/* Total Cost */}
          <div className="p-4 bg-muted/50 rounded-lg border">
            <div className="text-xs text-muted-foreground mb-1">Total Cost</div>
            <div className="text-2xl font-bold">
              ${response.totalCost.toFixed(4)}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Across {response.modelsUsed.length} model{response.modelsUsed.length !== 1 ? 's' : ''}
            </div>
          </div>

          {/* Execution Time */}
          <div className="p-4 bg-muted/50 rounded-lg border">
            <div className="text-xs text-muted-foreground mb-1">Execution Time</div>
            <div className="text-2xl font-bold">
              {response.executionTime.toFixed(1)}s
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {response.orchestrationMetadata.parallelExecutions > 0 && (
                <>With {response.orchestrationMetadata.parallelExecutions} parallel executions</>
              )}
            </div>
          </div>

          {/* Subtasks */}
          <div className="p-4 bg-muted/50 rounded-lg border">
            <div className="text-xs text-muted-foreground mb-1">Subtasks</div>
            <div className="text-2xl font-bold">
              {response.orchestrationMetadata.totalSubtasks}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Decomposed and processed
            </div>
          </div>
        </div>

        {/* Models Used */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium">Models Used</h3>
          <div className="flex flex-wrap gap-2">
            {response.modelsUsed.map((model, index) => (
              <div
                key={index}
                className="px-3 py-1.5 bg-primary/10 text-primary rounded-full text-sm font-medium"
              >
                {model}
              </div>
            ))}
          </div>
        </div>

        {/* Arbitration Decisions */}
        {response.arbitrationDecisions && response.arbitrationDecisions.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-medium">Arbitration Decisions</h3>
            <div className="space-y-2">
              {response.arbitrationDecisions.map((decision, index) => (
                <div key={index} className="p-3 bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-900 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">⚖️</span>
                    <span className="text-sm font-medium">
                      Resolved {decision.conflictingResults} conflicting results
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Reason: {decision.reason}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quality Indicators */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-900 rounded-lg">
            <div className="text-2xl">✅</div>
            <div>
              <div className="text-sm font-medium">High Confidence</div>
              <div className="text-xs text-muted-foreground">
                {response.confidence >= 0.8 ? 'Excellent' : response.confidence >= 0.6 ? 'Good' : 'Moderate'} quality response
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 rounded-lg">
            <div className="text-2xl">⚡</div>
            <div>
              <div className="text-sm font-medium">Parallel Processing</div>
              <div className="text-xs text-muted-foreground">
                {response.orchestrationMetadata.parallelExecutions} concurrent executions
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 bg-purple-50 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-900 rounded-lg">
            <div className="text-2xl">🎯</div>
            <div>
              <div className="text-sm font-medium">Multi-Model</div>
              <div className="text-xs text-muted-foreground">
                {response.modelsUsed.length} specialized models
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
