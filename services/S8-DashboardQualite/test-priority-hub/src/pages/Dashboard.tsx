import { useState, useEffect } from 'react';
import { KPICard } from '@/components/dashboard/KPICard';
import { CoverageChart } from '@/components/dashboard/CoverageChart';
import { RiskDistributionChart } from '@/components/dashboard/RiskDistributionChart';
import { TopPriorityChart } from '@/components/dashboard/TopPriorityChart';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { useDashboardData, useAllServicesHealth } from '@/hooks/useApi';
import { useRepository } from '@/context/RepositoryContext';
import {
  Shield,
  AlertTriangle,
  FileCode,
  Zap,
  Target,
  Clock,
  RefreshCw,
  Plus,
  Server,
  CheckCircle2,
  XCircle,
} from 'lucide-react';

// Default chart data for fallback
const defaultCoverageTrend = [
  { date: '08 Nov', lineCoverage: 58.2, branchCoverage: 52.1, mutationCoverage: 45.3 },
  { date: '12 Nov', lineCoverage: 59.5, branchCoverage: 53.2, mutationCoverage: 46.1 },
  { date: '16 Nov', lineCoverage: 60.1, branchCoverage: 53.8, mutationCoverage: 46.8 },
  { date: '20 Nov', lineCoverage: 61.3, branchCoverage: 54.2, mutationCoverage: 47.5 },
  { date: '24 Nov', lineCoverage: 61.8, branchCoverage: 54.5, mutationCoverage: 47.9 },
  { date: '28 Nov', lineCoverage: 62.0, branchCoverage: 54.6, mutationCoverage: 48.0 },
  { date: '02 Dec', lineCoverage: 62.3, branchCoverage: 54.7, mutationCoverage: 48.1 },
  { date: '06 Dec', lineCoverage: 62.5, branchCoverage: 54.8, mutationCoverage: 48.2 },
];

// OFFLINE FALLBACK - shows 0 when API is unavailable
const defaultRiskDistribution = [
  { bucket: '0.0 - 0.4', count: 0, color: 'hsl(160, 84%, 39%)' },
  { bucket: '0.4 - 0.7', count: 0, color: 'hsl(38, 92%, 50%)' },
  { bucket: '0.7 - 1.0', count: 0, color: 'hsl(0, 84%, 60%)' },
];

// FALLBACK DATA - Shows "[OFFLINE]" prefix when API is not available
const defaultPriorityClasses = [
  { className: 'OFFLINE.fallback.MockClass1', shortName: '[OFFLINE] MockClass1', riskScore: 0.99, riskLevel: 'high' as const },
  { className: 'OFFLINE.fallback.MockClass2', shortName: '[OFFLINE] MockClass2', riskScore: 0.88, riskLevel: 'high' as const },
  { className: 'OFFLINE.fallback.MockClass3', shortName: '[OFFLINE] MockClass3', riskScore: 0.77, riskLevel: 'high' as const },
  { className: 'OFFLINE.fallback.MockClass4', shortName: '[OFFLINE] MockClass4', riskScore: 0.66, riskLevel: 'medium' as const },
];

