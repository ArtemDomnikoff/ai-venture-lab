import { apiFetch } from "./api";
import type { User } from "@/types/api";

export interface AuthCredentials {
  email: string;
  password: string;
}

export function getCurrentUser() {
  return apiFetch<User>("/auth/me");
}

export function register(
  credentials: AuthCredentials,
) {
  return apiFetch<User>("/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  });
}

export function login(
  credentials: AuthCredentials,
) {
  return apiFetch<User>("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  });
}

export function logout() {
  return apiFetch<void>("/auth/logout", {
    method: "POST",
  });
}
