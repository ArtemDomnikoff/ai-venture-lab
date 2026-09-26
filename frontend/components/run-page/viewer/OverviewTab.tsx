import type {
  AnalysisResult,
  DetailedAnalysisResult,
  Project,
} from "@/types/api";

import {
  AGENTS,
} from "@/components/run-page/viewer/constants";

import {
  ScoreRing,
  SectionTitle,
  Stat,
} from "@/components/run-page/viewer/ui";

import {
  buildNextSteps,
  clampScore,
  countSources,
  getReportValue,
} from "@/components/run-page/viewer/utils";

import type {
  AgentKey,
} from "@/components/run-page/viewer/types";
import DecisionBadge from "@/components/run-page/DecisionBadge";


function DimensionIcon({
  type,
}: {
  type: AgentKey;
}) {
  const commonProps = {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    className: "h-4 w-4",
    "aria-hidden": true,
  };

  switch (type) {
    case "researcher":
      return (
        <svg {...commonProps}>
          <circle
            cx="11"
            cy="11"
            r="7"
          />
          <path d="m20 20-4-4" />
        </svg>
      );

    case "customer":
      return (
        <svg {...commonProps}>
          <circle
            cx="12"
            cy="8"
            r="3"
          />
          <path d="M5 20a7 7 0 0 1 14 0" />
        </svg>
      );

    case "competitor":
      return (
        <svg {...commonProps}>
          <path d="M4 17h16" />
          <path d="M6 17V8h12v9" />
          <path d="M8 8V5h8v3" />
          <path d="M8 12h8" />
        </svg>
      );

    case "tech":
      return (
        <svg {...commonProps}>
          <rect
            x="7"
            y="7"
            width="10"
            height="10"
            rx="2"
          />
          <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" />
        </svg>
      );

    case "business":
      return (
        <svg {...commonProps}>
          <path d="M4 19V5" />
          <path d="M4 19h16" />
          <path d="m7 15 3-3 3 2 5-6" />
        </svg>
      );

    default:
      return null;
  }
}


function scoreColor(
  score: number,
) {
  if (score <= 35) {
    return "var(--danger)";
  }

  if (score <= 50) {
    return "var(--warning)";
  }

  if (score <= 65) {
    return "var(--caution)";
  }

  if (score <= 80) {
    return "var(--good)";
  }

  return "var(--success)";
}


function OverallCard({
  result,
  detailed,
  sourcesCount,
  gapsCount,
}: {
  result: AnalysisResult;
  detailed: DetailedAnalysisResult | null;
  sourcesCount: number;
  gapsCount: number;
}) {

  const confidence =
    clampScore(
      detailed?.judge?.confidence,
    );

  const evidenceQuality =
    clampScore(
      detailed?.skeptic?.evidence_quality,
    );


  return (
    <section
      className="
        rounded-2xl
        border
        border-border
        bg-card
        p-6
        shadow-[0_1px_2px_rgba(15,23,42,0.04)]
      "
    >
      <div
        className="
          flex
          flex-col
          items-center
          text-center
        "
      >
        <ScoreRing
          score={
            result.score
          }
        />

        <div
          className="
            mt-4
          "
        >
          <DecisionBadge
          decision={result.decision}>
          </DecisionBadge>
        </div>
      </div>

      <div
        className="
          mt-6
          grid
          grid-cols-2
          gap-x-6
          gap-y-6
          border-t
          border-border
          pt-6
        "
      >
        <Stat
          label="Confidence"
          value={`${confidence}%`}
        />

        <Stat
          label="Evidence quality"
          value={`${evidenceQuality}%`}
        />

        <Stat
          label="Sources"
          value={
            sourcesCount
          }
          hint="across research agents"
        />

        <Stat
          label="Evidence gaps"
          value={
            gapsCount
          }
          hint={
            gapsCount
              ? "needs validation"
              : "none reported"
          }
        />
      </div>
    </section>
  );
}


