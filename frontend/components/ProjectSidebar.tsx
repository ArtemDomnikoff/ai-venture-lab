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
  ApiError,
} from "@/lib/api";

import {
  deleteProject,
  getProjects,
} from "@/lib/projects";

import {
  useAuth,
} from "@/components/AuthProvider";

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
      : "hover:bg-[var(--background)]",
  ].join(" ");
}


function getAvatarLetter(
  email: string,
): string {
  return email
    .trim()
    .charAt(0)
    .toUpperCase();
}


export default function ProjectSidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const {
    user,
    loading: authLoading,
    logoutUser,
  } = useAuth();

  const userId =
  user?.id;

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    expanded,
    setExpanded,
  ] = useState(false);

  const [
    accountMenuOpen,
    setAccountMenuOpen,
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
  ] = useState<string | null>(null);


  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!userId) {
      return;
    }

    let cancelled = false;

    async function loadProjects() {
      setLoading(true);

      try {
        const response =
          await getProjects();

        if (cancelled) {
          return;
        }

        const sorted =
          [...response.items].sort(
            (a, b) =>
              new Date(
                b.created_at,
              ).getTime()
              -
              new Date(
                a.created_at,
              ).getTime(),
          );

        setProjects(sorted);
      } catch (error) {
        if (cancelled) {
          return;
        }

        if (
          error instanceof ApiError
          && error.status === 401
        ) {
          setProjects([]);
          return;
        }

        console.error(
          "Failed to load projects",
          error,
        );

        setProjects([]);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadProjects();

    return () => {
      cancelled = true;
    };
  }, [
    authLoading,
    userId,
  ]);


  function toggleSidebar() {
    setAccountMenuOpen(false);

    if (open) {
      setExpanded(false);
      setOpen(false);
      return;
    }

    setOpen(true);

    window.setTimeout(
      () => {
        setExpanded(true);
      },
      150,
    );
  }


  async function handleDeleteProject(
    event: React.MouseEvent,
    id: string,
  ) {
    event.preventDefault();
    event.stopPropagation();

    if (deletingId) {
      return;
    }

    setDeletingId(id);

    try {
      await deleteProject(id);

      setProjects(
        current =>
          current.filter(
            project =>
              project.id !== id,
          ),
      );

      if (
        pathname.startsWith(
          `/projects/${id}`,
        )
      ) {
        router.push("/");
      }
    } catch (error) {
      if (
        error instanceof ApiError
        && error.status === 401
      ) {
        router.replace(
          `/login?next=/projects/${id}`,
        );

        return;
      }

      console.error(
        "Failed to delete project",
        error,
      );
    } finally {
      setDeletingId(null);
    }
  }


  async function handleLogout() {
    setAccountMenuOpen(false);

    try {
      await logoutUser();
      router.push("/");
    } catch (error) {
      console.error(
        "Failed to logout",
        error,
      );
    }
  }


  const filteredProjects =
    projects.filter(
      project => {
        const value =
          search
            .toLowerCase()
            .trim();

        if (!value) {
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
        relative
        z-40
        flex
        h-screen
        shrink-0
        flex-col
        overflow-visible
        border-r
        border-[var(--border)]
        bg-[var(--card)]
        transition-[width]
        duration-150
        ease-in-out

        ${
          open
            ? "w-72"
            : "w-14"
        }
      `}
    >
      {/* Header */}
      <div
        className="
          flex
          h-14
          shrink-0
          items-center
          overflow-hidden
          border-b
          border-[var(--border)]
        "
      >
        <button
          onClick={toggleSidebar}
          type="button"
          aria-label="Toggle sidebar"
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

        <div
          className={`
            overflow-hidden
            whitespace-nowrap
            pl-3
            font-bold
            transition-[opacity,width]
            duration-200

            ${
              expanded
                ? "w-auto opacity-100"
                : "w-0 opacity-0"
            }
          `}
        >
          AI Venture Lab
        </div>
      </div>


      {/* Main */}
      <div
        className="
          flex
          min-h-0
          flex-1
          flex-col
          overflow-hidden
        "
      >
        {expanded && (
          <>
            {!user && !authLoading && (
              <div
                className="
                  flex-1
                  overflow-y-auto
                  p-3
                "
              >
                <div
                  className="
                    px-2
                    text-sm
                    text-[var(--muted)]
                  "
                >
                  Sign in to create and
                  manage venture analyses.
                </div>
              </div>
            )}


            {user && (
              <div
                className="
                  flex
                  min-h-0
                  flex-1
                  flex-col
                  px-2
                  py-3
                "
              >
                {/* New Project */}
                <Link
                  href="/"
                  aria-label="New project"
                  className="
                    relative
                    mb-4
                    flex
                    h-10
                    w-full
                    shrink-0
                    items-center
                    overflow-hidden
                    rounded-xl
                    bg-[var(--primary)]
                    text-sm
                    font-semibold
                    text-white
                    transition
                    hover:opacity-90
                  "
                >
                  <span
                    className="
                      absolute
                      left-0
                      flex
                      h-10
                      w-10
                      shrink-0
                      items-center
                      justify-center
                      text-xl
                      font-medium
                    "
                  >
                    +
                  </span>

                  <span
                    className="
                      whitespace-nowrap
                      pl-10
                    "
                  >
                    New Project
                  </span>
                </Link>


                <input
                  value={search}
                  onChange={event =>
                    setSearch(
                      event.target.value,
                    )
                  }
                  placeholder="Search projects..."
                  className="
                    mb-4
                    w-full
                    shrink-0
                    rounded-xl
                    border
                    border-[var(--border)]
                    bg-[var(--background)]
                    px-3
                    py-2
                    text-sm
                    outline-none
                    focus:border-[var(--primary)]
                  "
                />


                <div
                  className="
                    mb-3
                    shrink-0
                    px-2
                    text-xs
                    font-semibold
                    uppercase
                    text-[var(--muted)]
                  "
                >
                  Projects
                </div>


                <div
                  className="
                    min-h-0
                    flex-1
                    overflow-y-auto
                  "
                >
                  {loading && (
                    <div
                      className="
                        px-2
                        text-sm
                        text-[var(--muted)]
                      "
                    >
                      Loading...
                    </div>
                  )}


                  {!loading
                    && filteredProjects.length === 0
                    && (
                      <div
                        className="
                          px-2
                          text-sm
                          text-[var(--muted)]
                        "
                      >
                        No projects
                      </div>
                    )}


                  <div className="space-y-2">
                    {filteredProjects.map(
                      project => (
                        <div
                          key={project.id}
                          className="
                            group
                            relative
                          "
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
                              {project.name}
                            </div>

                            <div
                              className="
                                mt-1
                                line-clamp-2
                                text-xs
                                text-[var(--muted)]
                              "
                            >
                              {project.idea}
                            </div>
                          </Link>


                          <button
                            type="button"
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
                            aria-label={
                              `Delete ${project.name}`
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
                      ),
                    )}
                  </div>
                </div>
              </div>
            )}
          </>
        )}


        {/* Collapsed state */}
        {!expanded && user && (
          <div
            className="
              flex
              flex-1
              flex-col
              overflow-hidden
              px-2
              py-3
            "
          >
            <Link
              href="/"
              aria-label="New project"
              title="New project"
              className="
                relative
                flex
                h-10
                w-full
                shrink-0
                items-center
                overflow-hidden
                rounded-xl
                bg-[var(--primary)]
                text-white
                transition
                hover:opacity-90
              "
            >
              <span
                className="
                  absolute
                  left-0
                  flex
                  h-10
                  w-10
                  shrink-0
                  items-center
                  justify-center
                  text-xl
                  font-medium
                "
              >
                +
              </span>
            </Link>
          </div>
        )}
      </div>


      {/* Account */}
      <div
        className="
          relative
          shrink-0
          border-t
          border-[var(--border)]
          px-2
          py-2
        "
      >
        {user && (
          <>
            {accountMenuOpen && (
              <div
                className={`
                  absolute
                  bottom-full
                  z-50
                  mb-2
                  overflow-hidden
                  rounded-2xl
                  border
                  border-[var(--border)]
                  bg-[var(--card)]
                  shadow-2xl

                  ${
                    expanded
                      ? "left-0 right-0"
                      : "left-0 w-64"
                  }
                `}
              >
                <div
                  className="
                    border-b
                    border-[var(--border)]
                    p-4
                  "
                >
                  <div
                    className="
                      flex
                      items-center
                      gap-3
                    "
                  >
                    <div
                      className="
                        flex
                        h-9
                        w-9
                        shrink-0
                        items-center
                        justify-center
                        rounded-full
                        bg-[var(--primary)]
                        text-sm
                        font-semibold
                        text-white
                      "
                    >
                      {getAvatarLetter(
                        user.email,
                      )}
                    </div>

                    <div
                      className="
                        min-w-0
                      "
                    >
                      <div
                        className="
                          truncate
                          text-sm
                          font-medium
                        "
                      >
                        {user.email}
                      </div>

                      <div
                        className="
                          mt-0.5
                          text-xs
                          text-[var(--muted)]
                        "
                      >
                        {user.free_runs_remaining}{" "}
                        {user.free_runs_remaining === 1
                          ? "free analysis"
                          : "free analyses"}{" "}
                        remaining
                      </div>
                    </div>
                  </div>
                </div>


                <div className="p-2">
                  <Link
                    href="/account"
                    onClick={() =>
                      setAccountMenuOpen(false)
                    }
                    className="
                      flex
                      w-full
                      items-center
                      rounded-xl
                      px-3
                      py-2.5
                      text-sm
                      transition
                      hover:bg-[var(--background)]
                    "
                  >
                    Account
                  </Link>


                  <button
                    type="button"
                    onClick={handleLogout}
                    className="
                      mt-1
                      flex
                      w-full
                      items-center
                      rounded-xl
                      px-3
                      py-2.5
                      text-left
                      text-sm
                      text-red-400
                      transition
                      hover:bg-red-500/10
                    "
                  >
                    Sign out
                  </button>
                </div>
              </div>
            )}


            {/* Fixed avatar anchor */}
            <button
              type="button"
              onClick={() =>
                setAccountMenuOpen(
                  current => !current,
                )
              }
              aria-expanded={accountMenuOpen}
              className="
                relative
                flex
                h-10
                w-full
                items-center
                overflow-hidden
                rounded-xl
                text-left
                transition
                hover:bg-[var(--background)]
              "
            >
              <div
                className="
                  absolute
                  left-0
                  top-1/2
                  flex
                  h-9
                  w-9
                  -translate-y-1/2
                  shrink-0
                  items-center
                  justify-center
                  rounded-full
                  bg-[var(--primary)]
                  text-sm
                  font-semibold
                  text-white
                "
              >
                {getAvatarLetter(
                  user.email,
                )}
              </div>


              {expanded && (
                <>
                  <div
                    className="
                      min-w-0
                      flex-1
                      pl-12
                      pr-8
                    "
                  >
                    <div
                      className="
                        truncate
                        text-sm
                        font-medium
                      "
                    >
                      {user.email}
                    </div>

                    <div
                      className="
                        mt-0.5
                        truncate
                        text-xs
                        text-[var(--muted)]
                      "
                    >
                      {user.free_runs_remaining}{" "}
                      free analyses
                    </div>
                  </div>


                  <span
                    className="
                      absolute
                      right-2
                      shrink-0
                      text-xs
                      text-[var(--muted)]
                    "
                  >
                    ⋯
                  </span>
                </>
              )}
            </button>
          </>
        )}


        {!user && !authLoading && (
          <Link
            href="/login"
            aria-label="Sign in"
            className="
              relative
              flex
              h-10
              w-full
              items-center
              overflow-hidden
              rounded-xl
              border
              border-[var(--border)]
              bg-[var(--background)]
              text-sm
              font-medium
              transition
              hover:bg-[var(--card)]
            "
          >
            <span
              className="
                absolute
                left-0
                flex
                h-10
                w-10
                items-center
                justify-center
                text-lg
              "
            >
              ↪
            </span>

            {expanded && (
              <span
                className="
                  whitespace-nowrap
                  pl-10
                "
              >
                Sign in
              </span>
            )}
          </Link>
        )}
      </div>
    </aside>
  );
}
