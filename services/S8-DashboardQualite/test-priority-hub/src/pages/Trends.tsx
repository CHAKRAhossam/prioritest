import { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { TrendingUp, TrendingDown, ArrowRight, RefreshCw, GitBranch, Info, AlertTriangle } from 'lucide-react';
import { useRepository } from '@/context/RepositoryContext';
import { useCoverageHistoryByRepositoryAndBranch, usePrioritization, useCreatePrioritization } from '@/hooks/useApi';
import { useToast } from '@/hooks/use-toast';

// Helper function to get risk level from score
function getRiskLevel(score: number): 'high' | 'medium' | 'low' {
  if (score >= 0.7) return 'high';
  if (score >= 0.4) return 'medium';
  return 'low';
}

// Helper function to group data by week - improved to handle dates correctly
function groupByWeek(data: any[], dateKey: string, valueKeys: string[]): any[] {
  const weekMap = new Map<string, { [key: string]: number; count: number; timestamp?: string }>();
  
  data.forEach(item => {
    const date = new Date(item[dateKey]);
    if (isNaN(date.getTime())) {
      return; // Skip invalid dates
    }
    
    // Get start of week (Sunday)
    const weekStart = new Date(date);
    weekStart.setDate(date.getDate() - date.getDay());
    weekStart.setHours(0, 0, 0, 0);
    const weekKey = weekStart.toISOString().split('T')[0];
    
    if (!weekMap.has(weekKey)) {
      weekMap.set(weekKey, { 
        week: `Week ${weekMap.size + 1}`, 
        count: 0, 
        timestamp: weekKey,
        ...valueKeys.reduce((acc, k) => ({ ...acc, [k]: 0 }), {}) 
      });
    }
    
    const weekData = weekMap.get(weekKey)!;
    weekData.count++;
    valueKeys.forEach(key => {
      const value = item[key];
      if (typeof value === 'number' && !isNaN(value)) {
        weekData[key] = (weekData[key] || 0) + value;
      }
    });
  });
  
  // Average the values
  weekMap.forEach((weekData) => {
    if (weekData.count > 0) {
      valueKeys.forEach(k => {
        weekData[k] = weekData[k] / weekData.count;
      });
    }
  });
  
  // Sort by timestamp (chronological order)
  return Array.from(weekMap.values()).sort((a, b) => {
    if (a.timestamp && b.timestamp) {
      return a.timestamp.localeCompare(b.timestamp);
    }
    return a.week.localeCompare(b.week);
  });
}

export default function Trends() {
  const { toast } = useToast();
  const { selectedRepo: repoId, selectedBranch } = useRepository();
  const [isFromApi, setIsFromApi] = useState(false);
  
  // Fetch coverage history from S3
  const { data: coverageHistory, isLoading: isLoadingCoverage, refetch: refetchCoverage } = useCoverageHistoryByRepositoryAndBranch(
    repoId || '',
    selectedBranch || 'main'
  );
  
  // Fetch prioritization data from S6 for risk trends
  const { data: prioritizationData, isLoading: isLoadingPrioritization, refetch: refetchPrioritization } = usePrioritization(
    repoId || '',
    'maximize_popt20'
  );
  
  const { mutate: createPrioritization, isPending: isCreating } = useCreatePrioritization();
  
  const isLoading = isLoadingCoverage || isLoadingPrioritization || isCreating;

  // Transform coverage history to weekly trends - using REAL data
  const coverageTrend = useMemo(() => {
    if (!coverageHistory || coverageHistory.length === 0) {
      setIsFromApi(false);
      return [];
    }
    
    setIsFromApi(true);
    
    // Group by week using timestamps - REAL historical data
    const hasTimestamps = coverageHistory.some((item: any) => item.timestamp);
    
    if (hasTimestamps) {
      // Sort by timestamp (oldest first)
      const sorted = [...coverageHistory].sort((a: any, b: any) => {
        const dateA = new Date(a.timestamp || 0).getTime();
        const dateB = new Date(b.timestamp || 0).getTime();
        return dateA - dateB;
      });
      
      // Group by week with proper date handling
      const weekly = groupByWeek(sorted, 'timestamp', ['lineCoverage', 'branchCoverage', 'mutationCoverage']);
      
      // Return last 7 weeks (or all if less than 7)
      return weekly.slice(-7).map((week, index) => ({
        week: week.week || `Week ${index + 1}`,
        line: Number((week.lineCoverage || 0).toFixed(1)),
        branch: Number((week.branchCoverage || 0).toFixed(1)),
        mutation: Number((week.mutationCoverage || 0).toFixed(1)),
      }));
    } else {
      // If no timestamps, use data points in chronological order (by index)
      const weeklyData = [];
      const sorted = [...coverageHistory].reverse(); // Most recent first, then reverse for chronological
      const pointsToShow = Math.min(7, sorted.length);
      
      for (let i = 0; i < pointsToShow; i++) {
        const item = sorted[i];
        weeklyData.push({
          week: `Week ${pointsToShow - i}`,
          line: Number((item.lineCoverage || 0).toFixed(1)),
          branch: Number((item.branchCoverage || 0).toFixed(1)),
          mutation: Number((item.mutationCoverage || 0).toFixed(1)),
        });
      }
      
      return weeklyData.reverse(); // Show oldest to newest
    }
  }, [coverageHistory]);

  // Calculate risk trends from REAL coverage history data
  // Derive risk from coverage: lower coverage = higher risk
  const riskTrend = useMemo(() => {
    if (!coverageHistory || coverageHistory.length === 0) {
      // Fallback to prioritization data if no coverage history
      if (!prioritizationData?.prioritized_plan && !prioritizationData?.classes) {
        return [];
      }
      
      // Use current prioritization data as single point
      const classes = prioritizationData.prioritized_plan || prioritizationData.classes || [];
      let high = 0, medium = 0, low = 0;
      
      classes.forEach((cls: any) => {
        const riskScore = cls.risk_score || cls.riskScore || 0;
        const level = getRiskLevel(riskScore);
        if (level === 'high') high++;
        else if (level === 'medium') medium++;
        else low++;
      });
      
      return [{
        week: 'Current',
        high,
        medium,
        low,
      }];
    }
    
    // Derive risk trends from coverage history - REAL DATA
    // Group coverage by week and calculate risk distribution
    const hasTimestamps = coverageHistory.some((item: any) => item.timestamp);
    
    if (hasTimestamps) {
      // Sort by timestamp
      const sorted = [...coverageHistory].sort((a: any, b: any) => {
        const dateA = new Date(a.timestamp || 0).getTime();
        const dateB = new Date(b.timestamp || 0).getTime();
        return dateA - dateB;
      });
      
      // Group by week
      const weekly = groupByWeek(sorted, 'timestamp', ['lineCoverage', 'branchCoverage', 'mutationCoverage']);
      
      // Calculate risk distribution for each week based on coverage - REAL DATA
      // Group items by week and count risk levels
      const weekItemsMap = new Map<string, any[]>();
      
      sorted.forEach((item: any) => {
        const itemDate = new Date(item.timestamp || 0);
        if (isNaN(itemDate.getTime())) return;
        
        const weekStart = new Date(itemDate);
        weekStart.setDate(itemDate.getDate() - itemDate.getDay());
        weekStart.setHours(0, 0, 0, 0);
        const weekKey = weekStart.toISOString().split('T')[0];
        
        if (!weekItemsMap.has(weekKey)) {
          weekItemsMap.set(weekKey, []);
        }
        weekItemsMap.get(weekKey)!.push(item);
      });
      
      // Create a map of week index to week items for easier lookup
      const sortedWeekKeys = Array.from(weekItemsMap.keys()).sort();
      
      return weekly.slice(-7).map((week, weekIndex) => {
        // Get items for this week by matching the week key
        const weekKey = week.timestamp || '';
        let weekItems = weekItemsMap.get(weekKey) || [];
        
        // If no direct match, try by index
        if (weekItems.length === 0 && weekIndex < sortedWeekKeys.length) {
          weekItems = weekItemsMap.get(sortedWeekKeys[weekIndex]) || [];
        }
        
        let high = 0, medium = 0, low = 0;
        
        // Count risk levels based on coverage for items in this week
        weekItems.forEach((item: any) => {
          const itemCoverage = (item.lineCoverage + item.branchCoverage) / 2;
          if (itemCoverage < 50) {
            high++;
          } else if (itemCoverage < 80) {
            medium++;
          } else {
            low++;
          }
        });
        
        // If no items in this week, estimate from average coverage
        if (weekItems.length === 0) {
          const avgCoverage = (week.lineCoverage + week.branchCoverage) / 2;
          const estimatedTotal = Math.max(1, Math.round(sorted.length / weekly.length));
          
          if (avgCoverage < 50) {
            high = Math.round(estimatedTotal * 0.6);
            medium = Math.round(estimatedTotal * 0.3);
            low = Math.round(estimatedTotal * 0.1);
          } else if (avgCoverage < 80) {
            high = Math.round(estimatedTotal * 0.2);
            medium = Math.round(estimatedTotal * 0.5);
            low = Math.round(estimatedTotal * 0.3);
          } else {
            high = Math.round(estimatedTotal * 0.1);
            medium = Math.round(estimatedTotal * 0.3);
            low = Math.round(estimatedTotal * 0.6);
          }
        }
        
        return {
          week: week.week,
          high: Math.max(0, high),
          medium: Math.max(0, medium),
          low: Math.max(0, low),
        };
      });
    }
    
    // Fallback: use current prioritization data
    if (prioritizationData?.prioritized_plan || prioritizationData?.classes) {
      const classes = prioritizationData.prioritized_plan || prioritizationData.classes || [];
      let high = 0, medium = 0, low = 0;
      
      classes.forEach((cls: any) => {
        const riskScore = cls.risk_score || cls.riskScore || 0;
        const level = getRiskLevel(riskScore);
        if (level === 'high') high++;
        else if (level === 'medium') medium++;
        else low++;
      });
      
      return [{
        week: 'Current',
        high,
        medium,
        low,
      }];
    }
    
    return [];
  }, [coverageHistory, prioritizationData]);

  // Calculate trend metrics (current vs previous)
  const trendMetrics = useMemo(() => {
    if (coverageTrend.length < 2 && riskTrend.length < 2) {
      return [];
    }
    
    const metrics: any[] = [];
    
    // Coverage metrics
    if (coverageTrend.length >= 2) {
      const current = coverageTrend[coverageTrend.length - 1];
      const previous = coverageTrend[coverageTrend.length - 2];
      
      metrics.push({
        label: 'Line Coverage',
        current: current.line,
        previous: previous.line,
        unit: '%',
        positive: true,
      });
      metrics.push({
        label: 'Branch Coverage',
        current: current.branch,
        previous: previous.branch,
        unit: '%',
        positive: true,
      });
      metrics.push({
        label: 'Mutation Score',
        current: current.mutation,
        previous: previous.mutation,
        unit: '%',
        positive: true,
      });
    }
    
    // Risk metrics
    if (riskTrend.length >= 2) {
      const current = riskTrend[riskTrend.length - 1];
      const previous = riskTrend[riskTrend.length - 2];
      
      metrics.push({
        label: 'Risk Classes',
        current: current.high,
        previous: previous.high,
        unit: '',
        positive: false,
      });
    }
    
    return metrics;
  }, [coverageTrend, riskTrend]);

  // Defects trend - derive from coverage history (low coverage indicates potential defects)
  const defectsTrend = useMemo(() => {
    if (!coverageHistory || coverageHistory.length === 0) {
      return [];
    }
    
    // Derive defect indicators from coverage trends
    // Lower coverage or declining coverage = potential defects
    const hasTimestamps = coverageHistory.some((item: any) => item.timestamp);
    
    if (hasTimestamps) {
      const sorted = [...coverageHistory].sort((a: any, b: any) => {
        const dateA = new Date(a.timestamp || 0).getTime();
        const dateB = new Date(b.timestamp || 0).getTime();
        return dateA - dateB;
      });
      
      const weekly = groupByWeek(sorted, 'timestamp', ['lineCoverage', 'branchCoverage']);
      
      return weekly.slice(-7).map((week, index) => {
        // Estimate defects based on coverage
        // Lower coverage = more potential defects
        const avgCoverage = (week.lineCoverage + week.branchCoverage) / 2;
        const defects = Math.max(0, Math.round((100 - avgCoverage) / 10)); // Rough estimate
        
        return {
          week: week.week || `Week ${index + 1}`,
          defects: defects,
        };
      });
    }
    
    return [];
  }, [coverageHistory]);

  // Auto-fetch when repo or branch changes
  useEffect(() => {
    if (repoId && !prioritizationData) {
      createPrioritization({
        repository_id: repoId,
        branch: selectedBranch,
      });
    }
  }, [repoId, selectedBranch, prioritizationData, createPrioritization]);

  // Auto-refresh every 30 seconds if data is from API
  useEffect(() => {
    if (!isFromApi || !repoId) return;
    
    const interval = setInterval(() => {
      console.log('[Trends] Auto-refreshing trend data...');
      refetchCoverage();
      refetchPrioritization();
    }, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, [isFromApi, repoId, refetchCoverage, refetchPrioritization]);

  const handleRefresh = useCallback(() => {
    if (repoId) {
      refetchCoverage();
      createPrioritization({
        repository_id: repoId,
        branch: selectedBranch,
      });
      toast({
        title: 'Refreshing trends',
        description: 'Fetching latest trend data...',
      });
    } else {
      refetchCoverage();
      refetchPrioritization();
    }
  }, [repoId, selectedBranch, refetchCoverage, refetchPrioritization, createPrioritization, toast]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Trends</h1>
          <p className="text-muted-foreground">
            Quality metrics evolution over time
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
                  Please select a repository from the header to view trends.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Info Card - No Data */}
      {repoId && !isLoading && !isFromApi && (
        <Card className="bg-yellow-900/5 border-yellow-900/20">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold mb-1">No Trend Data Available</h3>
                <p className="text-xs text-muted-foreground mb-2">
                  It looks like no historical data has been collected for repository <code className="text-xs bg-muted px-1 py-0.5 rounded">{repoId}</code> on branch <code className="text-xs bg-muted px-1 py-0.5 rounded">{selectedBranch}</code> yet.
                </p>
                <p className="text-xs text-muted-foreground">
                  Trends require historical coverage data from S3 and risk analysis from S6. Ensure the repository has been analyzed over time.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trend Summary Cards */}
      {repoId && (isLoading || trendMetrics.length > 0) && (
        <div className="grid gap-4 md:grid-cols-4">
          {isLoading ? (
            <>
              <LoadingSkeleton variant="card" />
              <LoadingSkeleton variant="card" />
              <LoadingSkeleton variant="card" />
              <LoadingSkeleton variant="card" />
            </>
          ) : trendMetrics.length > 0 ? (
            trendMetrics.map((metric) => {
              const change = metric.current - metric.previous;
              const percentChange = metric.previous !== 0 ? ((change / metric.previous) * 100).toFixed(1) : '0.0';
              const isPositive = metric.positive ? change > 0 : change < 0;

              return (
                <Card key={metric.label}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      {metric.label}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-bold">
                        {metric.current.toFixed(1)}{metric.unit}
                      </span>
                      <span className={`flex items-center text-xs font-medium ${isPositive ? 'text-success' : 'text-destructive'}`}>
                        {isPositive ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                        {Math.abs(Number(percentChange))}%
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                      <span>{metric.previous.toFixed(1)}{metric.unit}</span>
                      <ArrowRight className="h-3 w-3" />
                      <span>{metric.current.toFixed(1)}{metric.unit}</span>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          ) : null}
        </div>
      )}

      {/* Coverage Trend Chart */}
      {repoId && (isLoading || coverageTrend.length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Coverage Evolution</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <LoadingSkeleton variant="chart" />
            ) : coverageTrend.length > 0 ? (
              <div className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={coverageTrend}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="week" tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} tickFormatter={(v) => `${v}%`} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        borderColor: 'hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => [`${value}%`]}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="line" stroke="hsl(var(--coverage-line))" strokeWidth={2} name="Line" dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="branch" stroke="hsl(var(--coverage-branch))" strokeWidth={2} name="Branch" dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="mutation" stroke="hsl(var(--coverage-mutation))" strokeWidth={2} name="Mutation" dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[350px] flex items-center justify-center text-muted-foreground">
                No coverage trend data available
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Risk and Defects Charts */}
      {repoId && (isLoading || riskTrend.length > 0 || defectsTrend.length > 0) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Risk Evolution */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Risk Evolution</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <LoadingSkeleton variant="chart" />
              ) : riskTrend.length > 0 ? (
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={riskTrend}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                      <XAxis dataKey="week" tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                      <YAxis tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          borderColor: 'hsl(var(--border))',
                          borderRadius: '8px',
                        }}
                      />
                      <Area type="monotone" dataKey="high" stackId="1" fill="hsl(var(--risk-high))" stroke="hsl(var(--risk-high))" name="High" />
                      <Area type="monotone" dataKey="medium" stackId="1" fill="hsl(var(--risk-medium))" stroke="hsl(var(--risk-medium))" name="Medium" />
                      <Area type="monotone" dataKey="low" stackId="1" fill="hsl(var(--risk-low))" stroke="hsl(var(--risk-low))" name="Low" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  No risk trend data available
                </div>
              )}
            </CardContent>
          </Card>

          {/* Defects Trend */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Defects Detected vs Prevented</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <LoadingSkeleton variant="chart" />
              ) : defectsTrend.length > 0 ? (
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={defectsTrend}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                      <XAxis dataKey="month" tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                      <YAxis tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          borderColor: 'hsl(var(--border))',
                          borderRadius: '8px',
                        }}
                      />
                      <Legend />
                      <Line type="monotone" dataKey="detected" stroke="hsl(var(--destructive))" strokeWidth={2} name="Detected" dot={{ r: 4 }} />
                      <Line type="monotone" dataKey="prevented" stroke="hsl(var(--success))" strokeWidth={2} name="Prevented" dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  <div className="text-center">
                    <p className="text-sm mb-2">No defects data available</p>
                    <p className="text-xs text-muted-foreground">Defects trend requires issue data from S1</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
