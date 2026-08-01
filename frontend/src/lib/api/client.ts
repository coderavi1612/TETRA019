
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(
    public message: string,
    public errors: string[] = [],
    public warnings: string[] = [],
    public request_id?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
  
  const headers = new Headers(options.headers || {});
  // Do not set Content-Type header manually if options.body is FormData
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const mergedOptions: RequestInit = {
    ...options,
    headers,
  };

  try {
    const res = await fetch(url, mergedOptions);
    if (!res.ok) {
      let errBody: { errors?: string[]; warnings?: string[]; request_id?: string } = {};
      try {
        errBody = await res.json();
      } catch {}
      const errMsg = errBody.errors?.join(', ') || `HTTP Error ${res.status}: ${res.statusText}`;
      throw new APIError(
        errMsg,
        errBody.errors || [],
        errBody.warnings || [],
        errBody.request_id
      );
    }

    const envelope = await res.json();
    console.log('[API Client Debug] Path:', path, 'Response Envelope:', envelope);
    if (
      envelope &&
      typeof envelope === 'object' &&
      'success' in envelope &&
      typeof (envelope as { success?: unknown }).success === 'boolean'
    ) {
      const apiEnv = envelope as { success: boolean; data: unknown; errors?: string[]; warnings?: string[]; request_id?: string };
      if (!apiEnv.success) {
        throw new APIError(
          apiEnv.errors?.join(', ') || 'Request returned unsuccessful status.',
          apiEnv.errors || [],
          apiEnv.warnings || [],
          apiEnv.request_id
        );
      }
      return apiEnv.data as T;
    }

    return envelope as T;
  } catch (err: unknown) {
    if (err instanceof APIError) {
      throw err;
    }
    const msg = err instanceof Error ? err.message : 'Network Fetch Error';
    throw new APIError(msg);
  }
}

export function getBaseApiUrl(): string {
  return API_BASE_URL;
}
