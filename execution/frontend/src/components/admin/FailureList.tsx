'use client';

import React, { useState } from 'react';
import { DiagnosticLog } from './DiagnosticLog';
import { RescoreModal } from './RescoreModal';

interface CompanyFailure {
    id: number;
    name: string;
    score: number;
    updated_at: string;
    trace: any;
    probable_cause?: string;
}

interface FailureListProps {
    failures: CompanyFailure[];
    onRefresh?: () => void;
}

export function FailureList({ failures, onRefresh }: FailureListProps) {
    const [expandedId, setExpandedId] = useState<number | null>(null);
    const [rescoreCompany, setRescoreCompany] = useState<string | null>(null);

    const toggleExpand = (id: number) => {
        setExpandedId(expandedId === id ? null : id);
    };

    const handleRescoreSuccess = () => {
        // Optionally refresh the list after successful rescore
        onRefresh?.();
    };

    return (
        <>
            <div className="space-y-4">
                {failures.map((company) => (
                    <div key={company.id} className="bg-white border rounded-lg shadow-sm overflow-hidden">
                        <div
                            className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50/50 transition-colors"
                            onClick={() => toggleExpand(company.id)}
                        >
                            <div className="flex items-center gap-4">
                                <div className={`
                                    w-2 h-2 rounded-full 
                                    ${company.score < 10 ? 'bg-red-500' : 'bg-yellow-500'}
                                  `} />
                                <div>
                                    <h3 className="font-semibold text-gray-900">{company.name}</h3>
                                    <div className="text-sm text-gray-500">
                                        Last updated: {new Date(company.updated_at).toLocaleDateString()}
                                    </div>
                                </div>
                                {company.probable_cause && (
                                    <span className={`px-2 py-0.5 rounded text-xs font-medium border
                                        ${company.probable_cause === 'Blocked' ? 'bg-red-50 text-red-600 border-red-100' :
                                            company.probable_cause === 'Ghost' ? 'bg-purple-50 text-purple-600 border-purple-100' :
                                                'bg-gray-100 text-gray-600 border-gray-200'
                                        }`}>
                                        {company.probable_cause}
                                    </span>
                                )}
                            </div>

                            <div className="flex items-center gap-4">
                                <div className="text-right">
                                    <div className="text-xs text-gray-500 uppercase">Score</div>
                                    <div className="font-mono font-bold text-lg">{company.score.toFixed(1)}</div>
                                </div>

                                <button
                                    className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setRescoreCompany(company.name);
                                    }}
                                >
                                    Rescore
                                </button>

                                <button
                                    className="text-gray-400 hover:text-gray-600 px-2"
                                    onClick={(e) => { e.stopPropagation(); toggleExpand(company.id); }}
                                >
                                    {expandedId === company.id ? 'Hide Log' : 'View Log'}
                                </button>
                            </div>
                        </div>

                        {expandedId === company.id && (
                            <div className="border-t bg-gray-50 p-4">
                                <DiagnosticLog trace={company.trace} />
                            </div>
                        )}
                    </div>
                ))}

                {failures.length === 0 && (
                    <div className="text-center py-12 text-gray-400 bg-gray-50 rounded border border-dashed">
                        No failures detected. System healthy.
                    </div>
                )}
            </div>

            {/* Rescore Modal */}
            <RescoreModal
                isOpen={!!rescoreCompany}
                onClose={() => setRescoreCompany(null)}
                companyName={rescoreCompany || ''}
                onSuccess={handleRescoreSuccess}
            />
        </>
    );
}

