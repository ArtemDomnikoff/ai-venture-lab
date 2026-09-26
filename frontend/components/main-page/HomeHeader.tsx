"use client";

import Link from "next/link";

import {
  useAuth,
} from "@/components/AuthProvider";


export default function HomeHeader() {
  const {
    user,
    loading,
  } = useAuth();

  if (loading || user) {
    return null;
  }

  return (
    <div
      className="
        absolute
        right-6
        top-6
        z-20
        flex
        items-center
        gap-2
      "
    >
      <Link
        href="/login"
        className="
          rounded-xl
          px-4
          py-2.5
          text-md
          font-medium
          text-[var(--foreground)]
          transition
          hover:bg-[var(--card)]
        "
      >
        Sign in
      </Link>

      <Link
        href="/register"
        className="
          rounded-xl
          bg-[var(--primary)]
          px-4
          py-2.5
          text-md
          font-medium
          text-white
          shadow-sm
          transition
          hover:bg-[var(--primary-hover)]
          hover:shadow-md
        "
      >
        Sign up
      </Link>
    </div>
  );
}
