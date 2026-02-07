// Types for AI Council requests and responses

export type ExecutionMode = 'fast' | 'balanced' | 'best_quality';

export interface CostEstimate {
  fast: number;
  balanced: number;
  bestQuality: number;
  estimatedTime: {
    fast: number;
    balanced: number;
    bestQuality: number;
  };
}

export interface CouncilRequest {
  content: string;
  executionMode: ExecutionMode;
}

export interface CouncilRequestResponse {
  requestId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  websocketUrl: string;
}

export interface Subtask {
  id: string;
  content: string;
  taskType: string;
  priority: string;
  assignedModel?: string;
  status?: 'pending' | 'processing' | 'completed' | 'failed';
  result?: string;
  confidence?: number;
  cost?: number;
  executionTime?: number;
}

export interface ModelContribution {
  modelId: string;
  subtasksHandled: number;
  totalCost: number;
  averageConfidence: number;
}

export interface ArbitrationDecision {
  subtaskId: string;
  conflictingResults: number;
  selectedResult: string;
  reason: string;
}

export interface SubtaskResult {
  subtaskId: string;
  content: string;
  confidence: number;
  cost: number;
  executionTime: number;
  modelId: string;
}

export interface CouncilResponse {
  requestId: string;
  content: string;
  confidence: number;
  executionTime: number;
  totalCost: number;
  modelsUsed: string[];
  subtaskResults: SubtaskResult[];
  arbitrationDecisions?: ArbitrationDecision[];
  orchestrationMetadata: {
    totalSubtasks: number;
    parallelExecutions: number;
    decompositionTree?: any;
  };
}

export interface OrchestrationState {
  stage: 'analysis' | 'routing' | 'execution' | 'arbitration' | 'synthesis' | 'complete';
  subtasks: Subtask[];
  activeExecutions: string[];
  completedSubtasks: number;
  totalSubtasks: number;
  intent?: string;
  complexity?: string;
}

export interface TimelineEvent {
  timestamp: Date;
  stage: string;
  message: string;
  metadata?: Record<string, any>;
}

export interface WebSocketMessage {
  type: 'analysis_started' | 'analysis_complete' | 'decomposition_complete' | 'routing_complete' | 
        'execution_progress' | 'arbitration_decision' | 'synthesis_progress' | 'final_response' | 
        'error' | 'heartbeat';
  timestamp: string;
  data: any;
}
