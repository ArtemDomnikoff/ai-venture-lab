import type {
  AgentConfig,
  TabKey,
} from "@/components/run-page/viewer/types";


export const AGENTS: AgentConfig[] = [
  {
    key: "researcher",
    label: "Market Agent",
    short: "Market",
    color: "#2563eb",
    soft: "#eff6ff",
    icon: "M",
  },
  {
    key: "customer",
    label: "Customer Agent",
    short: "Customer",
    color: "#7c3aed",
    soft: "#f5f3ff",
    icon: "C",
  },
  {
    key: "competitor",
    label: "Competition Agent",
    short: "Competition",
    color: "#ea580c",
    soft: "#fff7ed",
    icon: "R",
  },
  {
    key: "tech",
    label: "Technology Agent",
    short: "Technology",
    color: "#0891b2",
    soft: "#ecfeff",
    icon: "T",
  },
  {
    key: "business",
    label: "Business Agent",
    short: "Business",
    color: "#059669",
    soft: "#ecfdf5",
    icon: "B",
  },
  {
    key: "skeptic",
    label: "Skeptic Agent",
    short: "Skeptic",
    color: "#dc2626",
    soft: "#fef2f2",
    icon: "S",
  },
  {
    key: "judge",
    label: "Judge Agent",
    short: "Judge",
    color: "#9333ea",
    soft: "#faf5ff",
    icon: "J",
  },
];


export const PLANNER_CONFIG = {
  label: "Planner",
  short: "Planner",
  color: "#2563eb",
  soft: "#eff6ff",
  icon: "P",
};


export const tabs: Array<{
  key: TabKey;
  label: string;
}> = [
  {
    key: "overview",
    label: "Overview",
  },
  {
    key: "agents",
    label: "Agent Analysis",
  },
  {
    key: "evidence",
    label: "Evidence",
  },
];


export const iconPaths: Record<
  string,
  string[]
> = {
  arrow: [
    "M5 12h14",
    "M13 6l6 6-6 6",
  ],
  search: [
    "M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16z",
    "M21 21l-4.35-4.35",
  ],
  warning: [
    "M12 9v4",
    "M12 17h.01",
    "M10.3 3.9L2.8 17a2 2 0 0 0 1.75 3h14.9a2 2 0 0 0 1.75-3L13.7 3.9a2 2 0 0 0-3.4 0z",
  ],
  info: [
    "M12 16v-4",
    "M12 8h.01",
    "M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z",
  ],
  external: [
    "M14 3h7v7",
    "M10 14L21 3",
    "M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5",
  ],
};
