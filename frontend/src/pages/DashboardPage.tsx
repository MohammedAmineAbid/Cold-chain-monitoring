import { useEffect, useMemo, useState } from "react";
import dayjs from "dayjs";

import ChartCard from "../components/ChartCard";
import DataTable from "../components/DataTable";
import StatCard from "../components/StatCard";
import { fetchDashboard } from "../services/api";

const DashboardPage = () => {
  const [data, setData] = useState<any>({
    measurements: [],
    alerts: [],
    tickets: [],
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      try {
        const dashboard = await fetchDashboard();
        setData(dashboard);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const chartData = useMemo(
    () =>
      data.measurements.slice(0, 20).map((measurement: any) => ({
        recorded_at: dayjs(measurement.recorded_at).format("HH:mm"),
        temperature: Number(measurement.temperature),
      })),
    [data.measurements],
  );

  if (isLoading) {
    return <p>Loading dashboard...</p>;
  }

  const todayMeasurementCount = data.measurements.filter((measurement: any) =>
    dayjs(measurement.recorded_at).isSame(dayjs(), "day"),
  ).length;
  const todayAlerts = data.alerts.filter((alert: any) =>
    dayjs(alert.created_at).isSame(dayjs(), "day"),
  ).length;
  const openTickets = data.tickets.filter((ticket: any) => ticket.status !== "closed").length;
  const lastAlert = data.alerts[0];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <section style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <StatCard label="Today Measurements" value={todayMeasurementCount} />
        <StatCard label="Alerts (24h)" value={todayAlerts} />
        <StatCard label="Open Tickets" value={openTickets} />
        {lastAlert && (
          <StatCard
            label="Last Alert"
            value={dayjs(lastAlert.created_at).format("HH:mm A")}
            sublabel={lastAlert.sensor?.name}
          />
        )}
      </section>
      <ChartCard data={chartData} />
      <section style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1rem" }}>
        <DataTable
          columns={[
            { key: "recorded_at", label: "Timestamp", render: (value: unknown) => dayjs(String(value)).format("MMM D HH:mm") },
            { key: "sensor", label: "Sensor", render: (_value: unknown, row: any) => row.sensor?.name ?? row.sensor },
            { key: "temperature", label: "Temp (°C)" },
            { key: "humidity", label: "Humidity (%)" },
            { key: "status", label: "Status" },
          ]}
          data={data.measurements.slice(0, 8)}
          emptyMessage="No measurements yet"
        />
      </section>
    </div>
  );
};

export default DashboardPage;

