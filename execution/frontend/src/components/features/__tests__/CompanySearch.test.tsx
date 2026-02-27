
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { CompanySearch } from '../CompanySearch';
import { scoresApi } from '@/lib/api-client';

// Mock the API client
vi.mock('@/lib/api-client', () => ({
    scoresApi: {
        create: vi.fn(),
        get: vi.fn(),
        getJobStatus: vi.fn(),
    },
}));

// Mock the validators
vi.mock('@/lib/validators', () => ({
    validateInputUrl: vi.fn(),
}));
import { validateInputUrl } from '@/lib/validators';

/** Helper: type a URL and submit the form */
function submitUrl(url: string) {
    const input = screen.getByPlaceholderText(/enter company url/i);
    fireEvent.change(input, { target: { value: url } });
    fireEvent.submit(input.closest('form')!);
}

describe('CompanySearch Polling', () => {
    beforeEach(() => {
        vi.useFakeTimers({ shouldAdvanceTime: true });
        vi.clearAllMocks();
        // Default valid validation
        vi.mocked(validateInputUrl).mockReturnValue({ isValid: true, normalizedUrl: 'http://example.com' });
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('starts polling when API returns 202 processing', async () => {
        // Setup initial response: Processing with job_id
        vi.mocked(scoresApi.create).mockResolvedValue({
            status: 'processing',
            company_name: 'Example',
            job_id: 'test-job-123',
        } as any);

        // Setup polling response: Still processing
        vi.mocked(scoresApi.getJobStatus).mockResolvedValue({
            status: 'processing',
            company_name: 'Example',
        } as any);

        render(<CompanySearch />);
        submitUrl('example.com');

        // Initial state should show ProcessingState
        await waitFor(() => {
            expect(scoresApi.create).toHaveBeenCalled();
            expect(screen.getByText(/Scoring Engine Active/i)).toBeInTheDocument();
        });

        // Fast-forward time to trigger poll (4s)
        await act(async () => {
            vi.advanceTimersByTime(4000);
        });

        expect(scoresApi.getJobStatus).toHaveBeenCalledWith('test-job-123');
    });

    it('stops polling and shows results when status is completed', async () => {
        vi.mocked(scoresApi.create).mockResolvedValue({
            status: 'processing',
            company_name: 'Example',
            job_id: 'test-job-456',
        } as any);

        // First poll: Processing
        vi.mocked(scoresApi.getJobStatus).mockResolvedValueOnce({
            status: 'processing',
            company_name: 'Example',
        } as any);

        // Second poll: Completed
        vi.mocked(scoresApi.getJobStatus).mockResolvedValueOnce({
            status: 'completed',
            company_name: 'Example',
        } as any);

        // Full score fetch after job completes
        vi.mocked(scoresApi.get).mockResolvedValue({
            status: 'completed',
            company_name: 'Example',
            score: 5,
            careers_url: 'https://example.com',
        } as any);

        render(<CompanySearch />);
        submitUrl('example.com');

        // Wait for create
        await waitFor(() => expect(screen.getByText(/Scoring Engine Active/i)).toBeInTheDocument());

        // Advance for first poll
        await act(async () => { vi.advanceTimersByTime(4000); });

        // Advance for second poll
        await act(async () => { vi.advanceTimersByTime(4000); });

        // Should now be finished — ProcessingState should be gone
        await waitFor(() => {
            expect(screen.queryByText(/Scoring Engine Active/i)).not.toBeInTheDocument();
        });
    });

    it('shows timeout warning after 5 minutes', async () => {
        vi.mocked(scoresApi.create).mockResolvedValue({
            status: 'processing',
            company_name: 'SlowCo',
            job_id: 'test-job-slow',
        } as any);

        // Always processing
        vi.mocked(scoresApi.getJobStatus).mockResolvedValue({
            status: 'processing',
            company_name: 'SlowCo',
        } as any);

        render(<CompanySearch />);
        submitUrl('slow.com');

        // Wait for initial processing state
        await waitFor(() => expect(screen.getByText(/Scoring Engine Active/i)).toBeInTheDocument());

        // Advance past TIMEOUT_MS (300000ms = 5 min) in increments to trigger polls
        for (let i = 0; i < 80; i++) {
            await act(async () => { vi.advanceTimersByTime(4000); });
        }

        expect(screen.getByText(/Taking longer than usual/i)).toBeInTheDocument();
    });

    it('renders idleContent when status is idle', () => {
        render(<CompanySearch idleContent={<div data-testid="idle-content">Idle Content</div>} />);
        expect(screen.getByTestId('idle-content')).toBeInTheDocument();
    });

    it('retries once on cold-start 503 error then succeeds', async () => {
        // First call: 503 (cold start)
        vi.mocked(scoresApi.create)
            .mockRejectedValueOnce({ status: 503, message: 'Service Unavailable' })
            .mockResolvedValueOnce({
                status: 'processing',
                company_name: 'Example',
                job_id: 'retry-job-1',
            } as any);

        vi.mocked(scoresApi.getJobStatus).mockResolvedValue({
            status: 'processing',
            company_name: 'Example',
        } as any);

        render(<CompanySearch />);
        submitUrl('example.com');

        // Wait for the first call to be made and rejected
        await waitFor(() => {
            expect(scoresApi.create).toHaveBeenCalledTimes(1);
        });

        // Advance past the 3s retry delay
        await act(async () => { vi.advanceTimersByTime(3500); });

        // Should have retried and started polling
        await waitFor(() => {
            expect(scoresApi.create).toHaveBeenCalledTimes(2);
        });

        // Should show processing state (not error)
        expect(screen.getByText(/Scoring Engine Active/i)).toBeInTheDocument();
    });

    it('hides idleContent when analyzing', async () => {
        vi.mocked(scoresApi.create).mockResolvedValue({
            status: 'processing',
            company_name: 'Example',
            job_id: 'test-job-789',
        } as any);

        vi.mocked(scoresApi.getJobStatus).mockResolvedValue({ status: 'processing', company_name: 'Example' } as any);

        render(<CompanySearch idleContent={<div data-testid="idle-content">Idle Content</div>} />);

        expect(screen.getByTestId('idle-content')).toBeInTheDocument();

        submitUrl('example.com');

        // Should hide immediately when status changes to analyzing
        await waitFor(() => {
            expect(screen.queryByTestId('idle-content')).not.toBeInTheDocument();
        });
    });
});
