/**
 * Mock data for development and testing.
 * 
 * Used when backend is not available or for demo purposes.
 */

import type { Company } from '@/lib/api-client/schema';

export const MOCK_COMPANIES: Company[] = [
    {
        id: 1,
        name: "ACME Grandiose Industries",
        domain: "acme-grandiose-industries.com",
        url: "https://acme-grandiose-industries.com",
        createdAt: "2026-02-03T12:00:00Z",
        updatedAt: "2026-02-03T12:00:00Z",
    },
    {
        id: 2,
        name: "Stripe",
        domain: "stripe.com",
        url: "https://stripe.com",
        createdAt: "2026-02-01T10:00:00Z",
        updatedAt: "2026-02-03T15:30:00Z",
    },
    {
        id: 3,
        name: "Shopify",
        domain: "shopify.com",
        url: "https://shopify.com",
        createdAt: "2026-02-01T10:00:00Z",
        updatedAt: "2026-02-03T14:00:00Z",
    },
    {
        id: 4,
        name: "OpenAI",
        domain: "openai.com",
        url: "https://openai.com",
        createdAt: "2026-02-02T08:00:00Z",
        updatedAt: "2026-02-03T16:00:00Z",
    },
    {
        id: 5,
        name: "Anthropic",
        domain: "anthropic.com",
        url: "https://anthropic.com",
        createdAt: "2026-02-02T09:00:00Z",
        updatedAt: "2026-02-03T11:00:00Z",
    },
    {
        id: 6,
        name: "GitHub",
        domain: "github.com",
        url: "https://github.com",
        createdAt: "2026-02-01T07:00:00Z",
        updatedAt: "2026-02-03T13:00:00Z",
    },
];

/**
 * Mock search function - filters companies by query
 */
export function mockSearch(query: string): Company[] {
    const normalizedQuery = query.toLowerCase().trim();

    if (!normalizedQuery) return [];

    return MOCK_COMPANIES.filter(company =>
        company.name.toLowerCase().includes(normalizedQuery) ||
        (company.url?.toLowerCase().includes(normalizedQuery) ?? false)
    );
}
