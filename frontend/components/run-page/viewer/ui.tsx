import type {
  ReactNode,
} from "react";

import type {
  Run,
} from "@/types/api";

import {
  iconPaths,
    AGENTS,
    PLANNER_CONFIG
} from "@/components/run-page/viewer/constants";

import {
  clampScore,
  scoreTone,
    formatRunError,
} from "@/components/run-page/viewer/utils";


export function Icon({
  name,
  size = 16,
  strokeWidth = 1.8,
}: {
  name: string;
  size?: number;
  strokeWidth?: number;
}) {
  const paths =
    iconPaths[name];

  if (!paths) {
    return null;
  }

  return (
    <svg
      aria-hidden="true"
      fill="none"
      height={size}
      viewBox="0 0 24 24"
      width={size}
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={strokeWidth}
    >
      {paths.map(
        (
          d,
          index,
        ) => (
          <path
            d={d}
            key={`${name}-${index}`}
          />
        ),
      )}
    </svg>
  );
}


export function SectionTitle({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
}) {
  return (
    <div className="
    mb-5
    p-2
    border-b
    "
    >
      {eyebrow && (
        <div
          className="
            mb-1
            text-[11px]
            font-semibold
            uppercase
            tracking-[0.14em]
            text-slate-400
          "
        >
          {eyebrow}
        </div>
      )}

      <h2
        className="
          text-[20px]
          font-semibold
          tracking-tight
          text-foreground
        "
      >
        {title}
      </h2>

      {description && (
        <p
          className="
            mt-1
            text-sm
            leading-6
            text-slate-500
          "
        >
          {description}
        </p>
      )}
    </div>
  );
}


export function Badge({
  children,
  color,
  background,
  border,
}: {
  children: ReactNode;
  color: string;
  background: string;
  border: string;
}) {
  return (
    <span
      className="
        inline-flex
        items-center
        rounded-full
        border
        px-2.5
        py-1
        text-[11px]
        font-semibold
      "
      style={{
        color,
        background,
        borderColor: border,
      }}
    >
      {children}
    </span>
  );
}


export function Stat({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <div>
      <div
        className="
            flex
            h-8
            items-start
          text-[11px]
          font-medium
          uppercase
          tracking-[0.12em]
          text-slate-400
        "
      >
        {label}
      </div>

      <div
        className="
          mt-1
          text-[21px]
          font-semibold
          tracking-tight
          text-foreground
        "
      >
        {value}
      </div>

      {hint && (
        <div
          className="
            mt-0.5
            text-xs
            text-slate-500
          "
        >
          {hint}
        </div>
      )}
    </div>
  );
}


export function ProgressBar({
  value,
  color = "#2563eb",
}: {
  value: number;
  color?: string;
}) {
  return (
    <div
      className="
        h-2
        overflow-hidden
        rounded-full
        bg-slate-100
      "
    >
      <div
        className="
          h-full
          rounded-full
          transition-[width]
          duration-500
        "
        style={{
          width: `${clampScore(value)}%`,
          background: color,
        }}
      />
    </div>
  );
}


export function ScoreRing({
  score,
}: {
  score: number;
}) {
  const value =
    clampScore(
      score,
    );

  const tone =
    scoreTone(
      value,
    );

  return (
    <div
      className="
        relative
        h-48
        w-48
        shrink-0
      "
    >
      <div
        className="
          absolute
          inset-0
          rounded-full
        "
        style={{
          background:
            `conic-gradient(
            ${tone.color}
            ${value * 3.6}deg,
             var(--border)
            ${value * 3.6}deg
          )`,
        }}
      />

      <div
        className="
          absolute
          inset-3
          flex
          flex-col
          items-center
          justify-center
          rounded-full
          bg-card
        "
      >
        <div
          className="
            text-[54px]
            text-foreground
            font-semibold
            leading-none
            tracking-[-0.06em]
          "
        >
          {value}
        </div>

        <div
          className="
            mt-1
            text-xs
            font-medium
            uppercase
            tracking-[0.14em]
            text-slate-400
          "
        >
          / 100
        </div>

        <div
            className="
            mt-3
            text-foreground"
        >
          Overall score
        </div>
      </div>
    </div>
  );
}


