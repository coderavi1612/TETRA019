import { apiFetch } from './client';
import { CompanyMetadata, ArtifactsManifest, CompanyRunSummary } from '../../types/api';

export async function getCompanyMetadata(companyId: string): Promise<CompanyMetadata> {
  return apiFetch<CompanyMetadata>(`/api/v1/companies/${companyId}`);
}

export async function getCompanyArtifacts(companyId: string): Promise<ArtifactsManifest> {
  return apiFetch<ArtifactsManifest>(`/api/v1/companies/${companyId}/artifacts`);
}

export async function listAllCompanies(): Promise<CompanyRunSummary[]> {
  return apiFetch<CompanyRunSummary[]>('/api/v1/companies');
}

