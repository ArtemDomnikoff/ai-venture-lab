import type {
  AgentReport,
  AnalysisDecision,
  DetailedAnalysisResult,
} from "@/types/api";

import {
  AGENTS,
} from "@/components/run-page/viewer/constants";

import type {
  AgentKey,
  EvidenceItem,
} from "@/components/run-page/viewer/types";


export type AgentStatus =
  | "waiting"
  | "running"
  | "failed"
  | "completed";


export function clampScore(
  value: number | undefined | null,
) {
  if (
    !Number.isFinite(value)
  ) {
    return 0;
  }

  return Math.min(
    100,
    Math.max(
      0,
      Math.round(
        Number(value),
      ),
    ),
  );
}


export function scoreTone(
  score: number,
) {
  if (score >= 80) {
    return {
      color: "#16a34a",
      background: "#ecfdf5",
      border: "#a7f3d0",
    };
  }

  if (score >= 65) {
    return {
      color: "#65a30d",
      background: "#fffbeb",
      border: "#a7f3d0",
    };
  }

  if (score >= 50) {
    return {
      color: "#ca8a04",
      background: "#fffbeb",
      border: "#fde68a",
    };
  }

  if (score >= 35) {
    return {
      color: "#ea580c",
      background: "#fff7ed",
      border: "#fed7aa",
    };
  }

  return {
    color: "#dc2626",
    background: "#fef2f2",
    border: "#fecaca",
  };
}


