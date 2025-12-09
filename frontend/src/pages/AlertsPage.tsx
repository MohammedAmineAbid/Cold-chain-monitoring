import { useEffect, useState } from "react";
import dayjs from "dayjs";

import DataTable from "../components/DataTable";
import { apiClient } from "../services/api";

const AlertsPage = () => {
  const [alerts, setAlerts] = useState<any[]>([]);

  const loadAlerts = async () => {
    const { data } = await apiClient.get("/alerts/");
    setAlerts(data.results ?? data);
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleAction = async (id: string, action: "acknowledge" | "resolve") => {
    await apiClient.post(`/alerts/${id}/${action}/`);
    loadAlerts();
  };

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <header>
        <h2 style={{ margin: 0 }}>Alerts</h2>
        <p style={{ margin: 0, color: "#64748b" }}>Triggered when sensors leave the 2-8°C window.</p>
      </header>
      <DataTable
        columns={[
          { key: "created_at", label: "Created", render: (value: unknown) => dayjs(String(value)).format("MMM D HH:mm") },
          { key: "sensor", label: "Sensor", render: (_value: unknown, row: any) => row.sensor?.name ?? "N/A" },
          { key: "severity", label: "Severity" },
          { key: "status", label: "Status" },
          { key: "message", label: "Message" },
          {
            key: "id",
            label: "Actions",
            render: (_value: unknown, row: any) => (
              <div style={{ display: "flex", gap: 8 }}>
                <button type="button" onClick={() => handleAction(row.id, "acknowledge")}>
                  Acknowledge
                </button>
                <button type="button" onClick={() => handleAction(row.id, "resolve")}>
                  Resolve
                </button>
              </div>
            ),
          },
        ]}
        data={alerts}
        emptyMessage="No alerts 🎉"
      />
    </section>
  );
};

export default AlertsPage;

