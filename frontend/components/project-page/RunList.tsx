"use client";


import {
  useState,
} from "react";


import RunCard from "@/components/project-page/RunCard";


import type {
  Run,
} from "@/types/api";



interface Props {

  initialRuns: Run[];

}





export default function RunList(
  {
    initialRuns,
  }: Props,
) {


  const [
    runs,
    setRuns,
  ] = useState<Run[]>(
    () =>
      [...initialRuns].sort(
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
      ),
  );





  function handleDelete(
    id: string,
  ) {

    setRuns(
      current =>
        current.filter(
          run =>
            run.id !== id,
        ),
    );

  }





  if(
    runs.length === 0
  ) {

    return (

      <div
        className="
          rounded-2xl
          border
          p-8
          text-center
          text-muted
        "
      >

        No analyses yet.

      </div>

    );

  }





  return (

    <div
      className="
        grid
        gap-5
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
                index + 1
              }

              onDelete={
                handleDelete
              }

            />

          ),
        )
      }

    </div>

  );

}
