/**
 * Auto-generated TypeScript types from backend OpenAPI spec.
 * 
 * Regenerate with: npm run generate-client
 * Requires backend running at http://localhost:8000
 * 
 * This is a placeholder - run generation after backend is running.
 */

export interface paths {
    "/health": {
        get: {
            responses: {
                200: {
                    content: {
                        "application/json": {
                            status: string;
                        };
                    };
                };
            };
        };
    };
    "/api/v1/ping": {
        get: {
            responses: {
                200: {
                    content: {
                        "application/json": {
                            message: string;
                        };
                    };
                };
            };
        };
    };
    "/api/v1/companies/search": {
        get: {
            parameters: {
                query: {
                    q: string;
                    limit?: number;
                    offset?: number;
                };
            };
            responses: {
                200: {
                    content: {
                        "application/json": components["schemas"]["CompanyRead"][];
                    };
                };
            };
        };
    };
    "/api/v1/companies/{company_id}": {
        get: {
            parameters: {
                path: {
                    company_id: number;
                };
            };
            responses: {
                200: {
                    content: {
                        "application/json": components["schemas"]["CompanyRead"];
                    };
                };
                404: {
                    content: {
                        "application/json": {
                            detail: string;
                        };
                    };
                };
            };
        };
    };
    "/api/v1/companies": {
        get: {
            parameters: {
                query?: {
                    limit?: number;
                    offset?: number;
                };
            };
            responses: {
                200: {
                    content: {
                        "application/json": components["schemas"]["CompanyRead"][];
                    };
                };
            };
        };
        post: {
            requestBody: {
                content: {
                    "application/json": components["schemas"]["CompanyCreate"];
                };
            };
            responses: {
                201: {
                    content: {
                        "application/json": components["schemas"]["CompanyRead"];
                    };
                };
                409: {
                    content: {
                        "application/json": {
                            detail: string;
                        };
                    };
                };
            };
        };
    };
}

export interface components {
    schemas: {
        CompanyRead: {
            id: number;
            name: string;
            domain: string | null;
            url: string | null;
            createdAt: string;
            updatedAt: string;
        };
        CompanyCreate: {
            name: string;
            url?: string | null;
        };
        CompanyList: {
            items: components["schemas"]["CompanyRead"][];
            total: number;
        };
        SignalResponse: {
            ai_keywords: number;
            agentic_signals: number;
            tool_stack: string[];
            non_eng_ai_roles: number;
            ai_in_it_signals: number;
            has_ai_platform_team: boolean;
            jobs_analyzed: number;
            marketing_only: boolean;
            source_attribution: Record<string, string[]>;
            confidence_score: number;
        };
        ComponentScoresResponse: {
            ai_keywords: number;
            agentic_signals: number;
            tool_stack: number;
            non_eng_ai: number;
            ai_in_it: number;
        };
        SourceResponse: {
            url: string;
            source_type: string;
        };
        ScoreResponse: {
            status: "completed";
            company_id?: number;
            company_name: string;
            careers_url?: string | null;
            score: number;
            category: "high" | "medium_high" | "medium_low" | "low" | "transformational" | "no_signal";
            category_label: string;
            signals: components["schemas"]["SignalResponse"];
            component_scores: components["schemas"]["ComponentScoresResponse"];
            evidence: string[];
            sources?: components["schemas"]["SourceResponse"][];
            scored_at?: string | null;
        };
        ScoringStatusResponse: {
            status: "processing" | "completed" | "failed";
            message: string;
            job_id?: string;
            company_name?: string | null;
            careers_url?: string | null;
            error?: string | null;
        };
        ScoreListResponse: {
            companies: components["schemas"]["ScoreResponse"][];
            count: number;
        };
        ScoreRequest: {
            url: string;
        };
        CompanySourceSubmission: {
            urls: string[];
        };
        SourceSubmissionResponse: {
            message: string;
            verified_count: number;
            pending_count: number;
            status: "processing" | "queued";
        };
    };
}

// Convenience type exports
export type Company = components["schemas"]["CompanyRead"];
export type CompanyCreate = components["schemas"]["CompanyCreate"];
export type CompanyList = components["schemas"]["CompanyList"];
export type Score = components["schemas"]["ScoreResponse"];
export type ScoreResponse = components["schemas"]["ScoreResponse"];
export type ScoreListResponse = components["schemas"]["ScoreListResponse"];
export type ScoringStatusResponse = components["schemas"]["ScoringStatusResponse"];
export type ScoreRequest = components["schemas"]["ScoreRequest"];
export type SourceSubmissionResponse = components["schemas"]["SourceSubmissionResponse"];
