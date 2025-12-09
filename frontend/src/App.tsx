import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout.js";
import { useAuth } from "./context/AuthContext.js";
import AlertsPage from "./pages/AlertsPage.js";
import AuditLogsPage from "./pages/AuditLogsPage.js";
import DashboardPage from "./pages/DashboardPage.js";
import LoginPage from "./pages/LoginPage.js";
import SensorsPage from "./pages/SensorsPage.js";
import TicketsPage from "./pages/TicketsPage.js";

const ProtectedRoute = () => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

const App = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route element={<ProtectedRoute />}>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/sensors" element={<SensorsPage />} />
      <Route path="/alerts" element={<AlertsPage />} />
      <Route path="/tickets" element={<TicketsPage />} />
      <Route path="/audit-logs" element={<AuditLogsPage />} />
    </Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

export default App;

