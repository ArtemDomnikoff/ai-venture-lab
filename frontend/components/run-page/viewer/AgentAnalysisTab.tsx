import type {
  ReactNode,
} from "react";

import type {
  AgentReport,
  DetailedAnalysisResult,
  Finding,
  Run,
} from "@/types/api";

import {
  AGENTS,
} from "@/components/run-page/viewer/constants";

import {
  Badge,
  TextList,
  Unavailable,
} from "@/components/run-page/viewer/ui";

import {
  categoryForAgent,
  clampScore,
  getAgentStatus,
  getReportValue,
  sourceHost,
} from "@/components/run-page/viewer/utils";

import type {
  AgentKey,
} from "@/components/run-page/viewer/types";


interface DimensionScore {
  dimension: string;
  score: number;
  rationale: string;
  evidence_sources?: number[];
}


interface ScoreBreakdown {
  dimension: string;
  score: number;
  weight: number;
  contribution: number;
}


interface ExtendedAgentReport
  extends AgentReport {
  opportunities?: string[];
  dimension_scores?: DimensionScore[];
  evidence_quality?: number;
  score_issues?: string[];
  score_breakdown?: ScoreBreakdown[];
  risk_penalty?: number;
}


const DIMENSION_TITLES: Record<
  string,
  string
> = {
  researcher:
    "Market",

  customer:
    "Customer",

  competitor:
    "Competition",

  tech:
    "Technology",

  business:
    "Business",

  skeptic:
    "Skeptic",

  judge:
    "Judge",

  demand_strength:
    "Demand strength",

  growth_attractiveness:
    "Growth attractiveness",

  market_size_evidence:
    "Market size evidence",

  accessibility:
    "Market accessibility",

  market_structure:
    "Market structure",

  pain_intensity:
    "Pain intensity",

  problem_frequency:
    "Problem frequency",

  willingness_to_pay:
    "Willingness to pay",

  icp_clarity:
    "ICP clarity",

  adoption_feasibility:
    "Adoption feasibility",

  differentiation_strength:
    "Differentiation strength",

  competitive_gap:
    "Competitive gap",

  substitute_defensibility:
    "Substitute defensibility",

  switching_advantage:
    "Switching advantage",

  defensibility:
    "Defensibility",

  technical_feasibility:
    "Technical feasibility",

  implementation_manageability:
    "Implementation manageability",

  infrastructure_readiness:
    "Infrastructure readiness",

  scalability:
    "Scalability",

  time_to_mvp:
    "Time to MVP",

  monetization_clarity:
    "Monetization clarity",

  pricing_power:
    "Pricing power",

  unit_economics_potential:
    "Unit economics potential",

  distribution_feasibility:
    "Distribution feasibility",
};


function dimensionTitle(
  value: string,
) {
  return (
    DIMENSION_TITLES[value]
    ?? value
      .replaceAll(
        "_",
        " ",
      )
      .replace(
        /\b\w/g,
        letter =>
          letter.toUpperCase(),
      )
  );
}


function statusLabel(
  status: string,
) {
  switch (status) {
    case "completed":
      return "Completed";

    case "running":
      return "Running";

    case "failed":
      return "Failed";

    default:
      return "Waiting";
  }
}


