import { COMPARISON, DISCREPANCIES, QUESTIONS, SUMMARY } from "@/data/mock";

export async function downloadPDF() {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "mm", format: "a4" });

  const W = 210;
  const marginL = 18;
  const marginR = 18;
  const contentW = W - marginL - marginR;
  const date = new Date().toLocaleDateString("en-IN", { dateStyle: "long" });

  let y = 0;

  // helpers
  const gap = (n = 4) => { y += n; };
  const checkPage = (needed = 10) => {
    if (y + needed > 275) { doc.addPage(); y = 18; }
  };

  const text = (
    str: string,
    x: number,
    size = 10,
    style: "normal" | "bold" = "normal",
    color: [number, number, number] = [30, 30, 30],
  ) => {
    doc.setFontSize(size);
    doc.setFont("helvetica", style);
    doc.setTextColor(...color);
    doc.text(str, x, y);
  };

  const divider = (color: [number, number, number] = [220, 220, 225]) => {
    doc.setDrawColor(...color);
    doc.setLineWidth(0.3);
    doc.line(marginL, y, W - marginR, y);
    gap(4);
  };

  const pill = (
    label: string,
    x: number,
    pillY: number,
    bg: [number, number, number],
    fg: [number, number, number],
  ) => {
    const pad = 3;
    doc.setFontSize(8);
    const w = doc.getTextWidth(label) + pad * 2;
    doc.setFillColor(...bg);
    doc.roundedRect(x, pillY - 4, w, 5.5, 1.5, 1.5, "F");
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...fg);
    doc.text(label, x + pad, pillY);
    return w;
  };

  // ── Header bar ────────────────────────────────────────────────────────────
  doc.setFillColor(14, 97, 221);
  doc.rect(0, 0, W, 28, "F");
  y = 12;
  text("DUELENS", marginL, 16, "bold", [255, 255, 255]);
  doc.setFontSize(9);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(180, 210, 255);
  doc.text("Investor Readiness Report", marginL, y + 7);
  doc.setTextColor(180, 210, 255);
  doc.text(date, W - marginR, y + 7, { align: "right" });
  y = 36;

  // ── Company banner ────────────────────────────────────────────────────────
  doc.setFillColor(245, 247, 255);
  doc.roundedRect(marginL, y - 5, contentW, 22, 3, 3, "F");

  text("TechNova Pvt Ltd", marginL + 5, 13, "bold", [14, 30, 70]);
  y += 4;
  text("Company under review", marginL + 5, 8, "normal", [100, 110, 140]);
  y += 8;

  // Score + Status inline
  text("Consistency Score:", marginL + 5, 9, "normal", [80, 90, 120]);
  text("88%", marginL + 47, 11, "bold", [14, 97, 221]);
  text("Status:", marginL + 110, 9, "normal", [80, 90, 120]);
  pill("Investor Ready", marginL + 124, y - 1, [220, 243, 230], [22, 130, 70]);
  y += 14;

  divider();

  // ── Summary cards ─────────────────────────────────────────────────────────
  text("SUMMARY", marginL, 9, "bold", [100, 110, 140]);
  gap(6);

  const cardW = (contentW - 9) / 4;
  const tones: Record<string, { bg: [number,number,number]; fg: [number,number,number] }> = {
    verified: { bg: [220, 243, 230], fg: [22, 130, 70] },
    warning:  { bg: [255, 244, 214], fg: [160, 100, 10] },
    critical: { bg: [255, 230, 228], fg: [190, 40, 30] },
    muted:    { bg: [240, 242, 248], fg: [80, 90, 120] },
  };

  SUMMARY.forEach((s, i) => {
    const cx = marginL + i * (cardW + 3);
    const t = tones[s.tone];
    doc.setFillColor(...t.bg);
    doc.roundedRect(cx, y - 4, cardW, 18, 2, 2, "F");
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...t.fg);
    doc.text(String(s.value), cx + cardW / 2, y + 6, { align: "center" });
    doc.setFontSize(7.5);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(80, 90, 120);
    doc.text(s.label, cx + cardW / 2, y + 12, { align: "center" });
  });
  y += 22;
  divider();

  // ── Comparison table ──────────────────────────────────────────────────────
  checkPage(60);
  text("CROSS-DOCUMENT COMPARISON", marginL, 9, "bold", [100, 110, 140]);
  gap(6);

  const cols = ["Metric", "Pitch Deck", "Financials", "MIS", "Projection", "Cap Table", "Status"];
  const colW = [32, 22, 22, 18, 22, 22, 22];
  const rowH = 8;

  // header row
  doc.setFillColor(235, 238, 250);
  doc.rect(marginL, y - 5, contentW, rowH, "F");
  let cx = marginL + 2;
  cols.forEach((c, i) => {
    doc.setFontSize(7.5);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(60, 70, 110);
    doc.text(c, cx, y);
    cx += colW[i]!;
  });
  y += rowH;

  const statusColors: Record<string, { bg: [number,number,number]; fg: [number,number,number] }> = {
    Verified: { bg: [220, 243, 230], fg: [22, 130, 70] },
    Warning:  { bg: [255, 244, 214], fg: [160, 100, 10] },
    Mismatch: { bg: [255, 230, 228], fg: [190, 40, 30] },
  };

  COMPARISON.forEach((row, ri) => {
    checkPage(rowH + 2);
    if (ri % 2 === 0) {
      doc.setFillColor(250, 251, 255);
      doc.rect(marginL, y - 5, contentW, rowH, "F");
    }
    cx = marginL + 2;
    doc.setFontSize(8.5);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(20, 30, 60);
    doc.text(row.metric, cx, y);
    cx += colW[0]!;

    row.values.forEach((v, i) => {
      doc.setFont("helvetica", "normal");
      doc.setTextColor(v === "—" ? 160 : 40, v === "—" ? 165 : 50, v === "—" ? 175 : 80);
      doc.text(v, cx, y);
      cx += colW[i + 1]!;
    });

    // status pill
    const sc = statusColors[row.status] ?? statusColors["Verified"]!;
    pill(row.status, cx, y, sc.bg, sc.fg);
    y += rowH;
  });
  y += 4;
  divider();

  // ── Discrepancies ─────────────────────────────────────────────────────────
  checkPage(50);
  text("DISCREPANCIES", marginL, 9, "bold", [100, 110, 140]);
  gap(6);

  const sevColors: Record<string, { bg: [number,number,number]; fg: [number,number,number] }> = {
    High:   { bg: [255, 230, 228], fg: [190, 40, 30] },
    Medium: { bg: [255, 244, 214], fg: [160, 100, 10] },
    Low:    { bg: [240, 242, 248], fg: [80, 90, 120] },
  };

  DISCREPANCIES.forEach((d) => {
    checkPage(24);
    doc.setFillColor(248, 249, 252);
    doc.roundedRect(marginL, y - 5, contentW, 20, 2, 2, "F");

    text(d.title, marginL + 4, 10, "bold", [20, 30, 60]);
    const sc = sevColors[d.severity] ?? sevColors["Low"]!;
    pill(d.severity, W - marginR - 22, y - 1, sc.bg, sc.fg);
    y += 7;

    doc.setFontSize(8);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(80, 90, 120);
    doc.text(d.kind, marginL + 4, y);
    y += 6;

    if (d.pairs.length > 0) {
      const detail = d.pairs.map((p) => `${p.label}: ${p.value}`).join("   →   ");
      doc.setFontSize(8.5);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(40, 50, 90);
      doc.text(detail, marginL + 4, y);
    } else if (d.note) {
      doc.setFontSize(8);
      doc.setFont("helvetica", "normal");
      doc.setTextColor(100, 110, 140);
      doc.text(d.note, marginL + 4, y);
    }
    y += 10;
  });

  divider();

  // ── Questions ─────────────────────────────────────────────────────────────
  checkPage(40);
  text("AI FOLLOW-UP QUESTIONS", marginL, 9, "bold", [100, 110, 140]);
  gap(6);

  QUESTIONS.forEach((q, i) => {
    checkPage(12);
    doc.setFillColor(235, 242, 255);
    doc.roundedRect(marginL, y - 5, contentW, 10, 2, 2, "F");
    doc.setFontSize(8);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(14, 97, 221);
    doc.text(`Q${i + 1}`, marginL + 3, y);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(30, 40, 80);
    doc.text(q, marginL + 12, y);
    y += 13;
  });

  divider();

  // ── Recommendation ────────────────────────────────────────────────────────
  checkPage(20);
  text("RECOMMENDATION", marginL, 9, "bold", [100, 110, 140]);
  gap(6);
  doc.setFillColor(235, 242, 255);
  doc.roundedRect(marginL, y - 5, contentW, 14, 2, 2, "F");
  doc.setFontSize(9);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(30, 40, 80);
  const rec =
    "Clarify customer count and ownership discrepancies before proceeding with investment due diligence.";
  const recLines = doc.splitTextToSize(rec, contentW - 8) as string[];
  doc.text(recLines, marginL + 4, y);
  y += 14;

  // ── Footer ────────────────────────────────────────────────────────────────
  const pageCount = doc.getNumberOfPages();
  for (let p = 1; p <= pageCount; p++) {
    doc.setPage(p);
    doc.setFontSize(7.5);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(160, 165, 180);
    doc.text(
      "Generated by Duelens · Prototype demo · All data is illustrative",
      W / 2,
      290,
      { align: "center" },
    );
    doc.text(`Page ${p} of ${pageCount}`, W - marginR, 290, { align: "right" });
  }

  doc.save("duelens-investor-report.pdf");
}
