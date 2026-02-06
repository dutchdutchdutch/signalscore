import { render, screen } from '@testing-library/react';
import { SampleTable } from '../SampleTable';

describe('SampleTable', () => {
    it('renders the sample data for ACME Anvils', () => {
        render(<SampleTable />);

        expect(screen.getByText('ACME Anvils')).toBeInTheDocument();
        expect(screen.getByText('AI Keywords')).toBeInTheDocument();
        expect(screen.getByText('85')).toBeInTheDocument();
    });
});