function statusTone(
  status: string,
) {
  switch (status) {
    case "completed":
      return {
        color:
          "var(--success)",
        background:
          "color-mix(in srgb, var(--success) 10%, var(--card))",
        border:
          "color-mix(in srgb, var(--success) 25%, var(--card))",
      };

    case "running":
      return {
        color:
          "var(--primary)",
        background:
          "color-mix(in srgb, var(--primary) 10%, var(--card))",
        border:
          "color-mix(in srgb, var(--primary) 28%, var(--card))",
      };

    case "failed":
      return {
        color:
          "var(--danger)",
        background:
          "color-mix(in srgb, var(--danger) 10%, var(--card))",
        border:
          "color-mix(in srgb, var(--danger) 25%, var(--card))",
      };

    default:
      return {
        color:
          "var(--muted)",
        background:
          "color-mix(in srgb, var(--muted) 7%, var(--card))",
        border:
          "color-mix(in srgb, var(--muted) 18%, var(--card))",
      };
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


function emptyText(
  value: string,
) {
  return (
    <div
      className="
        rounded-xl
        border
        border-dashed
        border-border
        bg-background
        px-4
        py-4
        text-sm
        text-muted
      "
    >
      {value}
    </div>
  );
}


function Section({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div>
      <div
        className="
          mb-3
          text-md
          font-semibold
          uppercase
          tracking-[0.12em]
          text-foreground
        "
      >
        {title}
      </div>

      {children}
    </div>
  );
}


function DimensionScores({
  dimensions,
}: {
  dimensions: DimensionScore[];
}) {
  if (!dimensions.length) {
    return null;
  }

  return (
    <Section title="Dimensions">
      <div
        className="
          space-y-5
        "
      >
        {dimensions.map(
          dimension => {
            const score =
              clampScore(
                dimension.score,
              );

            const color =
              scoreColor(
                score,
              );

            return (
              <div
                  key={
                  dimension.dimension
                }
              className="
              border
              bg-background
              rounded-2xl
              p-4
              sm:p-5
            "
              >
                <div
                className="
                  grid
                  w-full
                  grid-cols-[34%_66%]
                  items-center
                  text-left
                  transition-opacity
                "
              >
                  <div
                    className="
                    flex
                    min-w-0
                    items-center
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
                      {
                        dimensionTitle(
                          dimension.dimension,
                        )
                      }
                    </div>
                  </div>

                  <div
                    className="
                      flex
                      min-w-0
                      items-center
                      gap-4
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
                            ease-out
                          "
                          style={{
                            width:
                              `${score}%`,
                            backgroundColor:
                              color,
                          }}
                        />
                      </div>
                    </div>
                      <span
                      className="
                      inline-flex
                        w-8
                        h-9
                        shrink-0
                        text-center
                        justify-center
                        text-lg
                        font-semibold
                        text-foreground
                      "
                    >
                      {score}
                    </span>
                  </div>
              </div>
              <p
                  className="
                    mt-2
                    p-2
                    text-sm
                    leading-6
                    text-muted
                    border-t
                  "
                >
                  {
                    dimension.rationale
                  }
                </p>

                {(
                  dimension
                    .evidence_sources
                    ?.length
                  ?? 0
                ) > 0 && (
                  <div
                    className="
                      mt-1
                      text-xs
                      text-muted
                    "
                  >
                    Evidence:{" "}
                    {dimension
                      .evidence_sources
                      ?.map(
                        source =>
                          `[${source}]`,
                      )
                      .join(
                        ", ",
                      )}
                  </div>
                )}
              </div>
            );
          },
        )}
      </div>
    </Section>
  );
}


function EvidenceList({
  evidence,
}: {
  evidence: NonNullable<
    AgentReport["evidence"]
  >;
}) {
  if (!evidence.length) {
    return null;
  }

  return (
    <Section title="Evidence">
      <div className="space-y-3">
        {evidence.map(
          (
            item,
            index,
          ) => (
            <div
              key={`${item.source}-${index}`}
              className="
                rounded-xl
                border
                border-border
                bg-background
                p-4
              "
            >
              <div
                className="
                  flex
                  items-start
                  justify-between
                  gap-4
                "
              >
                <div className="min-w-0">
                  <div
                    className="
                      text-sm
                      font-medium
                      leading-6
                      text-foreground
                    "
                  >
                    {item.claim}
                  </div>

                  <div
                    className="
                      mt-1
                      text-xs
                      text-muted
                    "
                  >
                    {sourceHost(
                      item.source,
                    )}

                    {" · "}

                    {item.source_type ||
                      "Source"}
                  </div>
                </div>

                <div
                  className="
                    shrink-0
                    text-xs
                    font-semibold
                    text-foreground
                  "
                >
                  {clampScore(
                    item.confidence,
                  )}
                  %
                </div>
              </div>

              <p
                className="
                  mt-3
                  text-sm
                  leading-6
                  text-muted
                "
              >
                {item.excerpt}
              </p>
            </div>
          ),
        )}
      </div>
    </Section>
  );
}


function ListBlock({
  title,
  items,
  tone,
}: {
  title: string;
  items: string[];
  tone:
    | "neutral"
    | "positive"
    | "risk"
    | "warning";
}) {
  return (
    <TextList
      title={title}
      items={items}
      tone={tone}
    />
  );
}


function JudgeBreakdown({
  report,
}: {
  report: ExtendedAgentReport;
}) {
  const breakdown =
    report.score_breakdown ??
    [];

  if (!breakdown.length) {
    return null;
  }

  return (
    <Section title="Score breakdown">
      <div
        className="
          overflow-x-auto
          rounded-2xl
          border
          border-border
        "
      >
        <table
          className="
            w-full
            border-collapse
            text-sm
          "
        >
          <thead>
            <tr
              className="
                border-b
                border-border
                bg-background
                text-xs
                font-semibold
                uppercase
                tracking-[0.08em]
                text-muted
              "
            >
              <th
                className="
                  px-4
                  py-2.5
                  text-left
                "
              >
                Domain
              </th>

              <th
                className="
                  border-l
                  border-border
                  px-4
                  py-2.5
                  text-center
                "
              >
                Score
              </th>

              <th
                className="
                  border-l
                  border-border
                  px-4
                  py-2.5
                  text-center
                "
              >
                Weight
              </th>

              <th
                className="
                  border-l
                  border-border
                  px-4
                  py-2.5
                  text-center
                "
              >
                Contribution
              </th>
            </tr>
          </thead>

          <tbody>
            {breakdown.map(
              item => (
                <tr
                  key={
                    item.dimension
                  }
                  className="
                    border-b
                    border-border
                    last:border-b-0
                  "
                >
                  <td
                    className="
                      px-4
                      py-3
                      font-medium
                      text-foreground
                    "
                  >
                    {dimensionTitle(
                      item.dimension,
                    )}
                  </td>

                  <td
                    className="
                      border-l
                      border-border
                      px-4
                      py-3
                      text-center
                      font-semibold
                      text-foreground
                    "
                  >
                    {item.score}
                  </td>

                  <td
                    className="
                      border-l
                      border-border
                      px-4
                      py-3
                      text-center
                      text-muted
                    "
                  >
                    {Math.round(
                      item.weight * 100,
                    )}
                    %
                  </td>

                  <td
                    className="
                      border-l
                      border-border
                      px-4
                      py-3
                      text-center
                      font-semibold
                      text-foreground
                    "
                  >
                    {
                      item.contribution
                    }
                  </td>
                </tr>
              ),
            )}
          </tbody>

          {typeof report.risk_penalty ===
            "number" && (
            <tfoot>
              <tr
                className="
                  border-t
                  border-border
                  bg-background
                "
              >
                <td
                  className="
                    px-4
                    py-3
                    text-muted
                  "
                  colSpan={3}
                >
                  Skeptic risk penalty
                </td>

                <td
                  className="
                    border-l
                    border-border
                    px-4
                    py-3
                    text-center
                    font-semibold
                    text-danger
                  "
                >
                  -{report.risk_penalty}
                </td>
              </tr>
            </tfoot>
          )}
        </table>
      </div>
    </Section>
  );
}


export default function AgentAnalysisTab({
  run,
  detailed,
  findings,
  selectedAgent,
  setSelectedAgent,
}: {
  run: Run;
  detailed: DetailedAnalysisResult | null;
  findings: Finding[];
  selectedAgent: AgentKey;
  setSelectedAgent: (
    key: AgentKey,
  ) => void;
}) {
  const config =
    AGENTS.find(
      agent =>
        agent.key === selectedAgent,
    ) ?? AGENTS[0];

  const report =
    getReportValue(
      detailed,
      selectedAgent,
    ) as ExtendedAgentReport | null;

  const finding =
    findings.find(
      item =>
        item.category ===
        categoryForAgent(
          selectedAgent,
        ),
    );

  const confidence =
    clampScore(
      report?.confidence ??
        finding?.confidence,
    );

  const score =
    typeof report?.score ===
    "number"
      ? clampScore(
          report.score,
        )
      : null;

  const status =
    getAgentStatus(
      selectedAgent,
      detailed,
      run.progress,
    );

  const strengths =
    report?.strengths ??
    [];

  const risks =
    report?.risks ??
    [];

  const opportunities =
    report?.opportunities ??
    [];

  const claims =
    report?.claims ??
    [];

  const dimensions =
    report?.dimension_scores ??
    [];

  const isSkeptic =
    selectedAgent ===
    "skeptic";

  const isJudge =
    selectedAgent ===
    "judge";

  return (
    <div
      className="
        grid
        gap-5
        xl:grid-cols-[300px_minmax(0,1fr)]
      "
    >
      <section
        className="
          self-start
          rounded-2xl
          border
          border-border
          bg-card
          p-3
          shadow-[0_1px_2px_rgba(15,23,42,0.04)]
        "
      >
        <div
          className="
            px-2
            pb-3
            pt-2
          "
        >
          <div
            className="
              text-xs
              font-semibold
              uppercase
              tracking-[0.12em]
              text-muted
            "
          >
            Agents
          </div>
        </div>

        <div className="space-y-1.5">
          {AGENTS.map(
            agent => {
              const agentReport =
                getReportValue(
                  detailed,
                  agent.key,
                ) as ExtendedAgentReport | null;

              const agentFinding =
                findings.find(
                  item =>
                    item.category ===
                    categoryForAgent(
                      agent.key,
                    ),
                );

              const agentScore =
                typeof agentReport?.score ===
                "number"
                  ? clampScore(
                      agentReport.score,
                    )
                  : null;

              const agentConfidence =
                clampScore(
                  agentReport?.confidence ??
                    agentFinding?.confidence,
                );

              const isSelected =
                agent.key ===
                selectedAgent;

              return (
                <button
                  key={
                    agent.key
                  }
                  type="button"
                  onClick={() =>
                    setSelectedAgent(
                      agent.key,
                    )
                  }
                  className={`
                    w-full
                    rounded-xl
                    border
                    px-3
                    py-3
                    text-left
                    transition-all
                    duration-200
                    ${
                      isSelected
                        ? "border-[var(--primary)] bg-background shadow-sm"
                        : "border-transparent hover:border-border hover:bg-background"
                    }
                  `}
                >
                  <div
                    className="
                      flex
                      items-center
                      gap-3
                    "
                  >
                    <div
                      className="
                        flex
                        h-9
                        w-9
                        shrink-0
                        items-center
                        justify-center
                        rounded-lg
                        text-xs
                        font-semibold
                      "
                      style={{
                        color:
                          agent.color,
                        background:
                          `color-mix(in srgb, ${agent.color} 12%, var(--card))`,
                      }}
                    >
                      {agent.icon}
                    </div>

                    <div
                      className="
                        min-w-0
                        flex-1
                      "
                    >
                      <div
                        className="
                          truncate
                          text-md
                          font-medium
                          text-foreground
                        "
                      >
                        {agent.label}
                      </div>

                      <div
                        className="
                          mt-1
                          flex
                          items-center
                          gap-2
                        "
                      >
                        {agentScore !==
                          null && (
                          <span
                            className="
                              text-sm
                              font-medium
                              text-muted
                            "
                          >
                            {
                              agentScore
                            }{" "}
                            score
                          </span>
                        )}

                        {agentScore ===
                          null &&
                          agentConfidence >
                            0 && (
                            <span
                              className="
                                text-sm
                                text-muted
                              "
                            >
                              {
                                agentConfidence
                              }
                              %
                              {" "}
                              confidence
                            </span>
                          )}
                      </div>
                    </div>

                    <span
                      className="
                        shrink-0
                        text-lg
                        leading-none
                        text-muted
                      "
                    >
                      ›
                    </span>
                  </div>
                </button>
              );
            },
          )}
        </div>
      </section>

      <section
        className="
          min-w-0
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
            border-b
            border-border
            pb-5
          "
        >
          <div
            className="
              flex
              flex-col
              gap-5
              sm:flex-row
              sm:items-start
              sm:justify-between
            "
          >
            <div
              className="
                flex
                min-w-0
                items-start
                gap-3
              "
            >
              <div
                className="
                  flex
                  h-11
                  w-11
                  shrink-0
                  items-center
                  justify-center
                  rounded-xl
                  text-xs
                  font-semibold
                "
                style={{
                  color:
                    config.color,
                  background:
                    `color-mix(in srgb, ${config.color} 12%, var(--card))`,
                }}
              >
                {config.icon}
              </div>

              <div className="min-w-0">
                <h2
                  className="
                    truncate
                    text-xl
                    font-semibold
                    tracking-tight
                    text-foreground
                  "
                >
                  {config.label}
                </h2>

                <div
                  className="
                    mt-1
                    flex
                    flex-wrap
                    items-center
                    gap-2
                    text-xs
                    text-muted
                  "
                >
                  <Badge
                    color={
                      statusTone(
                        status,
                      ).color
                    }
                    background={
                      statusTone(
                        status,
                      ).background
                    }
                    border={
                      statusTone(
                        status,
                      ).border
                    }
                  >
                    {statusLabel(
                      status,
                    )}
                  </Badge>

                  {confidence >
                    0 && (
                    <span>
                      {confidence}%
                      {" "}
                      confidence
                    </span>
                  )}
                </div>
              </div>
            </div>

            {score !==
              null && (
              <div
                className="
                  flex
                  shrink-0
                  items-end
                  gap-3
                "
              >
                <div className="text-right">
                  <div
                    className="
                      text-xs
                      font-medium
                      uppercase
                      tracking-[0.1em]
                      text-muted
                    "
                  >
                    Domain score
                  </div>

                  <div
                    className="
                      mt-1
                      text-3xl
                      font-semibold
                      tracking-tight
                      text-foreground
                    "
                  >
                    {score}

                    <span
                      className="
                        text-base
                        font-medium
                        text-muted
                        p-2
                      "
                    >
                        / 100
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {!report && (
          <div className="py-12">
            <Unavailable
              title="Agent detail is not available"
              description="This run does not contain a detailed report for the selected agent."
            />
          </div>
        )}

        {report && (
          <div
            className="
              mt-6
              space-y-7
            "
          >
            {isJudge ? (
              <>
                {report.summary && (
                  <Section title="Summary">
                    <p
                      className="
                        text-sm
                        leading-7
                        text-muted
                      "
                    >
                      {
                        report.summary
                      }
                    </p>
                  </Section>
                )}

                <JudgeBreakdown
                  report={
                    report
                  }
                />

                <div
                  className="
                    grid
                    gap-4
                    lg:grid-cols-2
                  "
                >
                  <ListBlock
                    title="Strengths"
                    items={
                      strengths
                    }
                    tone="positive"
                  />

                  <ListBlock
                    title="Risks"
                    items={
                      risks
                    }
                    tone="risk"
                  />
                </div>
              </>
            ) : isSkeptic ? (
              <>
                {report.summary && (
                  <Section title="Audit summary">
                    <p
                      className="
                        text-sm
                        leading-7
                        text-muted
                      "
                    >
                      {
                        report.summary
                      }
                    </p>
                  </Section>
                )}

                <div
                  className="
                    grid
                    gap-4
                    lg:grid-cols-2
                  "
                >
                  <ListBlock
                    title="Contradictions"
                    items={
                      report.contradictions ??
                      []
                    }
                    tone="risk"
                  />

                  <ListBlock
                    title="Unsupported claims"
                    items={
                      report.unsupported_claims ??
                      []
                    }
                    tone="warning"
                  />

                  <ListBlock
                    title="Score issues"
                    items={
                      report.score_issues ??
                      []
                    }
                    tone="warning"
                  />

                  <ListBlock
                    title="Missing evidence"
                    items={
                      report.missing_evidence ??
                      []
                    }
                    tone="warning"
                  />
                </div>

                <ListBlock
                  title="Risks"
                  items={
                    risks
                  }
                  tone="risk"
                />
              </>
            ) : (
              <>
                {report.summary && (
                  <Section title="Summary">
                    <p
                      className="
                        text-sm
                        leading-7
                        text-muted
                      "
                    >
                      {
                        report.summary
                      }
                    </p>
                  </Section>
                )}

                <DimensionScores
                  dimensions={
                    dimensions
                  }
                />

                {claims.length >
                  0 && (
                  <ListBlock
                    title="Key findings"
                    items={
                      claims
                    }
                    tone="neutral"
                  />
                )}

                <div
                  className="
                    grid
                    gap-4
                    lg:grid-cols-2
                  "
                >
                  <ListBlock
                    title="Strengths"
                    items={
                      strengths
                    }
                    tone="positive"
                  />

                  <ListBlock
                    title="Risks"
                    items={
                      risks
                    }
                    tone="risk"
                  />

                  <ListBlock
                    title="Opportunities"
                    items={
                      opportunities
                    }
                    tone="neutral"
                  />
                </div>

                {dimensions.length ===
                  0 &&
                  claims.length ===
                    0 &&
                  strengths.length ===
                    0 &&
                  risks.length ===
                    0 &&
                  opportunities.length ===
                    0 && (
                    <div>
                      {emptyText(
                        "No structured findings are available for this agent.",
                      )}
                    </div>
                  )}
              </>
            )}

            {(report.evidence
              ?.length ?? 0) > 0 && (
              <EvidenceList
                evidence={
                  report.evidence ??
                  []
                }
              />
            )}
          </div>
        )}
      </section>
    </div>
  );
}
