import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RiskBadge } from './RiskBadge';

describe('RiskBadge', () => {
  it('renders with high risk', () => {
    render(<RiskBadge riskLevel="high" />);
    expect(screen.getByText(/high/i)).toBeInTheDocument();
  });

  it('renders with medium risk', () => {
    render(<RiskBadge riskLevel="medium" />);
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
  });

  it('renders with low risk', () => {
    render(<RiskBadge riskLevel="low" />);
    expect(screen.getByText(/low/i)).toBeInTheDocument();
  });

  it('applies correct styling for high risk', () => {
    const { container } = render(<RiskBadge riskLevel="high" />);
    const badge = container.firstChild;
    expect(badge).toHaveClass(/bg-red|text-red|border-red/i);
  });
});

