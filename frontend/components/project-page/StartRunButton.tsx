"use client";

import {
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  ApiError,
} from "@/lib/api";

import {
  createRun,
} from "@/lib/projects";

import {
  useAuth,
} from "@/components/AuthProvider";


export default function StartRunButton({
  projectId,
}: {
  projectId: string;
}) {
  const router = useRouter();

  const {
    user,
    refreshUser,
  } = useAuth();

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );


  async function handleStart() {
    if (
      loading
      || !user
      || user.free_runs_remaining <= 0
    ) {
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const run =
        await createRun(
          projectId,
        );

      await refreshUser();

      router.push(
        `/projects/${projectId}/runs/${run.id}`,
      );
    } catch (error) {
      if (
        error instanceof ApiError
      ) {
        if (
          error.status === 401
        ) {
          router.replace(
            `/login?next=/projects/${projectId}`,
          );

          return;
        }

        if (
          error.code ===
          "FREE_RUNS_EXHAUSTED"
        ) {
          setError(
            "You have used all free analyses.",
          );

          await refreshUser();

          return;
        }

        if (
          error.code ===
          "RATE_LIMIT_EXCEEDED"
        ) {
          const retryAfter =
            error.details.retry_after;

          if (
            typeof retryAfter === "number"
          ) {
            setError(
              `Too many requests. Please try again in ${retryAfter} seconds.`,
            );
          } else {
            setError(
              "Too many requests. Please try again later.",
            );
          }

          return;
        }

        if (
          error.code ===
          "RUN_ALREADY_RUNNING"
        ) {
          setError(
            "This project already has an active analysis.",
          );

          return;
        }

        setError(
          error.message,
        );

        return;
      }

      setError(
        "Failed to create analysis.",
      );
    } finally {
      setLoading(false);
    }
  }


  if (!user) {
    return null;
  }


  const hasFreeRuns =
    user.free_runs_remaining > 0;


  return (
    <div>
      <button
        type="button"
        onClick={handleStart}
        disabled={
          loading
          || !hasFreeRuns
        }
        className="
          inline-flex
          rounded-xl
          bg-primary
          px-5
          py-3
          font-semibold
          text-white
          transition
          hover:bg-primary-hover
          disabled:cursor-not-allowed
          disabled:opacity-50
        "
      >
        {loading
          ? "Starting..."
          : hasFreeRuns
            ? "Start new analysis"
            : "No free analyses left"}
      </button>


      <div
        className="
          mt-3
          text-sm
          text-[var(--muted)]
        "
      >
        {user.free_runs_remaining} free{" "}
        {user.free_runs_remaining === 1
          ? "analysis"
          : "analyses"}{" "}
        remaining
      </div>


      {error && (
        <div
          role="alert"
          aria-live="polite"
          className="
            mt-3
            text-sm
            text-red-400
          "
        >
          {error}
        </div>
      )}
    </div>
  );
}
