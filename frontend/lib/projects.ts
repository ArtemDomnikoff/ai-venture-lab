import {
    apiFetch,
} from "./api";

import type {
    Project,
    ProjectListResponse,
    Run,
} from "@/types/api";


export function getProjects() {
    return apiFetch<ProjectListResponse>(
        "/projects",
    );
}


export function getProject(
    id: string,
) {
    return apiFetch<Project>(
        `/projects/${id}`,
    );
}


export function createProject(
    name: string,
    idea: string,
) {
    return apiFetch<Project>(
        "/projects",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name,
                idea,
            }),
        },
    );
}


export function updateProject(
    id: string,
    idea: string,
) {
    return apiFetch<Project>(
        `/projects/${id}`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                idea,
            }),
        },
    );
}


export function deleteProject(
    id: string,
) {
    return apiFetch<void>(
        `/projects/${id}`,
        {
            method: "DELETE",
        },
    );
}


export function createRun(
    projectId: string,
) {
    return apiFetch<Run>(
        `/projects/${projectId}/runs`,
        {
            method: "POST",
        },
    );
}

