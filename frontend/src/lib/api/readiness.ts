import { apiFetch } from './client';
import { ReadinessBundle, ExtractionDocument } from '../../types/api';

export async function getReadinessBundle(companyId: string): Promise<ReadinessBundle> {
  return apiFetch<ReadinessBundle>(`/api/v1/readiness/${companyId}/results`);
}

export async function getExtractedDocuments(companyId: string): Promise<{ documents: ExtractionDocument }> {
  return apiFetch<{ documents: ExtractionDocument }>(`/api/v1/extract/${companyId}/documents`);
}
