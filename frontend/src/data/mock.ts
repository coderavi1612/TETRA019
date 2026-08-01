export const DOC_TYPES = [
  "Pitch Deck",
  "Historical Financial Statements",
  "Monthly MIS",
  "Financial Projections",
  "Cap Table",
  "Unknown",
] as const;

export type DocType = (typeof DOC_TYPES)[number];

export type Classified = {
  file: string;
  type: DocType;
  confidence: number;
  status: string;
};

export const MOCK_FILES = [
  "PitchDeck.pdf",
  "FinancialStatements.pdf",
  "MIS.xlsx",
  "FinancialProjection.xlsx",
  "CapTable.csv",
];

export const CLASSIFICATION: Classified[] = [
  { file: "PitchDeck.pdf", type: "Pitch Deck", confidence: 99, status: "Verified" },
  {
    file: "FinancialStatements.pdf",
    type: "Historical Financial Statements",
    confidence: 98,
    status: "Verified",
  },
  { file: "MIS.xlsx", type: "Monthly MIS", confidence: 97, status: "Verified" },
  {
    file: "FinancialProjection.xlsx",
    type: "Financial Projections",
    confidence: 95,
    status: "Verified",
  },
  { file: "CapTable.csv", type: "Cap Table", confidence: 100, status: "Verified" },
];

export const CLASSIFY_MESSAGES = [
  "Reading filenames...",
  "Inspecting document contents...",
  "Matching document patterns...",
  "Classifying document types...",
  "Classification complete.",
];

export const PROCESS_MESSAGES = [
  "Extracting financial metrics",
  "Normalizing revenue",
  "Checking customer metrics",
  "Comparing ownership",
  "Validating financial consistency",
  "Generating investor report",
];

export const SUMMARY = [
  { label: "Verified Matches", value: 24, tone: "verified" as const },
  { label: "Warnings", value: 4, tone: "warning" as const },
  { label: "Critical Issues", value: 2, tone: "critical" as const },
  { label: "Missing Information", value: 3, tone: "muted" as const },
];

export type RowStatus = "Verified" | "Mismatch" | "Warning";

export const COMPARISON: {
  metric: string;
  values: string[];
  status: RowStatus;
}[] = [
  { metric: "Revenue", values: ["₹2 Cr", "₹2 Cr", "₹2 Cr", "₹2 Cr", "—"], status: "Verified" },
  { metric: "Customer Count", values: ["500", "—", "420", "600", "—"], status: "Mismatch" },
  { metric: "Cash Balance", values: ["₹90L", "₹90L", "₹85L", "₹80L", "—"], status: "Warning" },
  { metric: "Founder Ownership", values: ["70%", "—", "—", "—", "62%"], status: "Mismatch" },
  { metric: "Funding Raised", values: ["₹5Cr", "₹5Cr", "—", "—", "₹5Cr"], status: "Verified" },
];

export const DISCREPANCIES = [
  {
    title: "Customer Count",
    kind: "Verified Mismatch",
    severity: "High" as const,
    pairs: [
      { label: "Pitch Deck", value: "500" },
      { label: "MIS", value: "420" },
    ],
    note: "",
  },
  {
    title: "Cash Balance",
    kind: "Unresolved Inconsistency",
    severity: "Medium" as const,
    pairs: [],
    note: "Different reporting dates detected.",
  },
  {
    title: "Runway",
    kind: "Missing Information",
    severity: "Low" as const,
    pairs: [],
    note: "Projection document does not contain runway.",
  },
];

export const QUESTIONS = [
  "Customer count differs between Pitch Deck and MIS.",
  "Revenue growth assumptions appear aggressive.",
  "Founder ownership differs from Cap Table.",
];
