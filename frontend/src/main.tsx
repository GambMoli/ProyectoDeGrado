import React from "react";
import ReactDOM from "react-dom/client";
import { CssBaseline, ThemeProvider, useMediaQuery } from "@mui/material";
import "katex/dist/katex.min.css";

import App from "./App";
import "./index.css";
import { BrowserRouter } from "react-router-dom";
import { createAppTheme } from "./themes";

function Root() {
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");
  const theme = createAppTheme(prefersDarkMode ? "dark" : "light");

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ThemeProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
