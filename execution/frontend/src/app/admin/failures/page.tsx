'use client';

import React, { useEffect, useState } from 'react';
import { FailureList } from '@/components/admin/FailureList';

const API_BASE = '';

export default function FailuresPage() {
    const [failures, setFailures] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        async function loadData() {
            try {
                const res = await fetch(`${API_BASE}/api/v1/admin/failures`);
                if (!res.ok) throw new Error('Failed to load data');
                const data = await res.json();
                setFailures(data);
            } catch (err) {
                setError('Could not load failure data. Is the backend running?');
                console.error(err);
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, []);

    if (loading) return <div className="p-8 text-center text-gray-500">Loading diagnostics...</div>;
    if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Scraper Failures & Low Scores</h1>
                    <p className="text-gray-500 text-sm mt-1">Companies requiring attention (Score &lt; 15.0 or Errors)</p>
                </div>
                <div className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full text-sm font-medium">
                    {failures.length} Issues Found
                </div>
            </div>

            <FailureList failures={failures} />
        </div>
    );
}
