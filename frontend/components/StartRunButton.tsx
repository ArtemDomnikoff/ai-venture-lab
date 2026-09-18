"use client";


import {
  useState,
} from "react";


import {
  useRouter,
} from "next/navigation";


import {
  createRun,
} from "@/lib/projects";



export default function StartRunButton(
  {
    projectId,
  }: {
    projectId: string;
  },
) {


  const router =
    useRouter();


  const [
    loading,
    setLoading,
  ] = useState(false);



  async function handleStart() {

    if (loading) {
      return;
    }


    setLoading(true);


    try {

      const run =
        await createRun(
          projectId,
        );


      router.push(
        `/projects/${projectId}/runs/${run.id}`,
      );


    }

    catch(error) {

      console.error(
        "Failed to create run",
        error,
      );


      setLoading(false);

    }

  }




  return (

    <button

      onClick={
        handleStart
      }

      disabled={
        loading
      }

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

        disabled:opacity-50
      "

    >

      {
        loading
          ? "Starting..."
          : "Start new analysis"
      }

    </button>

  );

}