import React from "react";
import { Routes, Route } from "react-router-dom";
import { ChatPage } from "./pages/ChatPage";
import { ReportsPage } from "./pages/ReportsPage";
import { MainLayout } from "./layouts/MainLayout";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ChatPage />} />
      <Route path="/reports" element={
        <MainLayout>
          <ReportsPage />
        </MainLayout>
      } />
    </Routes>
  );
}
