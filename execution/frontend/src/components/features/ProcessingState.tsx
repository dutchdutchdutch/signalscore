
import React from 'react';

interface ProcessingStateProps {
    status?: 'connecting' | 'extracting' | 'calculating' | 'processing' | 'completed' | 'failed';
    companyName?: string;
    onReset?: () => void;
}

export function ProcessingState({ status = 'processing', companyName = 'Company' }: ProcessingStateProps) {
    // Rotation messages for long-running states
    const [messageIndex, setMessageIndex] = React.useState(0);

    // Reset rotation when status changes
    React.useEffect(() => {
        setMessageIndex(0);
    }, [status]);

    // Auto-rotate messages every 3 seconds
    React.useEffect(() => {
        const interval = setInterval(() => {
            setMessageIndex(prev => prev + 1);
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    const getStatusMessage = (currentStatus: string) => {
        const rotation = [
            'Extracting signals...',
            'Analyzing career pages...',
            'Checking engineering blogs...',
            'Identifying AI keywords...',
            'Calculating score...'
        ];

        switch (currentStatus) {
            case 'connecting':
                return 'Connecting to site...';
            case 'extracting':
            case 'processing':
                // Rotate through messages for these states
                return rotation[messageIndex % rotation.length];
            case 'calculating':
                return 'Calculating score...';
            default:
                return 'Processing request...';
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto space-y-6 text-center py-12">
            <div className="relative inline-flex items-center justify-center">
                {/* Pulse animation matching system minimal design */}
                <div className="absolute w-16 h-16 bg-blue-500/20 rounded-full animate-pulse"></div>
                <div className="w-4 h-4 bg-blue-500 rounded-full relative z-10 shadow-[0_0_12px_rgba(59,130,246,0.5)]"></div>
            </div>

            <div className="space-y-2">
                <h3 className="text-xl font-medium text-white">Scoring Engine Active</h3>
                <p className="text-lg text-blue-200 font-medium animate-pulse min-h-[28px]">
                    {getStatusMessage(status)}
                </p>
                {companyName && (
                    <p className="text-sm text-gray-400">
                        Analyzing {companyName}
                    </p>
                )}
            </div>

            <div className="bg-white/5 border border-white/10 rounded-xl p-6 max-w-lg mx-auto backdrop-blur-sm">
                <div className="flex items-start gap-3 text-left">
                    <span className="text-blue-400 mt-0.5 text-lg">ℹ️</span>
                    <div className="space-y-1">
                        <p className="text-sm text-gray-300">
                            Deep analysis commonly takes <strong>3 to 5 minutes</strong>.
                        </p>
                        <p className="text-xs text-gray-500">
                            We scrape careers pages, blogs, and press releases in real-time. You can navigate away and return later; the score will be cached for this URL.
                        </p>
                    </div>
                </div>
            </div>

            <div className="pt-4">
                <a
                    href="/methodology"
                    className="text-xs text-gray-500 hover:text-blue-400 hover:underline transition-colors flex items-center justify-center gap-1.5"
                >
                    While you wait, learn about our Scoring Methodology <span>→</span>
                </a>
            </div>
        </div>
    );
}
