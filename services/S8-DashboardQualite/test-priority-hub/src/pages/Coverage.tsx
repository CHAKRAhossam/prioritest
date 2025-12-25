import { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { CoverageChart } from '@/components/dashboard/CoverageChart';
import { Button } from '@/components/ui/button';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { useToast } from '@/hooks/use-toast';
import { useRepository } from '@/context/RepositoryContext';
import { useCoverageSummary, useCoverageHistoryByRepositoryAndBranch } from '@/hooks/useApi';
import api from '@/lib/api/client';
import { RefreshCw, GitBranch, AlertTriangle, Upload, FileText, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

// Removed default mock data - page now starts empty and loads from API

interface CoverageBarProps {
  value: number;
  color: string;
}

function CoverageBar({ value, color }: CoverageBarProps) {
  return (
    <div className="flex items-center gap-2">
      <Progress value={value} className="h-2 flex-1" style={{ '--progress-color': color } as React.CSSProperties} />
      <span className="text-sm tabular-nums w-12 text-right">{value.toFixed(1)}%</span>
    </div>
  );
}

export default function Coverage() {
  const { toast } = useToast();
  const { selectedRepo: repoId, selectedBranch } = useRepository();
  const [isLoading, setIsLoading] = useState(false);
  const [coverageData, setCoverageData] = useState<Array<{ date: string; lineCoverage: number; branchCoverage: number; mutationCoverage: number }>>([]);
  const [commitCoverage, setCommitCoverage] = useState<Array<{ sha: string; date: string; line: number; branch: number; mutation: number; classes: number }>>([]);
  const [classCoverage, setClassCoverage] = useState<Array<{ name: string; package: string; line: number; branch: number; mutation: number }>>([]);
  const [moduleCoverage, setModuleCoverage] = useState<Array<{ name: string; classes: number; line: number; branch: number; mutation: number }>>([]);
  const [summary, setSummary] = useState({ line: 0, branch: 0, mutation: 0 });
  const [isFromApi, setIsFromApi] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadType, setUploadType] = useState<'jacoco' | 'pit' | 'surefire'>('jacoco');
  const [uploadCommitSha, setUploadCommitSha] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  // Fetch coverage history to get latest commit SHA
  const { data: coverageHistory } = useCoverageHistoryByRepositoryAndBranch(
    repoId || '',
    selectedBranch || 'main'
  );

  // Get latest commit SHA from coverage history
  const latestCommitSha = useMemo(() => {
    if (coverageHistory && coverageHistory.length > 0) {
      // Sort by timestamp (most recent first) and get the first commit SHA
      const sorted = [...coverageHistory].sort((a, b) => {
        const timeA = a.timestamp ? new Date(a.timestamp).getTime() : 0;
        const timeB = b.timestamp ? new Date(b.timestamp).getTime() : 0;
        return timeB - timeA; // Descending order
      });
      return sorted[0]?.commitSha || '';
    }
    return '';
  }, [coverageHistory]);

  // Fetch coverage summary using hook (only if we have a commit SHA)
  const { data: coverageSummary, isLoading: isLoadingSummary, refetch: refetchSummary } = useCoverageSummary(
    latestCommitSha || ''
  );

  // Fetch coverage data from S3 API
  const fetchCoverageData = useCallback(async () => {
    if (!repoId) {
      // Reset to empty if no repo selected
      setCoverageData([]);
      setCommitCoverage([]);
      setClassCoverage([]);
      setModuleCoverage([]);
      setSummary({ line: 0, branch: 0, mutation: 0 });
      setIsFromApi(false);
      return;
    }

    setIsLoading(true);
    try {
      // If we don't have a commit SHA yet, try to get it from coverage history first
      if (!latestCommitSha) {
        // Wait a bit for coverage history to load, or skip this fetch
        setIsLoading(false);
        return;
      }

      // Try to get coverage data for the latest commit
      const response = await api.getCoverageSummary(latestCommitSha);
      if (response.data) {
        const data = response.data;
        
        // Check if we actually have coverage data (not just zeros)
        const hasData = data.totalClasses > 0 && (
          (data.averageLineCoverage > 0) || 
          (data.averageBranchCoverage > 0) || 
          (data.averageMutationScore > 0)
        );
        
        if (!hasData) {
          // API returned data but it's all zeros - no coverage reports uploaded yet
          setSummary({ line: 0, branch: 0, mutation: 0 });
          setCoverageData([]);
          setCommitCoverage([]);
          setClassCoverage([]);
          setModuleCoverage([]);
          setIsFromApi(false);
          
          toast({
            title: 'No coverage data available',
            description: 'No coverage reports have been uploaded for this repository yet. Upload JaCoCo or PIT reports to see coverage metrics.',
            variant: 'default',
          });
          return;
        }
        
        setSummary({
          line: data.averageLineCoverage || 0,
          branch: data.averageBranchCoverage || 0,
          mutation: data.averageMutationScore || 0,
        });
        setIsFromApi(true);

        // Note: Coverage evolution chart will be populated from coverageHistory via useEffect
        // This ensures we use real historical data instead of simulated data

        // Note: commitCoverage is populated from coverageHistory via useEffect
        // TODO: Fetch actual class coverage and module coverage from S3
        setClassCoverage([]);
        setModuleCoverage([]);

        toast({
          title: 'Coverage data loaded',
          description: `Fetched coverage metrics for ${repoId}`,
        });
      }
    } catch (error) {
      console.log('[Coverage] S3 service may not have data yet:', error);
      // Reset to empty on error
      setCoverageData([]);
      setCommitCoverage([]);
      setClassCoverage([]);
      setModuleCoverage([]);
      setSummary({ line: 0, branch: 0, mutation: 0 });
      setIsFromApi(false);
      
      if (repoId) {
        toast({
          title: 'No coverage data available',
          description: 'S3 service may not have coverage data for this repository yet. Upload JaCoCo/PIT reports to see coverage.',
          variant: 'default',
        });
      }
    } finally {
      setIsLoading(false);
    }
  }, [repoId, selectedBranch, latestCommitSha, toast]);

  // Process coverage history to populate commit, class, and module coverage tables
  useEffect(() => {
    if (coverageHistory && coverageHistory.length > 0) {
      // Group coverage history by commit SHA
      const commitMap = new Map<string, Array<typeof coverageHistory[0]>>();
      
      coverageHistory.forEach((item: any) => {
        const commitSha = item.commitSha;
        if (!commitMap.has(commitSha)) {
          commitMap.set(commitSha, []);
        }
        commitMap.get(commitSha)!.push(item);
      });

      // Transform grouped data into commit coverage format
      const commitCoverageData = Array.from(commitMap.entries()).map(([sha, items]) => {
        // Calculate averages for this commit
        const lineCoverage = items.reduce((sum, item) => sum + (item.lineCoverage || 0), 0) / items.length;
        const branchCoverage = items.reduce((sum, item) => sum + (item.branchCoverage || 0), 0) / items.length;
        const mutationCoverage = items.reduce((sum, item) => sum + (item.mutationCoverage || 0), 0) / items.length;
        
        // Get the most recent timestamp for this commit
        const timestamps = items
          .map(item => item.timestamp ? new Date(item.timestamp).getTime() : 0)
          .filter(t => t > 0);
        const latestTimestamp = timestamps.length > 0 ? Math.max(...timestamps) : Date.now();
        const date = new Date(latestTimestamp).toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });

        return {
          sha: sha.substring(0, 8), // Short SHA for display
          date: date,
          line: Number(lineCoverage.toFixed(1)),
          branch: Number(branchCoverage.toFixed(1)),
          mutation: Number(mutationCoverage.toFixed(1)),
          classes: items.length, // Number of classes in this commit
          _timestamp: latestTimestamp, // Store timestamp for sorting
        };
      });

      // Sort by timestamp (most recent first)
      commitCoverageData.sort((a, b) => (b as any)._timestamp - (a as any)._timestamp);
      
      // Remove the temporary timestamp field
      commitCoverageData.forEach(item => delete (item as any)._timestamp);

      setCommitCoverage(commitCoverageData);

      // Group by class name to get latest coverage for each class
      const classMap = new Map<string, typeof coverageHistory[0]>();
      
      coverageHistory.forEach((item: any) => {
        const className = item.className || '';
        if (!className) return;
        
        // Get the most recent entry for this class
        const existing = classMap.get(className);
        if (!existing) {
          classMap.set(className, item);
        } else {
          // Compare timestamps to keep the most recent
          const existingTime = existing.timestamp ? new Date(existing.timestamp).getTime() : 0;
          const itemTime = item.timestamp ? new Date(item.timestamp).getTime() : 0;
          if (itemTime > existingTime) {
            classMap.set(className, item);
          }
        }
      });

      // Transform to class coverage format
      const classCoverageData = Array.from(classMap.entries()).map(([className, item]) => {
        // Extract package name (everything before the last dot)
        const lastDotIndex = className.lastIndexOf('.');
        const packageName = lastDotIndex > 0 ? className.substring(0, lastDotIndex) : 'default';
        const shortClassName = lastDotIndex > 0 ? className.substring(lastDotIndex + 1) : className;

        return {
          name: shortClassName,
          package: packageName,
          line: Number((item.lineCoverage || 0).toFixed(1)),
          branch: Number((item.branchCoverage || 0).toFixed(1)),
          mutation: Number((item.mutationCoverage || 0).toFixed(1)),
          _fullName: className, // Store full name for sorting/grouping
        };
      });

      // Sort by package then class name
      classCoverageData.sort((a, b) => {
        if (a.package !== b.package) {
          return a.package.localeCompare(b.package);
        }
        return a.name.localeCompare(b.name);
      });

      // Remove temporary field
      classCoverageData.forEach(item => delete (item as any)._fullName);

      setClassCoverage(classCoverageData);

      // Group by module/package
      const moduleMap = new Map<string, Array<typeof coverageHistory[0]>>();
      
      coverageHistory.forEach((item: any) => {
        const className = item.className || '';
        if (!className) return;
        
        // Extract package/module name
        const lastDotIndex = className.lastIndexOf('.');
        const moduleName = lastDotIndex > 0 ? className.substring(0, lastDotIndex) : 'default';
        
        if (!moduleMap.has(moduleName)) {
          moduleMap.set(moduleName, []);
        }
        moduleMap.get(moduleName)!.push(item);
      });

      // Transform to module coverage format
      const moduleCoverageData = Array.from(moduleMap.entries()).map(([moduleName, items]) => {
        // Get unique classes in this module (by className)
        const uniqueClasses = new Set(items.map(item => item.className || '').filter(Boolean));
        
        // Calculate averages for this module
        const lineCoverage = items.reduce((sum, item) => sum + (item.lineCoverage || 0), 0) / items.length;
        const branchCoverage = items.reduce((sum, item) => sum + (item.branchCoverage || 0), 0) / items.length;
        const mutationCoverage = items.reduce((sum, item) => sum + (item.mutationCoverage || 0), 0) / items.length;

        return {
          name: moduleName,
          classes: uniqueClasses.size,
          line: Number(lineCoverage.toFixed(1)),
          branch: Number(branchCoverage.toFixed(1)),
          mutation: Number(mutationCoverage.toFixed(1)),
        };
      });

      // Sort by module name
      moduleCoverageData.sort((a, b) => a.name.localeCompare(b.name));

      setModuleCoverage(moduleCoverageData);

      // Generate coverage evolution chart data from historical data
      // Group by date and calculate daily averages
      const dateMap = new Map<string, Array<typeof coverageHistory[0]>>();
      
      coverageHistory.forEach((item: any) => {
        if (!item.timestamp) return;
        
        const date = new Date(item.timestamp);
        const dateKey = date.toLocaleDateString('en-US', { day: '2-digit', month: 'short' });
        
        if (!dateMap.has(dateKey)) {
          dateMap.set(dateKey, []);
        }
        dateMap.get(dateKey)!.push(item);
      });

      // Transform to chart data format, sorted by date
      const chartData = Array.from(dateMap.entries())
        .map(([dateKey, items]) => {
          // Calculate averages for this date
          const lineCoverage = items.reduce((sum, item) => sum + (item.lineCoverage || 0), 0) / items.length;
          const branchCoverage = items.reduce((sum, item) => sum + (item.branchCoverage || 0), 0) / items.length;
          const mutationCoverage = items.reduce((sum, item) => sum + (item.mutationCoverage || 0), 0) / items.length;

          // Get the timestamp for sorting
          const timestamps = items
            .map(item => item.timestamp ? new Date(item.timestamp).getTime() : 0)
            .filter(t => t > 0);
          const avgTimestamp = timestamps.length > 0 
            ? timestamps.reduce((sum, t) => sum + t, 0) / timestamps.length 
            : Date.now();

          return {
            date: dateKey,
            lineCoverage: Number(lineCoverage.toFixed(1)),
            branchCoverage: Number(branchCoverage.toFixed(1)),
            mutationCoverage: Number(mutationCoverage.toFixed(1)),
            _timestamp: avgTimestamp,
          };
        })
        .sort((a, b) => a._timestamp - b._timestamp) // Sort by date ascending
        .map(item => {
          // Remove temporary timestamp field
          const { _timestamp, ...rest } = item;
          return rest;
        });

      // If we have historical data, use it; otherwise keep empty (will show "no data" message)
      if (chartData.length > 0) {
        setCoverageData(chartData);
      } else {
        // If no historical data but we have current summary, create a single data point
        if (coverageSummary) {
          const now = new Date();
          const dateKey = now.toLocaleDateString('en-US', { day: '2-digit', month: 'short' });
          setCoverageData([{
            date: dateKey,
            lineCoverage: coverageSummary.averageLineCoverage || 0,
            branchCoverage: coverageSummary.averageBranchCoverage || 0,
            mutationCoverage: coverageSummary.averageMutationScore || 0,
          }]);
        }
      }
    } else {
      setCommitCoverage([]);
      setClassCoverage([]);
      setModuleCoverage([]);
      // Keep existing coverageData if available, otherwise clear it
      if (!coverageHistory || coverageHistory.length === 0) {
        setCoverageData([]);
      }
    }
  }, [coverageHistory, coverageSummary]);

  // Auto-fetch when repo or branch changes
  useEffect(() => {
    fetchCoverageData();
  }, [fetchCoverageData]);

  // Use coverage summary from hook when available
  useEffect(() => {
    if (coverageSummary) {
      setSummary({
        line: coverageSummary.averageLineCoverage || 0,
        branch: coverageSummary.averageBranchCoverage || 0,
        mutation: coverageSummary.averageMutationScore || 0,
      });
      setIsFromApi(true);
    }
  }, [coverageSummary]);

  const handleRefresh = () => {
    refetchSummary();
    fetchCoverageData();
  };

  // Auto-refresh every 30 seconds if we have a repo
  useEffect(() => {
    if (!repoId || !isFromApi) return;
    
    const interval = setInterval(() => {
      refetchSummary();
      fetchCoverageData();
    }, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, [repoId, isFromApi, refetchSummary, fetchCoverageData]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Coverage Analysis</h1>
          <p className="text-muted-foreground">
            Code coverage and mutation testing metrics
            {isLoading && <span className="ml-2 text-xs text-primary animate-pulse">(Loading...)</span>}
            {isFromApi && !isLoading && (
              <span className="ml-2 text-xs text-success font-medium">✓ Live API Data</span>
            )}
            {!isFromApi && !isLoading && repoId && (
              <span className="ml-2 text-xs text-muted-foreground">(No data available)</span>
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
          <Button variant="outline" onClick={() => setUploadDialogOpen(true)} disabled={!repoId}>
            <Upload className="mr-2 h-4 w-4" />
            Upload Report
          </Button>
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading || !repoId}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Upload Coverage Report</DialogTitle>
            <DialogDescription>
              Upload a JaCoCo, PIT mutation testing, or Surefire test results report to S3
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="artifact-type">Report Type</Label>
              <Select value={uploadType} onValueChange={(v) => setUploadType(v as 'jacoco' | 'pit' | 'surefire')}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="jacoco">JaCoCo (Coverage)</SelectItem>
                  <SelectItem value="pit">PIT (Mutation Testing)</SelectItem>
                  <SelectItem value="surefire">Surefire (Test Results - for Flaky Tests)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="commit-sha">Commit SHA</Label>
              <Input
                id="commit-sha"
                placeholder="abc1234 or 'latest'"
                value={uploadCommitSha}
                onChange={(e) => setUploadCommitSha(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Enter commit SHA or leave empty to use latest commit
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="file-upload">Report File</Label>
              <div className="flex items-center gap-2">
                <Input
                  id="file-upload"
                  type="file"
                  accept=".xml"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="cursor-pointer"
                />
                {uploadFile && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setUploadFile(null)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
              {uploadFile && (
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <FileText className="h-3 w-3" />
                  {uploadFile.name} ({(uploadFile.size / 1024).toFixed(1)} KB)
                </p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setUploadDialogOpen(false);
              setUploadFile(null);
              setUploadCommitSha('');
            }}>
              Cancel
            </Button>
            <Button
              onClick={async () => {
                if (!uploadFile || !repoId) {
                  toast({
                    title: 'Error',
                    description: 'Please select a file and ensure a repository is selected',
                    variant: 'destructive',
                  });
                  return;
                }

                setIsUploading(true);
                try {
                  // Get actual commit SHA - use latestCommitSha from coverage history, or require user to provide one
                  let commitSha = uploadCommitSha;
                  if (!commitSha) {
                    if (latestCommitSha) {
                      commitSha = latestCommitSha;
                    } else {
                      toast({
                        title: 'Commit SHA required',
                        description: 'Please enter a commit SHA or wait for coverage history to load.',
                        variant: 'destructive',
                      });
                      setIsUploading(false);
                      return;
                    }
                  }
                  
                  // Use S3 direct upload for coverage reports or Surefire for test results
                  if (uploadType === 'surefire') {
                    await api.uploadSurefireReport(repoId, commitSha, uploadFile, undefined, selectedBranch);
                    toast({
                      title: 'Upload successful',
                      description: 'Surefire test results uploaded. This will help detect flaky tests.',
                    });
                  } else {
                    await api.uploadCoverageReport(uploadType as 'jacoco' | 'pit', repoId, commitSha, uploadFile, undefined, selectedBranch);
                    toast({
                      title: 'Upload successful',
                      description: `${uploadType.toUpperCase()} report uploaded. S3 will process it automatically.`,
                    });
                  }
                  
                  setUploadDialogOpen(false);
                  setUploadFile(null);
                  setUploadCommitSha('');
                  
                  // Refresh coverage data after a short delay
                  setTimeout(() => {
                    refetchSummary();
                    fetchCoverageData();
                  }, 2000);
                } catch (error: any) {
                  console.error('Upload error:', error);
                  toast({
                    title: 'Upload failed',
                    description: error.response?.data?.error || error.message || 'Failed to upload report',
                    variant: 'destructive',
                  });
                } finally {
                  setIsUploading(false);
                }
              }}
              disabled={!uploadFile || !repoId || isUploading}
            >
              {isUploading ? 'Uploading...' : 'Upload'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Line Coverage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-coverage-line">{summary.line.toFixed(1)}%</div>
              <Progress value={summary.line} className="h-2" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Branch Coverage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-coverage-branch">{summary.branch.toFixed(1)}%</div>
              <Progress value={summary.branch} className="h-2" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Mutation Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-3xl font-bold text-coverage-mutation">{summary.mutation.toFixed(1)}%</div>
              <Progress value={summary.mutation} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Coverage Chart */}
      {coverageData.length > 0 ? (
        <CoverageChart data={coverageData} className="mb-6" />
      ) : (
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="text-center py-12 text-muted-foreground">
              <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium mb-2">
                {repoId ? 'No Coverage Data Available' : 'No Repository Selected'}
              </p>
              <p className="text-sm">
                {repoId 
                  ? 'Upload JaCoCo or PIT coverage reports to S3 to see coverage metrics here.'
                  : 'Please select a repository from the header to view coverage data.'}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Detailed Tabs */}
      <Tabs defaultValue="commits" className="space-y-4">
        <TabsList>
          <TabsTrigger value="commits">By Commit</TabsTrigger>
          <TabsTrigger value="classes">By Class</TabsTrigger>
          <TabsTrigger value="modules">By Module</TabsTrigger>
        </TabsList>

        <TabsContent value="commits">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Coverage by Commit</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>SHA</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Line</TableHead>
                    <TableHead>Branch</TableHead>
                    <TableHead>Mutation</TableHead>
                    <TableHead className="text-right">Classes</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {commitCoverage.length > 0 ? (
                    commitCoverage.map((commit) => (
                      <TableRow key={commit.sha}>
                        <TableCell className="font-mono text-sm">{commit.sha}</TableCell>
                        <TableCell>{commit.date}</TableCell>
                        <TableCell>
                          <CoverageBar value={commit.line} color="hsl(var(--coverage-line))" />
                        </TableCell>
                        <TableCell>
                          <CoverageBar value={commit.branch} color="hsl(var(--coverage-branch))" />
                        </TableCell>
                        <TableCell>
                          <CoverageBar value={commit.mutation} color="hsl(var(--coverage-mutation))" />
                        </TableCell>
                        <TableCell className="text-right">{commit.classes}</TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                        <p className="mb-2">No commit coverage data available</p>
                        <p className="text-xs">Upload coverage reports to see commit-by-commit coverage history</p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="classes">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Coverage by Class</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Class</TableHead>
                    <TableHead>Package</TableHead>
                    <TableHead>Line</TableHead>
                    <TableHead>Branch</TableHead>
                    <TableHead>Mutation</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {classCoverage.length > 0 ? (
                    classCoverage.map((cls, index) => (
                      <TableRow key={`${cls.package}.${cls.name}-${index}`}>
                        <TableCell className="font-mono text-sm">{cls.name}</TableCell>
                        <TableCell className="text-muted-foreground text-sm">{cls.package}</TableCell>
                        <TableCell>
                          <CoverageBar value={cls.line} color="hsl(var(--coverage-line))" />
                        </TableCell>
                        <TableCell>
                          <CoverageBar value={cls.branch} color="hsl(var(--coverage-branch))" />
                        </TableCell>
                        <TableCell>
                          <CoverageBar value={cls.mutation} color="hsl(var(--coverage-mutation))" />
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        <p className="mb-2">No class coverage data available</p>
                        <p className="text-xs">Upload coverage reports to see per-class coverage details</p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="modules">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Coverage by Module</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Module</TableHead>
                    <TableHead className="text-right">Classes</TableHead>
                    <TableHead>Line</TableHead>
                    <TableHead>Branch</TableHead>
                    <TableHead>Mutation</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {moduleCoverage.length > 0 ? (
                    moduleCoverage.map((mod) => (
                      <TableRow key={mod.name}>
                        <TableCell className="font-mono text-sm">{mod.name}</TableCell>
                        <TableCell className="text-right">{mod.classes}</TableCell>
                        <TableCell>
                          <CoverageBar value={mod.line} color="hsl(var(--coverage-line))" />
                        </TableCell>
                        <TableCell>
                          <CoverageBar value={mod.branch} color="hsl(var(--coverage-branch))" />
                        </TableCell>
                        <TableCell>
                          <CoverageBar value={mod.mutation} color="hsl(var(--coverage-mutation))" />
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        <p className="mb-2">No module coverage data available</p>
                        <p className="text-xs">Upload coverage reports to see per-module coverage aggregation</p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
