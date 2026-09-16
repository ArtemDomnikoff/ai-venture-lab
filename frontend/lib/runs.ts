import {
  apiFetch,
} from "./api";

import type {
  Run,
  AnalysisResult,
  Finding,
  RunListResponse,
} from "@/types/api";


export function getRun(
  runId: string,
) {
  return apiFetch<Run>(
    `/runs/${runId}`,
  );
}


export function getRunResult(
  runId: string,
) {
  return apiFetch<AnalysisResult>(
    `/runs/${runId}/result`,
  );
}


export function getRunFindings(
  runId: string,
) {
  return apiFetch<Finding[]>(
    `/runs/${runId}/findings`,
  );
}

export function getProjectRuns(
  projectId:string,
) {
  return apiFetch<RunListResponse>(
    `/projects/${projectId}/runs`,
  );
}