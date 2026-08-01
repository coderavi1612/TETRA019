export interface APIResponse<T> {
  success: boolean;
  api_version: string;
  request_id: string;
  data: T;
  meta: Record<string, unknown>;
  warnings: string[];
  errors: string[];
  timestamp: string;
}

export interface PipelineStageInfo {
  name: string;
  status: 'idle' | 'running' | 'completed' | 'failed' | 'cancelled';
  duration_ms: number;
}

export interface PipelineStatus {
  job_id: string;
  company_id: string;
  status: 'ACCEPTED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'idle';
  current_stage: string;
  stages: PipelineStageInfo[];
  progress: number;
  started_at?: string;
  updated_at?: string;
  failed_stage?: string;
  error?: string;
}

export interface CompanyMetadata {
  company_id: string;
  pipeline_status: string;
  parsed: boolean;
  extracted: boolean;
  verified: boolean;
  readiness: boolean;
  documents: number;
  artifacts: number;
  latest_job: string;
  latest_status: string;
  latest_run: string;
}

export interface Artifact {
  name: string;
  category: 'parsed' | 'extracted' | 'verification' | 'readiness' | 'manifests' | 'logs';
  mime_type: string;
  size: number;
  download_url: string;
  generated_at: string;
  stage: string;
}

export interface ArtifactsManifest {
  manifest_version: string;
  pipeline_version: string;
  generated_at: string;
  company_id: string;
  artifacts: Artifact[];
}

export interface Issue {
  id: string;
  field_path: string;
  description: string;
  severity: 'CRITICAL' | 'WARNING' | 'NOTICE';
  classification: string;
  source_values: Record<string, unknown>;
  resolved: boolean;
}

export interface ComparisonCell {
  value: unknown;
  source_file: string;
  confidence: number;
  extracted_at: string;
}

export interface ComparisonRow {
  field_path: string;
  description: string;
  values: Record<string, ComparisonCell>;
  is_consistent: boolean;
}

export interface ComparisonSummary {
  fields: ComparisonRow[];
}

export interface Question {
  id: string;
  question: string;
  rationale: string;
  target_document: string;
  target_metric: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface ReadinessSummary {
  overall_readiness_score: number;
  scoring_breakdown: {
    completeness: number;
    consistency: number;
    recency: number;
    factuality: number;
  };
  overall_evaluation_narrative: string;
  key_positives: string[];
  critical_gaps: string[];
  recommendations: string[];
}

export interface ExecutiveSummary {
  company_overview: string;
  overall_readiness: string;
  top_risks: string[];
  top_strengths: string[];
  critical_issues: string[];
  immediate_actions: string[];
  investor_readiness: string;
}

export interface DownloadInfo {
  name: string;
  type: 'pdf' | 'md' | 'json';
  url: string;
}

export interface ReadinessBundle {
  summary: ReadinessSummary;
  executive: ExecutiveSummary;
  questions: Question[];
  downloads: DownloadInfo[];
  status: string;
}

export interface ExtractionDocument {
  pitch_deck?: Record<string, unknown>;
  mis?: Record<string, unknown>;
  cap_table?: Record<string, unknown>;
  financial_projections?: Record<string, unknown>;
  historical_financial_statements?: Record<string, unknown>;
  [key: string]: unknown;
}
