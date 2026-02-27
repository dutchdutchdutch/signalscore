import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProcessingState } from '../ProcessingState';

describe('ProcessingState', () => {
    it('renders with initial status', () => {
        render(<ProcessingState status="connecting" />);
        // First rotation message for 'connecting' is "Discovering sources..."
        expect(screen.getByText(/Discovering sources/i)).toBeInTheDocument();
        expect(screen.getByText(/Scoring Engine Active/i)).toBeInTheDocument();
    });

    it('displays SLA warning', () => {
        render(<ProcessingState status="extracting" />);
        // Text is split by <strong> tag, so match the container's full text
        expect(screen.getByText((_content, el) =>
            el?.tagName === 'P' && (el?.textContent?.includes('3 to 5 minutes') ?? false)
        )).toBeInTheDocument();
    });

    it('shows methodology link', () => {
        render(<ProcessingState status="calculating" />);
        const link = screen.getByRole('link', { name: /methodology/i });
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', expect.stringContaining('methodology'));
    });

    it('updates message based on status', () => {
        const { rerender } = render(<ProcessingState status="connecting" />);
        // First rotation message for 'connecting'
        expect(screen.getByText(/Discovering sources/i)).toBeInTheDocument();

        rerender(<ProcessingState status="extracting" />);
        // First rotation message for 'extracting' (messageIndex resets to 0 on status change)
        expect(screen.getByText(/Scraping career pages/i)).toBeInTheDocument();

        rerender(<ProcessingState status="calculating" />);
        expect(screen.getByText(/Calculating AI readiness score/i)).toBeInTheDocument();
    });

    it('uses system minimal design tokens', () => {
        const { container } = render(<ProcessingState status="connecting" />);
        // Check for pulse animation class
        expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
    });
});