export default function Dashboard() {
  const { toast } = useToast();
  const { selectedRepo: repoId, setSelectedRepo: setRepoId, selectedBranch, addRepository } = useRepository();
  const [newRepoUrl, setNewRepoUrl] = useState('');
  const [platform, setPlatform] = useState<'github' | 'gitlab'>('github');
  const [dialogOpen, setDialogOpen] = useState(false);

  // Fetch dashboard data - use repoId AND branch from context
  // Data will automatically refetch when branch changes
  const { data: dashboardData, isLoading, error, refetch, isRefetching } = useDashboardData(repoId, selectedBranch);
  
  console.log('[Dashboard] Current repoId:', repoId, 'Branch:', selectedBranch);
  
  // Track previous branch to detect changes
  const [prevBranch, setPrevBranch] = useState<string | undefined>(selectedBranch);
  
  // Show notification when branch changes (not on initial load)
  useEffect(() => {
    if (prevBranch && prevBranch !== selectedBranch && isLoading) {
      toast({
        title: 'Branch changed',
        description: `Loading data for ${selectedBranch} branch...`,
      });
    }
    setPrevBranch(selectedBranch);
  }, [selectedBranch, isLoading, prevBranch, toast]);

  // Fetch services health
  const { data: servicesHealth } = useAllServicesHealth();

  // Count healthy services
  const healthyServices = servicesHealth
    ? Object.values(servicesHealth).filter((s) => s?.status === 'ok' || s?.status === 'healthy').length
    : 0;
  const totalServices = servicesHealth ? Object.keys(servicesHealth).length : 0;

  // Handle refresh
  const handleRefresh = () => {
    refetch();
    toast({
      title: 'Refreshing data',
      description: 'Fetching latest metrics from services...',
    });
  };

  // Handle adding new repository
  const handleAddRepository = async () => {
    if (!newRepoUrl) {
      toast({
        title: 'Error',
        description: 'Please enter a repository URL',
        variant: 'destructive',
      });
      return;
    }

    // Extract repo ID from URL - handle various URL formats
    let extractedRepoId: string;
    let repoName: string;
    
    try {
      // Remove protocol and domain
      const cleanUrl = newRepoUrl
        .replace(/https?:\/\//, '')
        .replace(/(github|gitlab)\.com\//, '')
        .replace(/\.git$/, '')
        .trim();
      
      const urlParts = cleanUrl.split('/').filter(Boolean);
      
      if (urlParts.length >= 2) {
        // Format: owner/repo or owner/repo/...
        repoName = urlParts.slice(0, 2).join('/');
        // Generate ID: github_owner_repo format for consistency
        extractedRepoId = `github_${urlParts.slice(0, 2).join('_')}`;
      } else if (urlParts.length === 1) {
        // Just repo name - try to infer owner (common cases)
        repoName = urlParts[0];
        // For spring-projects repos, use github_spring-projects_repo
        if (newRepoUrl.includes('spring-projects')) {
          extractedRepoId = `github_spring-projects_${urlParts[0]}`;
        } else {
          extractedRepoId = urlParts[0];
        }
      } else {
        throw new Error('Invalid URL format');
      }
    } catch {
      toast({
        title: 'Error',
        description: 'Invalid repository URL format',
        variant: 'destructive',
      });
      return;
    }

    console.log('[Dashboard] Adding repository:', extractedRepoId);

    try {
      // Add to context first (this will register with S1 and start collection)
      // Prioritization will happen automatically once data is collected
      addRepository({ 
        id: extractedRepoId, 
        name: repoName,
        url: newRepoUrl // Store full URL for fetching real branches
      });
      
      setDialogOpen(false);
      setNewRepoUrl('');

      toast({
        title: 'Repository added',
        description: `Repository "${repoName}" has been added. Collection and analysis will start automatically.`,
      });

      // Note: Prioritization will happen automatically once:
      // 1. S1 collects the repository data
      // 2. S2 analyzes the code  
      // 3. S3 processes coverage data
      // 4. S4 preprocesses features
      // 5. S5 trains the model
      // The user can manually trigger prioritization later or it will happen automatically
    } catch (err) {
      console.error('[Dashboard] Failed to add repository:', err);
      toast({
        title: 'Error',
        description: 'Failed to add repository',
        variant: 'destructive',
      });
    }
  };

  // OFFLINE FALLBACK KPIs - Shows 0 values when API is unavailable
  const defaultKPIs = {
    globalCoverage: 0,
    highRiskClasses: 0,
    testDebt: 0,
    flakyTests: 0,
    defectsAvoided: 0,
    totalEffort: 0,
  };

  // KPI data from API or defaults
  const kpis = dashboardData?.kpis || defaultKPIs;
  const kpiData = [
    {
      label: 'Global Coverage',
      value: `${kpis.globalCoverage.toFixed(1)}%`,
      trend: 3.8,
      trendLabel: 'vs last week',
      icon: Shield,
      color: 'success' as const,
    },
    {
      label: 'High Risk Classes',
      value: kpis.highRiskClasses.toString(),
      trend: -12.5,
      trendLabel: 'vs last week',
      icon: AlertTriangle,
      color: 'danger' as const,
    },
    {
      label: 'Test Debt',
      value: kpis.testDebt.toLocaleString(),
      trend: -8.2,
      trendLabel: 'uncovered lines',
      icon: FileCode,
      color: 'warning' as const,
    },
    {
      label: 'Flaky Tests',
      value: kpis.flakyTests.toString(),
      trend: -15.4,
      trendLabel: 'vs last week',
      icon: Zap,
      color: 'danger' as const,
    },
    {
      label: 'Defects Avoided',
      value: kpis.defectsAvoided.toString(),
      trend: 28.6,
      trendLabel: 'this month',
      icon: Target,
      color: 'success' as const,
    },
    {
      label: 'Total Estimated Effort',
      value: `${kpis.totalEffort}h`,
      icon: Clock,
      color: 'default' as const,
    },
  ];

  // Always render the dashboard - show loading indicator in header if loading
  // This ensures users see content immediately with fallback data
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Main Dashboard</h1>
          <p className="text-muted-foreground">
            Quality and test prioritization overview
            {isLoading && <span className="ml-2 text-xs text-primary animate-pulse">(Loading real-time data...)</span>}
            {error && <span className="ml-2 text-xs text-destructive">(API error - using fallback)</span>}
            {dashboardData?.isFromApi && !isLoading && (
              <span className="ml-2 text-xs text-success font-medium">✓ Live API Data</span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Services Health Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/50 text-sm">
            <Server className="h-4 w-4" />
            <span className="text-muted-foreground">Services:</span>
            <span className={healthyServices === totalServices ? 'text-success' : 'text-warning'}>
              {healthyServices}/{totalServices}
            </span>
            {healthyServices === totalServices ? (
              <CheckCircle2 className="h-4 w-4 text-success" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-warning" />
            )}
          </div>

          {/* Add Repository Dialog */}
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Plus className="mr-2 h-4 w-4" />
                Add Repository
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Repository</DialogTitle>
                <DialogDescription>
                  Connect a GitHub or GitLab repository to analyze
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="platform">Platform</Label>
                  <Select value={platform} onValueChange={(v) => setPlatform(v as 'github' | 'gitlab')}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="github">GitHub</SelectItem>
                      <SelectItem value="gitlab">GitLab</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="repo-url">Repository URL</Label>
                  <Input
                    id="repo-url"
                    placeholder="https://github.com/owner/repository"
                    value={newRepoUrl}
                    onChange={(e) => setNewRepoUrl(e.target.value)}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddRepository} disabled={!newRepoUrl}>
                  Add Repository
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Refresh Button */}
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isRefetching}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isRefetching ? 'animate-spin' : ''}`} />
            {isRefetching ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>
      </div>

      {/* Current Repository & Branch Indicator */}
      <Card className="bg-primary/5 border-primary/20">
        <CardContent className="py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
              <span className="text-sm font-medium">Repository:</span>
              <code className="text-sm bg-muted px-2 py-0.5 rounded">{repoId}</code>
              <span className="text-sm text-muted-foreground">•</span>
              <span className="text-sm font-medium">Branch:</span>
              <code className="text-sm bg-muted px-2 py-0.5 rounded">{selectedBranch}</code>
              {isLoading ? (
                <span className="ml-2 px-2 py-0.5 text-xs font-semibold bg-blue-500/20 text-blue-600 rounded-full animate-pulse">
                  ⟳ Loading...
                </span>
              ) : dashboardData?.isFromApi ? (
                <span className="ml-2 px-2 py-0.5 text-xs font-semibold bg-green-500/20 text-green-600 rounded-full">
                  ✓ LIVE API DATA
                </span>
              ) : (
                <span className="ml-2 px-2 py-0.5 text-xs font-semibold bg-orange-500/20 text-orange-600 rounded-full">
                  ⚠ OFFLINE / FALLBACK
                </span>
              )}
            </div>
            <span className="text-xs text-muted-foreground">
              Last updated: {new Date().toLocaleTimeString()}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {kpiData.map((kpi, index) => (
          <KPICard
            key={index}
            label={kpi.label}
            value={kpi.value}
            trend={kpi.trend}
            trendLabel={kpi.trendLabel}
            icon={kpi.icon}
            color={kpi.color}
          />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <CoverageChart data={dashboardData?.coverageTrend || defaultCoverageTrend} />
        <RiskDistributionChart data={dashboardData?.riskDistribution || defaultRiskDistribution} />
      </div>

      {/* Top Priority Classes */}
      <TopPriorityChart data={dashboardData?.topPriorityClasses || defaultPriorityClasses} />
    </div>
  );
}
