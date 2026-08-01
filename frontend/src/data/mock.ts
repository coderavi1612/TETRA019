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
  { metric: "Revenue (LTM)", values: ["$12.4M", "$12.38M", "$12.38M", "$15.0M", "—"], status: "Verified" },
  { metric: "Customer Count", values: ["420+", "—", "428", "550", "—"], status: "Mismatch" },
  { metric: "Cash Balance", values: ["$4.21M", "$4.21M", "$4.20M", "$18.5M", "—"], status: "Warning" },
  { metric: "Founder Ownership", values: ["45%", "—", "—", "—", "44.82%"], status: "Mismatch" },
  { metric: "Gross Margin", values: ["72%", "71.4%", "71.8%", "75%", "—"], status: "Warning" },
  { metric: "Growth Rate (YoY)", values: ["115%", "—", "112.5%", "140%", "—"], status: "Mismatch" },
];

export const DISCREPANCIES = [
  {
    id: "INV-204",
    title: "Customer Count Mismatch",
    kind: "Verified Mismatch",
    severity: "High" as const,
    pairs: [
      { label: "Pitch Deck", value: "420+" },
      { label: "MIS Report", value: "428" },
    ],
    note: "Pitch deck rounds down customer count while MIS lists active accounts at 428.",
  },
  {
    id: "INV-205",
    title: "Cash Balance Variance",
    kind: "Unresolved Inconsistency",
    severity: "Medium" as const,
    pairs: [
      { label: "Audited Financials", value: "$4.21M" },
      { label: "Bank Reconciliation", value: "$4.20M" },
    ],
    note: "$10k variance due to end-of-month uncleared transactions.",
  },
  {
    id: "INV-206",
    title: "Growth Rate Discrepancy",
    kind: "Verified Mismatch",
    severity: "High" as const,
    pairs: [
      { label: "Pitch Deck", value: "115%" },
      { label: "MIS (Calculated)", value: "112.5%" },
    ],
    note: "Deck presents annualized Q4 rate instead of full fiscal year compound growth rate.",
  },
  {
    id: "INV-207",
    title: "Cap Table Dilution Variance",
    kind: "Verified Mismatch",
    severity: "Medium" as const,
    pairs: [
      { label: "Pitch Deck", value: "45.0%" },
      { label: "Cap Table", value: "44.82%" },
    ],
    note: "Unallocated ESOP pool of 0.18% causes minor discrepancy in founder equity calculation.",
  },
  {
    id: "INV-208",
    title: "Runway Projections Missing",
    kind: "Missing Information",
    severity: "Low" as const,
    pairs: [],
    note: "Projections sheet omits explicit monthly burn rate breakdown for Q4 2026.",
  },
];

export const QUESTIONS = [
  {
    id: "Q-101",
    category: "Financial Performance",
    priority: "Urgent" as const,
    question: "Can management clarify the 2.5% discrepancy in YoY Growth Rate between the Pitch Deck (115%) and the monthly MIS (112.5%)?",
    context: "The investor presentation rounds up YoY growth. MIS transactional data shows 112.5% actual growth.",
    suggestedAnswer: "The Pitch Deck figure represents the Q4 annualized run-rate growth, whereas the MIS reflects the full 12-month trailing actuals.",
  },
  {
    id: "Q-102",
    category: "Cap Table & Equity",
    priority: "High" as const,
    question: "What accounts for the 0.18% founder share variance between the Pitch Deck (45%) and Cap Table (44.82%)?",
    context: "Cap table lists 44.82% founder equity after accounting for unallocated ESOP pool reserved under Series A terms.",
    suggestedAnswer: "The 0.18% difference is held in the unissued option pool. Post-funding, founder stake snaps to 44.82%.",
  },
  {
    id: "Q-103",
    category: "Operational Metrics",
    priority: "Normal" as const,
    question: "Are the 8 additional active customers in the MIS included in the Q1 ARR calculations?",
    context: "MIS lists 428 active accounts versus 420 in the pitch deck deck snapshot.",
    suggestedAnswer: "Yes, the 8 customers onboarded in the final week of March were included in MIS after deck publication.",
  },
];

