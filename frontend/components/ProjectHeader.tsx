"use client";

import {
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  ApiError,
} from "@/lib/api";

import {
  updateProject,
} from "@/lib/projects";

import type {
  Project,
} from "@/types/api";


function StatusBadge({
  status,
}: {
  status: string;
}) {
  return (
    <span
      className="
        inline-flex
        rounded-full
        border
        border-[var(--border)]
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


export default function ProjectHeader({
  project,
}: {
  project: Project;
}) {
  const router = useRouter();

  const [
    editing,
    setEditing,
  ] = useState(false);

  const [
    idea,
    setIdea,
  ] = useState(project.idea);

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );


  function startEditing() {
    setError(null);
    setEditing(true);
  }


  function cancelEditing() {
    setIdea(project.idea);
    setError(null);
    setEditing(false);
  }


  async function handleSave() {
    if (saving) {
      return;
    }

    const trimmedIdea =
      idea.trim();

    if (trimmedIdea.length < 10) {
      setError(
        "The startup idea must contain at least 10 characters.",
      );

      return;
    }

    setError(null);
    setSaving(true);

    try {
      const updated =
        await updateProject(
          project.id,
          trimmedIdea,
        );

      setIdea(
        updated.idea,
      );

      setEditing(false);
    } catch (error) {
      if (
        error instanceof ApiError
        && error.status === 401
      ) {
        router.replace(
          `/login?next=/projects/${project.id}`,
        );

        return;
      }

      if (
        error instanceof ApiError
        && error.status === 404
      ) {
        setError(
          "This project could not be found.",
        );

        return;
      }

      setError(
        error instanceof ApiError
          ? error.message
          : "Failed to update project.",
      );
    } finally {
      setSaving(false);
    }
  }


  return (
    <section
      className="
        rounded-2xl
        border
        border-[var(--border)]
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
            min-w-0
            flex-1
          "
        >
          <h1
            className="
              text-4xl
              font-bold
              text-[var(--foreground)]
            "
          >
            {project.name}
          </h1>


          {editing ? (
            <textarea
              value={idea}
              onChange={(event) =>
                setIdea(
                  event.target.value,
                )
              }
              disabled={saving}
              autoFocus
              className="
                mt-4
                min-h-32
                w-full
                resize-y
                rounded-xl
                border
                border-[var(--border)]
                bg-[var(--background)]
                p-3
                text-sm
                text-[var(--foreground)]
                outline-none
                focus:border-[var(--primary)]
                disabled:cursor-not-allowed
                disabled:opacity-60
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
          )}


          {error && (
            <div
              role="alert"
              aria-live="polite"
              className="
                mt-4
                rounded-xl
                border
                border-red-500/30
                bg-red-500/10
                px-4
                py-3
                text-sm
                text-red-300
              "
            >
              {error}
            </div>
          )}


          <div
            className="
              mt-5
              flex
              gap-3
            "
          >
            {editing ? (
              <>
                <button
                  type="button"
                  onClick={
                    handleSave
                  }
                  disabled={
                    saving
                    || idea.trim().length < 10
                    || idea.trim() ===
                      project.idea.trim()
                  }
                  className="
                    rounded-xl
                    bg-[var(--primary)]
                    px-4
                    py-2
                    text-sm
                    font-semibold
                    text-white
                    transition
                    hover:bg-[var(--primary-hover)]
                    disabled:cursor-not-allowed
                    disabled:opacity-50
                  "
                >
                  {saving
                    ? "Saving..."
                    : "Save"}
                </button>


                <button
                  type="button"
                  onClick={
                    cancelEditing
                  }
                  disabled={saving}
                  className="
                    rounded-xl
                    border
                    border-[var(--border)]
                    px-4
                    py-2
                    text-sm
                    font-medium
                    transition
                    hover:bg-[var(--background)]
                    disabled:cursor-not-allowed
                    disabled:opacity-50
                  "
                >
                  Cancel
                </button>
              </>
            ) : (
              <button
                type="button"
                onClick={
                  startEditing
                }
                className="
                  rounded-xl
                  border
                  border-[var(--border)]
                  px-4
                  py-2
                  text-sm
                  font-medium
                  transition
                  hover:bg-[var(--background)]
                "
              >
                Edit
              </button>
            )}
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
