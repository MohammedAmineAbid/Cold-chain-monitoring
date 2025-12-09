import { useEffect, useState } from "react";
import dayjs from "dayjs";

import DataTable from "../components/DataTable";
import { apiClient } from "../services/api";

const TicketsPage = () => {
  const [tickets, setTickets] = useState<any[]>([]);

  const loadTickets = async () => {
    const { data } = await apiClient.get("/tickets/");
    setTickets(data.results ?? data);
  };

  useEffect(() => {
    loadTickets();
  }, []);

  const updateStatus = async (ticketId: string, status: string) => {
    await apiClient.patch(`/tickets/${ticketId}/`, { status });
    loadTickets();
  };

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <header>
        <h2 style={{ margin: 0 }}>Tickets</h2>
        <p style={{ margin: 0, color: "#64748b" }}>Track remediation actions for each alert.</p>
      </header>
      <DataTable
        columns={[
          { key: "title", label: "Title" },
          { key: "priority", label: "Priority" },
          { key: "status", label: "Status" },
          { key: "created_at", label: "Opened", render: (value: unknown) => dayjs(String(value)).format("MMM D HH:mm") },
          {
            key: "id",
            label: "Actions",
            render: (_value: unknown, row: any) => (
              <div style={{ display: "flex", gap: 8 }}>
                <button type="button" onClick={() => updateStatus(row.id, "in_progress")}>
                  In Progress
                </button>
                <button type="button" onClick={() => updateStatus(row.id, "closed")}>Close</button>
              </div>
            ),
          },
        ]}
        data={tickets}
        emptyMessage="No tickets open"
      />
    </section>
  );
};

export default TicketsPage;

