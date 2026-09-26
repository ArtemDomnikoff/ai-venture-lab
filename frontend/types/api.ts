export interface User {
  id: string;
  email: string;
  free_runs_remaining: number;
  created_at: string;
}

export type ProjectStatus = "draft" | "active" | "archived";
export type RunStatus = "queued" | "running" | "completed" | "failed" | "cancelled";

export interface Project {
  id: string;
  name: string;
  idea: string;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
}

export interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
}

export interface Run {
  id: string;
  project_id: string;
  status: RunStatus;
  progress: Record<string, string>;
  current_node: string | null;
  started_at: string | null;
  finished_at: string | null;
  error: string | null;
  created_at: string;
}

export interface RunListResponse {
  items: Run[];
  total: number;
  page: number;
  page_size: number;
}

export interface Evidence {
  claim: string;
  source: string;
  excerpt: string;
  confidence: number;
  source_type?: string;
}

export interface AgentReport {
  summary?: string;
  claims?: string[];
  evidence?: Evidence[];
  risks?: string[];
  strengths?: string[];
  contradictions?: string[];
  missing_evidence?: string[];
  unsupported_claims?: string[];
  confidence?: number;
  score?: number;
  decision?: string;
  evidence_quality?: number;
  [key: string]: unknown;
}

export interface Metrics {
  total_runs: number;
  queued_runs: number;
  running_runs: number;
  completed_runs: number;
  failed_runs: number;
  average_duration_ms: number | null;
}

export type AnalysisDecision =
  | "strong_opportunity"
  | "promising_but_risky"
  | "needs_more_research"
  | "weak_opportunity"
  | "not_recommended";

export type FindingCategory =
  | "market"
  | "customer"
  | "competition"
  | "technology"
  | "business"
  | "skeptic";

export interface AnalysisResult {
  run_id: string;
  score: number;
  decision: AnalysisDecision;
  summary: string;
  created_at: string;
}

export interface Finding {
  id: string;
  category: FindingCategory;
  title: string;
  summary: string;
  confidence: number;
}

export interface DetailedAnalysisResult extends AnalysisResult {
  judge?: AgentReport;
  skeptic?: AgentReport;
  agents?: Record<string, AgentReport>;
  plan?: Record<string, unknown>;
}
