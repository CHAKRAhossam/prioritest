import { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { CreditCard, TrendingDown, AlertTriangle, FileCode, ArrowUpRight, RefreshCw, GitBranch, Info } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useRepository } from '@/context/RepositoryContext';
import { useDebtSummary, useHighDebtClasses, useCoverageHistoryByRepositoryAndBranch } from '@/hooks/useApi';
import { useToast } from '@/hooks/use-toast';

// Helper function to extract module from class name
function extractModule(className: string): string {
  const parts = className.split('.');
  if (parts.length > 1) {
    return parts.slice(0, -1).join('.');
  }
  return 'default';
}

export default function Debt() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { selectedRepo: repoId, selectedBranch } = useRepository();
  const [isFromApi, setIsFromApi] = useState(false);
  
  // Fetch coverage history to get latest commit and calculate debt
  const { data: coverageHistory, isLoading: isLoadingCoverage } = useCoverageHistoryByRepositoryAndBranch(
    repoId || '',
    selectedBranch || 'main'
  );
  
  // Get latest commit SHA from coverage history
  const latestCommitSha = useMemo(() => {
    if (coverageHistory && coverageHistory.length > 0) {
      // Get the most recent commit
      const sorted = [...coverageHistory].sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );
      return sorted[0]?.commitSha || 'latest';
    }
    return 'latest';
  }, [coverageHistory]);
  
  // Fetch debt summary from S3
  const { data: debtSummary, isLoading: isLoadingDebtSummary, refetch: refetchDebtSummary } = useDebtSummary(
    repoId ? latestCommitSha : ''
  );
  
  // Fetch high debt classes from S3 (filtered by repository)
  const { data: highDebtClasses, isLoading: isLoadingHighDebt, refetch: refetchHighDebt } = useHighDebtClasses(
    50.0,
    repoId || undefined
  );
  
  const isLoading = isLoadingDebtSummary || isLoadingHighDebt || isLoadingCoverage;

  // Transform debt classes data - use high debt classes OR derive from coverage history
  // MUST be defined before debtByModule since debtByModule depends on it
  const debtClasses = useMemo(() => {
    // First, try to use high debt classes if available
    let filteredHighDebt = highDebtClasses || [];
    if (repoId && filteredHighDebt.length > 0) {
      filteredHighDebt = filteredHighDebt.filter((debt: any) => 
        debt.repositoryId === repoId
      );
    }
    
    // If we have high debt classes, use them
    if (filteredHighDebt.length > 0) {
      setIsFromApi(true);
      return filteredHighDebt
        .map((debt: any, index: number) => {
          const className = debt.className || debt.class_name || 'Unknown';
          const uncoveredLines = debt.uncoveredLines || 0;
          const module = extractModule(className);
          
          // Estimate total lines from debt score
          const coveragePercent = Math.max(0, 100 - (debt.debtScore || 0));
          const estimatedTotal = coveragePercent > 0 
            ? Math.round(uncoveredLines / (1 - coveragePercent / 100))
            : uncoveredLines * 2;
          const totalLines = Math.max(uncoveredLines, estimatedTotal);
          
          return {
            name: className.split('.').pop() || className,
            fullName: className,
            module: module.split('.').pop() || module,
            uncoveredLines: uncoveredLines,
            totalLines: totalLines || uncoveredLines || 1,
            priority: index + 1,
          };
        })
        .sort((a, b) => b.uncoveredLines - a.uncoveredLines)
        .slice(0, 20);
    }
    
    // Fallback: derive from coverage history if available - REAL DATA
    if (coverageHistory && coverageHistory.length > 0) {
      setIsFromApi(true);
      // Filter by repository
      let filtered = coverageHistory;
      if (repoId) {
        filtered = coverageHistory.filter((item: any) => 
          item.repositoryId === repoId
        );
      }
      
      // Get unique classes with their coverage data (keep most recent)
      const classMap = new Map<string, any>();
      filtered.forEach((item: any) => {
        const className = item.className || 'Unknown';
        if (!className || className === 'Unknown') return;
        
        if (!classMap.has(className)) {
          classMap.set(className, item);
        } else {
          // Keep the one with worse coverage (lower lineCoverage) or more recent timestamp
          const existing = classMap.get(className)!;
          const existingCoverage = existing.lineCoverage || 100;
          const currentCoverage = item.lineCoverage || 100;
          const existingTime = existing.timestamp ? new Date(existing.timestamp).getTime() : 0;
          const currentTime = item.timestamp ? new Date(item.timestamp).getTime() : 0;
          
          // Prefer worse coverage, or if same, prefer more recent
          if (currentCoverage < existingCoverage || (currentCoverage === existingCoverage && currentTime > existingTime)) {
            classMap.set(className, item);
          }
        }
      });
      
      // Calculate estimated uncovered lines from coverage percentage
      // Estimate: if we have debt summary, distribute totalUncoveredLines proportionally
      // Otherwise, estimate based on coverage percentage (assume average class size)
      const totalUncoveredFromSummary = debtSummary?.totalUncoveredLines || 0;
      const classCount = classMap.size;
      const avgUncoveredPerClass = classCount > 0 ? Math.round(totalUncoveredFromSummary / classCount) : 0;
      
      return Array.from(classMap.values())
        .map((item: any, index: number) => {
          const className = item.className || 'Unknown';
          const lineCoverage = item.lineCoverage || 100;
          const coverageDeficit = 100 - lineCoverage; // Percentage uncovered
          
          // Estimate uncovered lines: use debt summary if available, otherwise estimate
          let uncoveredLines = 0;
          if (totalUncoveredFromSummary > 0 && classCount > 0) {
            // Distribute proportionally based on coverage deficit
            const totalDeficit = Array.from(classMap.values()).reduce((sum, i) => 
              sum + (100 - (i.lineCoverage || 100)), 0
            );
            if (totalDeficit > 0) {
              uncoveredLines = Math.round((coverageDeficit / totalDeficit) * totalUncoveredFromSummary);
            } else {
              uncoveredLines = avgUncoveredPerClass;
            }
          } else {
            // Estimate: assume average class has ~50 lines, uncovered = (100 - coverage) / 100 * 50
            const estimatedTotalLines = 50; // Average estimate
            uncoveredLines = Math.round((coverageDeficit / 100) * estimatedTotalLines);
          }
          
          // Ensure at least 1 uncovered line if coverage is less than 100%
          if (uncoveredLines === 0 && lineCoverage < 100) {
            uncoveredLines = 1;
          }
          
          // Estimate total lines
          const totalLines = uncoveredLines > 0 && coverageDeficit > 0
            ? Math.round((uncoveredLines / coverageDeficit) * 100)
            : uncoveredLines + 10; // Fallback estimate
          
          const module = extractModule(className);
          
          return {
            name: className.split('.').pop() || className,
            fullName: className,
            module: module.split('.').pop() || module,
            uncoveredLines: uncoveredLines,
            totalLines: Math.max(totalLines, uncoveredLines + 1),
            priority: index + 1,
          };
        })
        .filter(item => item.uncoveredLines > 0) // Only show classes with uncovered lines
        .sort((a, b) => b.uncoveredLines - a.uncoveredLines)
        .slice(0, 20);
    }
    
    setIsFromApi(false);
    return [];
  }, [highDebtClasses, coverageHistory, repoId]);

  // Calculate debt by module from debt classes data
  // MUST be defined after debtClasses since it depends on it
  const debtByModule = useMemo(() => {
    // Use debtClasses if available (which may come from high debt or coverage history)
    if (debtClasses.length > 0) {
      setIsFromApi(true);
      const moduleMap = new Map<string, { lines: number; classes: Set<string> }>();
      
      debtClasses.forEach((debt: any) => {
        const module = debt.module || 'default';
        const uncoveredLines = debt.uncoveredLines || 0;
        const fullName = debt.fullName || debt.name || 'Unknown';
        
        if (!moduleMap.has(module)) {
          moduleMap.set(module, { lines: 0, classes: new Set() });
        }
        
        const moduleData = moduleMap.get(module)!;
        moduleData.lines += uncoveredLines;
        moduleData.classes.add(fullName);
      });
      
      return Array.from(moduleMap.entries())
        .map(([module, data]) => ({
          module: module,
          lines: data.lines,
          classes: data.classes.size,
        }))
        .sort((a, b) => b.lines - a.lines)
        .slice(0, 10); // Top 10 modules
    }
    
    // Fallback: try high debt classes directly
    let filteredHighDebt = highDebtClasses || [];
    if (repoId && filteredHighDebt.length > 0) {
      filteredHighDebt = filteredHighDebt.filter((debt: any) => 
        debt.repositoryId === repoId
      );
    }
    
    if (filteredHighDebt.length > 0) {
      setIsFromApi(true);
      const moduleMap = new Map<string, { lines: number; classes: Set<string> }>();
      
      filteredHighDebt.forEach((debt: any) => {
        const className = debt.className || debt.class_name || 'Unknown';
        const module = extractModule(className);
        const uncoveredLines = debt.uncoveredLines || 0;
        
        if (!moduleMap.has(module)) {
          moduleMap.set(module, { lines: 0, classes: new Set() });
        }
        
        const moduleData = moduleMap.get(module)!;
        moduleData.lines += uncoveredLines;
        moduleData.classes.add(className);
      });
      
      return Array.from(moduleMap.entries())
        .map(([module, data]) => ({
          module: module.split('.').pop() || module,
          lines: data.lines,
          classes: data.classes.size,
        }))
        .sort((a, b) => b.lines - a.lines)
        .slice(0, 10);
    }
    
    return [];
  }, [debtClasses, highDebtClasses, repoId]);

  // Calculate summary metrics - use REAL data from debtSummary or derived from classes
  const totalDebt = useMemo(() => {
    // Prefer debt summary data (most accurate)
    if (debtSummary?.totalUncoveredLines && debtSummary.totalUncoveredLines > 0) {
      setIsFromApi(true);
      return debtSummary.totalUncoveredLines;
    }
    // Fallback to sum from modules or classes
    return debtByModule.reduce((acc, m) => acc + m.lines, 0) || 
           debtClasses.reduce((acc, c) => acc + (c.uncoveredLines || 0), 0) || 0;
  }, [debtByModule, debtSummary, debtClasses]);

  const totalClasses = useMemo(() => {
    // Prefer debt summary data
    if (debtSummary?.totalClasses && debtSummary.totalClasses > 0) {
      setIsFromApi(true);
      return debtSummary.totalClasses;
    }
    // Fallback to count of debt classes
    return debtClasses.length || 0;
  }, [debtSummary, debtClasses]);
  
  const averageDebtScore = useMemo(() => {
    if (debtSummary?.averageDebtScore !== undefined) {
      setIsFromApi(true);
      return debtSummary.averageDebtScore;
    }
    return 0;
  }, [debtSummary]);

  // Auto-calculate debt if it doesn't exist
  useEffect(() => {
    if (!repoId || !latestCommitSha || latestCommitSha === 'latest' || isLoading) return;
    
    // Check if debt summary exists, if not, calculate it
    if (debtSummary && debtSummary.totalClasses === 0 && latestCommitSha) {
      // Try to calculate debt using API client
      const calculateDebt = async () => {
        try {
          const response = await api.calculateTestDebt(latestCommitSha);
          if (response.data) {
            console.log('[Debt] Auto-calculated test debt for commit:', latestCommitSha);
            // Refetch after a short delay
            setTimeout(() => {
              refetchDebtSummary();
              refetchHighDebt();
            }, 1000);
          }
        } catch (error) {
          console.warn('[Debt] Could not auto-calculate debt:', error);
        }
      };
      calculateDebt();
    }
  }, [repoId, latestCommitSha, debtSummary, isLoading, refetchDebtSummary, refetchHighDebt]);

  // Auto-refresh every 30 seconds if data is from API
  useEffect(() => {
    if (!isFromApi || !repoId) return;
    
    const interval = setInterval(() => {
      console.log('[Debt] Auto-refreshing debt data...');
      refetchDebtSummary();
      refetchHighDebt();
    }, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, [isFromApi, repoId, refetchDebtSummary, refetchHighDebt]);

  const handleRefresh = useCallback(() => {
    refetchDebtSummary();
    refetchHighDebt();
    toast({
      title: 'Refreshing test debt',
      description: 'Fetching latest debt data from S3...',
    });
  }, [refetchDebtSummary, refetchHighDebt, toast]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dette de Test</h1>
          <p className="text-muted-foreground">
            Lignes de code non couvertes nécessitant des tests
            {isLoading && <span className="ml-2 text-xs text-primary animate-pulse">(Loading...)</span>}
            {isFromApi && !isLoading && (
              <span className="ml-2 text-xs text-success font-medium">✓ Live API Data</span>
            )}
            {!isFromApi && !isLoading && repoId && (
              <span className="ml-2 text-xs text-muted-foreground">(No API data yet)</span>
            )}
          </p>
          {repoId && (
            <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
              <GitBranch className="h-3 w-3" />
              <span>Repository: <code className="text-xs bg-muted px-1.5 py-0.5 rounded">{repoId}</code></span>
              {selectedBranch && (
                <>
                  <span>•</span>
                  <span>Branch: <code className="text-xs bg-muted px-1.5 py-0.5 rounded">{selectedBranch}</code></span>
                </>
              )}
            </div>
          )}
        </div>
        <Button variant="outline" onClick={handleRefresh} disabled={isLoading || !repoId}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Info Card - No Repository */}
      {!repoId && (
        <Card className="bg-blue-900/5 border-blue-900/20">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-blue-500 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold mb-1">No Repository Selected</h3>
                <p className="text-xs text-muted-foreground">
                  Please select a repository from the header to view test debt analysis.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Cards - Show if we have data from API or debt summary */}
      {repoId && (isLoading || isFromApi || debtSummary || debtClasses.length > 0) && (
        <div className="grid gap-4 md:grid-cols-4">
          {isLoading ? (
            <>
              <LoadingSkeleton variant="card" />
              <LoadingSkeleton variant="card" />
              <LoadingSkeleton variant="card" />
              <LoadingSkeleton variant="card" />
            </>
          ) : (
            <>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Dette Totale
                  </CardTitle>
                  <CreditCard className="h-4 w-4 text-warning" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{totalDebt.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground mt-1">lignes non couvertes</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Classes Affectées
                  </CardTitle>
                  <FileCode className="h-4 w-4 text-primary" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{totalClasses}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {debtSummary?.totalClasses ? `sur ${debtSummary.totalClasses} classes totales` : 'classes avec dette'}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Score Moyen de Dette
                  </CardTitle>
                  <TrendingDown className="h-4 w-4 text-success" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-warning">{averageDebtScore.toFixed(1)}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {debtSummary?.highDebtClasses ? `${debtSummary.highDebtClasses} classes à haute dette` : 'score moyen'}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Effort Estimé
                  </CardTitle>
                  <AlertTriangle className="h-4 w-4 text-warning" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{Math.round(totalDebt / 10)}h</div>
                  <p className="text-xs text-muted-foreground mt-1">estimation (10 lignes/h)</p>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      )}

      {/* Debt by Module Chart */}
      {repoId && (isLoading || debtByModule.length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Dette par Module</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <LoadingSkeleton variant="chart" />
            ) : debtByModule.length > 0 ? (
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={debtByModule}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="module" tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                    <YAxis tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        borderColor: 'hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => [`${value} lignes`, 'Dette']}
                    />
                    <Bar dataKey="lines" fill="hsl(var(--warning))" name="Lignes non couvertes" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                No module debt data available
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Debt Classes Table */}
      {repoId && (isLoading || debtClasses.length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Classes avec le Plus de Dette</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <LoadingSkeleton variant="table" />
            ) : debtClasses.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">Priorité</TableHead>
                    <TableHead>Classe</TableHead>
                    <TableHead>Module</TableHead>
                    <TableHead>Lignes Non Couvertes</TableHead>
                    <TableHead>Couverture</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {debtClasses.map((cls) => {
                    const coverage = cls.totalLines > 0 
                      ? ((cls.totalLines - cls.uncoveredLines) / cls.totalLines) * 100 
                      : 0;
                    return (
                      <TableRow key={`${cls.name}-${cls.priority}`}>
                        <TableCell className="font-medium text-center">{cls.priority}</TableCell>
                        <TableCell className="font-mono text-sm">{cls.name}</TableCell>
                        <TableCell className="text-muted-foreground">{cls.module}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <span className="text-warning font-medium">{cls.uncoveredLines}</span>
                            <span className="text-muted-foreground">/ {cls.totalLines}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Progress value={coverage} className="w-20 h-2" />
                            <span className="text-sm">{coverage.toFixed(0)}%</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => navigate('/test-generator', { 
                              state: { className: cls.fullName || cls.name } 
                            })}
                          >
                            <ArrowUpRight className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No debt classes found
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
