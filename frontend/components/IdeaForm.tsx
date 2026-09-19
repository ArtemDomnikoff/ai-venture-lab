"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  ApiError,
} from "@/lib/api";

import {
  createProject,
  createRun,
} from "@/lib/projects";

import {
  useAuth,
} from "@/components/AuthProvider";


const IDEA_DRAFT_KEY =
  "venture-lab:idea-draft";


export default function IdeaForm() {
  const router = useRouter();

  const {
    user,
    loading: authLoading,
    refreshUser,
  } = useAuth();

  const [idea, setIdea] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const textareaRef =
    useRef<HTMLTextAreaElement>(null);


  useEffect(() => {
    try {
      const draft =
        window.sessionStorage.getItem(
          IDEA_DRAFT_KEY,
        );

      if (draft) {
        setIdea(draft);
      }
    } catch {
      // Session storage may be unavailable.
    }
  }, []);


  useEffect(() => {
    const textarea =
      textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";

    const maxHeight = 160;

    if (
      textarea.scrollHeight <= maxHeight
    ) {
      textarea.style.height =
        `${textarea.scrollHeight}px`;

      textarea.style.overflowY =
        "hidden";
    } else {
      textarea.style.height =
        `${maxHeight}px`;

      textarea.style.overflowY =
        "auto";
    }
  }, [idea]);


  function saveDraft() {
    if (!idea.trim()) {
      return;
    }

    try {
      window.sessionStorage.setItem(
        IDEA_DRAFT_KEY,
        idea,
      );
    } catch {
      // Session storage may be unavailable.
    }
  }


  function clearDraft() {
    try {
      window.sessionStorage.removeItem(
        IDEA_DRAFT_KEY,
      );
    } catch {
      // Session storage may be unavailable.
    }
  }


  function goToAuth(
    path: "login" | "register",
  ) {
    saveDraft();

    const nextPath = encodeURIComponent(
      "/",
    );

    router.push(
      `/${path}?next=${nextPath}`,
    );
  }


  async function submit() {
    if (!user) {
      goToAuth("login");
      return;
    }

    if (!idea.trim()) {
      return;
    }

    if (
      user.free_runs_remaining <= 0
    ) {
      setError(
        "You have used all free analyses.",
      );

      return;
    }

    setError(null);
    setLoading(true);

    try {
      const project =
        await createProject(
          "New Venture Analysis",
          idea,
        );

      const run =
        await createRun(
          project.id,
        );

      clearDraft();

      await refreshUser();

      router.push(
        `/projects/${project.id}/runs/${run.id}`,
      );
    } catch (error) {
      if (
        error instanceof ApiError
      ) {
        if (
          error.code ===
          "FREE_RUNS_EXHAUSTED"
        ) {
          setError(
            "You have used all free analyses.",
          );
        } else if (
          error.code ===
          "RATE_LIMIT_EXCEEDED"
        ) {
          setError(
            "Too many analysis requests. Please try again later.",
          );
        } else {
          setError(
            error.message,
          );
        }
      } else {
        setError(
          "Failed to start analysis.",
        );
      }
    } finally {
      setLoading(false);
    }
  }


  if (authLoading) {
    return (
      <div
        className="
          w-full
          max-w-2xl
        "
      >
        <div
          className="
            h-12
            w-full
            animate-pulse
            rounded-2xl
            border
            border-[var(--border)]
            bg-[var(--card)]
          "
        />

        <div
          className="
            mt-4
            h-14
            w-full
            animate-pulse
            rounded-2xl
            bg-[var(--card)]
          "
        />
      </div>
    );
  }


  return (
    <div
      className="
        w-full
        max-w-2xl
      "
    >
      <textarea
        ref={textareaRef}
        value={idea}
        onChange={(event) =>
          setIdea(
            event.target.value,
          )
        }
        placeholder={
          user
            ? "Describe your startup idea..."
            : "Describe your startup idea..."
        }
        rows={1}
        disabled={
          loading
          || (
            !!user
            && user.free_runs_remaining <= 0
          )
        }
        className="
          min-h-12
          max-h-40
          w-full
          resize-none
          overflow-hidden
          rounded-2xl
          border
          border-[var(--border)]
          bg-[var(--card)]
          px-5
          py-3
          text-xl
          leading-7
          text-[var(--foreground)]
          placeholder:text-[var(--muted)]
          outline-none
          transition-all
          duration-200
          focus:border-[var(--primary)]
          focus:ring-2
          focus:ring-[var(--primary)]
          focus:ring-opacity-30
          disabled:cursor-not-allowed
          disabled:opacity-60
        "
      />


      {!user ? (
        <>
          <button
            type="button"
            onClick={() =>
              submit()
            }
            disabled={
              !idea.trim()
              || loading
            }
            className="
              mt-4
              flex
              w-full
              items-center
              justify-center
              gap-2
              rounded-2xl
              bg-[var(--primary)]
              px-6
              py-4
              text-xl
              font-semibold
              text-white
              transition
              hover:bg-[var(--primary-hover)]
              hover:shadow-lg
              active:scale-[0.98]
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            <span>
              Sign in to analyze
            </span>
          </button>

          <div
            className="
              mt-3
              text-center
              text-sm
              text-[var(--muted)]
            "
          >
            Sign in to run the analysis.
            New accounts include 3 free analyses.
          </div>

          <div
            className="
              mt-2
              text-center
              text-xs
              text-[var(--muted)]
            "
          >
            Don't have an account?{" "}
            <button
              type="button"
              onClick={() =>
                goToAuth("register")
              }
              className="
                font-medium
                text-[var(--primary)]
                hover:underline
              "
            >
              Create one
            </button>
          </div>
        </>
      ) : (
        <>
          <button
            type="button"
            onClick={submit}
            disabled={
              loading
              || !idea.trim()
              || user.free_runs_remaining <= 0
            }
            className="
              mt-4
              w-full
              rounded-2xl
              bg-[var(--primary)]
              px-6
              py-4
              text-xl
              font-semibold
              text-white
              transition
              hover:bg-[var(--primary-hover)]
              hover:shadow-lg
              active:scale-[0.98]
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            {loading
              ? "Starting analysis..."
              : user.free_runs_remaining <= 0
                ? "No free analyses left"
                : "Analyze Idea"}
          </button>

          <div
            className="
              mt-3
              text-center
              text-sm
              text-[var(--muted)]
            "
          >
            {user.free_runs_remaining} free{" "}
            {user.free_runs_remaining === 1
              ? "analysis"
              : "analyses"}{" "}
            remaining
          </div>
        </>
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
    </div>
  );
}
