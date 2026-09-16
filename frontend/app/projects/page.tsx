import Link from "next/link";

import {
  getProjects,
} from "@/lib/projects";


export default async function ProjectsPage() {

  const data = await getProjects();


  return (

    <main
      className="
        min-h-screen
        bg-[var(--background)]
        px-4
        py-8
        sm:px-8
        lg:px-12
      "
    >

      <div
        className="
          mx-auto
          max-w-6xl
        "
      >

        <div
          className="
            flex
            flex-col
            gap-6
            sm:flex-row
            sm:items-center
            sm:justify-between
          "
        >

          <div>

            <h1
              className="
                text-3xl
                font-bold
                tracking-tight
                text-[var(--foreground)]
                sm:text-4xl
              "
            >
              Projects
            </h1>


            <p
              className="
                mt-2
                text-[var(--muted)]
              "
            >
              Venture analysis projects
            </p>

          </div>



          <Link
            href="/projects/new"
            className="
              inline-flex
              items-center
              justify-center
              rounded-xl
              bg-[var(--primary)]
              px-5
              py-3
              font-medium
              text-white
              transition
              hover:bg-[var(--primary-hover)]
            "
          >
            New Project
          </Link>

        </div>



        <div
          className="
            mt-10
            grid
            gap-5
            sm:grid-cols-2
            lg:grid-cols-3
          "
        >

          {data.items.map(
            (project) => (

              <Link
                key={project.id}
                href={`/projects/${project.id}`}
                className="
                  group
                  rounded-2xl
                  border
                  border-[var(--border)]
                  bg-[var(--card)]
                  p-6
                  transition
                  hover:-translate-y-1
                  hover:shadow-lg
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

                  <h2
                    className="
                      text-xl
                      font-semibold
                      text-[var(--foreground)]
                    "
                  >
                    {project.name}
                  </h2>


                  <span
                    className="
                      rounded-full
                      bg-[var(--background)]
                      px-3
                      py-1
                      text-xs
                      font-medium
                      text-[var(--muted)]
                    "
                  >
                    {project.status}
                  </span>

                </div>



                <p
                  className="
                    mt-4
                    line-clamp-3
                    text-sm
                    leading-6
                    text-[var(--muted)]
                  "
                >
                  {project.idea}
                </p>



                <div
                  className="
                    mt-6
                    text-sm
                    text-[var(--muted)]
                  "
                >
                  Open analysis →
                </div>


              </Link>

            )
          )}

        </div>



        {data.items.length === 0 && (

          <div
            className="
              mt-10
              rounded-2xl
              border
              border-[var(--border)]
              bg-[var(--card)]
              p-8
              text-center
            "
          >

            <p
              className="
                text-[var(--muted)]
              "
            >
              No projects yet.
            </p>

          </div>

        )}

      </div>

    </main>

  );
}