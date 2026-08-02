# 🔍 DueLens — AI-Powered Data-Room Integrity & Due Diligence Engine
> **Automated Cross-Document Financial Reconciliation, Verification, and Investment Readiness Certification for Venture Capital & Private Equity.**
---
## 📌 Executive Summary
**DueLens** is an enterprise-grade AI audit platform designed to streamline startup due diligence for investors and investment committees. It ingests core fundraising data-room documents—**Pitch Decks**, **Historical Financial Statements**, **Monthly MIS Reports**, **Financial Projections**, and **Cap Tables**—and reconciles financial metrics across all documents to uncover inconsistencies, mathematical deltas, and potential red flags before investment decisions are finalized.
By combining **Google Gemini 3.1 Flash-Lite AI**, a **Deterministic Verification & Reconciliation Engine**, and **ReportLab PDF Generation**, DueLens reduces due diligence audit times from weeks to minutes while delivering structured, verifiable audit logs backed by Supabase PostgreSQL persistence.
---
## ✨ Key Capabilities & Features
### 1. 📄 Multi-Format Data-Room Intake
- Supports **PDF**, **Microsoft PowerPoint (`.pptx`)**, **Microsoft Excel (`.xlsx`)**, and **CSV** uploads.
- Parses unstructured slides, complex multi-tab workbooks, and financial tables into canonical, indexed content blocks with page, slide, sheet, and cell traceability.
### 2. 🧠 Hardened Fact Extraction Engine
- Powered by **Google Gemini 3.1 Flash-Lite**.
- Built on a **Hardened Extraction Suite** enforcing:
  - **Currency & Scale Normalization** (thousands, millions, lakhs, crores converted to base units).
  - **Period Alignment Discipline** (CY vs. FY, monthly run-rates vs. annual figures).
  - **Duplicate Value Discipline** (deduplication across slides/pages).
  - **Null Discipline** (explicit null handling vs. zero values).
  - **Source Evidence Tracing** (exact block ID and text snippet mapping for every extracted fact).
### 3. 🎯 Field Criticality Matrix
- Categorizes all extracted data points into **3 Criticality Tiers** per document type:
  - 🔴 **Mandatory Tier**: Critical red flags (e.g. ARR, Net Revenue, Burn Rate, Shareholding %, ESOP Pool).
  - 🟡 **Optional Tier**: Informational metrics (e.g. Headcount breakdown, CAC trends, Secondary transfers).
  - ⚪ **Negligible Tier**: Supporting commentary and qualitative notes.
### 4. ⚖️ Cross-Document Reconciliation Engine (12 VC Checkpoints)
- Evaluates 12 mandatory Venture Capital due diligence reconciliation rules across all 5 core documents:
  - `REV_PITCH_VS_HIST`: Pitch Deck Revenue vs. Historical Financial Statements.
  - `ARR_PITCH_VS_MIS`: ARR in Pitch Deck vs. Monthly MIS Run Rate.
  - `PROJ_REV_VS_HIST`: Year 1 Projections vs. Historical Actuals (Realism check).
  - `CAP_TOTAL_SHARES`: Sum of Cap Table shareholder shares vs. Total Issued Shares.
  - `ESOP_POOL_CONSISTENCY`: ESOP pool size across Pitch Deck and Cap Table.
  - `VALUATION_CONSISTENCY`: Post-money valuation consistency across documents.
  - `BURN_RATE_ALIGNMENT`: Net Burn Rate in MIS vs. Projections cash-flow runway.
  - `GROSS_MARGIN_SANITY`: Gross Profit Margins sanity check across periods.
  - `GROWTH_RATE_VERIFICATION`: YoY & MoM Growth Rate calculation accuracy.
  - `DEBT_LIABILITIES_MATCH`: Outstanding Debt in Financials vs. Pitch Deck Liabilities.
  - `SHAREHOLDER_OWNERSHIP_SUM`: Total ownership percentage equals exactly 100%.
  - `HISTORICAL_CASH_BALANCE`: Cash & Cash Equivalents alignment between Balance Sheet & MIS.
### 5. 🛡️ Deterministic Verification & Exception Dashboard
- Computes exact mathematical variances and assigns issue severity levels:
  - 🚨 **CRITICAL**: Significant financial discrepancies (e.g. >5% revenue delta, shareholding >100%).
  - ⚠️ **WARNING**: Moderate variance requiring founder clarification (e.g. date snapshot mismatches).
  - ℹ️ **NOTICE**: Minor rounding differences or formatting variations.
