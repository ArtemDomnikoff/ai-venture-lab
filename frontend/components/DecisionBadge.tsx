import type {
  AnalysisDecision,
} from "@/types/api";


interface Props {
  decision: AnalysisDecision;
}



const decisionConfig: Record<
  AnalysisDecision,
  {
    label: string;
    color: string;
  }
> = {

  strong_opportunity: {
    label: "Strong Opportunity",
    color: "var(--success)",
  },


  promising_but_risky: {
    label: "Promising but Risky",
    color: "var(--warning)",
  },


  needs_more_research: {
    label: "Needs More Research",
    color: "var(--primary)",
  },


  weak_opportunity: {
    label: "Weak Opportunity",
    color: "var(--warning)",
  },


  not_recommended: {
    label: "Not Recommended",
    color: "var(--danger)",
  },

};



export default function DecisionBadge(
  {
    decision,
  }: Props,
) {


  const config =
    decisionConfig[decision];



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
        color: config.color,

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

      {config.label}

    </span>

  );

}