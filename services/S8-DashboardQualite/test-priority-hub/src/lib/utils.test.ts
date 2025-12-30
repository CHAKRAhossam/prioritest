import { describe, it, expect } from 'vitest';
import { cn } from './utils';

describe('cn utility', () => {
  it('merges class names correctly', () => {
    const result = cn('class1', 'class2');
    expect(result).toContain('class1');
    expect(result).toContain('class2');
  });

  it('handles conditional classes', () => {
    const result = cn('base', true && 'conditional');
    expect(result).toContain('base');
    expect(result).toContain('conditional');
  });

  it('handles undefined and null', () => {
    const result = cn('base', undefined, null);
    expect(result).toContain('base');
  });
});

