"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import * as api from "./auth-api";
import type { AuthState } from "./auth-types";

interface AuthContextValue {
  state: AuthState;
  refresh: () => Promise<void>;
  initialize: (password: string, confirmation: string) => Promise<void>;
  login: (password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>("loading");
  const refresh = useCallback(async () => {
    setState("loading");
    try {
      if (await api.initializationRequired()) {
        setState("setup-required");
      } else {
        setState((await api.authenticated()) ? "authenticated" : "anonymous");
      }
    } catch {
      setState("anonymous");
    }
  }, []);
  useEffect(() => {
    const pendingRefresh = window.setTimeout(() => void refresh(), 0);
    return () => window.clearTimeout(pendingRefresh);
  }, [refresh]);
  useEffect(() => {
    const expire = () => setState("anonymous");
    window.addEventListener(api.SESSION_EXPIRED_EVENT, expire);
    return () => window.removeEventListener(api.SESSION_EXPIRED_EVENT, expire);
  }, []);
  const value = useMemo<AuthContextValue>(
    () => ({
      state,
      refresh,
      initialize: async (password, confirmation) => {
        await api.initialize(password, confirmation);
        setState("authenticated");
      },
      login: async (password) => {
        await api.login(password);
        setState("authenticated");
      },
      logout: async () => {
        await api.logout();
        setState("anonymous");
      },
    }),
    [state, refresh],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}

export function useOptionalAuth(): AuthContextValue | null {
  return useContext(AuthContext);
}
