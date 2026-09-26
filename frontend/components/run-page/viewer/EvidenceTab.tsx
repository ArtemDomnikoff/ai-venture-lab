"use client";

import {
  useMemo,
  useState,
} from "react";

import type {
  DetailedAnalysisResult,
} from "@/types/api";

import {
  Badge,
  Icon,
  SectionTitle,
  Stat,
  Unavailable,
} from "@/components/run-page/viewer/ui";

import {
  clampScore,
  collectEvidence,
  sourceHost,
} from "@/components/run-page/viewer/utils";

import type {
  EvidenceItem,
} from "@/components/run-page/viewer/types";


function EvidenceBadge({
  band,
}: {
  band: EvidenceItem["band"];
}) {
  const config =
    band === "strong"
      ? {
          label: "Strong",
          color: "var(--success)",
          icon: "✓",
        }
      : band === "partial"
        ? {
            label: "Partially supported",
            color: "var(--caution)",
            icon: "!",
          }
        : {
            label: "Weak",
            color: "var(--danger)",
            icon: "×",
          };

  return (
    <span
      className="
        inline-flex
        max-w-full
        items-center
        rounded-full
        border
        px-4
        py-2
        text-sm
        font-semibold
        whitespace-nowrap
      "
      style={{
        color:
          config.color,
        borderColor:
          config.color,
        backgroundColor:
          `color-mix(
            in srgb,
            ${config.color} 12%,
            transparent
          )`,
      }}
    >
      {config.icon}{" "}
      {config.label}
    </span>
  );
}


function EvidenceCard({
  item,
  onSelect,
}: {
  item: EvidenceItem;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className="
        group
        w-full
        rounded-2xl
        border
        border-border
        bg-card
        p-5
        text-left
        shadow-[0_1px_2px_rgba(15,23,42,0.04)]
        transition
        hover:-translate-y-0.5
        hover:shadow-[0_8px_24px_rgba(15,23,42,0.07)]
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
        <EvidenceBadge
          band={
            item.band
          }
        />

        <span
          className="
            text-sm
            font-semibold
            text-foreground
          "
        >
          {clampScore(
            item.confidence,
          )}
          %
        </span>
      </div>

      <h3
        className="
          mt-4
          text-[15px]
          font-semibold
          leading-6
          text-foreground
        "
      >
        {item.claim}
      </h3>

      <p
        className="
          mt-2
          line-clamp-3
          text-sm
          leading-6
          text-muted
        "
      >
        {item.excerpt}
      </p>

      <div
        className="
          mt-4
          flex
          flex-wrap
          items-center
          gap-x-3
          gap-y-2
          text-xs
          text-muted
        "
      >
        <span
          className="
            font-medium
            text-foreground
          "
        >
          {item.agent}
        </span>

        <span>·</span>

        <span>
          {item.source_type
            || "Source"}
        </span>

        <span>·</span>

        <span>
          {sourceHost(
            item.source,
          )}
        </span>

        <span
          className="
            ml-auto
            inline-flex
            items-center
            gap-1
            font-medium
            text-muted
            transition
            group-hover:text-foreground
          "
        >
          View source

          <Icon
            name="arrow"
            size={13}
          />
        </span>
      </div>
    </button>
  );
}


function EvidenceDrawer({
  item,
  onClose,
}: {
  item: EvidenceItem;
  onClose: () => void;
}) {
  return (
    <div
      className="
        fixed
        inset-0
        z-50
        flex
        justify-end
        backdrop-blur-[1px]
      "
      onMouseDown={
        onClose
      }
    >
      <aside
        className="
          h-full
          w-full
          max-w-xl
          overflow-y-auto
          border-l
          border-border
          bg-card
          p-6
          shadow-2xl
        "
        onMouseDown={
          event =>
            event.stopPropagation()
        }
      >
        <div
          className="
            flex
            items-center
            justify-between
            gap-4
          "
        >
          <div
            className="
              text-xs
              font-semibold
              uppercase
              tracking-[0.14em]
              text-muted
            "
          >
            Evidence detail
          </div>

          <button
            type="button"
            onClick={
              onClose
            }
            className="
              rounded-lg
              px-2.5
              py-1.5
              text-sm
              text-muted
              transition
              hover:bg-background
              hover:text-foreground
            "
          >
            Close
          </button>
        </div>

        <div
          className="
            mt-5
          "
        >
          <EvidenceBadge
            band={
              item.band
            }
          />
        </div>

        <h2
          className="
            mt-4
            text-xl
            font-semibold
            leading-7
            text-foreground
          "
        >
          {item.claim}
        </h2>

        <div
          className="
            mt-6
            space-y-5
          "
        >
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
              Evidence excerpt
            </div>

            <div
              className="
                mt-2
                rounded-xl
                bg-background
                p-4
                text-md
                leading-7
                text-foreground
              "
            >
              {item.excerpt}
            </div>
          </div>

          <div
            className="
              grid
              grid-cols-2
              gap-4
            "
          >
            <Stat
              label="Confidence"
              value={`${clampScore(item.confidence)}%`}
            />

            <Stat
              label="Agent"
              value={
                item.agent
              }
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
              Source
            </div>

            <a
              href={
                item.source
              }
              target="_blank"
              rel="noreferrer"
              className="
                mt-2
                flex
                items-center
                gap-2
                break-all
                text-sm
                font-medium
                text-primary
                hover:text-primary-hover
              "
            >
              {item.source}

              <Icon
                name="external"
                size={14}
              />
            </a>
          </div>
        </div>
      </aside>
    </div>
  );
}


