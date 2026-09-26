import RunPageClient from "@/components/run-page/RunPageClient";


export default async function RunPage({
  params,
}: {
  params: Promise<{
    id: string;
    runId: string;
  }>;
}) {
  const {
    id,
    runId,
  } = await params;

  return (
    <RunPageClient
      projectId={id}
      runId={runId}
    />
  );
}
