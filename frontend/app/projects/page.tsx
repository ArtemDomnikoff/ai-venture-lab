import Link from "next/link";

import {
  getProjects,
} from "@/lib/projects";


export default async function ProjectsPage() {
  const data = await getProjects();

  return (
    <main className="min-h-screen p-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold">
            Projects
          </h1>

          <p className="mt-2 text-gray-600">
            Venture analysis projects
          </p>
        </div>

        <Link
          href="/projects/new"
          className="rounded bg-black px-4 py-2 text-white"
        >
          New Project
        </Link>
      </div>


      <div className="mt-8 grid gap-4">
        {data.items.map((project) => (
          <Link
            key={project.id}
            href={`/projects/${project.id}`}
            className="rounded-lg border p-5 hover:bg-gray-50"
          >
            <h2 className="text-xl font-semibold">
              {project.name}
            </h2>

            <p className="mt-2 text-gray-600">
              {project.idea}
            </p>

            <div className="mt-3 text-sm">
              Status: {project.status}
            </div>
          </Link>
        ))}
      </div>


      {data.items.length === 0 && (
        <p className="mt-10 text-gray-500">
          No projects yet.
        </p>
      )}
    </main>
  );
}