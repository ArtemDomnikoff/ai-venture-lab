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
  getProject,
} from "@/lib/projects";

import {
  getRun,
  getRunDetailedResult,
  getRunFindings,
  getRunResult,
} from "@/lib/runs";

import type {
  AnalysisResult,
  DetailedAnalysisResult,
  Finding,
  Project,
  Run,
} from "@/types/api";

import AgentAnalysisTab from "@/components/run-page/viewer/AgentAnalysisTab";
import EvidenceTab from "@/components/run-page/viewer/EvidenceTab";
import OverviewTab from "@/components/run-page/viewer/OverviewTab";
import {
  FailedState,
  RunningState,
  Unavailable,
} from "@/components/run-page/viewer/ui";
import {
  tabs,
} from "@/components/run-page/viewer/constants";
import type {
  AgentKey,
  TabKey,
} from "@/components/run-page/viewer/types";


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
    project,
    setProject,
  ] = useState<Project | null>(
    null,
  );

  const [
    result,
    setResult,
  ] = useState<AnalysisResult | null>(
    null,
  );

  const [
    detailed,
    setDetailed,
  ] = useState<DetailedAnalysisResult | null>(
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

  const [
    tab,
    setTab,
  ] = useState<TabKey>(
    "overview",
  );

  const [
    selectedAgent,
    setSelectedAgent,
  ] = useState<AgentKey>(
    "researcher",
  );

  const [
    shareMessage,
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

          try {
            const nextDetailed =
              await getRunDetailedResult(
                runId,
              );

            setDetailed(
              nextDetailed,
            );
          } catch (detailError) {
            console.info(
              "Detailed result endpoint unavailable; using compact result data.",
              detailError,
            );

            setDetailed(null);
          }
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
    let cancelled = false;

    async function loadProject() {
      try {
        const nextProject =
          await getProject(
            run.project_id,
          );

        if (
          cancelled
        ) {
          return;
        }

        setProject(
          nextProject,
        );
      } catch (error) {
        if (
          cancelled
        ) {
          return;
        }

        if (
          error instanceof ApiError
          && error.status === 401
        ) {
          redirectToLogin();

          return;
        }

        console.info(
          "Project metadata unavailable",
          error,
        );
      }
    }

    void loadProject();

    return () => {
      cancelled = true;
    };
  }, [
    redirectToLogin,
    run.project_id,
  ]);


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

            if (
              cancelled
            ) {
              return;
            }

            setRun(
              updated,
            );
          } catch (error) {
            if (
              cancelled
            ) {
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


  function openTab(
    nextTab: TabKey,
  ) {
    setTab(
      nextTab,
    );

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }


  function handleAgentClick(
    key: AgentKey,
  ) {
    setSelectedAgent(
      key,
    );

    openTab(
      "agents",
    );
  }

  const completed =
    run.status === "completed";

  const running =
    run.status === "queued"
    || run.status === "running";


  return (
    <div
      className="
        min-h-full
        bg-background
        text-foreground
      "
    >
      <div
        className="
          mx-auto
          w-full
          max-w-375
          px-4
          pb-16
          pt-5
          sm:px-6
          lg:px-8
          xl:px-10

        "
      >
        <div
          className="
            flex
            flex-col
            gap-5
          "
        >
          {running && (
            <RunningState
              run={run}
            />
          )}


          {run.status === "failed" && (
            <FailedState
              run={run}
            />
          )}


          {run.status === "cancelled" && (
            <Unavailable
              title="Analysis cancelled"
              description="This run was cancelled and does not contain a final analysis result."
            />
          )}


          {resultError && (
            <section
              className="
                rounded-2xl
                border
                border-red-200
                bg-red-50
                p-4
                text-sm
                text-red-800
                print:hidden
              "
            >
              {resultError}
            </section>
          )}


          {completed && result && (
        <>
        <nav
          className="
            sticky
            top-0
            z-20
            -mx-4
            border-b
            px-4
            py-1
            backdrop-blur
            sm:-mx-6
            sm:px-6
            lg:-mx-8
            lg:px-8
            xl:-mx-10
            xl:px-10
            print:hidden
          "
        >
          <div
            className="
              flex
              min-w-max
              gap-3
              py-2
            "
          >
            {tabs.map(
              item => (
                <div
                  key={item.key}
                  className="
                    flex
                    flex-col
                    items-stretch
                    -mb-3
                  "
                >
                  <button
                    type="button"
                    onClick={() =>
                      openTab(
                        item.key,
                      )
                    }
                    className={`
                      relative
                      rounded-lg
                      px-3
                      py-2
                      text-md
                      font-semibold
                      transition
                      ${
                        tab === item.key
                          ? "text-primary shadow-sm ring-1 ring-border bg-background"
                          : "text-foreground shadow-sm ring-1 ring-border hover:bg-background bg-card"
                      }
                    `}
                  >
                    {item.label}
                  </button>

                  {tab === item.key && (
                    <div
                      className="
                        mt-1
                        h-0.5
                        w-full
                        rounded-full
                        bg-primary
                      "
                    />
                  )}
                </div>
              ),
            )}
          </div>
        </nav>


              {tab === "overview" && (
                <OverviewTab
                  result={result}
                  detailed={detailed}
                  project={project}
                  onAgentClick={
                    handleAgentClick
                  }
                />
              )}


              {tab === "agents" && (
                <AgentAnalysisTab
                    run={run}
                  detailed={detailed}
                  findings={findings}
                  selectedAgent={
                    selectedAgent
                  }
                  setSelectedAgent={
                    setSelectedAgent
                  }
                />
              )}

            {tab === "evidence" && (
                <EvidenceTab
                  detailed={detailed}
                />
              )}

            </>
          )}
        </div>
      </div>
    </div>
  );
}
