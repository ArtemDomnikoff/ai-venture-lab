interface Props {
  status: string;
}


const statusConfig: Record<
  string,
  {
    label: string;
    color: string;
    background: string;
  }
> = {

  queued: {
    label: "Queued",
    color: "var(--warning)",
    background:
      "color-mix(in srgb, var(--warning) 12%, transparent)",
  },


  running: {
    label: "Running",
    color: "var(--primary)",
    background:
      "color-mix(in srgb, var(--primary) 12%, transparent)",
  },


  completed: {
    label: "Completed",
    color: "var(--success)",
    background:
      "color-mix(in srgb, var(--success) 12%, transparent)",
  },


  failed: {
    label: "Failed",
    color: "var(--danger)",
    background:
      "color-mix(in srgb, var(--danger) 12%, transparent)",
  },

};




export default function StatusBadge(
  {
    status,
  }: Props,
) {


  const normalized =
    status.toLowerCase();



  const config =
    statusConfig[normalized]
    ??
    {
      label: status,
      color: "var(--muted)",
      background:
        "var(--background)",
    };




  return (

    <span
      className="
        inline-flex
        h-8
        shrink-0
        items-center
        rounded-full
        border
        px-4
        text-sm
        font-semibold
        capitalize
      "
      style={{
        color:
          config.color,

        backgroundColor:
          config.background,

        borderColor:
          config.color,
      }}
    >

      {config.label}

    </span>

  );

}