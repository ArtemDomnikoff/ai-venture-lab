"use client";

import {
  useEffect,
  useState,
} from "react";


import {
  getRun,
  getRunResult,
  getRunFindings,
} from "@/lib/runs";


import type {
  Run,
  AnalysisResult,
  Finding,
} from "@/types/api";


import StatusBadge from "@/components/StatusBadge";
import DecisionBadge from "@/components/DecisionBadge";
import ScoreCard from "@/components/ScoreCard";
import AgentTimeline from "@/components/AgentTimeline";
import FindingCard from "@/components/FindingCard";




export default function RunViewer(
  {
    initialRun,
  }: {
    initialRun: Run;
  },
) {


  const [
    run,
    setRun,
  ] = useState(initialRun);



  const [
    result,
    setResult,
  ] = useState<AnalysisResult | null>(
    null,
  );



  const [
    findings,
    setFindings,
  ] = useState<Finding[]>([]);






  async function loadResult(
    runId:string,
  ) {

    const [
      result,
      findings,
    ] = await Promise.all([
      getRunResult(runId),
      getRunFindings(runId),
    ]);


    setResult(result);
    setFindings(findings);

  }







  useEffect(
    () => {


      if(
        run.status === "completed"
      ) {

        loadResult(
          run.id,
        );

        return;

      }



      if(
        run.status === "failed"
      ) {

        return;

      }





      const interval =
        setInterval(
          async()=>{


            const updated =
              await getRun(
                run.id,
              );



            setRun(updated);



            if(
              updated.status === "completed"
            ) {

              loadResult(
                updated.id,
              );

            }


          },
          3000,
        );




      return () =>
        clearInterval(interval);



    },
    [
      run.id,
      run.status,
    ],
  );







  return (

    <div
      className="
        space-y-8
      "
    >




      <section
        className="
          rounded-2xl
          border
          border-[var(--border)]
          bg-[var(--card)]
          p-6
          sm:p-8
        "
      >

        <div
          className="
            flex
            flex-col
            gap-4
            sm:flex-row
            sm:items-start
            sm:justify-between
          "
        >

          <div>

            <h1
              className="
                text-4xl
                font-bold
                text-[var(--foreground)]
              "
            >
              Venture Analysis
            </h1>


            <p
              className="
                mt-2
                text-[var(--muted)]
              "
            >
              AI multi-agent evaluation report
            </p>

          </div>



          <StatusBadge
            status={
              run.status
            }
          />

        </div>


      </section>






      <section
        className="
          rounded-2xl
          border
          border-[var(--border)]
          bg-[var(--card)]
          p-6
          sm:p-8
        "
      >

        <h2
          className="
            text-2xl
            font-bold
            text-[var(--foreground)]
          "
        >
          Agent pipeline
        </h2>


        <p
          className="
            mt-2
            text-[var(--muted)]
          "
        >
          Analysis workflow status
        </p>



        <div className="mt-6">

          <AgentTimeline
            progress={
              run.progress
            }
          />

        </div>


      </section>







      {
        run.status === "failed"
        &&
        (

          <section
            className="
              rounded-2xl
              border
              border-[var(--danger)]
              bg-[var(--card)]
              p-6
            "
          >

            <h2
              className="
                text-2xl
                font-bold
                text-[var(--danger)]
              "
            >
              Analysis failed
            </h2>


            <p
              className="
                mt-3
                text-[var(--foreground)]
              "
            >
              {run.error}
            </p>


          </section>

        )
      }








      {
        result
        &&
        (

          <>

            <section
              className="
                grid
                gap-8
                rounded-2xl
                border
                border-[var(--border)]
                bg-[var(--card)]
                p-6
                md:grid-cols-3
                sm:p-8
              "
            >


              <div
                className="
                  flex
                  justify-center
                "
              >

                <ScoreCard
                  score={
                    result.score
                  }
                />

              </div>





              <div
                className="
                  md:col-span-2
                "
              >

                <DecisionBadge
                  decision={
                    result.decision
                  }
                />



                <h2
                  className="
                    mt-5
                    text-2xl
                    font-bold
                    text-[var(--foreground)]
                  "
                >
                  Final decision
                </h2>



                <p
                  className="
                    mt-4
                    leading-7
                    text-[var(--muted)]
                  "
                >
                  {result.summary}
                </p>


              </div>


            </section>








            <section>

              <h2
                className="
                  mb-5
                  text-2xl
                  font-bold
                  text-[var(--foreground)]
                "
              >
                Findings
              </h2>



              <div
                className="
                  grid
                  gap-6
                  md:grid-cols-2
                "
              >

                {
                  findings.map(
                    (
                      finding,
                    ) => (

                    <FindingCard
                      key={
                        finding.id
                      }
                      finding={
                        finding
                      }
                    />

                  ))
                }

              </div>


            </section>


          </>

        )
      }



    </div>

  );

}