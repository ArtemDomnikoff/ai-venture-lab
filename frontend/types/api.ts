export type ProjectStatus =
  | "draft"
  | "running"
  | "completed"
  | "failed";


export type RunStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed";


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

  progress: Record<
    string,
    string
  >;

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


export interface Metrics {
  total_runs: number;
  queued_runs: number;
  running_runs: number;
  completed_runs: number;
  failed_runs: number;
  average_duration_ms: number | null;
}