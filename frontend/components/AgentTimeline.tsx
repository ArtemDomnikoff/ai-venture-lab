interface Props {
  progress: Record<string,string>;
}



const agentOrder = [
  "planner",
  "tech",
  "business",
  "customer",
  "competitor",
  "researcher",
  "skeptic",
  "judge",
];



const agentLabels:Record<string,string> = {

  planner:
    "Planner",

  tech:
    "Technology Analysis",

  business:
    "Business Analysis",

  customer:
    "Customer Analysis",

  competitor:
    "Competitor Analysis",

  researcher:
    "Market Research",

  skeptic:
    "Skeptic Review",

  judge:
    "Final Judge",

};




function StatusColor(
  status:string,
) {


  switch(
    status.toLowerCase()
  ) {

    case "completed":
      return "var(--success)";


    case "running":
    case "analyzing":
      return "var(--primary)";


    case "failed":
      return "var(--danger)";


    case "queued":
    case "waiting":
    default:
      return "var(--muted)";

  }

}





function StatusLabel(
  status:string,
) {

  return status
    .replaceAll(
      "_",
      " ",
    )
    .toLowerCase();

}





export default function AgentTimeline(
  {
    progress,
  }:Props,
) {


  return (

    <div
      className="
        relative
        space-y-6
      "
    >


      <div
        className="
          absolute
          left-1.5
          top-3
          bottom-3
          w-px
          bg-[var(--border)]
        "
      />



      {
        agentOrder.map(
          agent => {


            const status =
              progress[agent]
              ??
              "queued";


            const color =
              StatusColor(
                status,
              );



            return (

              <div
                key={agent}
                className="
                  relative
                  flex
                  items-start
                  gap-5
                "
              >



                <div
                  className="
                    z-10
                    mt-1
                    h-3
                    w-3
                    shrink-0
                    rounded-full
                  "
                  style={{
                    background:
                      color,
                  }}
                />




                <div
                  className="
                    flex-1
                    rounded-xl
                    border
                    bg-[var(--card)]
                    p-4
                  "
                >


                  <div
                    className="
                      font-semibold
                      text-[var(--foreground)]
                    "
                  >
                    {agentLabels[agent]}
                  </div>



                  <div
                    className="
                      mt-1
                      text-sm
                      capitalize
                    "
                    style={{
                      color,
                    }}
                  >
                    {
                      StatusLabel(
                        status,
                      )
                    }
                  </div>



                </div>



              </div>

            );

          }
        )
      }


    </div>

  );

}