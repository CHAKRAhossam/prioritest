import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus, LucideIcon } from 'lucide-react';

interface KPICardProps {
  label: string;
  value: string | number;
  trend?: number;
  trendLabel?: string;
  icon: LucideIcon;
  color?: 'default' | 'success' | 'warning' | 'danger';
  className?: string;
}

export function KPICard({
  label,
  value,
  trend,
  trendLabel,
  icon: Icon,
  color = 'default',
  className,
}: KPICardProps) {
  const getTrendIcon = () => {
    if (trend === undefined) return null;
    if (trend > 0) return <TrendingUp className="h-3 w-3" />;
    if (trend < 0) return <TrendingDown className="h-3 w-3" />;
    return <Minus className="h-3 w-3" />;
  };

  const getTrendColor = () => {
    if (trend === undefined) return '';
    // For certain metrics, negative trends are good (e.g., bugs, debt)
    const isPositiveGood = !['danger'].includes(color);
    if (trend > 0) return isPositiveGood ? 'text-success' : 'text-destructive';
    if (trend < 0) return isPositiveGood ? 'text-destructive' : 'text-success';
    return 'text-muted-foreground';
  };

  const getIconColor = () => {
    switch (color) {
      case 'success':
        return 'text-success bg-success/10';
      case 'warning':
        return 'text-warning bg-warning/10';
      case 'danger':
        return 'text-destructive bg-destructive/10';
      default:
        return 'text-primary bg-primary/10';
    }
  };

  return (
    <div className={cn('kpi-card animate-fade-in', className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">{label}</p>
          <p className="text-3xl font-bold tracking-tight">{value}</p>
          {trend !== undefined && (
            <div className={cn('flex items-center gap-1 text-xs font-medium', getTrendColor())}>
              {getTrendIcon()}
              <span>{Math.abs(trend)}%</span>
              {trendLabel && (
                <span className="text-muted-foreground ml-1">{trendLabel}</span>
              )}
            </div>
          )}
        </div>
        <div className={cn('rounded-lg p-3', getIconColor())}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
