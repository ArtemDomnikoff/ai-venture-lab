import {
  getProject,
} from "@/lib/projects";


import {
  getProjectRuns,
} from "@/lib/runs";


import ProjectHeader from "@/components/ProjectHeader";
import StartRunButton from "@/components/StartRunButton";
import RunList from "@/components/RunList";






export default async function ProjectPage(
  {
    params,
  }: {
    params: Promise<{
      id: string;
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






  const sortedRuns =
    [...runs.items].sort(
      (
        a,
        b,
      ) =>

        new Date(
          a.created_at,
        ).getTime()

        -

        new Date(
          b.created_at,
        ).getTime()
    );







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

        <ProjectHeader
          project={
            project
          }
        />









        {/* ACTION */}

        <section
          className="
            rounded-2xl

            border

            bg-[var(--card)]

            p-6
          "
        >

          <StartRunButton
            projectId={
              project.id
            }
          />


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
            sortedRuns.length === 0 ? (

              <div
                className="
                  rounded-2xl

                  border

                  p-8

                  text-center

                  text-[var(--muted)]
                "
              >

                No analyses yet.

              </div>


            ) : (


              <RunList
                initialRuns={
                  sortedRuns
                }
              />


            )
          }





        </section>





      </div>



    </main>

  );

}