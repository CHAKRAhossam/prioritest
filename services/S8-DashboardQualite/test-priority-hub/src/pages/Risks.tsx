import { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RiskBadge } from '@/components/common/RiskBadge';
import { RiskProgress } from '@/components/common/RiskProgress';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { useToast } from '@/hooks/use-toast';
import { useRepository } from '@/context/RepositoryContext';
import { usePrioritization, useCreatePrioritization } from '@/hooks/useApi';
import api from '@/lib/api/client';
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
  Cell,
  PieChart,
  Pie,
} from 'recharts';
import { AlertTriangle, TrendingUp, TrendingDown, Shield, RefreshCw, GitBranch, Info } from 'lucide-react';

interface RiskClass {
  name: string;
  module: string;
  riskScore: number;
  factors: string[];
}

interface RiskByModule {
  module: string;
  highRisk: number;
  mediumRisk: number;
  lowRisk: number;
}

interface RiskDistribution {
  name: string;
  value: number;
  color: string;
}

// Helper function to extract module from class name
function extractModule(className: string): string {
  const parts = className.split('.');
  if (parts.length > 1) {
    return parts.slice(0, -1).join('.');
  }
  return 'default';
}

// Helper function to get risk level from score
function getRiskLevel(score: number): 'high' | 'medium' | 'low' {
  if (score >= 0.7) return 'high';
  if (score >= 0.4) return 'medium';
  return 'low';
}

// Helper function to generate risk factors from class data
function generateRiskFactors(riskScore: number, effort?: number, coverage?: number | null): string[] {
  const factors: string[] = [];
  
  if (riskScore >= 0.8) {
    factors.push('Very high risk score');
  } else if (riskScore >= 0.6) {
    factors.push('High risk score');
  }
  
  if (effort && effort > 8) {
    factors.push('High complexity');
  }
  
  if (coverage !== null && coverage < 50) {
    factors.push('Low coverage');
  } else if (coverage === null) {
    factors.push('No coverage data');
  }
  
  if (riskScore >= 0.7 && effort && effort > 5) {
    factors.push('High effort required');
  }
  
  if (factors.length === 0) {
    factors.push('Standard risk factors');
  }
  
  return factors;
}

