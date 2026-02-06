/** @type {import('next').NextConfig} */
const nextConfig = {
    // Proxy API calls to the backend service
    async rewrites() {
        return [
            {
                source: '/api/v1/:path*',
                destination: 'http://127.0.0.1:8000/api/v1/:path*',
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
