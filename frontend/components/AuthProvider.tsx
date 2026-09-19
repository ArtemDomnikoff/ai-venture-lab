"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ApiError,
} from "@/lib/api";

import {
  getCurrentUser,
  login,
  logout,
  register,
} from "@/lib/auth";

import type {
  User,
} from "@/types/api";


interface AuthContextValue {
  user: User | null;
  loading: boolean;

  refreshUser: () => Promise<User | null>;

  loginUser: (
    email: string,
    password: string,
  ) => Promise<User>;

  registerUser: (
    email: string,
    password: string,
  ) => Promise<User>;

  logoutUser: () => Promise<void>;
}


const AuthContext =
  createContext<AuthContextValue | undefined>(
    undefined,
  );


export default function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] =
    useState<User | null>(null);

  const [loading, setLoading] =
    useState(true);


  const refreshUser = useCallback(
    async () => {
      try {
        const nextUser =
          await getCurrentUser();

        setUser(nextUser);

        return nextUser;
      } catch (error) {
        if (
          error instanceof ApiError
          && error.status === 401
        ) {
          setUser(null);

          return null;
        }

        console.error(
          "Failed to load current user",
          error,
        );

        return null;
      } finally {
        setLoading(false);
      }
    },
    [],
  );


  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);


  const loginUser = useCallback(
    async (
      email: string,
      password: string,
    ) => {
      const nextUser =
        await login({
          email,
          password,
        });

      setUser(nextUser);

      return nextUser;
    },
    [],
  );


  const registerUser = useCallback(
    async (
      email: string,
      password: string,
    ) => {
      const nextUser =
        await register({
          email,
          password,
        });

      setUser(nextUser);

      return nextUser;
    },
    [],
  );


  const logoutUser = useCallback(
    async () => {
      try {
        await logout();
      } finally {
        setUser(null);
      }
    },
    [],
  );


  const value = useMemo(
    () => ({
      user,
      loading,
      refreshUser,
      loginUser,
      registerUser,
      logoutUser,
    }),
    [
      user,
      loading,
      refreshUser,
      loginUser,
      registerUser,
      logoutUser,
    ],
  );


  return (
    <AuthContext.Provider
      value={value}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth(): AuthContextValue {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider",
    );
  }

  return context;
}
