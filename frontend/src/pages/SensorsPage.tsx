import { useEffect, useState } from "react";
import dayjs from "dayjs";

import DataTable from "../components/DataTable";
import { apiClient } from "../services/api";
import { downloadCsv, downloadJsonAsPdf } from "../utils/export";

const SensorsPage = () => {
  const [sensors, setSensors] = useState<any[]>([]);

  useEffect(() => {
    const fetchSensors = async () => {
      const { data } = await apiClient.get("/sensors/");
      setSensors(data.results ?? data);
    };
    fetchSensors();
  }, []);

  const handleExportCsv = () => {
    downloadCsv(
      "sensors.csv",
      sensors.map((sensor) => ({
        name: sensor.name,
        location: sensor.location,
        serial_number: sensor.serial_number,
        threshold_min: sensor.threshold_min,
        threshold_max: sensor.threshold_max,
      })),
    );
  };

  const handleExportPdf = () => {
    void downloadJsonAsPdf("sensors.pdf", sensors);
  };

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ margin: 0 }}>Sensors</h2>
          <p style={{ margin: 0, color: "#64748b" }}>Registered cold chain nodes</p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button type="button" onClick={handleExportCsv}>
            Export CSV
          </button>
          <button type="button" onClick={handleExportPdf}>
            Export PDF
          </button>
        </div>
      </header>
      <DataTable
        columns={[
          { key: "name", label: "Name" },
          { key: "location", label: "Location" },
          { key: "serial_number", label: "Serial" },
          { key: "threshold_min", label: "Min °C" },
          { key: "threshold_max", label: "Max °C" },
          { key: "created_at", label: "Created", render: (value: unknown) => dayjs(String(value)).format("MMM D") },
        ]}
        data={sensors}
      />
    </section>
  );
};

export default SensorsPage;