function DimensionPanel({
  detailed,
  onAgentClick,
}: {
  detailed: DetailedAnalysisResult | null;
  onAgentClick: (
    key: AgentKey,
  ) => void;
}) {
  const rows =
    AGENTS.slice(
      0,
      5,
    ).map(
      config => {
        const report =
          getReportValue(
            detailed,
            config.key,
          );

        const score =
          typeof report?.score
            === "number"
            ? clampScore(
                report.score,
              )
            : null;

        const confidence =
          typeof report?.confidence
            === "number"
            ? clampScore(
                report.confidence,
              )
            : null;

        return {
          config,
          score,
          confidence,
        };
      },
    );


  return (
    <section
      className="
        rounded-2xl
        border
        border-border
        bg-card
        p-6
        shadow-[0_1px_2px_rgba(15,23,42,0.04)]
      "
    >
      <SectionTitle
        title="Research dimensions"
        description="Each domain score is calculated from five domain-specific criteria and weighted evidence."
      />

      <div
        className="
          space-y-5
        "
      >
        {rows.map(
          ({
            config,
            score,
            confidence,
          }) => {
            const value =
              score ?? 0;

            const color =
              scoreColor(
                value,
              );

            return (
              <button
                key={
                  config.key
                }
                type="button"
                onClick={() =>
                  onAgentClick(
                    config.key,
                  )
                }
                className="
                  grid
                  w-full
                  grid-cols-[34%_66%]
                  items-center
                  gap-4
                  text-left
                  transition-opacity
                  hover:opacity-80
                "
              >
                <div
                  className="
                    flex
                    min-w-0
                    items-center
                    gap-3
                  "
                >
                  <div
                    className="
                      flex
                      h-8
                      w-8
                      shrink-0
                      items-center
                      justify-center
                      rounded-lg
                    "
                    style={{
                      color:
                        config.color,
                      background:
                          `color-mix(in srgb, ${config.color} 14%, transparent)`,
                    }}
                  >
                    <DimensionIcon
                      type={
                        config.key
                      }
                    />
                  </div>

                  <div
                    className="
                      min-w-0
                    "
                  >
                    <div
                      className="
                        truncate
                        text-lg
                        font-medium
                        text-foreground
                      "
                    >
                      {config.short}
                    </div>

                    {confidence !== null && (
                      <div
                        className="
                          mt-0.5
                          text-xs
                          text-muted
                        "
                      >
                        {confidence}%
                        {" "}
                        confidence
                      </div>
                    )}
                  </div>
                </div>

                <div
                  className="
                    flex
                    min-w-0
                    items-center
                    gap-3
                  "
                >
                  <div
                    className="
                      min-w-0
                      flex-1
                    "
                  >
                    <div
                      className="
                        h-2.5
                        overflow-hidden
                        rounded-full
                        bg-[var(--border)]
                      "
                    >
                      <div
                        className="
                          h-full
                          rounded-full
                          transition-all
                          duration-500
                        "
                        style={{
                          width:
                            `${value}%`,
                          backgroundColor:
                            color,
                        }}
                      />
                    </div>
                  </div>

                  <span
                    className="
                      w-8
                      shrink-0
                      text-right
                      text-lg
                      font-semibold
                      text-foreground
                    "
                  >
                    {score !== null
                      ? score
                      : "—"}
                  </span>
                </div>
              </button>
            );
          },
        )}
      </div>
    </section>
  );
}


