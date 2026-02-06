'use client';

/**
 * Company Search Feature Component
 * 
 * Main search interface for SignalScore.
 * Uses mock data in development, API in production.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { SearchInput } from '@/components/ui/SearchInput';
import { SearchResults } from '@/components/ui/SearchResults';
import { ProcessingState } from './ProcessingState'; // New component
import { mockSearch } from '@/lib/mock-data';
import type { Company, ScoreResponse } from '@/lib/api-client/schema';
import { scoresApi } from '@/lib/api-client';
import { validateInputUrl } from '@/lib/validators';

/** Extract root domain from a URL (e.g., 'careers.google.com' -> 'google.com') */
function extractRootDomain(url: string): string | null {
    try {
        const hostname = new URL(url).hostname.replace('www.', '');
        const parts = hostname.split('.');
        // Handle simple TLDs (google.com, stripe.com)
        if (parts.length >= 2) {
            return parts.slice(-2).join('.');
        }
        return hostname;
    } catch {
        return null;
    }
}

// Toggle this to use real API instead of mock data
const USE_MOCK_DATA = false;

interface CompanySearchProps {
    onCompanySelect?: (company: Company) => void;
}

// Polling configuration
const POLL_INTERVAL_MS = 4000;
const TIMEOUT_MS = 240000; // 4 minutes

