import Link from "next/link";

import {
  getProject,
} from "@/lib/projects";


import {
  getProjectRuns,
} from "@/lib/runs";


function StatusBadge(
  {
    status,
  }: {
    status:string;
  },
) {

  return (
    <span
      className="
        inline-flex
        rounded-full
        border
        px-3
        py-1
        text-sm
        font-medium
      "
    >
      {status}
    </span>
  );

}



export default async function ProjectPage(
  {
    params,
  }: {
    params: Promise<{
      id:string;
    }>;
  },
) {


  const {
    id,
  } = await params;



  const [
    project,
    runs,
  ] = await Promise.all([
    getProject(id),
    getProjectRuns(id),
  ]);



  return (

    <main
      className="
        min-h-screen
        px-6
        py-10
      "
    >

      <div
        className="
          mx-auto
          max-w-5xl
          space-y-8
        "
      >



        {/* HEADER */}

        <section
          className="
            rounded-2xl
            border
            bg-[var(--card)]
            p-8
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

            <div>

              <h1
                className="
                  text-4xl
                  font-bold
                "
              >
                {project.name}
              </h1>


              <p
                className="
                  mt-4
                  leading-7
                "
                style={{
                  color:
                    "var(--muted)",
                }}
              >
                {project.idea}
              </p>


            </div>



            <StatusBadge
              status={
                project.status
              }
            />

          </div>


        </section>






        {/* ACTION */}

        <section
          className="
            rounded-2xl
            border
            bg-[var(--card)]
            p-6
          "
        >

          <Link
            href="/projects/new"
            className="
              inline-flex
              rounded-xl
              bg-[var(--primary)]
              px-5
              py-3
              font-semibold
              text-white
              transition
              hover:bg-[var(--primary-hover)]
            "
          >
            Start new analysis
          </Link>


        </section>






        {/* RUNS */}

        <section>

          <h2
            className="
              mb-5
              text-2xl
              font-bold
            "
          >
            Analysis runs
          </h2>



          {
            runs.items.length === 0 ? (

              <div
                className="
                  rounded-2xl
                  border
                  p-8
                  text-center
                "
                style={{
                  color:
                    "var(--muted)",
                }}
              >
                No analyses yet.
              </div>

            ) : (


              <div
                className="
                  grid
                  gap-5
                "
              >


                {
                  runs.items.map(
                    (
                      run,
                    ) => (

                    <Link
                      key={
                        run.id
                      }
                      href={
                        `/projects/${id}/runs/${run.id}`
                      }
                      className="
                        rounded-2xl
                        border
                        bg-[var(--card)]
                        p-6
                        transition
                        hover:scale-[1.01]
                      "
                    >


                      <div
                        className="
                          flex
                          items-center
                          justify-between
                        "
                      >

                        <div>

                          <h3
                            className="
                              font-semibold
                              text-lg
                            "
                          >
                            Run
                          </h3>


                          <p
                            className="
                              mt-1
                              text-sm
                            "
                            style={{
                              color:
                                "var(--muted)",
                            }}
                          >
                            {run.created_at}
                          </p>


                        </div>



                        <StatusBadge
                          status={
                            run.status
                          }
                        />


                      </div>


                    </Link>

                  ))
                }


              </div>


            )
          }


        </section>


      </div>


    </main>

  );

}