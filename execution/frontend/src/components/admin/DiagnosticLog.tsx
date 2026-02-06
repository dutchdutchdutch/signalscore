import React from 'react';

interface TraceStep {
    timestamp: string;
    step: string;
    detail?: any;
}

interface TraceData {
    steps: TraceStep[];
}

interface DiagnosticLogProps {
    trace: TraceData | null;
}

export function DiagnosticLog({ trace }: DiagnosticLogProps) {
    if (!trace || !trace.steps || trace.steps.length === 0) {
        return <div className="text-gray-500 italic p-4">No diagnostic trace available.</div>;
    }

    return (
        <div className="bg-gray-900 text-gray-100 font-mono text-xs p-4 rounded-md overflow-x-auto max-h-96 overflow-y-auto border border-gray-700">
            <h4 className="text-gray-400 font-bold mb-2 uppercase tracking-wider text-[10px]">Discovery Trace</h4>
            <div className="space-y-1">
                {trace.steps.map((step, idx) => (
                    <div key={idx} className="flex gap-2 border-l-2 border-indigo-500/30 pl-2 py-1 hover:bg-gray-800 transition-colors">
                        <span className="text-gray-500 min-w-[140px] shrink-0">
                            {new Date(step.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3 })}
                        </span>
                        <div className="flex-1">
                            <div className="text-indigo-300 font-semibold">{step.step}</div>
                            {step.detail && (
                                <pre className="text-gray-400 mt-1 whitespace-pre-wrap pl-2 border-l border-gray-700 text-[10px] break-all">
                                    {typeof step.detail === 'string' ? step.detail : JSON.stringify(step.detail, null, 2)}
                                </pre>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
