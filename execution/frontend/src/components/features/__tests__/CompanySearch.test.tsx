
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { CompanySearch } from '../CompanySearch';
import { scoresApi } from '@/lib/api-client';

// Mock the API client
vi.mock('@/lib/api-client', () => ({
    scoresApi: {
        create: vi.fn(),
        get: vi.fn(),
    },
}));

// Mock the validators
vi.mock('@/lib/validators', () => ({
    validateInputUrl: vi.fn(),
}));
import { validateInputUrl } from '@/lib/validators';

describe('CompanySearch Polling', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        vi.clearAllMocks();
        // Default valid validation
        vi.mocked(validateInputUrl).mockReturnValue({ isValid: true, normalizedUrl: 'http://example.com' });
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('starts polling when API returns 202 processing', async () => {
        // Setup initial response: Processing
        vi.mocked(scoresApi.create).mockResolvedValue({
            status: 'processing',
            company_name: 'Example',
            // other fields ignored for this test state
        } as any);

        // Setup polling response: Still processing
        vi.mocked(scoresApi.get).mockResolvedValue({
            status: 'processing',
            company_name: 'Example',
        } as any);

        render(<CompanySearch />);

        const input = screen.getByPlaceholderText(/enter company url/i);
        fireEvent.change(input, { target: { value: 'example.com' } });
        fireEvent.submit(screen.getByRole('button', { name: /check score/i }));

        // Initial state should be "Connecting" or "Processing" from ProcessingState
        await waitFor(() => {
            expect(scoresApi.create).toHaveBeenCalled();
            expect(screen.getByText(/Scoring Engine Active/i)).toBeInTheDocument();
        });

        // Fast-forward time to trigger poll (4s)
        await act(async () => {
            vi.advanceTimersByTime(4000);
        });

        expect(scoresApi.get).toHaveBeenCalledWith('Example');
    });

    it('stops polling and shows results when status is completed', async () => {
        vi.mocked(scoresApi.create).mockResolvedValue({
            status: 'processing',
            company_name: 'Example',
        } as any);

        // First poll: Processing
        vi.mocked(scoresApi.get).mockResolvedValueOnce({
            status: 'processing',
            company_name: 'Example',
        } as any);

        // Second poll: Completed
        vi.mocked(scoresApi.get).mockResolvedValueOnce({
            status: 'completed',
            company_name: 'Example',
            score: 5,
            // ... complete response
        } as any);

        render(<CompanySearch />);

        fireEvent.change(screen.getByPlaceholderText(/enter company url/i), { target: { value: 'example.com' } });
        fireEvent.submit(screen.getByRole('button', { name: /check score/i }));

        // Wait for create
        await waitFor(() => expect(screen.getByText(/Scoring Engine Active/i)).toBeInTheDocument());

        // Advance for first poll
        await act(async () => { vi.advanceTimersByTime(4000); });

        // Advance for second poll
        await act(async () => { vi.advanceTimersByTime(4000); });

        // Should now be finished, checking for success state (ScoreDisplay or results)
        // Since we don't mock ScoreDisplay, we look for result elements or absence of ProcessingState
        await waitFor(() => {
            expect(screen.queryByText(/Scoring Engine Active/i)).not.toBeInTheDocument();
        });
    });

    it('shows timeout warning after 4 minutes', async () => {
        vi.mocked(scoresApi.create).mockResolvedValue({
            status: 'processing',
            company_name: 'SlowCo',
        } as any);

        // Always processing
        vi.mocked(scoresApi.get).mockResolvedValue({
            status: 'processing',
            company_name: 'SlowCo',
        } as any);

        render(<CompanySearch />);
        fireEvent.change(screen.getByPlaceholderText(/enter company url/i), { target: { value: 'slow.com' } });
        fireEvent.submit(screen.getByRole('button'));

        // Advance 4 minutes + buffer
        await act(async () => {
            vi.advanceTimersByTime(241000); // 4 min + 1s
        });

        expect(screen.getByText(/Taking longer than usual/i)).toBeInTheDocument();
    });
    it('renders idleContent when status is idle', () => {
        render(<CompanySearch idleContent={<div data-testid="idle-content">Idle Content</div>} />);
        expect(screen.getByTestId('idle-content')).toBeInTheDocument();
    });

    it('hides idleContent when analyzing', async () => {
        vi.mocked(scoresApi.create).mockResolvedValue({
            status: 'processing',
            company_name: 'Example',
        } as any);

        vi.mocked(scoresApi.get).mockResolvedValue({ status: 'processing', company_name: 'Example' } as any);

        render(<CompanySearch idleContent={<div data-testid="idle-content">Idle Content</div>} />);

        expect(screen.getByTestId('idle-content')).toBeInTheDocument();

        fireEvent.change(screen.getByPlaceholderText(/enter company url/i), { target: { value: 'example.com' } });
        fireEvent.submit(screen.getByRole('button'));

        // Should hide immediately when status changes to analyzing
        await waitFor(() => {
            expect(screen.queryByTestId('idle-content')).not.toBeInTheDocument();
        });
    });
});
