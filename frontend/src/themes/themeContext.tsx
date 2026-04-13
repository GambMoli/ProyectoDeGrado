import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { ThemeProvider, CssBaseline } from "@mui/material";
import { AppThemeMode, createAppTheme } from "./appTheme";


interface ThemeContextValue {
  mode: AppThemeMode;
  toggleMode: () => void;
}

const THEME_STORAGE_KEY = "theme-mode";

function getSystemThemeMode(): AppThemeMode {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return "light";
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function getStoredThemeMode(): AppThemeMode | null {
  if (typeof window === "undefined") {
    return null;
  }

  const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
  return stored === "dark" || stored === "light" ? stored : null;
}

const ThemeContext = createContext<ThemeContextValue>({
  mode: "light",
  toggleMode: () => {},
});

export function useThemeMode() {
  return useContext(ThemeContext);
}

interface AppThemeProviderProps {
  children: React.ReactNode;
}

export function AppThemeProvider({ children }: AppThemeProviderProps) {
  const [mode, setMode] = useState<AppThemeMode>(() => {
    return getStoredThemeMode() ?? getSystemThemeMode();
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const syncSystemMode = (event?: MediaQueryListEvent) => {
      if (getStoredThemeMode()) {
        return;
      }

      setMode(event?.matches ? "dark" : mediaQuery.matches ? "dark" : "light");
    };

    syncSystemMode();

    if (typeof mediaQuery.addEventListener === "function") {
      mediaQuery.addEventListener("change", syncSystemMode);

      return () => {
        mediaQuery.removeEventListener("change", syncSystemMode);
      };
    }

    mediaQuery.addListener(syncSystemMode);

    return () => {
      mediaQuery.removeListener(syncSystemMode);
    };
  }, []);

  function toggleMode() {
    setMode((prev) => {
      const next = prev === "light" ? "dark" : "light";
      window.localStorage.setItem(THEME_STORAGE_KEY, next);
      return next;
    });
  }

  const theme = useMemo(() => createAppTheme(mode), [mode]);

  return (
    <ThemeContext.Provider value={{ mode, toggleMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
}
