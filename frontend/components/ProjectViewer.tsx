"use client";


import {
  useCallback,
  useEffect,
  useState,
} from "react";


import {
  createRun,
} from "@/lib/projects";


import {
  getProjectRuns,
} from "@/lib/runs";


import type {
  Project,
  Run,
} from "@/types/api";


import RunCard from "@/components/RunCard";



interface Props {

  project: Project;

  runs: Run[];

}




export default function ProjectViewer(
  {
    project,
    runs: initialRuns,
  }: Props,
) {


  const [
    runs,
    setRuns,
  ] = useState<Run[]>(
    initialRuns,
  );



  const [
    loading,
    setLoading,
  ] = useState(false);






  const refreshRuns =
    useCallback(
      async () => {

        try {

          const response =
            await getProjectRuns(
              project.id,
            );


          setRuns(
            response.items,
          );


        } catch(error) {

          console.error(
            "Failed to refresh runs",
            error,
          );

        }

      },
      [
        project.id,
      ],
    );







  async function startRun() {

    if (loading) {
      return;
    }


    setLoading(true);


    try {

      await createRun(
        project.id,
      );


      await refreshRuns();


    } catch(error) {

      console.error(
        "Failed to start run",
        error,
      );


    } finally {

      setLoading(false);

    }

  }







  useEffect(
    () => {

      const hasActiveRun =
        runs.some(
          run =>
            run.status === "queued"
            ||
            run.status === "running",
        );


      if (!hasActiveRun) {
        return;
      }


      const interval =
        setInterval(
          () => {
            refreshRuns();
          },
          3000,
        );


      return () =>
        clearInterval(
          interval,
        );


    },
    [
      runs,
      refreshRuns,
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
          border-border
          bg-card
          p-6
          sm:p-8
        "
      >


        <div
          className="
            flex
            flex-col
            gap-6
            sm:flex-row
            sm:items-start
            sm:justify-between
          "
        >


          <div
            className="
              max-w-3xl
            "
          >

            <h1
              className="
                text-4xl
                font-bold
                text-foreground
              "
            >
              {
                project.name
              }
            </h1>



            <p
              className="
                mt-4
                leading-7
                text-muted
              "
            >
              {
                project.idea
              }
            </p>


          </div>





          <button
            onClick={
              startRun
            }
            disabled={
              loading
            }
            className="
              rounded-xl
              bg-primary
              px-5
              py-3
              font-semibold
              text-white
              transition
              disabled:opacity-50
            "
          >

            {
              loading
                ? "Starting..."
                : "Run analysis"
            }


          </button>



        </div>


      </section>









      <section>


        <div
          className="
            mb-5
            flex
            items-center
            justify-between
          "
        >

          <h2
            className="
              text-2xl
              font-bold
              text-foreground
            "
          >
            Analysis history
          </h2>



          <span
            className="
              text-sm
              text-muted
            "
          >
            {
              runs.length
            }
            {" "}
            runs
          </span>


        </div>





        {
          runs.length === 0
          &&
          (

            <div
              className="
                rounded-2xl
                border
                border-border
                bg-card
                p-8
                text-center
              "
            >

              <p
                className="
                  text-muted
                "
              >
                No analyses yet.
              </p>


            </div>

          )
        }






        <div
          className="
            space-y-4
          "
        >

          {
            runs.map(
              (
                run,
                index,
              ) => (

                <RunCard
                  key={
                    run.id
                  }

                  run={
                    run
                  }

                  runNumber={
                    runs.length - index
                  }

                  onDelete={
                    refreshRuns
                  }

                />

              )
            )
          }


        </div>
      </section>
    </div>

  );

}