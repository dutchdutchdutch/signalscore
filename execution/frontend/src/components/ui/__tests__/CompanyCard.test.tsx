import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { CompanyCard } from '../CompanyCard'
import type { Company, ScoreResponse } from '@/lib/api-client/schema'

// Helper to create mock company data
const createMockCompany = (overrides: Partial<Company> = {}): Company => ({
    id: 1,
    name: 'Test Company',
    domain: 'example.com',
    url: 'https://www.example.com',
    createdAt: '2026-02-01T00:00:00Z',
    updatedAt: '2026-02-01T00:00:00Z',
    ...overrides,
})

// Helper to create mock score data
const createMockScore = (overrides: Partial<ScoreResponse> = {}): ScoreResponse => ({
    status: 'completed',
    company_name: 'Test Company',
    score: 4.2,
    category: 'high',
    category_label: 'High',
    signals: {
        ai_keywords: 10,
        agentic_signals: 5,
        tool_stack: ['Python', 'TensorFlow'],
        non_eng_ai_roles: 3,
        ai_in_it_signals: 8,
        has_ai_platform_team: true,
        jobs_analyzed: 50,
        marketing_only: false,
        source_attribution: {},
        confidence_score: 85,
    },
    component_scores: {
        ai_keywords: 4.0,
        agentic_signals: 3.5,
        tool_stack: 4.5,
        non_eng_ai: 3.0,
        ai_in_it: 5.0,
    },
    evidence: ['Evidence 1', 'Evidence 2'],
    scored_at: '2026-02-01T00:00:00Z',
    ...overrides,
})

describe('CompanyCard', () => {
    describe('Score-First Layout', () => {
        it('renders company name', () => {
            const company = createMockCompany({ name: 'Acme Corp' })
            render(<CompanyCard company={company} />)
            expect(screen.getByText('Acme Corp')).toBeInTheDocument()
        })

        it('renders score when provided', () => {
            const company = createMockCompany()
            const score = createMockScore({ score: 4.5 })
            render(<CompanyCard company={company} score={score} />)
            expect(screen.getByText('4.5')).toBeInTheDocument()
        })

        it('renders category label when score provided', () => {
            const company = createMockCompany()
            const score = createMockScore({ category_label: 'Transformational' })
            render(<CompanyCard company={company} score={score} />)
            expect(screen.getByText('Transformational')).toBeInTheDocument()
        })
    })

    describe('Placeholder Display', () => {
        it('shows placeholder when no score provided', () => {
            const company = createMockCompany()
            render(<CompanyCard company={company} />)
            expect(screen.getByText('No Score')).toBeInTheDocument()
            expect(screen.getByText('?')).toBeInTheDocument()
        })
    })

    describe('Domain Extraction', () => {
        it('extracts domain from valid URL', () => {
            const company = createMockCompany({ url: 'https://www.example.com/careers' })
            render(<CompanyCard company={company} />)
            expect(screen.getByText('example.com')).toBeInTheDocument()
        })

        it('removes www. prefix from domain', () => {
            const company = createMockCompany({ url: 'https://www.stripe.com' })
            render(<CompanyCard company={company} />)
            expect(screen.getByText('stripe.com')).toBeInTheDocument()
        })

        it('handles invalid URL gracefully (falls back to raw value)', () => {
            const company = createMockCompany({ url: 'invalid-url' })
            render(<CompanyCard company={company} />)
            expect(screen.getByText('invalid-url')).toBeInTheDocument()
        })

        it('handles null URL', () => {
            const company = createMockCompany({ url: null })
            const { container } = render(<CompanyCard company={company} />)
            expect(container.querySelector('.company-domain')).not.toBeInTheDocument()
        })
    })

    describe('Score Date Formatting', () => {
        it('displays formatted date when scored_at provided', () => {
            const company = createMockCompany()
            const score = createMockScore({ scored_at: '2026-02-01T00:00:00Z' })
            render(<CompanyCard company={company} score={score} />)
            // Format: "Scored: 1 Feb 2026"
            expect(screen.getByText(/Scored:/)).toBeInTheDocument()
        })

        it('does not display date when scored_at is null', () => {
            const company = createMockCompany()
            const score = createMockScore({ scored_at: null })
            render(<CompanyCard company={company} score={score} />)
            expect(screen.queryByText(/Scored:/)).not.toBeInTheDocument()
        })
    })

    describe('Navigation', () => {
        it('wraps card in link when domain is present', () => {
            const company = createMockCompany({ domain: 'stripe.com' })
            render(<CompanyCard company={company} />)

            const link = screen.getByRole('link')
            expect(link).toHaveAttribute('href', '/signal/stripe-com')
        })

        it('uses domain for slug, not URL subdomain', () => {
            // Domain should be google.com even if URL is careers.google.com
            const company = createMockCompany({
                domain: 'google.com',
                url: 'https://careers.google.com/jobs'
            })
            render(<CompanyCard company={company} />)

            const link = screen.getByRole('link')
            expect(link).toHaveAttribute('href', '/signal/google-com')
        })

        it('falls back to URL parsing when domain is null', () => {
            const company = createMockCompany({ domain: null, url: 'https://stripe.com/careers' })
            render(<CompanyCard company={company} />)

            const link = screen.getByRole('link')
            expect(link).toHaveAttribute('href', '/signal/stripe-com')
        })

        it('does not render link when both domain and URL are missing', () => {
            const company = createMockCompany({ domain: null, url: null })
            render(<CompanyCard company={company} />)

            expect(screen.queryByRole('link')).not.toBeInTheDocument()
        })
    })



    describe('Click Handler', () => {
        it('calls onClick when card is clicked', () => {
            const company = createMockCompany()
            const onClick = vi.fn()
            render(<CompanyCard company={company} onClick={onClick} />)

            const card = screen.getByRole('article')
            fireEvent.click(card)

            expect(onClick).toHaveBeenCalledWith(company)
        })

        it('does not throw when onClick is not provided', () => {
            const company = createMockCompany()
            render(<CompanyCard company={company} />)

            const card = screen.getByRole('article')
            expect(() => fireEvent.click(card)).not.toThrow()
        })
    })

    describe('Accessibility', () => {
        it('has accessible name including company and score', () => {
            const company = createMockCompany({ name: 'Test Corp' })
            const score = createMockScore({ score: 4.5 })
            render(<CompanyCard company={company} score={score} />)

            const card = screen.getByRole('article')
            expect(card).toHaveAttribute('aria-label', 'View Test Corp, AI Score: 4.5')
        })

        it('has accessible name without score when no score provided', () => {
            const company = createMockCompany({ name: 'Test Corp' })
            render(<CompanyCard company={company} />)

            const card = screen.getByRole('article')
            expect(card).toHaveAttribute('aria-label', 'View Test Corp')
        })
    })
})
