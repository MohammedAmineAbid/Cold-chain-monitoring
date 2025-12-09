export const downloadCsv = (filename: string, rows: Record<string, unknown>[]) => {
  if (!rows.length) return;
  const headers = Object.keys(rows[0]);
  const csv = [headers.join(","), ...rows.map((row) => headers.map((header) => row[header]).join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
};

export const downloadJsonAsPdf = async (filename: string, rows: Record<string, unknown>[]) => {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF();
  rows.slice(0, 30).forEach((row, index) => {
    doc.text(JSON.stringify(row), 10, 10 + index * 6);
  });
  doc.save(filename);
};

