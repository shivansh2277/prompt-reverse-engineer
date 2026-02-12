export interface Explainability {
  summary: string;
  key_signals: string[];
  risk_flags: string[];
}

export interface ReverseResponse {
  request_id: string;
  cached: boolean;
  inferred_prompt: string;
  prompt_style: string;
  task_type: string;
  constraints_detected: string[];
  temperature_estimate: string;
  reasoning_trace: string[];
  analyzer_scores: Record<string, number>;
  explainability: Explainability;
  confidence_score: number;
}
