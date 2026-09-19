"use client";

import {
  useCallback,
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
  getRun,
  getRunFindings,
  getRunResult,
} from "@/lib/runs";

import type {
  AnalysisResult,
  Finding,
  Run,
} from "@/types/api";

import StatusBadge from "@/components/StatusBadge";
import DecisionBadge from "@/components/DecisionBadge";
import ScoreCard from "@/components/ScoreCard";
import AgentTimeline from "@/components/AgentTimeline";
import FindingCard from "@/components/FindingCard";


export default function RunViewer({
  initialRun,
}: {
  initialRun: Run;
}) {
  const router = useRouter();

  const [
    run,
    setRun,
  ] = useState<Run>(
    initialRun,
  );

  const [
    result,
    setResult,
  ] = useState<AnalysisResult | null>(
    null,
  );

  const [
    findings,
    setFindings,
  ] = useState<Finding[]>(
    [],
  );

  const [
    resultError,
    setResultError,
  ] = useState<string | null>(
    null,
  );


  const redirectToLogin =
    useCallback(() => {
      router.replace(
        `/login?next=/projects/${run.project_id}/runs/${run.id}`,
      );
    }, [
      router,
      run.id,
      run.project_id,
    ]);


  const loadResult =
    useCallback(
      async (
        runId: string,
      ) => {
        setResultError(null);

        try {
          const [
            nextResult,
            nextFindings,
          ] = await Promise.all([
            getRunResult(runId),
            getRunFindings(runId),
          ]);

          setResult(
            nextResult,
          );

          setFindings(
            nextFindings,
          );
        } catch (error) {
          if (
            error instanceof ApiError
            && error.status === 401
          ) {
            redirectToLogin();

            return;
          }

          setResultError(
            error instanceof ApiError
              ? error.message
              : "Failed to load analysis result.",
          );

          console.error(
            "Failed to load run result",
            error,
          );
        }
      },
      [
        redirectToLogin,
      ],
    );


  useEffect(() => {
    if (
      run.status === "completed"
    ) {
      const timeout =
        window.setTimeout(
          () => {
            void loadResult(
              run.id,
            );
          },
          0,
        );

      return () => {
        window.clearTimeout(
          timeout,
        );
      };
    }


    if (
      run.status === "failed"
      || run.status === "cancelled"
    ) {
      return;
    }


    let cancelled = false;

    const interval =
      window.setInterval(
        async () => {
          try {
            const updated =
              await getRun(
                run.id,
              );

            if (cancelled) {
              return;
            }

            setRun(
              updated,
            );
          } catch (error) {
            if (cancelled) {
              return;
            }

            if (
              error instanceof ApiError
              && error.status === 401
            ) {
              redirectToLogin();

              return;
            }

            console.error(
              "Failed to refresh run",
              error,
            );
          }
        },
        3000,
      );


    return () => {
      cancelled = true;

      window.clearInterval(
        interval,
      );
    };
  }, [
    loadResult,
    redirectToLogin,
    run.id,
    run.status,
  ]);


  const isRunning =
    run.status === "queued"
    || run.status === "running";


  return (
    <div
      className="
        space-y-8
      "
    >
      <section
        className="
          rounded-2xl
          border
          border-border
          bg-card
          p-6
          sm:p-8
        "
      >
        <div
          className="
            flex
            flex-col
            gap-4
            sm:flex-row
            sm:items-start
            sm:justify-between
          "
        >
          <div>
            <h1
              className="
                text-4xl
                font-bold
                text-foreground
              "
            >
              Venture Analysis
            </h1>

            <p
              className="
                mt-2
                text-muted
              "
            >
              AI multi-agent evaluation report
            </p>
          </div>

          <StatusBadge
            status={
              run.status
            }
          />
        </div>
      </section>


      {isRunning && (
        <section
          className="
            rounded-2xl
            border
            border-border
            bg-card
            p-6
            sm:p-8
          "
        >
          <h2
            className="
              text-2xl
              font-bold
              text-foreground
            "
          >
            Agent pipeline
          </h2>

          <p
            className="
              mt-2
              text-muted
            "
          >
            Analysis workflow status
          </p>

          <div className="mt-6">
            <AgentTimeline
              progress={
                run.progress
              }
            />
          </div>
        </section>
      )}


      {run.status === "failed" && (
        <section
          className="
            rounded-2xl
            border
            border-danger
            bg-card
            p-6
          "
        >
          <h2
            className="
              text-2xl
              font-bold
              text-danger
            "
          >
            Analysis failed
          </h2>

          <p
            className="
              mt-3
              text-foreground
            "
          >
            {run.error}
          </p>
        </section>
      )}


      {run.status === "cancelled" && (
        <section
          className="
            rounded-2xl
            border
            border-border
            bg-card
            p-6
          "
        >
          <h2
            className="
              text-2xl
              font-bold
              text-foreground
            "
          >
            Analysis cancelled
          </h2>

          <p
            className="
              mt-3
              text-muted
            "
          >
            This analysis was cancelled.
          </p>
        </section>
      )}


      {resultError && (
        <section
          className="
            rounded-2xl
            border
            border-red-500/30
            bg-red-500/10
            p-6
            text-red-300
          "
        >
          {resultError}
        </section>
      )}


      {result && (
        <section
          className="
            grid
            gap-8
            rounded-2xl
            border
            border-border
            bg-card
            p-6
            md:grid-cols-3
            sm:p-8
          "
        >
          <div
            className="
              flex
              justify-center
            "
          >
            <ScoreCard
              score={
                result.score
              }
            />
          </div>

          <div
            className="
              md:col-span-2
            "
          >
            <DecisionBadge
              decision={
                result.decision
              }
            />

            <h2
              className="
                mt-5
                text-2xl
                font-bold
                text-foreground
              "
            >
              Final decision
            </h2>

            <p
              className="
                mt-4
                leading-7
                text-muted
              "
            >
              {result.summary}
            </p>
          </div>
        </section>
      )}


      {result && (
        <section>
          <h2
            className="
              mb-5
              text-2xl
              font-bold
              text-foreground
            "
          >
            Findings
          </h2>

          <div
            className="
              grid
              gap-6
              md:grid-cols-2
            "
          >
            {findings.map(
              finding => (
                <FindingCard
                  key={
                    finding.id
                  }
                  finding={
                    finding
                  }
                />
              ),
            )}
          </div>
        </section>
      )}
    </div>
  );
}
