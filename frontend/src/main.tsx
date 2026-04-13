import React from "react";
import ReactDOM from "react-dom/client";
import "katex/dist/katex.min.css";

import App from "./App";
import "./index.css";
import { BrowserRouter } from "react-router-dom";
import { AppThemeProvider } from "./themes/themeContext";

function Root() {
  return (
    <BrowserRouter>
      <AppThemeProvider>
        <App />
      </AppThemeProvider>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
