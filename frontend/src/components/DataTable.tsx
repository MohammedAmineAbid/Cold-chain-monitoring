import { ReactNode } from "react";

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: T[keyof T], row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  emptyMessage?: string;
}

const DataTable = <T extends Record<string, unknown>>({
  columns,
  data,
  emptyMessage = "No records available",
}: DataTableProps<T>) => (
  <div style={{ overflowX: "auto", background: "#fff", borderRadius: 12, boxShadow: "0 10px 15px -10px rgba(15, 23, 42, 0.4)" }}>
    <table style={{ borderCollapse: "collapse", width: "100%" }}>
      <thead>
        <tr>
          {columns.map((column) => (
            <th key={String(column.key)} style={{ textAlign: "left", padding: "0.75rem", borderBottom: "1px solid #e2e8f0" }}>
              {column.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.length === 0 ? (
          <tr>
            <td colSpan={columns.length} style={{ padding: "1rem", textAlign: "center", color: "#94a3b8" }}>
              {emptyMessage}
            </td>
          </tr>
        ) : (
          data.map((row, index) => (
            <tr key={index}>
              {columns.map((column) => (
                <td key={String(column.key)} style={{ padding: "0.75rem", borderBottom: "1px solid #e2e8f0" }}>
                  {column.render ? column.render(row[column.key], row) : (row[column.key] as ReactNode)}
                </td>
              ))}
            </tr>
          ))
        )}
      </tbody>
    </table>
  </div>
);

export default DataTable;