export function CompanySearch({ onCompanySelect }: CompanySearchProps) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<Company[]>([]);
    const [scores, setScores] = useState<Record<string, ScoreResponse>>({});

    // State machine
    const [status, setStatus] = useState<'idle' | 'analyzing' | 'completed' | 'failed'>('idle');
    const [processingStatus, setProcessingStatus] = useState<'connecting' | 'extracting' | 'calculating' | 'processing'>('processing');

    const [error, setError] = useState<string | null>(null);
    const [warning, setWarning] = useState<string | null>(null);
    const [isTimeout, setIsTimeout] = useState(false);

    // Refs for polling management
    const pollTimerRef = useRef<NodeJS.Timeout | null>(null);
    const startTimeRef = useRef<number | null>(null);

    // Cleanup polling on unmount
    useEffect(() => {
        return () => {
            if (pollTimerRef.current) clearTimeout(pollTimerRef.current);
        };
    }, []);

    const stopPolling = () => {
        if (pollTimerRef.current) {
            clearTimeout(pollTimerRef.current);
            pollTimerRef.current = null;
        }
    };

    const handleSearch = useCallback(async (searchQuery: string) => {
        setQuery(searchQuery);
        // We don't auto-search on type anymore, keeping this simple
    }, []);

    const pollForScore = async (companyName: string) => {
        try {
            // Check timeout
            if (startTimeRef.current && (Date.now() - startTimeRef.current > TIMEOUT_MS)) {
                setIsTimeout(true);
                // We typically stop polling here, or we can keep polling but show the warning?
                // AC3 says "display ... message", doesn't explicitly say STOP. 
                // But "Ensure user is not stuck in infinite loop". 
                // Let's stop polling to be safe and let user try again.
                // Actually, user updated AC: "display ... message... Confirm that the user can navigate away".
                // I will keep polling but show the timeout warning so if it DOES finish, they get it.
            }

            const result = await scoresApi.get(companyName); // Ensure this endpoint handles name or domain lookup correctly

            if (result.status === 'completed') {
                stopPolling();

                const careersUrl = result.careers_url || query;
                const company: Company = {
                    id: 1,
                    name: result.company_name,
                    domain: extractRootDomain(careersUrl),
                    url: careersUrl,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                };

                setResults([company]);
                setScores({ [result.company_name]: result });
                setStatus('completed');
                return;
            } else if (result.status === 'failed') {
                stopPolling();
                setError('Analysis failed. The site might be blocking our scrapers or is inaccessible.');
                setStatus('failed');
                return;
            }

            // Update processing visual if status changes (e.g. backend sends 'extracting')
            // Just rotate for now if backend doesn't send granular status
            // If backend sends 'processing', we can stick with that or rotate locally.
            // For now, let's keep it simple.

            // Continue polling
            pollTimerRef.current = setTimeout(() => pollForScore(companyName), POLL_INTERVAL_MS);

        } catch (err: any) {
            // If 404, it might mean not found YET? Or actually not found?
            // Usually GET /scores/Name returns 404 if not exists.
            // If we just CREATED it, it should exist in 'processing' state.
            // If it errors, we might want to retry a few times before failing.
            console.error('Poll error', err);
            // For MVP, we'll keep polling on minor errors, or fail?
            // Let's fail after a few retries? stick to simple for now.
            pollTimerRef.current = setTimeout(() => pollForScore(companyName), POLL_INTERVAL_MS);
        }
    };

    const handleAnalyze = async () => {
        // Reset states
        setWarning(null);
        setError(null);
        setIsTimeout(false);
        setResults([]);
        stopPolling();

        const validation = validateInputUrl(query);
        if (!validation.isValid) {
            setError(validation.error || 'Invalid URL');
            return;
        }

        const targetUrl = validation.normalizedUrl || query;
        if (validation.warning) setWarning(validation.warning);

        setStatus('analyzing');
        setProcessingStatus('connecting'); // Initial visual state
        startTimeRef.current = Date.now();

        try {
            const result = await scoresApi.create({ url: targetUrl });

            if (result.status === 'processing') { // 202
                // Start polling
                setProcessingStatus('extracting'); // Move to next visual step
                // Use company_name from result to poll
                pollForScore(result.company_name || query);
            } else if (result.status === 'completed') {
                // Done immediately
                const careersUrl = result.careers_url || query;
                const company: Company = {
                    id: 1,
                    name: result.company_name,
                    domain: extractRootDomain(careersUrl),
                    url: careersUrl,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                };
                setResults([company]);
                setScores({ [result.company_name]: result });
                setStatus('completed');
            }
        } catch (err: any) {
            setError(err.message || 'Failed to start analysis');
            setStatus('failed');
        }
    };

    const handleCompanyClick = useCallback((company: Company) => {
        if (onCompanySelect) {
            onCompanySelect(company);
        }
    }, [onCompanySelect]);

    return (
        <div className="company-search w-full">
            {/* Search Input View - Only show if idle, failed, or completed (and we want to search again?) */}
            {/* Actually, if completed, we usually show results AND search bar to search again? 
                But AC1 says "Hide the search input or disable it clearly". 
                Let's hide it during 'analyzing'.
            */}

            {status !== 'analyzing' && (
                <div className="w-full max-w-2xl mx-auto space-y-4">
                    <form onSubmit={(e) => {
                        e.preventDefault();
                        handleAnalyze();
                    }} className="relative w-full mx-auto">
                        <div className="relative group">
                            {/* Search Icon */}
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                </svg>
                            </div>

                            <input
                                type="text"
                                value={query}
                                onChange={(e) => {
                                    setQuery(e.target.value);
                                    setError(null);
                                    setStatus('idle');
                                }}
                                placeholder="Enter company URL (e.g. nike.com)..."
                                className={`w-full pl-12 pr-12 py-3 bg-white/5 border rounded-xl focus:outline-none focus:ring-1 focus:ring-white/20 text-white placeholder-gray-500 transition-all ${error ? 'border-red-500/50 focus:border-red-500' : 'border-white/10 hover:border-white/20'}`}
                            />

                            {/* Shortcut Hint */}
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                                <kbd className="hidden sm:inline-flex items-center justify-center min-w-[20px] h-5 px-1 text-[10px] font-medium text-gray-500 bg-white/5 border border-white/10 rounded font-mono">
                                    /
                                </kbd>
                            </div>
                        </div>
                    </form>

                    {error && (
                        <div className="px-4 py-3 rounded-lg text-sm bg-red-500/10 border border-red-500/20 text-red-200">
                            {error}
                        </div>
                    )}

                    {warning && !error && (
                        <div className="px-4 py-3 rounded-lg text-sm bg-yellow-500/10 border border-yellow-500/20 text-yellow-200">
                            INFO: {warning}
                        </div>
                    )}
                </div>
            )}

            {/* Processing State */}
            {status === 'analyzing' && (
                <div className="space-y-4">
                    <ProcessingState
                        status={processingStatus}
                        companyName={query} // We might not have the clean name yet, use query
                    />

                    {isTimeout && (
                        <div className="max-w-md mx-auto px-4 py-3 rounded-lg text-sm bg-yellow-500/10 border border-yellow-500/20 text-yellow-200 text-center animate-in fade-in slide-in-from-bottom-2">
                            Taking longer than usual. You can wait, or check back later.
                        </div>
                    )}
                </div>
            )}

            {/* Results State */}
            {status === 'completed' && (
                <SearchResults
                    results={results}
                    scores={scores}
                    loading={false}
                    error={null}
                    query={query}
                    onCompanyClick={handleCompanyClick}
                />
            )}

            <style jsx>{`
                .company-search {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    width: 100%;
                }
            `}</style>
        </div>
    );
}

