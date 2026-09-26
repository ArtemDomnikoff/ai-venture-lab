"use client";


import {
  useEffect,
  useState,
} from "react";


import Link from "next/link";


import {
  deleteRun,
  getRunResult,
} from "@/lib/runs";


import type {
  AnalysisResult,
  Run,
} from "@/types/api";


import StatusBadge from "@/components/project-page/StatusBadge";
import DecisionBadge from "@/components/run-page/DecisionBadge";
import {formatRunError} from "@/components/run-page/viewer/utils";



interface Props {

  run: Run;

  runNumber: number;

  onDelete: (
    id: string,
  ) => void;

}





function formatDate(
  value: string,
) {

  return new Intl.DateTimeFormat(
    "en",
    {
      timeZone: "UTC",
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    },
  ).format(
    new Date(value),
  );

}





export default function RunCard(
  {
    run,
    runNumber,
    onDelete,
  }: Props,
) {


  const [
    result,
    setResult,
  ] = useState<AnalysisResult | null>(
    null,
  );


  const [
    deleting,
    setDeleting,
  ] = useState(false);



  useEffect(
    () => {

      if(
        run.status !== "completed"
      ) {
        return;
      }


      getRunResult(
        run.id,
      )
        .then(
          setResult,
        )
        .catch(
          () => {
            setResult(null);
          },
        );


    },
    [
      run.id,
      run.status,
    ],
  );





  async function handleDelete() {


    if(
      deleting
    ) {
      return;
    }


    setDeleting(true);



    try {

      await deleteRun(
        run.id,
      );


      onDelete(
        run.id,
      );


    }

    catch(error) {

      console.error(
        "Failed to delete run",
        error,
      );


      setDeleting(false);

    }

  }





  return (

    <div

      className="
        relative

        rounded-2xl

        border
        border-border

        bg-card

        p-6

        transition

        hover:bg-background
      "

    >



      <button

        onClick={
          handleDelete
        }

        disabled={
          deleting
        }

        className="
          absolute

          right-4

          top-4


          flex

          h-7

          w-7


          items-center

          justify-center


          rounded-lg


          text-sm


          text-muted


          transition


          hover:bg-red-500/10


          hover:text-red-400


          disabled:opacity-50
        "

      >

        ×

      </button>







      <Link

        href={
          `/projects/${run.project_id}/runs/${run.id}`
        }

        className="
          block
        "

      >



        {/* HEADER */}

        <div
          className="
            flex
            flex-col

            gap-4
          "
        >


          <div>


            <h3
              className="
                text-xl

                font-semibold

                text-foreground
              "
            >

              Run {runNumber}

            </h3>



            <p
              className="
                mt-2

                text-sm

                text-muted
              "
            >

              {
                formatDate(
                  run.created_at,
                )
              }

            </p>


          </div>



          <div>

            <StatusBadge
              status={
                run.status
              }
            />

          </div>


        </div>







        {
          run.status === "running"
          &&
          (

            <div
              className="
                mt-5

                rounded-xl

                border

                border-border

                p-4
              "
            >

              <p
                className="
                  text-sm

                  text-muted
                "
              >

                Current step

              </p>


              <p
                className="
                  mt-1

                  font-semibold

                  text-foreground
                "
              >

                {
                  run.current_node
                  ??
                  "Processing"
                }

              </p>


            </div>

          )
        }







        {
          run.status === "failed"
          &&
          (

            <div
              className="
                mt-5

                rounded-xl

                border

                border-danger

                p-4
              "
            >

              <p
                className="
                  text-sm

                  text-danger
                "
              >

                Analysis failed

              </p>


              <p
                className="
                  mt-2

                  text-sm

                  text-foreground
                "
              >

                {formatRunError(
                    run.error,
                )}

              </p>


            </div>

          )
        }








        {
          result
          &&
          (

            <div
              className="
                mt-6

                flex

                flex-col

                gap-4


                border-t

                border-border


                pt-5


                sm:flex-row

                sm:items-center

                sm:justify-between
              "
            >


              <div>

                <p
                  className="
                    text-sm

                    text-muted
                  "
                >

                  Venture score

                </p>


                <p
                  className="
                    mt-1

                    text-3xl

                    font-bold

                    text-foreground
                  "
                >

                  {
                    result.score
                  }

                  <span
                    className="
                      text-lg

                      text-muted
                    "
                  >

                    /100

                  </span>


                </p>


              </div>





              <DecisionBadge

                decision={
                  result.decision
                }

              />


            </div>

          )
        }




      </Link>


    </div>

  );

}
