import React from 'react';

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white border-b sticky top-0 z-10">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                    <div className="font-bold text-gray-900 flex items-center gap-2">
                        <span className="text-indigo-600">SignalScore</span> Admin
                    </div>
                    <nav className="flex gap-4 text-sm text-gray-600">
                        <a href="/" className="hover:text-indigo-600">Main Site</a>
                        <a href="/admin/failures" className="text-indigo-600 font-medium">Failures</a>
                    </nav>
                </div>
            </header>
            <main className="container mx-auto px-4 py-8">
                {children}
            </main>
        </div>
    );
}
