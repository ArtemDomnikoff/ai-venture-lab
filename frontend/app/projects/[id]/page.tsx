import ProjectPageClient from "@/components/project-page/ProjectPageClient";

export default async function ProjectPage({
  params,
}: {
  params: Promise<{
    id: string;
  }>;
}) {
  const { id } = await params;

  return (
    <ProjectPageClient
      projectId={id}
    />
  );
}