export default function Risks() {
  const { toast } = useToast();
  const { selectedRepo: repoId, selectedBranch, repositories } = useRepository();
  const [isFromApi, setIsFromApi] = useState(false);
  
  // Fetch prioritization data from S6
  const { data: prioritizationData, isLoading: isLoadingPrioritization, refetch: refetchPrioritization } = usePrioritization(
    repoId || '',
    'maximize_popt20'
  );
  
  const { mutate: createPrioritization, isPending: isCreating } = useCreatePrioritization();
  
  const isLoading = isLoadingPrioritization || isCreating;

  // Transform prioritization data to risk data
  const riskData = useMemo(() => {
    // Handle both response formats: prioritized_plan (from API) or classes (legacy)
    const classes = prioritizationData?.prioritized_plan || prioritizationData?.classes || [];
    
    if (!classes || classes.length === 0) {
      setIsFromApi(false);
      return {
        highRiskClasses: [] as RiskClass[],
        riskByModule: [] as RiskByModule[],
        riskDistributionPie: [
          { name: 'High Risk', value: 0, color: 'hsl(var(--risk-high))' },
          { name: 'Medium Risk', value: 0, color: 'hsl(var(--risk-medium))' },
          { name: 'Low Risk', value: 0, color: 'hsl(var(--risk-low))' },
        ] as RiskDistribution[],
        summary: { high: 0, medium: 0, low: 0, avgScore: 0 },
      };
    }

    setIsFromApi(true);
    
    // Calculate risk distribution
    let highCount = 0;
    let mediumCount = 0;
    let lowCount = 0;
    let totalScore = 0;
    
    const highRiskClasses: RiskClass[] = [];
    const moduleRiskMap = new Map<string, { high: number; medium: number; low: number }>();
    
    classes.forEach((cls: any) => {
      const riskScore = cls.risk_score || cls.riskScore || 0;
      const riskLevel = getRiskLevel(riskScore);
      totalScore += riskScore;
      
      if (riskLevel === 'high') {
        highCount++;
        const className = cls.class_name || cls.className || 'Unknown';
        const module = extractModule(className);
        highRiskClasses.push({
          name: className.split('.').pop() || className,
          module: module,
          riskScore: riskScore,
          factors: generateRiskFactors(riskScore, cls.effort_hours || cls.effortHours, cls.coverage),
        });
      } else if (riskLevel === 'medium') {
        mediumCount++;
      } else {
        lowCount++;
      }
      
      // Group by module
      const module = extractModule(cls.class_name || cls.className || 'default');
      if (!moduleRiskMap.has(module)) {
        moduleRiskMap.set(module, { high: 0, medium: 0, low: 0 });
      }
      const moduleRisk = moduleRiskMap.get(module)!;
      if (riskLevel === 'high') moduleRisk.high++;
      else if (riskLevel === 'medium') moduleRisk.medium++;
      else moduleRisk.low++;
    });
    
    // Sort high risk classes by score
    highRiskClasses.sort((a, b) => b.riskScore - a.riskScore);
    
    // Convert module map to array
    const riskByModule: RiskByModule[] = Array.from(moduleRiskMap.entries())
      .map(([module, risks]) => ({
        module: module.split('.').pop() || module,
        highRisk: risks.high,
        mediumRisk: risks.medium,
        lowRisk: risks.low,
      }))
      .filter(m => m.highRisk + m.mediumRisk + m.lowRisk > 0)
      .sort((a, b) => (b.highRisk + b.mediumRisk) - (a.highRisk + a.mediumRisk));
    
    // Create pie chart data
    const riskDistributionPie: RiskDistribution[] = [
      { name: 'High Risk', value: highCount, color: 'hsl(var(--risk-high))' },
      { name: 'Medium Risk', value: mediumCount, color: 'hsl(var(--risk-medium))' },
      { name: 'Low Risk', value: lowCount, color: 'hsl(var(--risk-low))' },
    ];
    
    const avgScore = classes.length > 0 ? totalScore / classes.length : 0;
    
    return {
      highRiskClasses: highRiskClasses.slice(0, 20), // Top 20 high risk classes
      riskByModule,
      riskDistributionPie,
      summary: {
        high: highCount,
        medium: mediumCount,
        low: lowCount,
        avgScore: avgScore,
      },
    };
  }, [prioritizationData]);

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
      console.log('[Risks] Auto-refreshing risk data...');
      refetchPrioritization();
    }, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, [isFromApi, repoId, refetchPrioritization]);

  const handleRefresh = useCallback(() => {
    if (repoId) {
      createPrioritization({
        repository_id: repoId,
        branch: selectedBranch,
      });
      toast({
        title: 'Refreshing risk analysis',
        description: 'Fetching latest risk data from S6...',
      });
    } else {
      refetchPrioritization();
    }
  }, [repoId, selectedBranch, createPrioritization, refetchPrioritization, toast]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Risk Analysis</h1>
          <p className="text-muted-foreground">
            High-risk classes requiring priority attention
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
                  Please select a repository from the header to view risk analysis.
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
                <h3 className="text-sm font-semibold mb-1">No Risk Data Available</h3>
                <p className="text-xs text-muted-foreground mb-2">
                  It looks like no risk analysis has been generated for repository <code className="text-xs bg-muted px-1 py-0.5 rounded">{repoId}</code> on branch <code className="text-xs bg-muted px-1 py-0.5 rounded">{selectedBranch}</code> yet.
                </p>
                <p className="text-xs text-muted-foreground">
                  Risk analysis requires code analysis from S2 and ML predictions from S5. Ensure the repository has been analyzed.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Cards */}
      {repoId && (isLoading || isFromApi) && (
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
                    High Risk Classes
                  </CardTitle>
                  <AlertTriangle className="h-4 w-4 text-destructive" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-destructive">{riskData.summary.high}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Classes with risk score ≥ 0.7
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Medium Risk
                  </CardTitle>
                  <AlertTriangle className="h-4 w-4 text-warning" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-warning">{riskData.summary.medium}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Classes with risk score 0.4-0.7
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Low Risk
                  </CardTitle>
                  <Shield className="h-4 w-4 text-success" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-success">{riskData.summary.low}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Classes with risk score &lt; 0.4
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Average Risk Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{riskData.summary.avgScore.toFixed(2)}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    On a scale of 0 to 1
                  </p>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      )}

      {/* Charts Row */}
      {repoId && (isLoading || (isFromApi && (riskData.riskDistributionPie.some(d => d.value > 0) || riskData.riskByModule.length > 0))) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Risk Distribution Pie */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Risk Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <LoadingSkeleton variant="chart" />
              ) : riskData.riskDistributionPie.some(d => d.value > 0) ? (
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={riskData.riskDistributionPie}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={4}
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}`}
                        labelLine={false}
                      >
                        {riskData.riskDistributionPie.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          borderColor: 'hsl(var(--border))',
                          borderRadius: '8px',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  No risk distribution data available
                </div>
              )}
            </CardContent>
          </Card>

          {/* Risk by Module */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Risk by Module</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <LoadingSkeleton variant="chart" />
              ) : riskData.riskByModule.length > 0 ? (
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={riskData.riskByModule} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                      <XAxis type="number" tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                      <YAxis 
                        type="category" 
                        dataKey="module" 
                        tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                        width={80}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          borderColor: 'hsl(var(--border))',
                          borderRadius: '8px',
                        }}
                      />
                      <Bar dataKey="highRisk" stackId="a" fill="hsl(var(--risk-high))" name="High" />
                      <Bar dataKey="mediumRisk" stackId="a" fill="hsl(var(--risk-medium))" name="Medium" />
                      <Bar dataKey="lowRisk" stackId="a" fill="hsl(var(--risk-low))" name="Low" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  No module risk data available
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* High Risk Classes Table */}
      {repoId && (isLoading || (isFromApi && riskData.highRiskClasses.length > 0)) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">High Risk Classes</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <LoadingSkeleton variant="table" />
            ) : riskData.highRiskClasses.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Class</TableHead>
                    <TableHead>Module</TableHead>
                    <TableHead className="w-48">Risk Score</TableHead>
                    <TableHead>Level</TableHead>
                    <TableHead>Risk Factors</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {riskData.highRiskClasses.map((cls, index) => (
                    <TableRow key={`${cls.name}-${index}`}>
                      <TableCell className="font-mono text-sm font-medium">{cls.name}</TableCell>
                      <TableCell className="text-muted-foreground text-sm">{cls.module}</TableCell>
                      <TableCell>
                        <RiskProgress value={cls.riskScore} />
                      </TableCell>
                      <TableCell>
                        <RiskBadge level={getRiskLevel(cls.riskScore)} />
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {cls.factors.map((factor, i) => (
                            <span key={i} className="text-xs bg-muted px-2 py-0.5 rounded">
                              {factor}
                            </span>
                          ))}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No high risk classes found
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
