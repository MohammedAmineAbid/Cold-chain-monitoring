import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface ChartPoint {
  recorded_at: string;
  temperature: number;
}

const ChartCard = ({ data }: { data: ChartPoint[] }) => (
  <div
    style={{
      background: "#fff",
      borderRadius: 12,
      padding: "1rem",
      boxShadow: "0 10px 15px -10px rgba(15, 23, 42, 0.4)",
      height: 320,
    }}
  >
    <h3 style={{ marginTop: 0 }}>Last Measurements</h3>
    <ResponsiveContainer width="100%" height="85%">
      <LineChart data={data}>
        <XAxis dataKey="recorded_at" hide />
        <YAxis domain={[0, "auto"]} />
        <Tooltip />
        <Line type="monotone" dataKey="temperature" stroke="#2563eb" strokeWidth={3} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export default ChartCard;

