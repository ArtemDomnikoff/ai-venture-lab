"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  useAuth,
} from "@/components/AuthProvider";


export default function AccountPage() {
  const router = useRouter();

  const {
    user,
    loading,
    logoutUser,
  } = useAuth();

  const [
    logoutLoading,
    setLogoutLoading,
  ] = useState(false);


  useEffect(() => {
    if (!loading && !user) {
      router.replace(
        "/login?next=/account",
      );
    }
  }, [
    loading,
    router,
    user,
  ]);


  if (
    loading
    || !user
  ) {
    return (
      <main className="px-6 py-10">
        <div
          className="
            text-sm
            text-[var(--muted)]
          "
        >
          Loading...
        </div>
      </main>
    );
  }


  async function handleLogout() {
    if (logoutLoading) {
      return;
    }

    setLogoutLoading(true);

    try {
      await logoutUser();
    } finally {
      router.replace("/");
    }
  }


  return (
    <main
      className="
        min-h-screen
        px-6
        py-10
      "
    >
      <div
        className="
          mx-auto
          max-w-3xl
        "
      >
        <section
          className="
            rounded-2xl
            border
            border-[var(--border)]
            bg-[var(--card)]
            p-8
          "
        >
          <h1
            className="
              text-3xl
              font-bold
            "
          >
            Account
          </h1>


          <div className="mt-6 space-y-4">
            <div>
              <div
                className="
                  text-xs
                  font-semibold
                  uppercase
                  text-[var(--muted)]
                "
              >
                Email
              </div>

              <div className="mt-1">
                {user.email}
              </div>
            </div>


            <div>
              <div
                className="
                  text-xs
                  font-semibold
                  uppercase
                  text-[var(--muted)]
                "
              >
                Free analyses remaining
              </div>

              <div
                className="
                  mt-1
                  text-2xl
                  font-bold
                "
              >
                {user.free_runs_remaining}
              </div>
            </div>
          </div>


          <button
            type="button"
            onClick={handleLogout}
            disabled={logoutLoading}
            className="
              mt-8
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
            {logoutLoading
              ? "Signing out..."
              : "Sign out"}
          </button>
        </section>
      </div>
    </main>
  );
}
