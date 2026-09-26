import type {
  Evidence,
} from "@/types/api";


export type TabKey =
  | "overview"
  | "evidence"
  | "agents"
  | "details";


export type AgentKey =
  | "researcher"
  | "customer"
  | "competitor"
  | "tech"
  | "business"
  | "skeptic"
  | "judge";


export interface AgentConfig {
  key: AgentKey;
  label: string;
  short: string;
  color: string;
  soft: string;
  icon: string;
}


export interface EvidenceItem
  extends Evidence {
  agent: string;
  category: string;
  band:
    | "strong"
    | "partial"
    | "weak";
}
