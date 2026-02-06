'use client';

import Link from 'next/link';

export function Footer() {
    return (
        <footer className="w-full py-8 mt-12 border-t border-gray-200 dark:border-gray-800 text-center text-sm text-gray-500">
            <div className="container mx-auto px-4">

                <div className="space-x-4">
                    <Link href="/methodology" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                        Scoring Methodology
                    </Link>
                    <span>•</span>
                    <a
                        href="https://github.com/dutchdutchdutch/signalscore"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    >
                        GitHub
                    </a>
                </div>
                <p className="mt-4 text-xs text-gray-400">
                    &copy; {new Date().getFullYear()} SignalScore. Open Source.
                </p>
            </div>
        </footer>
    );
}