export default function EvidenceTab({
  detailed,
}: {
  detailed: DetailedAnalysisResult | null;
}) {
  const evidence =
    collectEvidence(
      detailed,
    );

  const [
    query,
    setQuery,
  ] = useState("");

  const [
    filter,
    setFilter,
  ] = useState<
    "all"
    | "strong"
    | "partial"
    | "weak"
  >("all");

  const [
    selected,
    setSelected,
  ] = useState<EvidenceItem | null>(
    null,
  );

  const filtered =
    useMemo(
      () => {
        const normalized =
          query
            .trim()
            .toLowerCase();

        return evidence.filter(
          item => {
            const matchesQuery =
              !normalized
              || `${item.claim} ${item.excerpt} ${item.source}`
                .toLowerCase()
                .includes(
                  normalized,
                );

            const matchesFilter =
              filter === "all"
              || item.band === filter;

            return (
              matchesQuery
              && matchesFilter
            );
          },
        );
      },
      [
        evidence,
        filter,
        query,
      ],
    );


  if (!detailed) {
    return (
      <Unavailable
        title="Evidence is not available yet"
        description="The run does not contain a detailed result payload."
      />
    );
  }


  const strong =
    evidence.filter(
      item =>
        item.band === "strong",
    ).length;

  const partial =
    evidence.filter(
      item =>
        item.band === "partial",
    ).length;

  const weak =
    evidence.filter(
      item =>
        item.band === "weak",
    ).length;


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
          p-5
          shadow-[0_1px_2px_rgba(15,23,42,0.04)]
        "
      >
        <div
          className="
            flex
            flex-col
            gap-4
            lg:flex-row
            lg:items-center
            lg:justify-between
          "
        >
          <div>
            <SectionTitle
              eyebrow="Evidence layer"
              title="Evidence"
              description="Claims, excerpts and source verification from the research agents."
            />

            <div
              className="
                flex
                flex-wrap
                gap-2
              "
            >
              <Badge
                color="var(--muted)"
                background="color-mix(in srgb, var(--muted) 12%, transparent)"
                border="color-mix(in srgb, var(--muted) 22%, transparent)"
              >
                {evidence.length} sources
              </Badge>

              <Badge
                color="var(--success)"
                background="color-mix(in srgb, var(--success) 12%, transparent)"
                border="var(--success)"
              >
                {strong} strong
              </Badge>

              <Badge
                color="var(--caution)"
                background="color-mix(in srgb, var(--caution) 12%, transparent)"
                border="var(--caution)"
              >
                {partial} partial
              </Badge>

              <Badge
                color="var(--danger)"
                background="color-mix(in srgb, var(--danger) 12%, transparent)"
                border="var(--danger)"
              >
                {weak} weak
              </Badge>
            </div>
          </div>

          <div
            className="
              flex
              w-full
              max-w-md
              items-center
              gap-2
              rounded-xl
              border
              border-border
              bg-background
              px-3
              py-2.5
              focus-within:border-primary
            "
          >
            <Icon
              name="search"
              size={16}
            />

            <input
              value={query}
              onChange={
                event =>
                  setQuery(
                    event.target.value,
                  )
              }
              placeholder="Search claims or sources..."
              className="
                min-w-0
                flex-1
                bg-transparent
                text-sm
                text-foreground
                outline-none
              "
            />
          </div>
        </div>

        <div
          className="
            mt-5
            flex
            flex-wrap
            gap-2
          "
        >
          {(
            [
              "all",
              "strong",
              "partial",
              "weak",
            ] as const
          ).map(
            value => (
              <button
                key={
                  value
                }
                type="button"
                onClick={() =>
                  setFilter(
                    value,
                  )
                }
                className={`
                  rounded-lg
                  border
                  px-3
                  py-1.5
                  text-sm
                  font-medium
                  transition

                  ${
                    filter === value
                      ? "border-border bg-background text-primary "
                      : "border-border text-muted hover:bg-background hover:text-foreground"
                  }
                `}
              >
                {value === "all"
                  ? "All"
                  : value === "strong"
                    ? "Strong"
                    : value === "partial"
                      ? "Partial"
                      : "Weak"}
              </button>
            ),
          )}
        </div>
      </section>


      {filtered.length === 0 && (
        <Unavailable
          title="No matching evidence"
          description="Try another search query or remove the current filter."
        />
      )}


      <div
        className="
          grid
          gap-4
        "
      >
        {filtered.map(
          (
            item,
            index,
          ) => (
            <EvidenceCard
              key={`${item.source}-${index}`}
              item={
                item
              }
              onSelect={() =>
                setSelected(
                  item,
                )
              }
            />
          ),
        )}
      </div>


      {selected && (
        <EvidenceDrawer
          item={
            selected
          }
          onClose={() =>
            setSelected(
              null,
            )
          }
        />
      )}
    </div>
  );
}
