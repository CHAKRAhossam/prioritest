import { cn } from '@/lib/utils';

interface RiskBadgeProps {
  riskLevel: 'high' | 'medium' | 'low';
  className?: string;
}

export function RiskBadge({ riskLevel, className }: RiskBadgeProps) {
  const styles = {
    high: 'bg-red-100 text-red-800 border-red-300',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    low: 'bg-green-100 text-green-800 border-green-300',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        styles[riskLevel],
        className
      )}
    >
      {riskLevel.toUpperCase()}
    </span>
  );
}
