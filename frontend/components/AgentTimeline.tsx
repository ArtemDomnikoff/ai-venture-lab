interface Props {
  progress: Record<string, string>;
}



function StatusColor(
  status: string,
) {

  switch (
    status.toLowerCase()
  ) {

    case "completed":
      return "var(--success)";


    case "running":
      return "var(--primary)";


    case "failed":
      return "var(--danger)";


    case "queued":
      return "var(--warning)";


    default:
      return "var(--muted)";

  }

}



function StatusLabel(
  status: string,
) {

  return status
    .replaceAll("_", " ")
    .replace(
      /^./,
      char => char.toUpperCase(),
    );

}



export default function AgentTimeline(
  {
    progress,
  }: Props,
) {


  const agents =
    Object.entries(progress);



  if (agents.length === 0) {

    return (

      <div
        className="
          rounded-xl
          border
          border-[var(--border)]
          bg-[var(--card)]
          p-5
          text-sm
          text-[var(--muted)]
        "
      >
        No agents available
      </div>

    );

  }



  return (

    <div
      className="
        relative
        space-y-4
      "
    >


      {
        agents.map(
          (
            [
              agent,
              status,
            ],
          ) => (

          <div
            key={agent}
            className="
              flex
              items-center
              gap-4
            "
          >


            <div
              className="
                h-3
                w-3
                shrink-0
                rounded-full
              "
              style={{
                backgroundColor:
                  StatusColor(status),
              }}
            />



            <div
              className="
                flex
                flex-1
                items-center
                justify-between
                gap-4
                rounded-xl
                border
                border-[var(--border)]
                bg-[var(--card)]
                p-4
              "
            >

              <span
                className="
                  font-semibold
                  capitalize
                  text-[var(--foreground)]
                "
              >
                {agent}
              </span>



              <span
                className="
                  rounded-full
                  px-3
                  py-1
                  text-sm
                  font-medium
                "
                style={{
                  color:
                    StatusColor(status),

                  backgroundColor:
                    "var(--background)",
                }}
              >
                {StatusLabel(status)}
              </span>


            </div>


          </div>

        ))
      }


    </div>

  );

}