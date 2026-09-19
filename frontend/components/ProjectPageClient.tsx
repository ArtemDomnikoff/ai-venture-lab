"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  ApiError,
} from "@/lib/api";

import {
  getProject,
} from "@/lib/projects";

import {
  getProjectRuns,
} from "@/lib/runs";

import {
  useAuth,
} from "@/components/AuthProvider";

import ProjectHeader from "@/components/ProjectHeader";
import StartRunButton from "@/components/StartRunButton";
import RunList from "@/components/RunList";

import type {
  Project,
  Run,
} from "@/types/api";


export default function ProjectPageClient({
  projectId,
}: {
  projectId: string;
}) {
  const router = useRouter();

  const {
    user,
    loading: authLoading,
  } = useAuth();

  const [project, setProject] =
    useState<Project | null>(null);

  const [runs, setRuns] =
    useState<Run[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      router.replace(
        `/login?next=/projects/${projectId}`,
      );

      return;
    }

    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [
          nextProject,
          nextRuns,
        ] = await Promise.all([
          getProject(projectId),
          getProjectRuns(projectId),
        ]);

        if (cancelled) {
          return;
        }

        setProject(nextProject);

        setRuns(
          [...nextRuns.items].sort(
            (a, b) =>
              new Date(
                a.created_at,
              ).getTime()
              -
              new Date(
                b.created_at,
              ).getTime(),
          ),
        );
      } catch (error) {
        if (cancelled) {
          return;
        }

        if (
          error instanceof ApiError
          && error.status === 401
        ) {
          router.replace(
            `/login?next=/projects/${projectId}`,
          );

          return;
        }

        setError(
          error instanceof ApiError
            ? error.message
            : "Failed to load project.",
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [
    authLoading,
    projectId,
    router,
    user?.id,
  ]);


  if (
    authLoading
    || loading
  ) {
    return (
      <main className="px-6 py-10">
        <div
          className="
            mx-auto
            max-w-5xl
            text-sm
            text-[var(--muted)]
          "
        >
          Loading project...
        </div>
      </main>
    );
  }


  if (error) {
    return (
      <main className="px-6 py-10">
        <div
          className="
            mx-auto
            max-w-5xl
            rounded-2xl
            border
            border-red-500/30
            bg-red-500/10
            p-6
            text-red-300
          "
        >
          {error}
        </div>
      </main>
    );
  }


  if (!project) {
    return null;
  }


  return (
    <main
      className="
        min-h-screen
        px-6
        py-10
      "
    >
      <div
        className="
          mx-auto
          max-w-5xl
          space-y-8
        "
      >
        <ProjectHeader
          project={project}
        />

        <section
          className="
            rounded-2xl
            border
            border-[var(--border)]
            bg-[var(--card)]
            p-6
          "
        >
          <StartRunButton
            projectId={project.id}
          />
        </section>

        <section>
          <h2
            className="
              mb-5
              text-2xl
              font-bold
            "
          >
            Analysis runs
          </h2>

          {runs.length === 0 ? (
            <div
              className="
                rounded-2xl
                border
                border-[var(--border)]
                p-8
                text-center
                text-[var(--muted)]
              "
            >
              No analyses yet.
            </div>
          ) : (
            <RunList
              initialRuns={runs}
            />
          )}
        </section>
      </div>
    </main>
  );
}
