"use client";

import {
  useEffect,
  useState,
} from "react";

import Link from "next/link";

import {
  usePathname,
  useRouter,
} from "next/navigation";

import {
  getProjects,
  deleteProject,
} from "@/lib/projects";

import type {
  Project,
} from "@/types/api";



function projectClass(
  active: boolean,
) {

  return [
    "relative",
    "block",
    "rounded-xl",
    "px-3",
    "py-3",
    "transition",

    active
      ? [
          "border",
          "border-[var(--border)]",
          "bg-[var(--background)]",
        ].join(" ")

      : [
          "hover:bg-[var(--background)]",
        ].join(" "),

  ].join(" ");

}





export default function ProjectSidebar() {


  const pathname =
    usePathname();


  const router =
    useRouter();




  const [
    open,
    setOpen,
  ] = useState(false);



  const [
    expanded,
    setExpanded,
  ] = useState(false);



  const [
    projects,
    setProjects,
  ] = useState<Project[]>([]);



  const [
    search,
    setSearch,
  ] = useState("");



  const [
    loading,
    setLoading,
  ] = useState(true);



  const [
    deletingId,
    setDeletingId,
  ] = useState<string | null>(
    null,
  );






  useEffect(
    () => {

      async function loadProjects() {

        try {

          const response =
            await getProjects();



          const sorted =
            [...response.items]
              .sort(
                (
                  a,
                  b,
                ) =>

                  new Date(
                    b.created_at,
                  ).getTime()

                  -

                  new Date(
                    a.created_at,
                  ).getTime()
              );


          setProjects(
            sorted,
          );


        } catch(error) {

          console.error(
            "Failed to load projects",
            error,
          );


          setProjects([]);

        } finally {

          setLoading(false);

        }

      }


      loadProjects();


    },
    [],
  );







  function toggleSidebar() {


    if(open) {

      setExpanded(false);


      setTimeout(
        () => {
          setOpen(false);
        },
        100,
      );


      return;

    }



    setOpen(true);


    setTimeout(
      () => {
        setExpanded(true);
      },
      300,
    );

  }








  async function handleDeleteProject(
    event: React.MouseEvent,
    id: string,
  ) {


    event.preventDefault();
    event.stopPropagation();



    if(
      deletingId
    ) {

      return;

    }



    setDeletingId(id);



    try {


      await deleteProject(
        id,
      );



      setProjects(
        current =>
          current.filter(
            project =>
              project.id !== id,
          ),
      );



      if(
        pathname.startsWith(
          `/projects/${id}`,
        )
      ) {

        router.push(
          "/",
        );

      }



      router.refresh();



    } catch(error) {


      console.error(
        "Failed to delete project",
        error,
      );


    } finally {


      setDeletingId(null);


    }

  }







  const filteredProjects =
    projects.filter(
      project => {

        const value =
          search
            .toLowerCase()
            .trim();



        if(!value) {

          return true;

        }



        return (

          project.name
            .toLowerCase()
            .includes(value)

          ||

          project.idea
            .toLowerCase()
            .includes(value)

        );

      },
    );







  return (

    <aside

      className={`
        flex

        h-screen

        shrink-0

        flex-col

        overflow-hidden

        border-r

        border-[var(--border)]

        bg-[var(--card)]

        transition-all

        duration-300

        ${
          open
            ? "w-72"
            : "w-14"
        }
      `}

    >



      <div

        className="
          flex
          h-14
          shrink-0
          items-center
          border-b
          border-[var(--border)]
        "

      >

        <button

          onClick={
            toggleSidebar
          }

          className="
            flex
            h-14
            w-14
            shrink-0
            items-center
            justify-center
            rounded-lg
            text-xl
            transition
            hover:bg-[var(--background)]
          "

        >

          ☰

        </button>



        {
          expanded
          &&
          (

            <span
              className="
                ml-3
                whitespace-nowrap
                font-bold
              "
            >

              AI Venture Lab

            </span>

          )
        }


      </div>







      <div

        className="
          flex-1
          overflow-y-auto
          p-3
        "

      >

        {
          expanded
          &&
          (

            <>

              <Link

                href="/"

                className="
                  mb-5
                  block
                  rounded-xl
                  bg-[var(--primary)]
                  px-4
                  py-3
                  text-center
                  text-sm
                  font-semibold
                  text-white
                  transition
                  hover:opacity-90
                "

              >

                New Project

              </Link>





              <input

                value={
                  search
                }

                onChange={
                  event =>
                    setSearch(
                      event.target.value,
                    )
                }

                placeholder="Search projects..."

                className="
                  mb-4
                  w-full
                  rounded-xl
                  border
                  border-[var(--border)]
                  bg-[var(--background)]
                  px-3
                  py-2
                  text-sm
                  outline-none
                "

              />





              <div

                className="
                  mb-3
                  px-2
                  text-xs
                  font-semibold
                  uppercase
                  text-[var(--muted)]
                "

              >

                Projects

              </div>





              {
                loading
                &&
                (

                  <div
                    className="
                      px-2
                      text-sm
                      text-[var(--muted)]
                    "
                  >

                    Loading...

                  </div>

                )
              }






              {
                !loading
                &&
                filteredProjects.length === 0
                &&
                (

                  <div
                    className="
                      px-2
                      text-sm
                      text-[var(--muted)]
                    "
                  >

                    No projects

                  </div>

                )
              }






              <div
                className="
                  space-y-2
                "
              >

                {
                  filteredProjects.map(
                    project => (

                      <div

                        key={
                          project.id
                        }

                        className="group relative"

                      >

                        <Link

                          href={
                            `/projects/${project.id}`
                          }

                          className={
                            projectClass(
                              pathname.startsWith(
                                `/projects/${project.id}`,
                              ),
                            )
                          }

                        >

                          <div

                            className="
                              truncate
                              pr-8
                              text-base
                              font-medium
                              text-[var(--foreground)]
                            "

                          >

                            {
                              project.name
                            }

                          </div>




                          <div

                            className="
                              mt-1
                              line-clamp-2
                              text-xs
                              text-[var(--muted)]
                            "

                          >

                            {
                              project.idea
                            }

                          </div>


                        </Link>





                        <button

                          onClick={
                            event =>
                              handleDeleteProject(
                                event,
                                project.id,
                              )
                          }

                          disabled={
                            deletingId === project.id
                          }

                          className="
                            absolute
                            right-2
                            top-2
                            flex
                            h-6
                            w-6
                            items-center
                            justify-center
                            rounded-md
                            text-sm
                            text-[var(--muted)]
                            opacity-0
                            transition-opacity
                            group-hover:opacity-100
                            hover:bg-red-500/10
                            hover:text-red-400
                            disabled:opacity-50
                          "

                        >

                          ×

                        </button>


                      </div>

                    )
                  )
                }


              </div>








              <div

                className="
                  mt-6
                  border-t
                  border-[var(--border)]
                  pt-3
                "

              >

                <div

                  className="
                    rounded-xl
                    px-3
                    py-2
                    text-xs
                    text-[var(--muted)]
                  "

                >

                  Multi-agent AI analysis

                </div>


              </div>



            </>

          )
        }


      </div>


    </aside>

  );

}