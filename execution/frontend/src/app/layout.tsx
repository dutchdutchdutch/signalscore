import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });

export const metadata: Metadata = {
    title: 'SignalScore - AI Readiness for Companies',
    description: 'The Glassdoor for AI Readiness. Discover which companies are truly building the future.',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={inter.variable}>
                {children}
            </body>
        </html>
    );
}
