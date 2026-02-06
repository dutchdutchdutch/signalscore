
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import SignalDetailPage from '../page'
import { scoresApi, ApiError } from '@/lib/api-client'

// Mock the API client but preserve ApiError class
vi.mock('@/lib/api-client', async (importOriginal) => {
    const actual = await importOriginal<typeof import('@/lib/api-client')>()
    return {
        ...actual,
        scoresApi: {
            get: vi.fn(),
        },
    }
})

// Mock ScoreDisplay specifically to simplify assertions (optional, but good for isolation)
// For now, we'll test integration with the real ScoreDisplay as it's a UI component

const mockScore = {
    status: 'completed',
    company_name: 'Stripe',
    score: 4.5,
    category: 'transformational',
    category_label: 'Transformational',
    signals: {},
    component_scores: {
        ai_keywords: 4.5,
        agentic_signals: 4.0,
        tool_stack: 4.8,
        non_eng_ai_roles: 3.5,
        ai_platform_team: 5.0,
    },
    evidence: [],
    scored_at: '2026-02-01T00:00:00Z',
}

describe('SignalDetailPage', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('renders loading state initially', () => {
        // Return a promise that never resolves immediately to test loading
        vi.mocked(scoresApi.get).mockReturnValue(new Promise(() => { }))

        render(<SignalDetailPage params={{ slug: 'www-stripe-com' }} />)
        expect(screen.getByText('Loading...')).toBeInTheDocument()
    })

    it('renders score details after loading', async () => {
        vi.mocked(scoresApi.get).mockResolvedValue(mockScore as any)

        render(<SignalDetailPage params={{ slug: 'www-stripe-com' }} />)

        await waitFor(() => {
            expect(screen.getByText('Stripe')).toBeInTheDocument()
        })

        expect(screen.getByText('www.stripe.com')).toBeInTheDocument()

        // Check for score value (might appear multiple times, in hero and breakdown)
        const scoreValues = screen.getAllByText('4.5');
        expect(scoreValues.length).toBeGreaterThan(0);

        // Check category breakdown
        expect(screen.getByText('AI Keywords')).toBeInTheDocument()
        expect(screen.getByText('AI Platform Team')).toBeInTheDocument()

        // Check scale reference
        expect(screen.getByText('Signal Scale Reference')).toBeInTheDocument()
        expect(screen.getByText('transformational')).toBeInTheDocument()
    })

    it('renders not found state on 404', async () => {
        // Use the real ApiError class
        const error = new ApiError(404, 'Not Found');
        vi.mocked(scoresApi.get).mockRejectedValue(error)

        render(<SignalDetailPage params={{ slug: 'unknown-com' }} />)

        await waitFor(() => {
            expect(screen.getByText('Company Not Found')).toBeInTheDocument()
        })

        expect(screen.getByText(/We couldn't find a score/)).toBeInTheDocument()
    })

    it('renders generic error state on other errors', async () => {
        vi.mocked(scoresApi.get).mockRejectedValue(new Error('Network Error'))

        render(<SignalDetailPage params={{ slug: 'broken-com' }} />)

        await waitFor(() => {
            expect(screen.getByText('Something went wrong')).toBeInTheDocument()
        })
    })

    it('converts slug to domain correctly', async () => {
        vi.mocked(scoresApi.get).mockResolvedValue(mockScore as any)

        render(<SignalDetailPage params={{ slug: 'careers-google-com' }} />)

        await waitFor(() => {
            expect(scoresApi.get).toHaveBeenCalledWith('careers.google.com')
        })
    })
})