export function formatRunError(
  error: string | null | undefined,
) {
  if (!error) {
    return "The run failed before producing a final result.";
  }

  const codeMatch =
    error.match(
      /Error code:\s*(\d+)/i,
    );

  const messageMatch =
    error.match(
      /['"]message['"]\s*:\s*['"]([^'"]+)['"]/i,
    );

  if (
    codeMatch?.[1]
    && messageMatch?.[1]
  ) {
    return `Error code: ${codeMatch[1]} - ${messageMatch[1]}`;
  }

  return error;
}


export function formatDate(
  value: string | null | undefined,
) {
  if (!value) {
    return "—";
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en",
    {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    },
  ).format(date);
}


export function formatDuration(
  started: string | null,
  finished: string | null,
) {
  if (!started) {
    return "—";
  }

  const start =
    new Date(
      started,
    ).getTime();

  const end =
    finished
      ? new Date(
          finished,
        ).getTime()
      : Date.now();

  if (
    !Number.isFinite(start)
    || !Number.isFinite(end)
    || end < start
  ) {
    return "—";
  }

  const seconds =
    Math.round(
      (end - start) / 1000,
    );

  if (seconds < 60) {
    return `${seconds}s`;
  }

  const minutes =
    Math.floor(
      seconds / 60,
    );

  const remainder =
    seconds % 60;

  return `${minutes}m ${remainder}s`;
}


export function sourceHost(
  source: string,
) {
  try {
    return new URL(
      source,
    ).hostname.replace(
      /^www\./,
      "",
    );
  } catch {
    return source;
  }
}


export function unique<T>(
  values: T[],
) {
  return Array.from(
    new Set(values),
  );
}


export function getReportValue(
  detailed: DetailedAnalysisResult | null,
  key: AgentKey,
): AgentReport | null {
  if (!detailed) {
    return null;
  }

  if (key === "judge") {
    return detailed.judge ?? null;
  }

  if (key === "skeptic") {
    return detailed.skeptic ?? null;
  }

  return detailed.agents?.[key] ?? null;
}


/**
 * Normalize any backend progress value to a supported agent status.
 */
export function normalizeAgentStatus(
  value: string | null | undefined,
): AgentStatus {
  switch (
    value?.toLowerCase()
  ) {
    case "completed":
      return "completed";

    case "running":
      return "running";

    case "failed":
      return "failed";

    case "waiting":
      return "waiting";

    default:
      return "waiting";
  }
}

export function statusForAgent(
  progress: Record<string, string>,
  key: AgentKey,
  hasReport: boolean,
): AgentStatus {
  if (hasReport) {
    return "completed";
  }

  return normalizeAgentStatus(
    progress[key],
  );
}


export function decisionText(
  decision: AnalysisDecision | undefined,
) {
  switch (decision) {
    case "strong_opportunity":
      return "Strong Opportunity";

    case "promising_but_risky":
      return "Promising but Risky";

    case "needs_more_research":
      return "Needs More Research";

    case "weak_opportunity":
      return "Weak Opportunity";

    case "not_recommended":
      return "Not Recommended";

    default:
      return "Assessment";
  }
}


export function decisionTone(
  decision: AnalysisDecision | undefined,
) {
  switch (decision) {
    case "strong_opportunity":
      return {
        color: "#059669",
        background: "#ecfdf5",
        border: "#a7f3d0",
      };

    case "promising_but_risky":
      return {
        color: "#d97706",
        background: "#fffbeb",
        border: "#fde68a",
      };

    case "needs_more_research":
      return {
        color: "#2563eb",
        background: "#eff6ff",
        border: "#bfdbfe",
      };

    case "weak_opportunity":
      return {
        color: "#ea580c",
        background: "#fff7ed",
        border: "#fed7aa",
      };

    case "not_recommended":
      return {
        color: "#dc2626",
        background: "#fef2f2",
        border: "#fecaca",
      };

    default:
      return {
        color: "#475569",
        background: "#f8fafc",
        border: "#e2e8f0",
      };
  }
}


export function categoryForAgent(
  key: AgentKey,
) {
  switch (key) {
    case "researcher":
      return "market";

    case "customer":
      return "customer";

    case "competitor":
      return "competition";

    case "tech":
      return "technology";

    case "business":
      return "business";

    case "skeptic":
      return "skeptic";

    default:
      return "";
  }
}


export function buildNextSteps(
  risks: string[],
  missing: string[],
) {
  const steps: string[] = [];

  for (
    const item of missing.slice(
      0,
      3,
    )
  ) {
    steps.push(
      `Validate: ${item}`,
    );
  }

  for (
    const item of risks.slice(
      0,
      3,
    )
  ) {
    if (
      steps.length >= 3
    ) {
      break;
    }

    steps.push(
      `Test risk: ${item}`,
    );
  }

  if (
    !steps.length
  ) {
    steps.push(
      "Review the strongest claims and source quality.",
    );

    steps.push(
      "Talk to target users to validate demand and willingness to pay.",
    );

    steps.push(
      "Compare the top alternatives and document the differentiation gap.",
    );
  }

  return steps.slice(
    0,
    3,
  );
}


export function countSources(
  detailed: DetailedAnalysisResult | null,
) {
  if (!detailed) {
    return 0;
  }

  const sources =
    AGENTS.slice(
      0,
      5,
    ).flatMap(
      agent =>
        (
          getReportValue(
            detailed,
            agent.key,
          )?.evidence ?? []
        ).map(
          item =>
            item.source,
        ),
    );

  return unique(
    sources,
  ).length;
}


export function countClaims(
  detailed: DetailedAnalysisResult | null,
) {
  if (!detailed) {
    return 0;
  }

  return AGENTS.slice(
    0,
    5,
  ).reduce(
    (
      total,
      agent,
    ) =>
      total
      + (
        getReportValue(
          detailed,
          agent.key,
        )?.claims ?? []
      ).length,
    0,
  );
}


/**
 * Get current agent status.
 *
 * IMPORTANT:
 * Pass the live progress map from the run viewer.
 */
export function getAgentStatus(
  key: AgentKey,
  detailed: DetailedAnalysisResult | null,
  progress: Record<string, string> = {},
): AgentStatus {
  const report =
    getReportValue(
      detailed,
      key,
    );

  return statusForAgent(
    progress,
    key,
    Boolean(report),
  );
}


export function collectEvidence(
  detailed: DetailedAnalysisResult | null,
): EvidenceItem[] {
  if (!detailed) {
    return [];
  }

  const items: EvidenceItem[] = [];

  for (
    const config of AGENTS.slice(
      0,
      5,
    )
  ) {
    const report =
      getReportValue(
        detailed,
        config.key,
      );

    for (
      const evidence of report?.evidence ?? []
    ) {
      const confidence =
        clampScore(
          evidence.confidence,
        );

      items.push({
        ...evidence,
        agent: config.label,
        category: config.short,
        band:
          confidence >= 80
            ? "strong"
            : confidence >= 55
              ? "partial"
              : "weak",
      });
    }
  }

  const seen =
    new Set<string>();

  return items.filter(
    item => {
      const key =
        `${item.claim}|${item.source}|${item.excerpt}`;

      if (
        seen.has(key)
      ) {
        return false;
      }

      seen.add(key);

      return true;
    },
  );
}
