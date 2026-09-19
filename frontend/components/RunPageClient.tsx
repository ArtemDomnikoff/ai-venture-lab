"use client";

import {
  useEffect,
  useState,
} from "react";

import Link from "next/link";

import {
  useRouter,
} from "next/navigation";

import {
  ApiError,
} from "@/lib/api";

import {
  getRun,
} from "@/lib/runs";

import {
  useAuth,
} from "@/components/AuthProvider";

import RunViewer from "@/components/RunViewer";

import type {
  Run,
} from "@/types/api";


interface Props {
  projectId: string;
  runId: string;
}


export default function RunPageClient({
  projectId,
  runId,
}: Props) {
  const router = useRouter();

  const {
    user,
    loading: authLoading,
  } = useAuth();

  const [run, setRun] =
    useState<Run | null>(null);

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
        `/login?next=/projects/${projectId}/runs/${runId}`,
      );

      return;
    }

    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const nextRun =
          await getRun(runId);

        if (cancelled) {
          return;
        }

        setRun(nextRun);
      } catch (error) {
        if (cancelled) {
          return;
        }

        if (
          error instanceof ApiError
          && error.status === 401
        ) {
          router.replace(
            `/login?next=/projects/${projectId}/runs/${runId}`,
          );

          return;
        }

        setError(
          error instanceof ApiError
            ? error.message
            : "Failed to load analysis.",
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
    runId,
    user?.id,
  ]);


  if (
    authLoading
    || loading
  ) {
    return (
      <main
        className="
          min-h-screen
          px-4
          py-8
          sm:px-8
        "
      >
        <div
          className="
            mx-auto
            max-w-6xl
          "
        >
          <div
            className="
              text-sm
              text-[var(--muted)]
            "
          >
            Loading analysis...
          </div>
        </div>
      </main>
    );
  }


  if (error) {
    return (
      <main
        className="
          min-h-screen
          px-4
          py-8
          sm:px-8
        "
      >
        <div
          className="
            mx-auto
            max-w-6xl
          "
        >
          <div
            className="
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
        </div>
      </main>
    );
  }


  if (!run) {
    return null;
  }


  return (
    <main
      className="
        min-h-screen
        bg-[var(--background)]
        px-4
        py-8
        sm:px-8
      "
    >
      <div
        className="
          mx-auto
          max-w-6xl
        "
      >
        <Link
          href={`/projects/${run.project_id}`}
          className="
            mb-6
            inline-flex
            items-center
            gap-2
            rounded-xl
            border
            border-[var(--border)]
            bg-[var(--card)]
            px-4
            py-2
            text-sm
            font-medium
            text-[var(--foreground)]
            transition
            hover:bg-[var(--background)]
          "
        >
          ← Back to project
        </Link>

        <RunViewer
          initialRun={run}
        />
      </div>
    </main>
  );
}
