import Link from "next/link";

import {
  getRun,
} from "@/lib/runs";

import RunViewer from "@/components/RunViewer";



export default async function RunPage(
  {
    params,
  }: {
    params: Promise<{
      id:string;
      runId:string;
    }>;
  },
) {


  const {
    runId,
  } = await params;



  const run =
    await getRun(runId);



  return (

    <main
      className="
        min-h-screen
        bg-[var(--background)]
        px-4
        py-8
        sm:px-8
      "
    >

      <div
        className="
          mx-auto
          max-w-6xl
        "
      >


        <Link
          href={`/projects/${run.project_id}`}
          className="
            mb-6
            inline-flex
            items-center
            gap-2

            rounded-xl

            border
            border-[var(--border)]

            bg-[var(--card)]

            px-4
            py-2

            text-sm
            font-medium

            text-[var(--foreground)]

            transition

            hover:bg-[var(--background)]
          "
        >

          ← Back to project

        </Link>



        <RunViewer
          initialRun={run}
        />


      </div>

    </main>

  );
}