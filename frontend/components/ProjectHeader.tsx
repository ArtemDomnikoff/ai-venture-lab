"use client";


import {
  useState,
} from "react";


import {
  updateProject,
} from "@/lib/projects";


import {
  useRouter,
} from "next/navigation";


import type {
  Project,
} from "@/types/api";




function StatusBadge(
  {
    status,
  }: {
    status: string;
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




export default function ProjectHeader(
  {
    project,
  }: {
    project: Project;
  },
) {


  const [
    editing,
    setEditing,
  ] = useState(false);


  const router =
  useRouter();


  const [
    idea,
    setIdea,
  ] = useState(
    project.idea,
  );



  const [
    saving,
    setSaving,
  ] = useState(false);



    async function handleSave() {
          if (saving) {
            return;
          }


          setSaving(true);


          try {

            const updated =
              await updateProject(
                project.id,
                idea,
              );


            setIdea(
              updated.idea,
            );


            setEditing(false);


            router.refresh();


          }

          catch(error) {

            console.error(
              "Failed to update project",
              error,
            );

          }

          finally {

            setSaving(false);

          }

        }




  return (

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


        <div
          className="
            flex-1
          "
        >


          <h1
            className="
              text-4xl
              font-bold
            "
          >

            {project.name}

          </h1>




          {
            editing ? (

              <textarea

                value={
                  idea
                }

                onChange={
                  event =>
                    setIdea(
                      event.target.value,
                    )
                }

                className="
                  mt-4
                  min-h-32
                  w-full
                  rounded-xl
                  border
                  border-[var(--border)]
                  bg-[var(--background)]
                  p-3
                  text-sm
                  outline-none
                "

              />

            ) : (

              <p
                className="
                  mt-4
                  leading-7
                  text-[var(--muted)]
                "
              >

                {idea}

              </p>

            )

          }





          <div
            className="
              mt-5
              flex
              gap-3
            "
          >

            {
              editing ? (

                <>

                  <button

                    onClick={
                      handleSave
                    }

                    disabled={
                      saving
                        ||
                        idea === project.idea
                    }

                    className="
                      rounded-xl
                      bg-[var(--primary)]
                      px-4
                      py-2
                      text-sm
                      font-semibold
                      text-white
                    "

                  >

                    {
                      saving
                      ? "Saving..."
                      : "Save"
                    }

                  </button>



                  <button

                      onClick={() => {

                        setIdea(
                          project.idea,
                        );

                        setEditing(false);

                      }}

                      className="
                        rounded-xl
                        border
                        px-4
                        py-2
                        text-sm
                      "

                    >

                      Cancel

                    </button>


                </>

              ) : (

                <button

                  onClick={
                    () =>
                      setEditing(true)
                  }

                  className="
                    rounded-xl
                    border
                    px-4
                    py-2
                    text-sm
                    font-medium
                  "

                >

                  Edit

                </button>

              )
            }


          </div>


        </div>




        <StatusBadge
          status={
            project.status
          }
        />


      </div>


    </section>

  );

}