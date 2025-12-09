interface StatCardProps {
  label: string;
  value: string | number;
  sublabel?: string;
}

const StatCard = ({ label, value, sublabel }: StatCardProps) => (
  <div
    style={{
      background: "#fff",
      borderRadius: 12,
      padding: "1rem",
      boxShadow: "0 10px 15px -10px rgba(15, 23, 42, 0.4)",
      minWidth: 160,
    }}
  >
    <p style={{ margin: 0, color: "#64748b", fontSize: 14 }}>{label}</p>
    <h3 style={{ margin: "0.5rem 0", fontSize: 28 }}>{value}</h3>
    {sublabel && (
      <p style={{ margin: 0, color: "#22c55e", fontSize: 12, fontWeight: 600 }}>{sublabel}</p>
    )}
  </div>
);

export default StatCard;