export const EXTRACTION_ROWS = [
  {
    kpi: "Revenue (LTM)",
    pitchDeck: { val: "$12.4M", conf: 98 },
    financials: { val: "$12,382,410", conf: 99 },
    mis: { val: "$12.38M", conf: 96 },
    projections: { val: "—", conf: 0 },
    capTable: { val: "—", conf: 0 },
    status: "Verified",
  },
  {
    kpi: "Gross Margin",
    pitchDeck: { val: "72%", conf: 92 },
    financials: { val: "71.4%", conf: 82, warning: true },
    mis: { val: "71.8%", conf: 89 },
    projections: { val: "—", conf: 0 },
    capTable: { val: "—", conf: 0 },
    status: "Warning",
  },
  {
    kpi: "Customer Count",
    pitchDeck: { val: "420+", conf: 94 },
    financials: { val: "—", conf: 0 },
    mis: { val: "428", conf: 97 },
    projections: { val: "550 (E)", conf: 91 },
    capTable: { val: "—", conf: 0 },
    status: "Mismatch",
  },
  {
    kpi: "Cash Balance",
    pitchDeck: { val: "—", conf: 0 },
    financials: { val: "$4,210,000", conf: 100 },
    mis: { val: "$4.2M", conf: 95 },
    projections: { val: "$18.5M (PF)", conf: 88 },
    capTable: { val: "—", conf: 0 },
    status: "Verified",
  },
  {
    kpi: "Growth Rate (YoY)",
    pitchDeck: { val: "115%", conf: 92 },
    financials: { val: "—", conf: 0 },
    mis: { val: "112.5%", conf: 76, warning: true },
    projections: { val: "140%", conf: 86 },
    capTable: { val: "—", conf: 0 },
    status: "Mismatch",
  },
  {
    kpi: "Founder Ownership %",
    pitchDeck: { val: "45%", conf: 88 },
    financials: { val: "—", conf: 0 },
    mis: { val: "—", conf: 0 },
    projections: { val: "—", conf: 0 },
    capTable: { val: "44.82%", conf: 81, warning: true },
    status: "Mismatch",
  },
];

export const MATRIX_FULL_DATA = [
  {
    metric: "Total Revenue (Q1)",
    trialBalance: "$4,250,000.00",
    bankStatement: "$4,248,500.00",
    glExtract: "$4,250,000.00",
    taxDoc: "$4,250,000.00",
    auditChecklist: "$4,250,000.00",
    status: "Mismatch",
    highlight: true,
  },
  {
    metric: "Total Assets (Current)",
    trialBalance: "$12,400,000.00",
    bankStatement: "$12,400,000.00",
    glExtract: "Missing",
    taxDoc: "$12,400,000.00",
    auditChecklist: "$12,400,000.00",
    status: "Missing",
    highlight: false,
  },
  {
    metric: "Payroll Expenses",
    trialBalance: "$840,000.00",
    bankStatement: "$840,000.00",
    glExtract: "$842,100.00",
    taxDoc: "$840,000.00",
    auditChecklist: "$840,000.00",
    status: "Unresolved",
    highlight: false,
  },
  {
    metric: "Active Customers",
    trialBalance: "452",
    bankStatement: "452",
    glExtract: "418",
    taxDoc: "452",
    auditChecklist: "452",
    status: "Mismatch",
    highlight: false,
  },
  {
    metric: "Accounts Receivable",
    trialBalance: "$1,224,900.00",
    bankStatement: "$1,224,900.00",
    glExtract: "$1,224,900.00",
    taxDoc: "$1,190,000.00",
    auditChecklist: "$1,224,900.00",
    status: "Mismatch",
    highlight: false,
  },
];
