/**
 * Type-safe API client for SignalScore backend.
 * 
 * Uses types generated from OpenAPI spec.
 * Provides typed methods for all API endpoints.
 */

import type {
    CompanyList,
    Company,
    CompanyCreate,
    Score,
    ScoreListResponse,
    ScoreResponse,
    ScoringStatusResponse,
    ScoreRequest,
    SourceSubmissionResponse,
} from './schema';

// API base URL - uses Next.js rewrites in development
const API_BASE = '/api/v1';

/**
 * Custom error for API responses
 */
export class ApiError extends Error {
    constructor(
        public status: number,
        public statusText: string,
        public detail?: string,
    ) {
        super(detail || statusText);
        this.name = 'ApiError';
    }
}

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
    path: string,
    options: RequestInit = {},
): Promise<T> {
    const url = `${API_BASE}${path}`;

    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });

    if (!response.ok) {
        let detail: string | undefined;
        try {
            const errorBody = await response.json();
            detail = errorBody.detail;
        } catch {
            // Ignore JSON parse errors
        }
        throw new ApiError(response.status, response.statusText, detail);
    }

    return response.json();
}

/**
 * Companies API client
 */
export const companiesApi = {
    /**
     * Search companies by name or URL
     */
    async search(
        query: string,
        options?: { limit?: number; offset?: number },
    ): Promise<Company[]> {
        const params = new URLSearchParams({ q: query });
        if (options?.limit) params.set('limit', String(options.limit));
        if (options?.offset) params.set('offset', String(options.offset));

        return apiFetch<Company[]>(`/companies/search?${params}`);
    },

    /**
     * Search with pagination metadata
     */
    async searchDetailed(
        query: string,
        options?: { limit?: number; offset?: number },
    ): Promise<CompanyList> {
        const params = new URLSearchParams({ q: query });
        if (options?.limit) params.set('limit', String(options.limit));
        if (options?.offset) params.set('offset', String(options.offset));

        return apiFetch<CompanyList>(`/companies/search/detailed?${params}`);
    },

    /**
     * Get company by ID
     */
    async getById(id: number): Promise<Company> {
        return apiFetch<Company>(`/companies/${id}`);
    },

    /**
     * List all companies
     */
    async list(options?: { limit?: number; offset?: number }): Promise<Company[]> {
        const params = new URLSearchParams();
        if (options?.limit) params.set('limit', String(options.limit));
        if (options?.offset) params.set('offset', String(options.offset));

        const queryString = params.toString();
        return apiFetch<Company[]>(`/companies${queryString ? `?${queryString}` : ''}`);
    },

    /**
     * Create a new company
     */
    async create(data: CompanyCreate): Promise<Company> {
        return apiFetch<Company>('/companies', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    /**
     * Submit sources for a company
     */
    async submitSources(
        companyId: number,
        urls: string[]
    ): Promise<SourceSubmissionResponse> {
        return apiFetch<SourceSubmissionResponse>(`/companies/${companyId}/sources`, {
            method: 'POST',
            body: JSON.stringify({ urls }),
        });
    },
};

/**
 * Health check API
 */
export const healthApi = {
    /**
     * Check if backend is healthy
     */
    async check(): Promise<{ status: string }> {
        // Health endpoint is at root, not under /api/v1
        const response = await fetch('/health');
        if (!response.ok) {
            throw new ApiError(response.status, response.statusText);
        }
        return response.json();
    },
};

/**
 * Scores API client
 */
export const scoresApi = {
    /**
     * List all AI readiness scores
     */
    async list(): Promise<ScoreListResponse> {
        return apiFetch<ScoreListResponse>('/scores');
    },

    /**
     * Get score for a specific company
     */
    async get(companyName: string): Promise<ScoreResponse> {
        return apiFetch<ScoreResponse>(`/scores/${companyName}`);
    },

    /**
     * Create a new score (e.g., analyze a company)
     */
    async create(data: ScoreRequest): Promise<ScoreResponse | ScoringStatusResponse> {
        return apiFetch<ScoreResponse | ScoringStatusResponse>('/scores', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
};
