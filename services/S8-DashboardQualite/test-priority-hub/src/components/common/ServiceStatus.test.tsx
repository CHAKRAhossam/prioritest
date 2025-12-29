import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ServiceStatus } from './ServiceStatus';

describe('ServiceStatus', () => {
  it('renders healthy status', () => {
    render(<ServiceStatus name="Test Service" status="healthy" />);
    expect(screen.getByText(/test service/i)).toBeInTheDocument();
    expect(screen.getByText(/healthy/i)).toBeInTheDocument();
  });

  it('renders unhealthy status', () => {
    render(<ServiceStatus name="Test Service" status="unhealthy" />);
    expect(screen.getByText(/unhealthy/i)).toBeInTheDocument();
  });

  it('renders loading status', () => {
    render(<ServiceStatus name="Test Service" status="loading" />);
    expect(screen.getByText(/checking/i)).toBeInTheDocument();
  });

  it('renders with version', () => {
    render(<ServiceStatus name="Test Service" status="healthy" version="1.0.0" />);
    expect(screen.getByText(/v1.0.0/i)).toBeInTheDocument();
  });
});

