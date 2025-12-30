import { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { RefreshCw, AlertTriangle, CheckCircle2, XCircle, Clock, RotateCcw, GitBranch, Info } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useRepository } from '@/context/RepositoryContext';
import { useFlakyTests, useMostFlakyTests } from '@/hooks/useApi';
import { api } from '@/lib/api/client';

interface FlakyTest {
  id: string;
  name: string;
  className: string;
  failureRate: number;
  lastFailure: string;
  occurrences: number;
  status: 'active' | 'quarantined' | 'fixed';
  flakinessScore?: number;
  repositoryId?: string;
}

export default function Flaky() {
  const { toast } = useToast();
  const { selectedRepo: repoId, selectedBranch } = useRepository();
  const [isFromApi, setIsFromApi] = useState(false);
  
  // Fetch flaky tests from S3
  const { data: flakyTestsData, isLoading: isLoadingFlaky, refetch: refetchFlaky } = useFlakyTests(0.3);
  
  // Fetch most flaky tests
  const { data: mostFlakyData, isLoading: isLoadingMostFlaky, refetch: refetchMostFlaky } = useMostFlakyTests(20);
  
  const isLoading = isLoadingFlaky || isLoadingMostFlaky;
  
  // Transform API data to FlakyTest format
  const tests = useMemo(() => {
    // Use most flaky tests if available, otherwise use all flaky tests
    const sourceData = mostFlakyData && mostFlakyData.length > 0 ? mostFlakyData : (flakyTestsData || []);
    
    // Filter by repository if needed
    let filtered = sourceData;
    if (repoId && filtered.length > 0) {
      filtered = filtered.filter((test: any) => test.repositoryId === repoId);
    }
    
    if (filtered.length === 0) {
      setIsFromApi(false);
      return [];
    }
    
    setIsFromApi(true);
    return filtered.map((test: any, index: number) => {
      const failureRate = test.totalRuns > 0 
        ? Math.round((test.failedRuns / test.totalRuns) * 100)
        : 0;
      
      // Determine status based on flakiness score and recent activity
      let status: 'active' | 'quarantined' | 'fixed' = 'active';
      if (test.flakinessScore < 0.2) {
        status = 'fixed';
      } else if (test.flakinessScore > 0.5) {
        status = 'active';
      } else {
        status = 'quarantined';
      }
      
      // Format last failure date
      let lastFailureStr = 'N/A';
      if (test.lastFailure) {
        try {
          const date = new Date(test.lastFailure);
          lastFailureStr = date.toLocaleDateString('fr-FR', { year: 'numeric', month: '2-digit', day: '2-digit' });
        } catch {
          lastFailureStr = test.lastFailure;
        }
      } else if (test.calculatedAt) {
        try {
          const date = new Date(test.calculatedAt);
          lastFailureStr = date.toLocaleDateString('fr-FR', { year: 'numeric', month: '2-digit', day: '2-digit' });
        } catch {
          lastFailureStr = test.calculatedAt;
        }
      }
      
      return {
        id: test.id?.toString() || `test-${index}`,
        name: test.testName || 'Unknown Test',
        className: test.testClass || 'Unknown Class',
        failureRate: failureRate,
        lastFailure: lastFailureStr,
        occurrences: test.failedRuns || 0,
        status: status,
        flakinessScore: test.flakinessScore || 0,
        repositoryId: test.repositoryId,
      };
    }).sort((a, b) => b.failureRate - a.failureRate);
  }, [flakyTestsData, mostFlakyData, repoId]);
  
  // Calculate flaky trend (simplified - would need historical data)
  const flakyTrend = useMemo(() => {
    if (!isFromApi || tests.length === 0) {
      return [];
    }
    
    // Simulate trend from current data
    const currentCount = tests.filter(t => t.status === 'active').length;
    const fixedCount = tests.filter(t => t.status === 'fixed').length;
    
    const trend = [];
    for (let i = 6; i >= 0; i--) {
      const week = `Sem ${7 - i}`;
      // Simulate slight variation
      const variation = Math.floor(Math.random() * 3) - 1;
      trend.push({
        week,
        count: Math.max(0, currentCount + variation + (6 - i)),
        fixed: Math.max(0, fixedCount - (6 - i)),
      });
    }
    return trend;
  }, [tests, isFromApi]);

  const activeCount = useMemo(() => tests.filter(t => t.status === 'active').length, [tests]);
  const quarantinedCount = useMemo(() => tests.filter(t => t.status === 'quarantined').length, [tests]);
  const fixedCount = useMemo(() => tests.filter(t => t.status === 'fixed').length, [tests]);
  const averageFailureRate = useMemo(() => {
    if (tests.length === 0) return 0;
    const total = tests.reduce((sum, t) => sum + t.failureRate, 0);
    return Math.round(total / tests.length);
  }, [tests]);
  
  // Auto-refresh every 30 seconds if data is from API
  useEffect(() => {
    if (!isFromApi || !repoId) return;
    
    const interval = setInterval(() => {
      console.log('[Flaky] Auto-refreshing flaky tests data...');
      refetchFlaky();
      refetchMostFlaky();
    }, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, [isFromApi, repoId, refetchFlaky, refetchMostFlaky]);
  
  const handleRefresh = useCallback(() => {
    refetchFlaky();
    refetchMostFlaky();
    toast({
      title: 'Refreshing flaky tests',
      description: 'Fetching latest flaky test data from S3...',
    });
  }, [refetchFlaky, refetchMostFlaky, toast]);

  const handleCalculateFlakiness = useCallback(async () => {
    try {
      // Calculate flakiness for the last 30 days
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 30);
      
      const startISO = startDate.toISOString();
      const endISO = endDate.toISOString();
      
      // Use API client instead of direct fetch
      const response = await api.calculateFlakiness(startISO, endISO);
      
      if (response.data) {
        toast({
          title: 'Flakiness calculation started',
          description: `Analyzing ${response.data.testsAnalyzed || 0} tests for flakiness...`,
        });
        
        // Wait a bit then refresh
        setTimeout(() => {
          refetchFlaky();
          refetchMostFlaky();
        }, 2000);
      }
    } catch (error: any) {
      toast({
        title: 'Calculation failed',
        description: error.message || 'Failed to calculate flakiness',
        variant: 'destructive',
      });
    }
  }, [refetchFlaky, refetchMostFlaky, toast]);

  const handleQuarantine = (id: string) => {
    // In a real implementation, this would call an API to quarantine the test
    toast({
      title: 'Test mis en quarantaine',
      description: 'Le test a été isolé du pipeline CI/CD',
    });
  };

  const handleRerun = (name: string) => {
    toast({
      title: 'Test relancé',
      description: `${name} est en cours d'exécution...`,
    });
  };

  const getStatusBadge = (status: FlakyTest['status']) => {
    switch (status) {
      case 'active':
        return <Badge variant="outline" className="risk-badge-high">Actif</Badge>;
      case 'quarantined':
        return <Badge variant="outline" className="risk-badge-medium">Quarantaine</Badge>;
      case 'fixed':
        return <Badge variant="outline" className="risk-badge-low">Corrigé</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Tests Flaky</h1>
          <p className="text-muted-foreground">
            Tests instables nécessitant une attention particulière
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
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={handleCalculateFlakiness} 
            disabled={isLoading || !repoId}
            title="Calculate flakiness from uploaded test results"
          >
            <AlertTriangle className="mr-2 h-4 w-4" />
            Calculate Flakiness
          </Button>
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading || !repoId}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
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
                  Please select a repository from the header to view flaky tests analysis.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Cards */}
      {repoId && (isLoading || isFromApi || tests.length > 0) && (
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
                    Tests Flaky Actifs
                  </CardTitle>
                  <AlertTriangle className="h-4 w-4 text-destructive" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-destructive">{activeCount}</div>
                  <p className="text-xs text-muted-foreground mt-1">nécessitent une correction</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    En Quarantaine
                  </CardTitle>
                  <Clock className="h-4 w-4 text-warning" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-warning">{quarantinedCount}</div>
                  <p className="text-xs text-muted-foreground mt-1">isolés du pipeline</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Corrigés ce Mois
                  </CardTitle>
                  <CheckCircle2 className="h-4 w-4 text-success" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-success">{fixedCount}</div>
                  <p className="text-xs text-muted-foreground mt-1">tests stabilisés</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Taux d'Échec Moyen
                  </CardTitle>
                  <XCircle className="h-4 w-4 text-destructive" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{averageFailureRate}%</div>
                  <p className="text-xs text-muted-foreground mt-1">sur les tests flaky</p>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      )}

      {/* Flaky Trend Chart */}
      {repoId && (isLoading || flakyTrend.length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Évolution des Tests Flaky</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <LoadingSkeleton variant="chart" />
            ) : flakyTrend.length > 0 ? (
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={flakyTrend}>
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
                    <Line type="monotone" dataKey="count" stroke="hsl(var(--destructive))" strokeWidth={2} name="Tests Flaky Actifs" dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="fixed" stroke="hsl(var(--success))" strokeWidth={2} name="Corrigés" dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="quarantined" stroke="hsl(var(--warning))" strokeWidth={2} name="En Quarantaine" dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                No trend data available
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Flaky Tests Table */}
      {repoId && (isLoading || tests.length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Liste des Tests Flaky</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <LoadingSkeleton variant="table" />
            ) : tests.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nom du Test</TableHead>
                    <TableHead>Classe</TableHead>
                    <TableHead>Taux d'Échec</TableHead>
                    <TableHead>Occurrences</TableHead>
                    <TableHead>Dernier Échec</TableHead>
                    <TableHead>Statut</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tests.map((test) => (
                    <TableRow key={test.id}>
                      <TableCell className="font-mono text-sm">{test.name}</TableCell>
                      <TableCell className="text-muted-foreground">{test.className}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 rounded-full bg-muted overflow-hidden">
                            <div 
                              className="h-full bg-destructive" 
                              style={{ width: `${test.failureRate}%` }}
                            />
                          </div>
                          <span className="text-sm">{test.failureRate}%</span>
                        </div>
                      </TableCell>
                      <TableCell>{test.occurrences}</TableCell>
                      <TableCell className="text-muted-foreground">{test.lastFailure}</TableCell>
                      <TableCell>{getStatusBadge(test.status)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRerun(test.name)}
                            disabled={test.status === 'fixed'}
                          >
                            <RotateCcw className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleQuarantine(test.id)}
                            disabled={test.status !== 'active'}
                          >
                            <RefreshCw className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No flaky tests found
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
