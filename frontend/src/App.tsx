import React from "react";
import { Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context";
import { ProtectedRoute } from "./components";
import { MainLayout } from "./layouts/MainLayout";
import { ChatPage } from "./pages/ChatPage";
import { LoginPage } from "./pages/LoginPage";
import { ReportsPage } from "./pages/ReportsPage";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute allowedRoles={["teacher"]}>
              <MainLayout>
                <ReportsPage />
              </MainLayout>
            </ProtectedRoute>

          }
        />
      </Routes>
    </AuthProvider>
  );
}
