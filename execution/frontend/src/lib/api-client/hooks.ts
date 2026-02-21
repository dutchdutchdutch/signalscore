/**
 * React hooks for SignalScore API.
 * 
 * Provides easy-to-use hooks for fetching and mutating data.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { companiesApi, ApiError } from '@/lib/api-client';
import type { Company } from '@/lib/api-client/schema';

/**
 * Hook for searching companies
 */
export function useCompanySearch(query: string, debounceMs = 300) {
    const [results, setResults] = useState<Company[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Don't search for empty queries
        if (!query.trim()) {
            setResults([]);
            setError(null);
            return;
        }

        // Debounce the search
        const timeoutId = setTimeout(async () => {
            setLoading(true);
            setError(null);

            try {
                const companies = await companiesApi.search(query);
                setResults(companies);
            } catch (err) {
                if (err instanceof ApiError) {
                    setError(err.detail || err.message);
                } else {
                    setError('Failed to search companies');
                }
                setResults([]);
            } finally {
                setLoading(false);
            }
        }, debounceMs);

        return () => clearTimeout(timeoutId);
    }, [query, debounceMs]);

    return { results, loading, error };
}

/**
 * Hook for fetching a single company
 */
export function useCompany(id: number | null) {
    const [company, setCompany] = useState<Company | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (id === null) {
            setCompany(null);
            return;
        }

        let cancelled = false;

        async function fetchCompany() {
            setLoading(true);
            setError(null);

            try {
                // id is guaranteed to be non-null here due to early return above
                const data = await companiesApi.getById(id as number);
                if (!cancelled) {
                    setCompany(data);
                }
            } catch (err) {
                if (!cancelled) {
                    if (err instanceof ApiError) {
                        setError(err.detail || err.message);
                    } else {
                        setError('Failed to fetch company');
                    }
                    setCompany(null);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        fetchCompany();

        return () => {
            cancelled = true;
        };
    }, [id]);

    return { company, loading, error };
}

/**
 * Hook for listing companies
 */
export function useCompanies(options?: { limit?: number; offset?: number }) {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const refetch = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const data = await companiesApi.list(options);
            setCompanies(data);
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.detail || err.message);
            } else {
                setError('Failed to fetch companies');
            }
        } finally {
            setLoading(false);
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [options?.limit, options?.offset]);

    useEffect(() => {
        refetch();
    }, [refetch]);

    return { companies, loading, error, refetch };
}
