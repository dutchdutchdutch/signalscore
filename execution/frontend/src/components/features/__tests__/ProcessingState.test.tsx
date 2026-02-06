import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProcessingState } from '../ProcessingState';

describe('ProcessingState', () => {
    it('renders with initial status', () => {
        render(<ProcessingState status="connecting" />);
        expect(screen.getByText(/Connecting to site/i)).toBeInTheDocument();
        expect(screen.getByText(/Scoring Engine Active/i)).toBeInTheDocument();
    });

    it('displays SLA warning', () => {
        render(<ProcessingState status="extracting" />);
        expect(screen.getByText(/commonly takes 3 to 5 minutes/i)).toBeInTheDocument();
    });

    it('shows methodology link', () => {
        render(<ProcessingState status="calculating" />);
        const link = screen.getByRole('link', { name: /methodology/i });
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', expect.stringContaining('methodology'));
    });

    it('updates message based on status', () => {
        const { rerender } = render(<ProcessingState status="connecting" />);
        expect(screen.getByText(/Connecting/i)).toBeInTheDocument();

        rerender(<ProcessingState status="extracting" />);
        expect(screen.getByText(/Extracting signals/i)).toBeInTheDocument();

        rerender(<ProcessingState status="calculating" />);
        expect(screen.getByText(/Calculating score/i)).toBeInTheDocument();
    });

    it('uses system minimal design tokens', () => {
        const { container } = render(<ProcessingState status="connecting" />);
        // Check for pulse animation class
        expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
    });
});