export function TextList({
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
  const accent =
    tone === "positive"
      ? "#059669"
      : tone === "risk"
        ? "#dc2626"
        : tone === "warning"
          ? "#d97706"
          : "#64748b";


  const values =
    items.length
      ? items
      : ["No items returned."];

  return (
    <div
      className="
        rounded-xl
        p-4
      "
    >
      <div
        className="
          text-md
          font-semibold
          text-foreground
        "
      >
        {title}
      </div>

      <div
        className="
          mt-3
          space-y-2
        "
      >
        {values
          .slice(
            0,
            6,
          )
          .map(
            (
              item,
              index,
            ) => (
              <div
                key={`${title}-${index}`}
                className="
                  rounded-lg
                  px-3
                  py-2.5
                  text-sm
                  leading-6
                  text-foreground
                  bg-background
                "
                style={{
                  borderLeft:
                    `3px solid ${accent}`,
                }}
              >
                {item}
              </div>
            ),
          )}
      </div>
    </div>
  );
}


export function Unavailable({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <section
      className="
        rounded-2xl
        border
        border-dashed
        border-slate-200
        bg-card
        p-8
        text-center
      "
    >
      <div
        className="
          mx-auto
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-full
          bg-background
          text-foreground
          shadow-sm
        "
      >
        <Icon
          name="info"
          size={24}
        />
      </div>

      <h3
        className="
          mt-3
          text-sm
          font-semibold
          text-foreground
        "
      >
        {title}
      </h3>

      <p
        className="
          mx-auto
          mt-1
          max-w-xl
          text-sm
          leading-6
          text-muted
        "
      >
        {description}
      </p>
    </section>
  );
}


export function RunningState({
  run,
}: {
  run: Run;
}) {
  const workflowNodes = [
    {
      key: "planner",
      label: PLANNER_CONFIG.label,
      short: PLANNER_CONFIG.short,
      color: PLANNER_CONFIG.color,
      soft: PLANNER_CONFIG.soft,
      icon: PLANNER_CONFIG.icon,
    },
    ...AGENTS,
  ];


  const getStatus = (
    key: string,
  ) => {
    return (
      run.progress?.[key]
      ?? "waiting"
    );
  };


  const statusLabel = (
    status: string,
  ) => {
    switch (status) {
      case "completed":
        return "Completed";

      case "running":
        return "Running";

      case "failed":
        return "Failed";

      case "waiting":
      default:
        return "Waiting";
    }
  };


  const statusColor = (
    status: string,
  ) => {
    switch (status) {
      case "completed":
        return "var(--success)";

      case "running":
        return "var(--primary)";

      case "failed":
        return "var(--danger)";

      default:
        return "var(--muted)";
    }
  };


  const statusBackground = (
    status: string,
  ) => {
    switch (status) {
      case "completed":
        return "color-mix(in srgb, var(--success) 10%, var(--card))";

      case "running":
        return "color-mix(in srgb, var(--primary) 10%, var(--card))";

      case "failed":
        return "color-mix(in srgb, var(--danger) 10%, var(--card))";

      default:
        return "color-mix(in srgb, var(--muted) 7%, var(--card))";
    }
  };


  const statusBorder = (
    status: string,
  ) => {
    switch (status) {
      case "completed":
        return "color-mix(in srgb, var(--success) 25%, var(--card))";

      case "running":
        return "color-mix(in srgb, var(--primary) 28%, var(--card))";

      case "failed":
        return "color-mix(in srgb, var(--danger) 25%, var(--card))";

      default:
        return "color-mix(in srgb, var(--muted) 18%, var(--card))";
    }
  };


  const completedCount =
    workflowNodes.filter(
      node =>
        getStatus(
          node.key,
        ) === "completed",
    ).length;


  const runningNodes =
    workflowNodes.filter(
      node =>
        getStatus(
          node.key,
        ) === "running",
    );


  const failedNodes =
    workflowNodes.filter(
      node =>
        getStatus(
          node.key,
        ) === "failed",
    );


  const progress =
    Math.round(
      (
        completedCount
        / workflowNodes.length
      ) * 100,
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
          gap-3
          sm:flex-row
          sm:items-start
          sm:justify-between
        "
      >
        <div
          className="
            flex
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
              bg-primary/10
              text-primary
            "
          >
            <span
              className="
                h-2.5
                w-2.5
                animate-pulse
                rounded-full
                bg-primary
              "
            />
          </div>

          <div>
            <div
              className="
                text-xs
                font-semibold
                uppercase
                tracking-[0.12em]
                text-muted
              "
            >
              Live workflow
            </div>

            <h2
              className="
                mt-1
                text-lg
                font-semibold
                tracking-tight
                text-foreground
              "
            >
              Analysis in progress
            </h2>
          </div>
        </div>

        <div
          className="
            shrink-0
            text-right
          "
        >
          <div
            className="
              text-xs
              text-muted
            "
          >
            Progress
          </div>

          <div
            className="
              mt-0.5
              text-lg
              font-semibold
              text-foreground
            "
          >
            {completedCount}/{workflowNodes.length}
          </div>
        </div>
      </div>


      <div
        className="
          mt-6
        "
      >
        <div
          className="
            mb-2
            flex
            items-center
            justify-between
            text-xs
            text-muted
          "
        >
          <span>
            Workflow progress
          </span>

          <span
            className="
              font-semibold
              text-foreground
            "
          >
            {progress}%
          </span>
        </div>

        <div
          className="
            h-2
            overflow-hidden
            rounded-full
            bg-background
          "
        >
          <div
            className="
              h-full
              rounded-full
              bg-primary
              transition-all
              duration-500
            "
            style={{
              width:
                `${progress}%`,
            }}
          />
        </div>
      </div>


      {failedNodes.length > 0 && (
        <div
          className="
            mt-2
            rounded-xl
            border
            border-red-200
            bg-red-50
            px-4
            py-3
          "
        >
          <div
            className="
              text-sm
              font-semibold
              text-red-800
            "
          >
            Analysis failed
          </div>

          <div
            className="
              mt-1
              text-xs
              leading-5
              text-red-700
            "
          >
            {failedNodes
              .map(
                node =>
                  node.label,
              )
              .join(
                ", ",
              )}
          </div>

          {run.error && (
            <div
              className="
                mt-2
                text-xs
                leading-5
                text-red-700
              "
            >
              {run.error}
            </div>
          )}
        </div>
      )}


      <div
        className="
          mt-8
          space-y-3
        "
      >
        {workflowNodes.map(
          (
            node,
          ) => {
            const status =
              getStatus(
                node.key,
              );

            const isCurrent =
              run.current_node
              === node.key;

            const isRunning =
              status === "running";

            const isCompleted =
              status === "completed";

            const isFailed =
              status === "failed";

            return (
              <div
                key={
                  node.key
                }
                className="
                  relative
                "
              >
                <div
                  className={`
                    flex
                    items-center
                    gap-3
                    rounded-xl
                    border
                    px-4
                    py-3
                    transition-all
                    duration-300

                    ${
                      isCurrent
                        ? "border-primary/40 bg-primary/[0.04] shadow-sm"
                        : isCompleted
                          ? "border-border bg-card"
                          : isFailed
                            ? "border-red-200 bg-red-50/50"
                            : isRunning
                              ? "border-primary/30 bg-primary/[0.025]"
                              : "border-border bg-card"
                    }
                  `}
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
                        node.color,
                      background:
                        node.soft,
                    }}
                  >
                    {node.icon}
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
                        text-sm
                        font-medium
                        text-foreground
                      "
                    >
                      {node.label}
                    </div>
                  </div>

                  <div
                    className="
                      flex
                      items-center
                      gap-2
                    "
                  >
                    {isRunning && (
                      <span
                        className="
                          h-2
                          w-2
                          animate-pulse
                          rounded-full
                          bg-primary
                        "
                      />
                    )}

                    {isFailed && (
                      <span
                        className="
                          flex
                          h-6
                          w-6
                          items-center
                          justify-center
                          rounded-full
                          bg-red-100
                          text-xs
                          font-bold
                          text-red-600
                        "
                      >
                        ×
                      </span>
                    )}

                    {!isRunning
                      && !isCompleted
                      && !isFailed && (
                        <span
                          className="
                            h-2
                            w-2
                            rounded-full
                            bg-slate-300
                          "
                        />
                      )}

                    <Badge
                      color={statusColor(
                        status,
                      )}
                      background={statusBackground(
                        status,
                      )}
                      border={statusBorder(
                        status,
                      )}
                    >
                      {statusLabel(
                        status,
                      )}
                    </Badge>
                  </div>
                </div>
              </div>
            );
          },
        )}
      </div>


      {runningNodes.length > 1 && (
        <div
          className="
            mt-4
            rounded-xl
            bg-background
            px-4
            py-3
            text-xs
            leading-5
            text-muted
          "
        >
          <span
            className="
              font-semibold
              text-foreground
            "
          >
            Parallel research:
          </span>
          {" "}
          {runningNodes
            .map(
              node =>
                node.label,
            )
            .join(
              ", ",
            )}
        </div>
      )}
    </section>
  );
}


export function FailedState({
  run,
}: {
  run: Run;
}) {
  return (
    <section
      className="
        rounded-2xl
        border
        border-red-200
        bg-red-50/70
        p-6
      "
    >
      <div
        className="
          flex
          items-start
          gap-3
        "
      >
        <div
          className="
            mt-0.5
            text-red-600
          "
        >
          <Icon
            name="warning"
            size={19}
          />
        </div>

        <div
          className="
            min-w-0
          "
        >
          <h2
            className="
              text-lg
              font-semibold
              text-red-950
            "
          >
            Analysis failed
          </h2>

          <p
            className="
              mt-1
              text-sm
              leading-6
              text-red-900/80
            "
          >
              {formatRunError(
                run.error,
              )}
          </p>
        </div>
      </div>
    </section>
  );
}
