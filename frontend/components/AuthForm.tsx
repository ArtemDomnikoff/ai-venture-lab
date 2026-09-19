"use client";

import {
  useState,
} from "react";

import Link from "next/link";

import {
  useRouter,
} from "next/navigation";

import {
  ApiError,
} from "@/lib/api";

import {
  useAuth,
} from "@/components/AuthProvider";


type Mode =
  | "login"
  | "register";


interface Props {
  mode: Mode;
  nextPath?: string;
}


function getSafeNextPath(
  value?: string,
): string {
  if (!value) {
    return "/";
  }

  if (!value.startsWith("/")) {
    return "/";
  }

  if (value.startsWith("//")) {
    return "/";
  }

  if (value.includes("\\")) {
    return "/";
  }

  return value;
}


export default function AuthForm({
  mode,
  nextPath,
}: Props) {
  const router = useRouter();

  const {
    loginUser,
    registerUser,
  } = useAuth();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const isLogin =
    mode === "login";

  const redirectPath =
    getSafeNextPath(nextPath);


  async function submit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (loading) {
      return;
    }

    const normalizedEmail =
      email.trim();

    if (!normalizedEmail) {
      setError(
        "Please enter your email.",
      );

      return;
    }

    if (!password) {
      setError(
        "Please enter your password.",
      );

      return;
    }

    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        await loginUser(
          normalizedEmail,
          password,
        );
      } else {
        await registerUser(
          normalizedEmail,
          password,
        );
      }

      router.replace(
        redirectPath,
      );
    } catch (error) {
      if (
        error instanceof ApiError
      ) {
        if (
          error.code ===
          "INVALID_CREDENTIALS"
        ) {
          setError(
            "Invalid email or password.",
          );
        } else if (
          error.code ===
          "EMAIL_ALREADY_REGISTERED"
        ) {
          setError(
            "An account with this email already exists.",
          );
        } else if (
          error.code ===
          "RATE_LIMIT_EXCEEDED"
        ) {
          setError(
            "Too many attempts. Please try again later.",
          );
        } else {
          setError(
            error.message,
          );
        }
      } else {
        setError(
          isLogin
            ? "Failed to sign in."
            : "Failed to create account.",
        );
      }
    } finally {
      setLoading(false);
    }
  }


  return (
    <div
      className="
        w-full
        max-w-md
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
        {isLogin
          ? "Sign in"
          : "Create account"}
      </h1>


      <p
        className="
          mt-2
          text-sm
          text-[var(--muted)]
        "
      >
        {isLogin
          ? "Continue your venture research."
          : "Get 3 free startup analyses."}
      </p>


      <form
        onSubmit={submit}
        className="
          mt-8
          space-y-5
        "
      >
        <div>
          <label
            htmlFor="email"
            className="
              mb-2
              block
              text-sm
              font-medium
            "
          >
            Email
          </label>

          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) =>
              setEmail(
                event.target.value,
              )
            }
            disabled={loading}
            required
            className="
              w-full
              rounded-xl
              border
              border-[var(--border)]
              bg-[var(--background)]
              px-4
              py-3
              outline-none
              focus:border-[var(--primary)]
              disabled:cursor-not-allowed
              disabled:opacity-60
            "
          />
        </div>


        <div>
          <label
            htmlFor="password"
            className="
              mb-2
              block
              text-sm
              font-medium
            "
          >
            Password
          </label>

          <input
            id="password"
            name="password"
            type="password"
            autoComplete={
              isLogin
                ? "current-password"
                : "new-password"
            }
            value={password}
            onChange={(event) =>
              setPassword(
                event.target.value,
              )
            }
            disabled={loading}
            minLength={8}
            maxLength={128}
            required
            className="
              w-full
              rounded-xl
              border
              border-[var(--border)]
              bg-[var(--background)]
              px-4
              py-3
              outline-none
              focus:border-[var(--primary)]
              disabled:cursor-not-allowed
              disabled:opacity-60
            "
          />
        </div>


        {error && (
          <div
            role="alert"
            aria-live="polite"
            className="
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


        <button
          type="submit"
          disabled={
            loading
            || !email.trim()
            || !password
          }
          className="
            w-full
            rounded-xl
            bg-[var(--primary)]
            px-4
            py-3
            font-semibold
            text-white
            transition
            hover:bg-[var(--primary-hover)]
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          {loading
            ? isLogin
              ? "Signing in..."
              : "Creating account..."
            : isLogin
              ? "Sign in"
              : "Create account"}
        </button>
      </form>


      <div
        className="
          mt-6
          text-center
          text-sm
          text-[var(--muted)]
        "
      >
        {isLogin
          ? (
            <>
              Don&apos;t have an account?{" "}
              <Link
                href={
                  redirectPath === "/"
                    ? "/register"
                    : `/register?next=${encodeURIComponent(redirectPath)}`
                }
                className="
                  text-[var(--primary)]
                  hover:underline
                "
              >
                Create one
              </Link>
            </>
          )
          : (
            <>
              Already have an account?{" "}
              <Link
                href={
                  redirectPath === "/"
                    ? "/login"
                    : `/login?next=${encodeURIComponent(redirectPath)}`
                }
                className="
                  text-[var(--primary)]
                  hover:underline
                "
              >
                Sign in
              </Link>
            </>
          )}
      </div>
    </div>
  );
}
