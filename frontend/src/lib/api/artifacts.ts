import { getBaseApiUrl } from './client';

export function getArtifactFileUrl(companyId: string, category: string, filename: string): string {
  return `${getBaseApiUrl()}/api/v1/files/${companyId}/${category}/${filename}`;
}

export async function getRawArtifactFile<T = unknown>(companyId: string, category: string, filename: string): Promise<T> {
  const path = `/api/v1/files/${companyId}/${category}/${filename}`;
  const url = `${getBaseApiUrl()}${path}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to load file: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}
