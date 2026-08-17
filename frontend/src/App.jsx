import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import ListingsPage from "./pages/ListingsPage";
import PropertyFormPage from "./pages/PropertyFormPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/listings" element={<ListingsPage />} />
          <Route path="/properties/new" element={<PropertyFormPage />} />
        </Route>

        <Route path="/" element={<Navigate to="/listings" replace />} />
        <Route path="*" element={<Navigate to="/listings" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
