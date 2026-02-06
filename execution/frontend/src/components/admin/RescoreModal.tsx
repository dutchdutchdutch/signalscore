'use client';

import React, { useState } from 'react';

interface RescoreModalProps {
    isOpen: boolean;
    onClose: () => void;
    companyName: string;
    onSuccess?: () => void;
}

export function RescoreModal({ isOpen, onClose, companyName, onSuccess }: RescoreModalProps) {
    const [careersUrl, setCareersUrl] = useState('');
    const [evidenceUrls, setEvidenceUrls] = useState('');
    const [researchMode, setResearchMode] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

    // L2 Fix: Reset state when modal closes
    const handleClose = () => {
        setCareersUrl('');
        setEvidenceUrls('');
        setResearchMode(false);
        setResult(null);
        onClose();
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setResult(null);

        try {
            const evidenceList = evidenceUrls
                .split('\n')
                .map(url => url.trim())
                .filter(url => url.length > 0);

            // M2 Fix: Use relative URL for staging/production compatibility
            const response = await fetch('/api/v1/admin/rescore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    company_name: companyName,
                    careers_url: careersUrl || `https://${companyName.toLowerCase()}.com/careers`,
                    evidence_urls: evidenceList.length > 0 ? evidenceList : null,
                    research_mode: researchMode,
                }),
            });

            // M3 Fix: Safe error parsing with fallback
            if (!response.ok) {
                let errorMessage = 'Rescore failed';
                try {
                    const error = await response.json();
                    errorMessage = error.detail || errorMessage;
                } catch {
                    errorMessage = `Request failed with status ${response.status}`;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            setResult({
                success: true,
                message: `Score: ${data.score} (${data.category}) - ${data.sources_scraped} sources scraped`,
            });
            onSuccess?.();
        } catch (err: any) {
            setResult({
                success: false,
                message: err.message || 'An error occurred',
            });
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4">
                <div className="flex items-center justify-between p-4 border-b">
                    <h2 className="text-lg font-semibold">Rescore: {companyName}</h2>
                    <button
                        onClick={handleClose}
                        className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
                    >
                        &times;
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-4 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Careers URL
                        </label>
                        <input
                            type="url"
                            value={careersUrl}
                            onChange={(e) => setCareersUrl(e.target.value)}
                            placeholder={`https://${companyName.toLowerCase()}.com/careers`}
                            className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            Leave empty to use default based on company name
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Evidence URLs (one per line)
                        </label>
                        <textarea
                            value={evidenceUrls}
                            onChange={(e) => setEvidenceUrls(e.target.value)}
                            placeholder="https://blog.company.com/ai-strategy&#10;https://github.com/company"
                            rows={4}
                            className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                        />
                    </div>

                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            id="research-mode"
                            checked={researchMode}
                            onChange={(e) => setResearchMode(e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="research-mode" className="text-sm text-gray-700">
                            Research Mode (auto-discover sources via web search)
                        </label>
                    </div>

                    {result && (
                        <div
                            className={`p-3 rounded-md text-sm ${result.success
                                ? 'bg-green-50 text-green-800 border border-green-200'
                                : 'bg-red-50 text-red-800 border border-red-200'
                                }`}
                        >
                            {result.message}
                        </div>
                    )}

                    <div className="flex justify-end gap-3 pt-2">
                        <button
                            type="button"
                            onClick={handleClose}
                            className="px-4 py-2 text-gray-600 hover:text-gray-800"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                    </svg>
                                    Rescoring...
                                </>
                            ) : (
                                'Start Rescore'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