### 6. 🏆 Investment Readiness Certification
- Computes an overall **Investment Readiness Score (0–100%)** based on 4 dimension metrics:
  - **Financial Integrity**: Reconciliation completeness across financial statements.
  - **Cap Table Health**: Ownership validation and share class equity checks.
  - **Projections Realism**: Realism of projected growth relative to historical run-rates.
  - **Compliance & Consistency**: Cross-document naming, date, and unit consistency.
- Assigns a final verdict: **`INVESTOR READY`** or **`CONDITIONAL AUDIT REQUIRED`**.
### 7. 📄 Automated PDF IC Memo & Question Assembly
- Generates 3 downloadable, print-ready PDF reports using **ReportLab**:
  - `executive_summary.pdf`: One-page executive summary & investment verdict.
  - `readiness_summary.pdf`: Full readiness audit report with scores, positives, and flagged risks.
  - `follow_up_questions.pdf`: Prioritized due diligence questions for founder management meetings.
### 8. 💾 Dual Persistence Architecture
- Uploaded raw files and stage JSON outputs are synced to both local storage (`backend/app/uploads/` and `backend/app/outputs/`) and **Supabase PostgreSQL** database (`pipeline_runs` & `pipeline_outputs` tables).
- Historical audit sessions can be recalled and inspected at any time with full PDF and document downloads.
---
## 🏗️ System Architecture & Workflow Pipeline
```mermaid
flowchart TD
    A[User / Data Room] -->|Upload PDF, PPTX, XLSX, CSV| B[FastAPI Ingestion Endpoint]
    
    subgraph Stage 1: Document Intake & Parsing
        B --> C[Document Parser Orchestrator]
        C --> D[Canonical JSON Blocks with Source Tracing]
    end
    
    subgraph Stage 2: Fact Extraction & Criticality
        D --> E[Gemini 3.1 Flash-Lite AI Extractor]
        E --> F[Field Criticality Matrix Loader]
        F --> G[Extracted Fact JSONs with Evidence Snippets]
    end
    
    subgraph Stage 3: Reconciliation & Verification
        G --> H[Reconciliation Engine - 12 VC Checkpoints]
        H --> I[Deterministic Rule Engine & Variance Calculator]
        I --> J[Comparison Matrix & Issues JSON]
    end
    
    subgraph Stage 4: Readiness & Report Generation
        J --> K[Readiness Evaluator & Score Calculator]
        K --> L[ReportLab PDF Assembler Engine]
        L --> M[executive_summary.pdf / readiness_summary.pdf / follow_up_questions.pdf]
    end
    subgraph Storage Layer
        M --> N[(Supabase PostgreSQL DB & Storage)]
        G --> N
    end
    
    N --> O[Next.js 15 Interactive Audit Dashboard]
```
---
## 📂 Project Directory Structure
```
TETRA019/
├── DueLens.png                      # Official DueLens Logo
├── README.md                        # Project Overview & Guide (This File)
│
├── backend/                         # FastAPI Backend Application
│   ├── app/
│   │   ├── api/                     # REST API Endpoints (Upload, Companies, Files, Pipeline)
│   │   │   ├── upload.py            # File Upload Handler & Supabase Sync
│   │   │   ├── companies.py         # Audit History & Session Summary API
│   │   │   ├── artifacts.py         # File Download & Artifact Manifest API
│   │   │   ├── pipeline.py          # Pipeline Execution & Status Polling
│   │   │   └── extract.py           # Extracted Facts Retrieval
│   │   │
│   │   ├── core/                    # Core Database & Utilities
│   │   │   └── db.py                # PostgreSQL / Supabase CRUD & Sync Methods
│   │   │
│   │   ├── extractors/              # Fact Extraction Engine
│   │   │   ├── extractor.py         # Main FactExtractor Class
│   │   │   ├── builder.py           # Hardened Extraction Prompt Builder
│   │   │   ├── gemini.py            # Gemini API Caller & Mock Fallback
│   │   │   ├── validator.py         # Pydantic & Schema Fact Validator
│   │   │   └── criticality.py       # Field Criticality Matrix Loader
│   │   │
│   │   ├── verification/            # Verification & Reconciliation Engine
│   │   │   ├── reconciliation.py    # 12 Mandatory VC Reconciliation Checkpoints
│   │   │   └── criticality_matrix.json # Field Criticality Tiers Definition
│   │   │
│   │   ├── readiness/               # Readiness Scoring & PDF Report Engine
│   │   │   ├── orchestrator.py      # Readiness Stage Orchestrator
│   │   │   ├── pdf/                 # ReportLab PDF Generators (Summary, Executive, Questions)
│   │   │   └── prompts/v1/          # Hardened Readiness Synthesis Prompts
│   │   │
│   │   ├── config.py                # App Configuration & Settings Loader
│   │   └── main.py                  # FastAPI Application Entry Point
│   │
│   ├── uploads/                     # Local Raw File Upload Storage
│   ├── outputs/                     # Local Audit Stage JSONs & PDF Reports Storage
│   ├── requirements.txt             # Python Dependencies
│   └── .env                         # Backend Environment Variables
│
└── frontend/                        # Next.js 15 Frontend Application
    ├── app/
    │   ├── page.tsx                 # Landing Page (/)
    │   └── dashboard/page.tsx       # Main Interactive Dashboard (/dashboard)
    │
    ├── public/
    │   └── DueLens.png              # Public Static Logo Asset
    │
    ├── src/
    │   ├── components/duelens/      # DueLens UI Components
    │   │   ├── AppNavbar.tsx        # Top Navigation Header & Brand Logo
    │   │   ├── AppSidebar.tsx       # Audit Session Sidebar & Module Switcher
    │   │   ├── UploadCard.tsx       # File Upload Drag-and-Drop Card
    │   │   ├── WorkflowSection.tsx  # Landing Workflow Section
    │   │   └── views/               # Module Audit Views
    │   │       ├── IntakeView.tsx              # Document Upload & Status
    │   │       ├── ExtractionReviewView.tsx    # Extracted Metrics Inspector
    │   │       ├── ComparisonMatrixView.tsx    # Side-by-Side Metric Matrix
    │   │       ├── ExceptionsDashboardView.tsx # Flagged Issues & Deltas
    │   │       ├── FollowUpQuestionsView.tsx   # Prioritized Questions List
    │   │       ├── ReadinessSummaryView.tsx    # Score Gauge & PDF Download
    │   │       └── HistoryView.tsx             # Past Audit Session Log & Files
    │   │
    │   ├── context/
    │   │   └── DuelensDataContext.tsx          # Global Audit Context & State Provider
    │   │
    │   └── lib/api/                 # API Client Functions (Fetchers & Endpoints)
    │
    ├── package.json                 # Frontend Node Dependencies
    └── tsconfig.json                # TypeScript Configuration
```
---
## 🚀 Getting Started
### Prerequisites
- **Python**: `3.10` or higher
- **Node.js**: `18.0` or higher (with `npm` or `pnpm`)
- **Google Gemini API Key**: `GEMINI_API_KEY` (Free tier or paid tier)
- **Supabase / PostgreSQL Database** (Optional for local testing; connects via `DATABASE_URL`)
---
### 1. Backend Setup
1. **Navigate to the `backend` directory**:
   ```bash
   cd backend
   ```
