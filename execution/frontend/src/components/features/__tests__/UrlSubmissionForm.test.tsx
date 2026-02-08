import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UrlSubmissionForm } from '../UrlSubmissionForm';
import { companiesApi } from '@/lib/api-client';

// Mock the API client
jest.mock('@/lib/api-client', () => ({
    companiesApi: {
        submitSources: jest.fn(),
    },
    ApiError: class extends Error {
        detail?: string;
        constructor(status: number, statusText: string, detail?: string) {
            super(detail || statusText);
            this.detail = detail;
        }
    }
}));

describe('UrlSubmissionForm', () => {
    const mockSubmitSources = companiesApi.submitSources as jest.Mock;

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders correctly', () => {
        render(<UrlSubmissionForm companyId={1} companyName="TestCorp" />);
        expect(screen.getByText('Submit Missing Sources')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('https://example.com/blog')).toBeInTheDocument();
    });

    it('submits valid URLs', async () => {
        mockSubmitSources.mockResolvedValue({
            message: 'Success',
            verified_count: 1,
            pending_count: 0,
            status: 'processing'
        });

        render(<UrlSubmissionForm companyId={1} companyName="TestCorp" />);

        const input = screen.getByPlaceholderText('https://example.com/blog');
        fireEvent.change(input, { target: { value: 'https://testcorp.com/blog' } });

        fireEvent.click(screen.getByText('Submit Sources'));

        await waitFor(() => {
            expect(mockSubmitSources).toHaveBeenCalledWith(1, ['https://testcorp.com/blog']);
            expect(screen.getByText(/Success/)).toBeInTheDocument();
        });
    });

    it('validates empty submission', async () => {
        render(<UrlSubmissionForm companyId={1} companyName="TestCorp" />);
        fireEvent.click(screen.getByText('Submit Sources'));

        await waitFor(() => {
            expect(screen.getByText('Please enter at least one URL.')).toBeInTheDocument();
            expect(mockSubmitSources).not.toHaveBeenCalled();
        });
    });

    it('handles errors', async () => {
        mockSubmitSources.mockRejectedValue(new Error('API Error'));

        render(<UrlSubmissionForm companyId={1} companyName="TestCorp" />);

        const input = screen.getByPlaceholderText('https://example.com/blog');
        fireEvent.change(input, { target: { value: 'https://testcorp.com/blog' } });

        fireEvent.click(screen.getByText('Submit Sources'));

        await waitFor(() => {
            expect(screen.getByText(/API Error/)).toBeInTheDocument();
        });
    });

    it('adds and removes fields', () => {
        render(<UrlSubmissionForm companyId={1} companyName="TestCorp" />);

        // Initial state: 1 field
        expect(screen.getAllByPlaceholderText('https://example.com/blog')).toHaveLength(1);

        // Add field
        fireEvent.click(screen.getByText('+ Add another URL'));
        expect(screen.getAllByPlaceholderText('https://example.com/blog')).toHaveLength(2);

        // Remove field (first one has remove button only if > 1)
        const removeButtons = screen.getAllByLabelText('Remove URL');
        fireEvent.click(removeButtons[0]);
        expect(screen.getAllByPlaceholderText('https://example.com/blog')).toHaveLength(1);
    });
});
