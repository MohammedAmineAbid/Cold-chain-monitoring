import { useEffect, useState } from "react";
import dayjs from "dayjs";

import DataTable from "../components/DataTable";
import { apiClient } from "../services/api";

const AuditLogsPage = () => {
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      const { data } = await apiClient.get("/audit-logs/");
      setLogs(data.results ?? data);
    };
    load();
  }, []);

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <header>
        <h2 style={{ margin: 0 }}>Audit Log</h2>
        <p style={{ margin: 0, color: "#64748b" }}>Every backend action is recorded for compliance.</p>
      </header>
      <DataTable
        columns={[
          { key: "created_at", label: "Time", render: (value: unknown) => dayjs(String(value)).format("MMM D HH:mm:ss") },
          { key: "action", label: "Action" },
          { key: "actor", label: "Actor", render: (_value: unknown, row: any) => row.actor?.username ?? "system" },
          { key: "target_model", label: "Target" },
        ]}
        data={logs}
        emptyMessage="No audits yet"
      />
    </section>
  );
};

export default AuditLogsPage;

