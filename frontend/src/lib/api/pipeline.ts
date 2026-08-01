import { apiFetch } from './client';
import { PipelineStatus } from '../../types/api';

export async function startPipeline(companyId: string): Promise<{ job_id: string; company_id: string; status: string }> {
  return apiFetch<{ job_id: string; company_id: string; status: string }>(`/api/v1/pipeline/${companyId}`, {
    method: 'POST',
  });
}

export async function getPipelineStatus(companyId: string, jobId?: string): Promise<PipelineStatus> {
  const query = jobId ? `?job_id=${jobId}` : '';
  return apiFetch<PipelineStatus>(`/api/v1/pipeline/${companyId}/status${query}`);
}
