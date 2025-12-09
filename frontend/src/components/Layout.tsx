import { NavLink, useNavigate } from "react-router-dom";
import { ReactNode } from "react";

import { useAuth } from "../context/AuthContext";

const navItems = [
  { path: "/", label: "Dashboard" },
  { path: "/sensors", label: "Sensors" },
  { path: "/alerts", label: "Alerts" },
  { path: "/tickets", label: "Tickets" },
  { path: "/audit-logs", label: "Audit Logs" },
];

const Layout = ({ children }: { children: ReactNode }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside
        style={{
          width: 220,
          background: "#0f172a",
          color: "#fff",
          padding: "1rem",
        }}
      >
        <h2>Cold Chain</h2>
        <nav style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 24 }}>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              style={({ isActive }) => ({
                padding: "0.5rem 0",
                color: isActive ? "#38bdf8" : "#e2e8f0",
                fontWeight: isActive ? 600 : 500,
              })}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <button
          type="button"
          onClick={handleLogout}
          style={{
            marginTop: "2rem",
            width: "100%",
            padding: "0.5rem",
            background: "#ef4444",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
          }}
        >
          Logout
        </button>
      </aside>
      <main style={{ flex: 1, padding: "1.5rem" }}>{children}</main>
    </div>
  );
};

export default Layout;

