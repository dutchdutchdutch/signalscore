import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ScoreDisplay } from '../ScoreDisplay'
import type { ScoreResponse } from '@/lib/api-client/schema'

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
        has_ai_platform_team: true,
        jobs_analyzed: 50,
    },
    component_scores: {
        ai_keywords: 4.0,
        agentic_signals: 3.5,
        tool_stack: 4.5,
        non_eng_ai: 3.0,
        ai_platform_team: 5.0,
    },
    evidence: ['Evidence 1', 'Evidence 2'],
    ...overrides,
})

describe('ScoreDisplay', () => {
    describe('Score Value Rendering', () => {
        it('renders the score value correctly', () => {
            const score = createMockScore({ score: 4.5 })
            render(<ScoreDisplay score={score} />)
            expect(screen.getByText('4.5')).toBeInTheDocument()
        })

        it('renders the category label', () => {
            const score = createMockScore({ category_label: 'Transformational' })
            render(<ScoreDisplay score={score} />)
            expect(screen.getByText('Transformational')).toBeInTheDocument()
        })
    })

    describe('Category Colors', () => {
        const categories: Array<ScoreResponse['category']> = [
            'transformational',
            'high',
            'medium_high',
            'medium_low',
            'low',
            'no_signal',
        ]

        categories.forEach((category) => {
            it(`renders ${category} category without errors`, () => {
                const score = createMockScore({ category, category_label: category.replace('_', ' ') })
                const { container } = render(<ScoreDisplay score={score} />)
                expect(container.querySelector('.score-circle')).toBeInTheDocument()
            })
        })
    })

    describe('Size Variants', () => {
        const sizes: Array<'small' | 'medium' | 'large'> = ['small', 'medium', 'large']

        sizes.forEach((size) => {
            it(`renders ${size} size variant`, () => {
                const score = createMockScore()
                const { container } = render(<ScoreDisplay score={score} size={size} />)
                expect(container.querySelector('.score-display')).toBeInTheDocument()
            })
        })
    })

    describe('Fallback Behavior', () => {
        it('handles unknown category gracefully', () => {
            const score = createMockScore({ category: 'unknown_category' as any })
            const { container } = render(<ScoreDisplay score={score} />)
            // Should still render with fallback to no_signal colors
            expect(container.querySelector('.score-circle')).toBeInTheDocument()
        })
    })
})
