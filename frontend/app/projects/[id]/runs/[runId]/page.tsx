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

        <RunViewer
          initialRun={run}
        />

      </div>

    </main>

  );
}