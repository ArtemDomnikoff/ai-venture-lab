import { apiFetch } from "./api";

import type {
  AnalysisResult,
  DetailedAnalysisResult,
  Finding,
  Run,
  RunListResponse,
} from "@/types/api";

export function getRun(runId: string) {
  return apiFetch<Run>(`/runs/${runId}`);
}

export function getRunResult(runId: string) {
  return apiFetch<AnalysisResult>(`/runs/${runId}/result`);
}

export function getRunDetailedResult(runId: string) {
  return apiFetch<DetailedAnalysisResult>(`/runs/${runId}/result/detail`);
}

export function getRunFindings(runId: string) {
  return apiFetch<Finding[]>(`/runs/${runId}/findings`);
}

export function getProjectRuns(projectId: string) {
  return apiFetch<RunListResponse>(`/projects/${projectId}/runs`);
}

export function deleteRun(runId: string) {
  return apiFetch<void>(`/runs/${runId}`, { method: "DELETE" });
}
