"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';
import {
  PipelineStatus,
  CompanyMetadata,
  Artifact,
  ExtractionDocument,
  ReadinessBundle,
  ComparisonSummary,
  Issue
} from '../types/api';
import {
  getCompanyMetadata,
  getCompanyArtifacts,
  getRawArtifactFile,
  getReadinessBundle,
  getExtractedDocuments
} from '../lib/api';

interface DuelensDataState {
  companyId: string;
  setCompanyId: (id: string) => void;
  jobId: string;
  setJobId: (id: string) => void;
  pipelineStatus: PipelineStatus | null;
  setPipelineStatus: (status: PipelineStatus | null) => void;
  metadata: CompanyMetadata | null;
  artifacts: Artifact[];
  extractedDocs: ExtractionDocument | null;
  readinessResults: ReadinessBundle | null;
  matrixData: ComparisonSummary | null;
  issues: Issue[];
  loading: boolean;
  error: string | null;
  setError: (err: string | null) => void;
  loadAllData: (companyId: string) => Promise<void>;
  resetState: () => void;
}

const DuelensDataContext = createContext<DuelensDataState | undefined>(undefined);

export const DuelensDataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [companyId, setCompanyId] = useState<string>('zestful');
  const [jobId, setJobId] = useState<string>('');
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);
  const [metadata, setMetadata] = useState<CompanyMetadata | null>(null);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [extractedDocs, setExtractedDocs] = useState<ExtractionDocument | null>(null);
  const [readinessResults, setReadinessResults] = useState<ReadinessBundle | null>(null);
  const [matrixData, setMatrixData] = useState<ComparisonSummary | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const resetState = () => {
    setJobId('');
    setPipelineStatus(null);
    setMetadata(null);
    setArtifacts([]);
    setExtractedDocs(null);
    setReadinessResults(null);
    setMatrixData(null);
    setIssues([]);
    setError(null);
  };

  const loadAllData = async (targetCompanyId: string) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch Company metadata
      const meta = await getCompanyMetadata(targetCompanyId);
      setMetadata(meta);

      // 2. Fetch Company artifacts
      const manifest = await getCompanyArtifacts(targetCompanyId);
      setArtifacts(manifest.artifacts || []);

      // 3. Fetch Extracted documents
      const docsRes = await getExtractedDocuments(targetCompanyId);
      setExtractedDocs(docsRes.documents);

      // 4. Fetch Readiness results bundle
      const readiness = await getReadinessBundle(targetCompanyId);
      setReadinessResults(readiness);

      // 5. Fetch Verification Matrix from files
      try {
        const matrixRaw = await getRawArtifactFile<{ matrix?: Record<string, Record<string, { value: unknown; document_type: string; source_block_id?: string }>> }>(
          targetCompanyId,
          'verification',
          'comparison_matrix.json'
        );
        
        const fields = Object.entries(matrixRaw.matrix || {}).map(([fieldPath, valuesObj]) => {
          const values: Record<string, { value: unknown; source_file: string; confidence: number; extracted_at: string }> = {};
          const cells = Object.values(valuesObj);
          
          const firstVal = cells[0]?.value;
          const isConsistent = cells.every((cell) => cell.value === firstVal);
          
          cells.forEach((cell) => {
            values[cell.document_type] = {
              value: cell.value,
              source_file: cell.source_block_id || '',
              confidence: 100,
              extracted_at: ''
            };
          });
          
          return {
            field_path: fieldPath,
            description: `Reconciliation for ${fieldPath}`,
            values,
            is_consistent: isConsistent
          };
        });

        setMatrixData({ fields });
      } catch (e) {
        console.warn('Failed to load comparison_matrix.json, using fallback empty structure', e);
        setMatrixData({ fields: [] });
      }

      // 6. Fetch Verification Issues list
      try {
        const rawIssuesRes = await getRawArtifactFile<any>(
          targetCompanyId,
          'verification',
          'issues.json'
        );
        const issuesList = Array.isArray(rawIssuesRes) ? rawIssuesRes : (rawIssuesRes?.issues || []);

        const mappedIssues: Issue[] = (issuesList || []).map((issue: any) => {
          const sourceValues: Record<string, unknown> = {};
          if (issue.evidence) {
            issue.evidence.forEach((ev: { document: string; value: unknown }) => {
              sourceValues[ev.document] = ev.value;
            });
          }

          return {
            id: issue.id,
            field_path: issue.field || '',
            description: issue.description || '',
            severity: (issue.severity === 'CRITICAL' || issue.severity === 'HIGH') ? 'CRITICAL' : issue.severity === 'WARNING' ? 'WARNING' : 'NOTICE',
            classification: issue.classification || '',
            source_values: sourceValues,
            resolved: issue.resolved || false
          };
        });

        setIssues(mappedIssues);
      } catch (e) {
        console.warn('Failed to load issues.json, using fallback empty list', e);
        setIssues([]);
      }

    } catch (err: unknown) {
      console.error('Error loading company data details:', err);
      const msg = err instanceof Error ? err.message : 'An error occurred while fetching company pipeline data.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DuelensDataContext.Provider
      value={{
        companyId,
        setCompanyId,
        jobId,
        setJobId,
        pipelineStatus,
        setPipelineStatus,
        metadata,
        artifacts,
        extractedDocs,
        readinessResults,
        matrixData,
        issues,
        loading,
        error,
        setError,
        loadAllData,
        resetState
      }}
    >
      {children}
    </DuelensDataContext.Provider>
  );
};

export const useDuelensData = () => {
  const context = useContext(DuelensDataContext);
  if (context === undefined) {
    throw new Error('useDuelensData must be used within a DuelensDataProvider');
  }
  return context;
};
