import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

interface RiskBadgeProps {
  level: 'high' | 'medium' | 'low';
  className?: string;
}

const levelLabels = {
  high: 'HIGH',
  medium: 'MEDIUM',
  low: 'LOW',
};

export function RiskBadge({ level, className }: RiskBadgeProps) {
  return (
    <Badge
      variant="outline"
      className={cn(
        'font-semibold text-xs uppercase',
        {
          'risk-badge-high': level === 'high',
          'risk-badge-medium': level === 'medium',
          'risk-badge-low': level === 'low',
        },
        className
      )}
    >
      {levelLabels[level]}
    </Badge>
  );
}
