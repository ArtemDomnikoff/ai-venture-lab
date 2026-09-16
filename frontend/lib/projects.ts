import {
  apiFetch,
} from "./api";

import type {
  Project,
  ProjectListResponse,
} from "@/types/api";


export function getProjects() {
  return apiFetch<ProjectListResponse>(
    "/api/v1/projects",
  );
}


export function getProject(
  id: string,
) {
  return apiFetch<Project>(
    `/api/v1/projects/${id}`,
  );
}


export function createProject(
  data: {
    name: string;
    idea: string;
  },
) {
  return apiFetch<Project>(
    "/api/v1/projects",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
}