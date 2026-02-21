/** @type {import('next').NextConfig} */
const nextConfig = {
    // Proxy API calls to the backend service (local dev; in production Firebase Hosting rewrites handle this)
    async rewrites() {
        const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
        return [
            {
                source: '/api/v1/:path*',
                destination: `${backendUrl}/api/v1/:path*`,
            },
        ];
    },
    // Output standalone build for Docker
    output: 'standalone',
    env: {
        NEXT_PUBLIC_APP_STAGE: process.env.NEXT_PUBLIC_APP_STAGE || 'EXPERIMENTAL',
    },
};

module.exports = nextConfig;