2. **Create and activate a virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables**:
   Ensure `.env` exists in the `backend/` directory (see [Environment Configuration](#-environment-variables-configuration-env) below).
5. **Start the FastAPI Backend Server**:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *The backend server will run at `http://127.0.0.1:8000`.*
---
### 2. Frontend Setup
1. **Navigate to the `frontend` directory**:
   ```bash
   cd frontend
   ```
2. **Install Node dependencies**:
   ```bash
   npm install
   ```
3. **Start the Next.js Development Server**:
   ```bash
   npm run dev
   ```
   *The frontend application will run at `http://localhost:3000`.*
---
## ⚙️ Environment Variables Configuration (`.env`)
Place the `.env` file in the `backend/` directory:
| Environment Variable | Required | Description | Example / Default |
| :--- | :---: | :--- | :--- |
| `GEMINI_API_KEY` | **Yes** | Google Gemini AI API key | `AIzaSy...` |
| `GEMINI_MODEL` | No | Model version for fact extraction | `gemini-3.1-flash-lite` |
| `REASONING_PROVIDER` | No | Provider mode for reasoning stage | `gemini` or `local` |
| `DATABASE_URL` | No | PostgreSQL / Supabase connection URI | `postgresql://postgres:pass@db.supabase.co:5432/postgres` |
| `SUPABASE_URL` | No | Supabase project API URL | `https://xyz.supabase.co` |
| `SUPABASE_SECRET_KEY` | No | Supabase secret key for API access | `sb_secret_...` |
| `UPLOAD_DIR` | No | Path to store uploaded raw files | `backend/app/uploads` |
| `OUTPUT_DIR` | No | Path to store stage JSONs & PDFs | `backend/app/outputs` |
---
## 📊 Verification & Reconciliation Rule Set
The reconciliation engine checks cross-document deltas across 12 mandatory rules:
| Checkpoint Code | Rule Title | Source Documents | Verification Logic |
| :--- | :--- | :--- | :--- |
| `REV_PITCH_VS_HIST` | Revenue Consistency | Pitch Deck ↔ Historical Financials | Verifies Net Revenue matches within 2% delta margin. |
| `ARR_PITCH_VS_MIS` | ARR vs. MIS Run Rate | Pitch Deck ↔ Monthly MIS | Reconciles stated ARR against 12x Monthly Recurring Revenue. |
| `PROJ_REV_VS_HIST` | Projections Realism | Financial Projections ↔ Historicals | Flags >3x YoY growth jumps without justification. |
| `CAP_TOTAL_SHARES` | Share Count Equity | Cap Table | Verifies sum of shareholder shares equals total issued shares. |
| `ESOP_POOL_CONSISTENCY` | ESOP Pool Allocation | Cap Table ↔ Pitch Deck | Checks pre/post-money ESOP pool percentage consistency. |
| `VALUATION_CONSISTENCY` | Valuation Sanity | Pitch Deck ↔ Cap Table | Reconciles target valuation against cap table pricing. |
| `BURN_RATE_ALIGNMENT` | Burn Rate & Runway | MIS ↔ Financial Projections | Checks monthly cash burn against projected runway months. |
| `GROSS_MARGIN_SANITY` | Gross Margin Check | Financials ↔ MIS | Ensures Gross Profit Margins are consistent across periods. |
| `GROWTH_RATE_VERIFICATION` | Growth Calculation | Pitch Deck ↔ Financials | Re-calculates YoY growth % to prevent mathematical errors. |
| `DEBT_LIABILITIES_MATCH` | Outstanding Liabilities | Balance Sheet ↔ Pitch Deck | Verifies all long-term debt and liabilities are declared. |
| `SHAREHOLDER_OWNERSHIP_SUM` | 100% Equity Sum | Cap Table | Enforces exact 100.00% ownership sum constraint. |
| `HISTORICAL_CASH_BALANCE` | Cash Balance Match | Balance Sheet ↔ MIS | Reconciles ending cash balance on balance sheet vs. MIS. |
---
## 📄 Output Artifacts & Reports
For every audited company session, DueLens generates the following outputs accessible via API or UI downloads:
1. **`readiness_summary.pdf`**: Complete due diligence audit report featuring overall score gauge, dimensional breakdown, key positive highlights, and conditional risk notes.
2. **`executive_summary.pdf`**: One-page IC memo summarizing investment readiness verdict for investment committee meetings.
3. **`follow_up_questions.pdf`**: Prioritized list of follow-up questions formulated from detected cross-document inconsistencies.
4. **`comparison_matrix.json`**: Side-by-side reconciliation matrix mapping every financial metric across all 5 core document slots.
5. **`issues.json`**: List of all flagged discrepancies with mathematical deltas, severity ratings, and source block evidence snippets.
---
## 🧪 Testing & Verification
Run the automated backend test suite using `unittest` or `pytest`:
```bash
cd backend
python -m unittest discover -s app/tests
```
All test suites verify:
- Fail-fast startup validations.
- Hardened prompt suite construction.
- 12 mandatory VC reconciliation checkpoints.
- ReportLab PDF compilation.
- Supabase database sync methods.
---
## 👥 Authors & License
- **Team**: TETRA019
- **Project**: DueLens — AI-Powered Data-Room Integrity Engine
- **License**: MIT License
---
