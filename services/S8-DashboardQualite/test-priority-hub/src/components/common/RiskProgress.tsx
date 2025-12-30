import { cn } from '@/lib/utils';

interface RiskProgressProps {
  value: number;
  className?: string;
  showLabel?: boolean;
}

export function RiskProgress({ value, className, showLabel = true }: RiskProgressProps) {
  const percentage = Math.min(100, Math.max(0, value * 100));
  
  const getColor = () => {
    if (percentage >= 70) return 'bg-risk-high';
    if (percentage >= 40) return 'bg-risk-medium';
    return 'bg-risk-low';
  };

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <div className="progress-bar flex-1">
        <div
          className={cn('progress-bar-fill', getColor())}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-sm font-medium tabular-nums w-12 text-right">
          {percentage.toFixed(0)}%
        </span>
      )}
    </div>
  );
}