function Takeaways({
  strengths,
  risks,
  nextSteps,
}: {
  strengths: string[];
  risks: string[];
  nextSteps: string[];
}) {
  function renderColumn(
    title: string,
    items: string[],
    kind:
      | "positive"
      | "risk"
      | "next",
  ) {
    const background =
      kind === "positive"
        ? "var(--success)"
        : kind === "risk"
          ? "var(--danger)"
          : "var(--primary)";

    const color =
      kind === "positive"
        ? "color-mix(in srgb, var(--success) 10%, var(--card))"
        : kind === "risk"
          ? "color-mix(in srgb, var(--danger) 10%, var(--card))"
          : "color-mix(in srgb, var(--primary) 10%, var(--card))";

    const icon =
      kind === "positive"
        ? "✓"
        : kind === "risk"
          ? "!"
          : "→";

    const fallback =
      kind === "positive"
        ? "No major strengths were returned."
        : kind === "risk"
          ? "No major risks were returned."
          : "No additional validation steps were returned.";

    const visibleItems =
      (
        items.length
          ? items
          : [fallback]
      ).slice(
        0,
        5,
      );


    return (
      <div
        className="
          grid
          gap-4
          rounded-xl
          border
          border-border
          bg-background
          p-4
          lg:grid-cols-[220px_minmax(0,1fr)]
          lg:items-start
        "
      >
        <div
          className="
            flex
            min-w-0
            items-center
            gap-2
          "
        >
          <div
            className="
              flex
              h-8
              w-8
              items-center
              justify-center
              rounded-lg
              text-xs
              font-semibold
            "
            style={{
              color:
                background,
              background:
                color,
            }}
          >
            {icon}
          </div>

          <h3
            className="
              text-md
              font-semibold
              text-foreground
            "
          >
            {title}
          </h3>
        </div>

        <div
          className="
            mt-3
            space-y-2.5
          "
        >
          {visibleItems.map(
            (
              item,
              index,
            ) => (
              <div
                key={
                  `${title}-${index}`
                }
                className="
                  flex
                  items-start
                  gap-2.5
                  text-sm
                  leading-6
                  text-muted
                "
              >
                <span
                  className="
                    mt-2
                    h-1.5
                    w-1.5
                    shrink-0
                    rounded-full
                  "
                  style={{
                    backgroundColor:
                      background,
                  }}
                />

                <span>
                  {item}
                </span>
              </div>
            ),
          )}
        </div>
      </div>
    );
  }


  return (
    <section
      className="
        rounded-2xl
        border
        border-border
        bg-card
        p-6
        shadow-[0_1px_2px_rgba(15,23,42,0.04)]
      "
    >
      <SectionTitle
        title="Key takeaways"
        description="The most important signals from the completed research and skeptic review."
      />

      <div
        className="
          space-y-3
        "
      >
        {renderColumn(
          "Main strengths",
          strengths,
          "positive",
        )}

        {renderColumn(
          "Main risks",
          risks,
          "risk",
        )}

        {renderColumn(
          "Next steps",
          nextSteps,
          "next",
        )}
      </div>
    </section>
  );
}


export default function OverviewTab({
  result,
  detailed,
  project,
  onAgentClick,
}: {
  result: AnalysisResult;
  detailed: DetailedAnalysisResult | null;
  project: Project | null;
  onAgentClick: (
    key: AgentKey,
  ) => void;
}) {
  const strengths =
    detailed?.judge?.strengths
    ?? [];

  const risks =
    detailed?.judge?.risks
    ?? detailed?.skeptic?.risks
    ?? [];

  const missingEvidence =
    detailed?.skeptic?.missing_evidence
    ?? [];

  const nextSteps =
    buildNextSteps(
      risks,
      missingEvidence,
    );

  const sourcesCount =
    countSources(
      detailed,
    );

  const gapsCount =
    missingEvidence.length;


  return (
    <div
      className="
        space-y-5
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
              {project ?(
                   <>
                   <h1
                      className="
                        text-4xl
                        font-bold
                        text-foreground
                      "
                    >
                        {project.name}
                    </h1>

                    <p
                      className="
                        mt-2
                        text-muted
                      "
                    >
                        {project.idea}
                    </p>
                   </>
              ) :(
                   <p className="text-foreground">Venture Analysis</p>
              )
              }
          </div>
        </div>
      </section>

      <div
        className="
          grid
          gap-5
          xl:grid-cols-3
          xl:items-start
        "
      >
        <OverallCard
          result={
            result
          }
          detailed={
            detailed
          }
          sourcesCount={
            sourcesCount
          }
          gapsCount={
            gapsCount
          }
        />

        <div
          className="
            flex
            min-w-0
            flex-col
            gap-5
            xl:col-span-2
          "
        >

            <section
            className="
              rounded-2xl
              border
              border-border
              bg-card
              p-6
              shadow-[0_1px_2px_rgba(15,23,42,0.04)]
            "
          >
            <SectionTitle
              title="Executive summary"
            />

            <div
              className="
                px-1
                text-md
                leading-7
                text-muted
              "
            >
              {detailed?.judge?.summary
                || detailed?.skeptic?.summary
                || result.summary}
            </div>
          </section>
          <DimensionPanel
            detailed={
              detailed
            }
            onAgentClick={
              onAgentClick
            }
          />

          <Takeaways
            strengths={
              strengths
            }
            risks={
              risks
            }
            nextSteps={
              nextSteps
            }
          />
        </div>
      </div>
    </div>
  );
}
