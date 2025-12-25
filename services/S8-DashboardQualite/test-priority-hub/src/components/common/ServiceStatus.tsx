import { cn } from '@/lib/utils';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';

interface ServiceStatusProps {
  name: string;
  status: 'healthy' | 'unhealthy' | 'loading';
  version?: string;
  className?: string;
}

export function ServiceStatus({ name, status, version, className }: ServiceStatusProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-between rounded-lg border border-border bg-card p-4',
        className
      )}
    >
      <div className="flex items-center gap-3">
        {status === 'loading' ? (
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        ) : status === 'healthy' ? (
          <CheckCircle2 className="h-5 w-5 text-success" />
        ) : (
          <XCircle className="h-5 w-5 text-destructive" />
        )}
        <div>
          <p className="font-medium">{name}</p>
          {version && (
            <p className="text-xs text-muted-foreground">v{version}</p>
          )}
        </div>
      </div>
      <span
        className={cn(
          'text-xs font-medium uppercase',
          status === 'healthy' ? 'text-success' : status === 'unhealthy' ? 'text-destructive' : 'text-muted-foreground'
        )}
      >
        {status === 'loading' ? 'Checking...' : status}
      </span>
    </div>
  );
}
