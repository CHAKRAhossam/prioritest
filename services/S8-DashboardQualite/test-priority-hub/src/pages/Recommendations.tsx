import { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { RiskBadge } from '@/components/common/RiskBadge';
import { RiskProgress } from '@/components/common/RiskProgress';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { useToast } from '@/hooks/use-toast';
import { useCreatePrioritization, usePrioritization } from '@/hooks/useApi';
import { useRepository } from '@/context/RepositoryContext';
import {
  Search,
  Download,
  FlaskConical,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  AlertTriangle,
  Clock,
  Target,
  GitBranch,
  ExternalLink,
  Info,
  Plus,
  Trash2,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';

interface RecommendedClass {
  rank: number;
  className: string;
  module: string;
  riskScore: number;
  effortHours: number;
  coverage: number | null;
  criticality: 'high' | 'medium' | 'low';
  isGenerated?: boolean; // Indicates if class is likely generated/non-existent
}

// Default mock data for fallback
const mockRecommendations: RecommendedClass[] = [
  { rank: 1, className: 'UserAuthenticationService', module: 'com.prioritest.auth', riskScore: 0.92, effortHours: 8, coverage: 45, criticality: 'high' },
  { rank: 2, className: 'PaymentProcessor', module: 'com.prioritest.payment', riskScore: 0.89, effortHours: 12, coverage: 38, criticality: 'high' },
  { rank: 3, className: 'DataValidationEngine', module: 'com.prioritest.validation', riskScore: 0.85, effortHours: 6, coverage: 52, criticality: 'medium' },
  { rank: 4, className: 'TransactionManager', module: 'com.prioritest.db', riskScore: 0.78, effortHours: 10, coverage: 41, criticality: 'high' },
  { rank: 5, className: 'RequestHandler', module: 'com.prioritest.api', riskScore: 0.72, effortHours: 5, coverage: 58, criticality: 'medium' },
  { rank: 6, className: 'CacheManager', module: 'com.prioritest.cache', riskScore: 0.65, effortHours: 4, coverage: 62, criticality: 'medium' },
  { rank: 7, className: 'MessageQueue', module: 'com.prioritest.queue', riskScore: 0.58, effortHours: 7, coverage: 55, criticality: 'medium' },
  { rank: 8, className: 'DateFormatter', module: 'com.prioritest.util', riskScore: 0.45, effortHours: 2, coverage: 78, criticality: 'low' },
  { rank: 9, className: 'ConfigLoader', module: 'com.prioritest.config', riskScore: 0.32, effortHours: 3, coverage: 82, criticality: 'low' },
  { rank: 10, className: 'LogManager', module: 'com.prioritest.log', riskScore: 0.25, effortHours: 2, coverage: 88, criticality: 'low' },
];

const strategies = [
  { value: 'maximize_popt20', label: 'Maximize POPT20', description: 'Optimizes the POPT20 score for maximum defect detection' },
  { value: 'top_k_coverage', label: 'Top K Coverage', description: 'Selects K classes with best effort/coverage ratio' },
  { value: 'budget_optimization', label: 'Budget Optimization', description: 'Maximizes coverage within a given hour budget' },
  { value: 'risk_first', label: 'Risk First', description: 'Prioritizes classes with highest risk scores' },
  { value: 'effort_aware', label: 'Effort Aware', description: 'Balances between risk and testing effort' },
];

export default function Recommendations() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { selectedRepo: repoId, selectedBranch, addRepository, setSelectedRepo, repositories } = useRepository();
  const [searchTerm, setSearchTerm] = useState('');
  const [strategy, setStrategy] = useState('risk_first');
  const [currentPage, setCurrentPage] = useState(1);
  const [recommendations, setRecommendations] = useState<RecommendedClass[]>([]);
  const [metrics, setMetrics] = useState({ totalEffort: 0, coverageGain: 0, popt20: 0 });
  const [isFromApi, setIsFromApi] = useState(false);
  const [dataSource, setDataSource] = useState<'real' | 'generated' | 'unknown'>('unknown');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newRepoUrl, setNewRepoUrl] = useState('');
  const [platform, setPlatform] = useState<'github' | 'gitlab'>('github');
  const itemsPerPage = 10;

  // Try to fetch existing prioritization first
  const { data: existingPrioritization, isLoading: isLoadingExisting, error: existingError, refetch: refetchPrioritization } = usePrioritization(
    repoId || '',
    strategy
  );

  // API mutation for creating prioritization
  const createPrioritization = useCreatePrioritization();

  // Check if class names are generated or likely don't exist (from ML service when S2 is not available)
  const isGeneratedClass = (className: string): boolean => {
    // Generated classes follow patterns like:
    // - com.example.* (generic pattern)
    // - org.springframework.samples.petclinic.* (for petclinic, but might be generated)
    // - Classes with suspicious patterns
    const suspiciousPatterns = [
      /^com\.example\./,
      /MarketPlace/,
      /\.Repository$/,
      /^offline\.fallback\./,
      /^mock\./,
      /^test_repo\./,
      /^fake\./,
    ];
    
    return suspiciousPatterns.some(pattern => pattern.test(className));
  };
  
  // Check if a class name looks like it might not exist in the repository
  // This is a heuristic - we can't know for sure without checking the repo
  const mightNotExist = (className: string): boolean => {
    // Classes that are very generic or follow patterns that suggest they're generated
    return isGeneratedClass(className) || 
           className.includes('Controller') && !className.includes('org.springframework.samples.petclinic');
  };

  // Transform API response to our format
  const transformPrioritizationData = (data: any): { recommendations: RecommendedClass[]; metrics: any; isGenerated: boolean } => {
    let hasGeneratedClasses = false;
    
    const transformedData: RecommendedClass[] = data.prioritized_plan.map((item: any, index: number) => {
      const fullClassName = item.class_name;
      const shortName = fullClassName.split('.').pop() || fullClassName;
      const module = fullClassName.substring(0, fullClassName.lastIndexOf('.')) || 'unknown';
      
      // Check if this is a generated class
      if (isGeneratedClass(fullClassName)) {
        hasGeneratedClasses = true;
      }
      
      // Risk score is between 0 and 1, determine criticality correctly
      const riskScore = item.risk_score;
      let criticality: 'high' | 'medium' | 'low';
      if (riskScore >= 0.7) {
        criticality = 'high';
      } else if (riskScore >= 0.4) {
        criticality = 'medium';
      } else {
        criticality = 'low';
      }
      
      // ALWAYS use calculated criticality based on risk score, ignore module_criticality if it's wrong
      // Module criticality might be incorrect, so we prioritize risk score
      const finalCriticality = criticality;
      
      // Coverage should come from actual test coverage data
      // The API might not provide coverage, so we'll show N/A or estimate
      // Don't calculate coverage from risk score as it's misleading
      const actualCoverage = item.coverage || item.estimated_coverage || item.current_coverage || null;
      
      return {
        rank: index + 1,
        className: fullClassName, // Store full class name
        module: module,
        riskScore: riskScore,
        effortHours: Math.round(item.effort_hours * 10) / 10, // Round to 1 decimal
        coverage: actualCoverage !== null ? Math.round(actualCoverage * 100) : null, // Only show if we have real data
        criticality: finalCriticality,
        isGenerated: isGeneratedClass(fullClassName), // Mark if generated
      };
    });

    const transformedMetrics = {
      totalEffort: Math.round(data.metrics.total_effort_hours),
      coverageGain: Math.round(data.metrics.estimated_coverage_gain * 100) / 100,
      popt20: Math.round(data.metrics.popt20_score * 100) / 100,
    };

    // Determine if data is generated based on class names or API response
    const apiSource = (data as any).source;
    const isGenerated = hasGeneratedClasses || apiSource === 'generated_features';

    return { recommendations: transformedData, metrics: transformedMetrics, isGenerated };
  };

  // Define fetchRecommendations before using it in useEffect
  const fetchRecommendations = useCallback(async () => {
    if (!repoId) {
      toast({
        title: 'No repository selected',
        description: 'Please select a repository from the header',
        variant: 'destructive',
      });
      return;
    }

    try {
      const result = await createPrioritization.mutateAsync({
        repository_id: repoId,
        branch: selectedBranch || 'main',
        strategy: strategy,
        constraints: {
          budget_hours: 40,
          target_coverage: 0.85,
        },
      });

      const { recommendations: transformedData, metrics: transformedMetrics, isGenerated } = transformPrioritizationData(result);

      setRecommendations(transformedData);
      setMetrics(transformedMetrics);
      setIsFromApi(true);
      // Set data source based on detection
      setDataSource(isGenerated ? 'generated' : 'real');
      setCurrentPage(1); // Reset pagination
      
      if (isGenerated) {
        toast({
          title: 'Generated data detected',
          description: 'Classes shown are generated. S2 static analysis may still be in progress. Real classes will appear once analysis completes.',
          variant: 'default',
        });
      }

      toast({
        title: 'Recommendations updated',
        description: `Strategy: ${strategies.find(s => s.value === strategy)?.label}`,
      });
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      toast({
        title: 'Failed to fetch recommendations',
        description: 'Using fallback data. Please check your repository selection.',
        variant: 'destructive',
      });
      setIsFromApi(false);
      // Keep using mock/fallback data on error
    }
  }, [repoId, selectedBranch, strategy, createPrioritization, toast]);

  // Auto-refresh when repository or branch changes - reset state first
  useEffect(() => {
    if (repoId) {
      // Reset state when repo/branch changes
      setRecommendations([]);
      setMetrics({ totalEffort: 0, coverageGain: 0, popt20: 0 });
      setIsFromApi(false);
      setDataSource('unknown');
      setCurrentPage(1);
    }
  }, [repoId, selectedBranch]);

  // Use existing prioritization data if available
  useEffect(() => {
    if (existingPrioritization) {
      const { recommendations: transformedData, metrics: transformedMetrics, isGenerated } = transformPrioritizationData(existingPrioritization);
      setRecommendations(transformedData);
      setMetrics(transformedMetrics);
      setIsFromApi(true);
      // Set data source based on detection
      setDataSource(isGenerated ? 'generated' : 'real');
      setCurrentPage(1); // Reset pagination
    } else if (repoId && !isLoadingExisting && !existingPrioritization) {
      // If no existing data and we have a repo, fetch it
      fetchRecommendations();
    }
  }, [existingPrioritization, repoId, selectedBranch, strategy, isLoadingExisting, fetchRecommendations]);

  // Reset pagination when search term changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  const filteredData = recommendations.filter(
    (item) =>
      item.className.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.module.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(filteredData.length / itemsPerPage) || 1;
  const paginatedData = filteredData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleGenerateTests = async (className: string) => {
    // Check if class is likely generated/non-existent
    const isGenerated = isGeneratedClass(className);
    if (isGenerated) {
      const proceed = window.confirm(
        `Warning: The class "${className}" appears to be generated and may not exist in the repository.\n\n` +
        `Do you want to continue? You can paste the code manually in Test Generator.`
      );
      if (!proceed) return;
    }
    
    try {
      // Show loading toast
      const loadingToast = toast({
        title: 'Fetching source code',
        description: `Retrieving code for ${className}...`,
      });

      // Get repository info
      const repo = repositories.find(r => r.id === repoId);
      if (!repo?.url) {
        toast({
          title: 'Repository not found',
          description: 'Cannot fetch source code without repository URL',
          variant: 'destructive',
        });
        return;
      }

      // Extract owner/repo from URL
      const urlMatch = repo.url.match(/(?:github|gitlab)\.com\/([^\/]+\/[^\/]+)/);
      if (!urlMatch) {
        toast({
          title: 'Invalid repository URL',
          description: 'Cannot extract repository information',
          variant: 'destructive',
        });
        return;
      }

      const [owner, repoName] = urlMatch[1].split('/');
      const isGitLab = repo.url.includes('gitlab');
      const branch = selectedBranch || 'main';
      
      // Convert package to path (e.g., com.example.Class -> com/example/Class.java)
      const classPath = className.replace(/\./g, '/') + '.java';
      const shortClassName = className.split('.').pop() || className;
      
      // Try common source paths
      const sourcePaths = [
        `src/main/java/${classPath}`,
        `src/${classPath}`,
        `${classPath}`,
      ];

      let sourceCode: string | null = null;
      let filePath: string | null = null;

      // Try direct paths using raw.githubusercontent.com (no auth needed for public repos)
      for (const path of sourcePaths) {
        try {
          if (isGitLab) {
            // GitLab API
            const gitlabUrl = `https://gitlab.com/api/v4/projects/${encodeURIComponent(`${owner}/${repoName}`)}/repository/files/${encodeURIComponent(path)}/raw?ref=${branch}`;
            const response = await fetch(gitlabUrl);
            if (response.ok) {
              sourceCode = await response.text();
              filePath = path;
              break;
            }
          } else {
            // GitHub - use raw.githubusercontent.com (simpler, no auth needed for public repos)
            const rawUrl = `https://raw.githubusercontent.com/${owner}/${repoName}/${branch}/${path}`;
            const rawResponse = await fetch(rawUrl);
            if (rawResponse.ok) {
              const contentType = rawResponse.headers.get('content-type');
              // Check if it's actually a file (not HTML error page)
              if (contentType && (contentType.includes('text') || contentType.includes('application'))) {
                sourceCode = await rawResponse.text();
                filePath = path;
                break;
              }
            }
            
            // Fallback to GitHub API (JSON with base64)
            const githubUrl = `https://api.github.com/repos/${owner}/${repoName}/contents/${path}?ref=${branch}`;
            const jsonResponse = await fetch(githubUrl);
            if (jsonResponse.ok) {
              const data = await jsonResponse.json();
              if (data.content && data.encoding === 'base64') {
                sourceCode = atob(data.content.replace(/\s/g, ''));
                filePath = path;
                break;
              }
            }
          }
        } catch (error) {
          // Continue to next path
          continue;
        }
      }

      if (sourceCode) {
        // Navigate with both className and sourceCode
        navigate('/test-generator', { 
          state: { 
            className,
            sourceCode,
            filePath,
            repositoryId: repoId,
            branch: selectedBranch,
          } 
        });
        toast({
          title: 'Source code loaded',
          description: `Code for ${className} fetched successfully`,
        });
      } else {
        // Navigate with className only (user can paste code manually)
        const isGenerated = isGeneratedClass(className);
        navigate('/test-generator', { 
          state: { 
            className,
            repositoryId: repoId,
            branch: selectedBranch,
          } 
        });
        toast({
          title: 'Source code not found',
          description: isGenerated 
            ? `The class ${className} appears to be generated and may not exist in the repository. Please paste the code manually or verify the class name.`
            : `The file for ${className} was not found in the repository. You can paste the code manually or use "Fetch from Repository" in Test Generator.`,
          variant: isGenerated ? 'destructive' : 'default',
        });
      }
    } catch (error: any) {
      console.error('Error fetching source code:', error);
      // Navigate anyway with className
      navigate('/test-generator', { 
        state: { 
          className,
          repositoryId: repoId,
          branch: selectedBranch,
        } 
      });
      toast({
        title: 'Error fetching source code',
        description: error.message || 'Please paste the code manually',
        variant: 'destructive',
      });
    }
  };

  const handleExportCSV = () => {
    const headers = ['Rank', 'Class', 'Module', 'Risk Score', 'Effort (h)', 'Coverage', 'Criticality'];
    const rows = filteredData.map((item) => [
      item.rank,
      item.className,
      item.module,
      `${(item.riskScore * 100).toFixed(0)}%`,
      item.effortHours,
      `${item.coverage}%`,
      item.criticality.toUpperCase(),
    ]);

    const csvContent = [headers, ...rows].map((row) => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'prioritest_recommendations.csv';
    link.click();

    toast({
      title: 'Export complete',
      description: `Exported ${filteredData.length} recommendations to CSV`,
    });
  };

  const handleRefresh = () => {
    if (repoId) {
      // Refetch existing prioritization first
      refetchPrioritization();
      // Also trigger new fetch
      fetchRecommendations();
    }
  };
  
  // Auto-refresh every 30 seconds if we have a repo and data is from API
  useEffect(() => {
    if (!repoId || !isFromApi) return;
    
    const interval = setInterval(() => {
      // Silently refresh to get latest data
      refetchPrioritization();
    }, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, [repoId, isFromApi, refetchPrioritization]);

  const handleClearData = () => {
    setRecommendations([]);
    setMetrics({ totalEffort: 0, coverageGain: 0, popt20: 0 });
    setIsFromApi(false);
    setDataSource('unknown');
    setCurrentPage(1);
    setSearchTerm('');
    toast({
      title: 'Data cleared',
      description: 'Recommendations data has been reset',
    });
  };

  const handleAddRepository = async () => {
    if (!newRepoUrl) {
      toast({
        title: 'Error',
        description: 'Please enter a repository URL',
        variant: 'destructive',
      });
      return;
    }

    // Extract repo ID from URL
    let extractedRepoId: string;
    let repoName: string;
    
    try {
      const cleanUrl = newRepoUrl
        .replace(/https?:\/\//, '')
        .replace(/(github|gitlab)\.com\//, '')
        .replace(/\.git$/, '')
        .trim();
      
      const urlParts = cleanUrl.split('/').filter(Boolean);
      
      if (urlParts.length >= 2) {
        repoName = urlParts.slice(0, 2).join('/');
        extractedRepoId = `github_${urlParts.slice(0, 2).join('_')}`;
      } else if (urlParts.length === 1) {
        repoName = urlParts[0];
        extractedRepoId = urlParts[0];
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

    try {
      // Add to context
      addRepository({ 
        id: extractedRepoId, 
        name: repoName,
        url: newRepoUrl
      });
      
      setDialogOpen(false);
      setNewRepoUrl('');

      toast({
        title: 'Repository added',
        description: `Repository "${repoName}" has been added. Fetching recommendations...`,
      });

      // Clear current data first
      setRecommendations([]);
      setMetrics({ totalEffort: 0, coverageGain: 0, popt20: 0 });
      setIsFromApi(false);
      setDataSource('unknown');
      setCurrentPage(1);
      
      // Select the new repository - this will trigger useEffect to fetch data
      setSelectedRepo(extractedRepoId);
    } catch (err) {
      console.error('Failed to add repository:', err);
      toast({
        title: 'Error',
        description: 'Failed to add repository',
        variant: 'destructive',
      });
    }
  };

  const isLoading = isLoadingExisting || createPrioritization.isPending;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Recommendations</h1>
          <p className="text-muted-foreground">
            Priority classes for unit testing based on ML analysis
            {isLoading && <span className="ml-2 text-xs text-primary animate-pulse">(Loading...)</span>}
            {isFromApi && !isLoading && dataSource === 'real' && (
              <span className="ml-2 text-xs text-success font-medium">✓ Live API Data (Real Classes)</span>
            )}
            {isFromApi && !isLoading && dataSource === 'generated' && (
              <span className="ml-2 text-xs text-warning font-medium">⚠ Generated Data (Classes may not exist in repo)</span>
            )}
            {!isFromApi && !isLoading && repoId && (
              <span className="ml-2 text-xs text-muted-foreground">(Fallback data)</span>
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
          <Button variant="outline" onClick={handleClearData} disabled={isLoading}>
            <Trash2 className="mr-2 h-4 w-4" />
            Clear Data
          </Button>
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
                <Button onClick={handleAddRepository} disabled={!newRepoUrl || createPrioritization.isPending}>
                  {createPrioritization.isPending ? 'Adding...' : 'Add Repository'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading || !repoId}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" onClick={handleExportCSV} disabled={!isFromApi || recommendations.length === 0}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
          <Button onClick={() => navigate('/test-generator')} disabled={!isFromApi || recommendations.length === 0}>
            <FlaskConical className="mr-2 h-4 w-4" />
            Generate All
          </Button>
        </div>
      </div>

      {/* Metrics Summary */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <Clock className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Effort</p>
                <p className="text-2xl font-bold">{metrics.totalEffort}h</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-success/10">
                <Target className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Est. Coverage Gain</p>
                <p className="text-2xl font-bold">+{metrics.coverageGain}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-warning/10">
                <AlertTriangle className="h-5 w-5 text-warning" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">POPT20 Score</p>
                <p className="text-2xl font-bold">{metrics.popt20}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Info Card - Explain Generated Data */}
      {dataSource === 'generated' && repoId && (
        <Card className="bg-warning/5 border-warning/20">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-warning mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold mb-1">Generated Data Detected</h3>
                <p className="text-xs text-muted-foreground mb-2">
                  The classes shown are <strong>generated placeholders</strong> because S2 (Static Analysis) hasn't analyzed your repository yet. 
                  These classes (like <code className="text-xs bg-muted px-1 py-0.5 rounded">com.example.MarketPlace.*</code>) are <strong>not real classes</strong> from your repository.
                </p>
                <p className="text-xs text-muted-foreground">
                  <strong>To get real classes:</strong> Wait for S2 to complete analysis (usually 1-2 minutes after adding a repository), then click "Refresh". 
                  Real classes from your codebase will appear automatically once S2 analysis completes.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search classes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex items-center gap-4">
              <Select 
                value={strategy} 
                onValueChange={(newStrategy) => {
                  setStrategy(newStrategy);
                  setCurrentPage(1); // Reset pagination when strategy changes
                }}
              >
                <SelectTrigger className="w-[220px]">
                  <SelectValue placeholder="Strategy" />
                </SelectTrigger>
                <SelectContent>
                  {strategies.map((s) => (
                    <SelectItem key={s.value} value={s.value}>
                      <div className="flex flex-col">
                        <span>{s.label}</span>
                        <span className="text-xs text-muted-foreground">{s.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recommendations Table */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center justify-between">
            <span>
              Prioritization Plan
              <span className="ml-2 text-sm font-normal text-muted-foreground">
                ({filteredData.length} classes)
              </span>
            </span>
            {isLoading && (
              <span className="text-sm font-normal text-muted-foreground flex items-center gap-2">
                <RefreshCw className="h-4 w-4 animate-spin" />
                Loading...
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!repoId ? (
            <div className="text-center py-12 text-muted-foreground">
              <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium mb-2">No Repository Selected</p>
              <p className="text-sm">Please select a repository from the header to view recommendations.</p>
            </div>
          ) : isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <LoadingSkeleton key={i} variant="table" />
              ))}
            </div>
          ) : (
            <>
              <div className="rounded-lg border border-border overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-muted/50 hover:bg-muted/50">
                      <TableHead className="w-16">
                        <Button variant="ghost" size="sm" className="h-8 p-0">
                          Rank
                          <ArrowUpDown className="ml-2 h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>Class</TableHead>
                      <TableHead>Module</TableHead>
                      <TableHead className="w-40">
                        <Button variant="ghost" size="sm" className="h-8 p-0">
                          Risk Score
                          <ArrowUpDown className="ml-2 h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead className="w-24">Effort (h)</TableHead>
                      <TableHead className="w-28">Coverage</TableHead>
                      <TableHead className="w-24">Criticality</TableHead>
                      <TableHead className="w-36 text-right">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedData.length > 0 ? (
                      paginatedData.map((item) => {
                        const shortName = item.className.split('.').pop() || item.className;
                        // Generate GitHub/GitLab link to verify class exists
                        const getClassUrl = (): string | null => {
                          if (!repoId) return null;
                          
                          // Get repository URL from context
                          const repo = repositories.find(r => r.id === repoId);
                          if (!repo?.url) return null;
                          
                          // Extract owner/repo from URL
                          const urlMatch = repo.url.match(/(?:github|gitlab)\.com\/([^\/]+\/[^\/]+)/);
                          if (!urlMatch) return null;
                          
                          const [owner, repoName] = urlMatch[1].split('/');
                          const isGitLab = repo.url.includes('gitlab');
                          const domain = isGitLab ? 'gitlab.com' : 'github.com';
                          const branch = selectedBranch || 'main';
                          
                          // Convert package to path (e.g., com.example.Class -> com/example/Class.java)
                          const classPath = item.className.replace(/\./g, '/') + '.java';
                          
                          // Try common source paths
                          const sourcePaths = [
                            `src/main/java/${classPath}`,
                            `src/${classPath}`,
                            `${classPath}`,
                          ];
                          
                          // Return first valid path (user can try others if needed)
                          return `https://${domain}/${owner}/${repoName}/blob/${branch}/${sourcePaths[0]}`;
                        };
                        
                        const classUrl = getClassUrl();
                        
                        return (
                          <TableRow key={item.rank}>
                            <TableCell className="font-medium text-center">
                              {item.rank}
                            </TableCell>
                            <TableCell className="font-mono text-sm">
                              <div className="flex flex-col gap-1">
                                <div className="flex items-center gap-2">
                                  <span className="font-semibold">{shortName}</span>
                                  {(dataSource === 'generated' || item.isGenerated) && (
                                    <span className="text-xs px-1.5 py-0.5 rounded bg-warning/20 text-warning border border-warning/30" title="This class may not exist in the repository. It might be generated or the file might not be found.">
                                      <AlertTriangle className="h-3 w-3 inline mr-1" />
                                      May not exist
                                    </span>
                                  )}
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className="text-xs text-muted-foreground truncate max-w-[300px]" title={item.className}>
                                    {item.className}
                                  </span>
                                  {classUrl && (
                                    <a
                                      href={classUrl}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-xs text-primary hover:underline flex items-center gap-1"
                                      title="View class in repository"
                                      onClick={(e) => e.stopPropagation()}
                                    >
                                      <ExternalLink className="h-3 w-3" />
                                      View
                                    </a>
                                  )}
                                </div>
                              </div>
                            </TableCell>
                            <TableCell className="text-muted-foreground text-sm max-w-[200px] truncate" title={item.module}>
                              {item.module}
                            </TableCell>
                            <TableCell>
                              <RiskProgress value={item.riskScore} />
                            </TableCell>
                            <TableCell className="text-center">{item.effortHours}h</TableCell>
                            <TableCell className="text-center">
                              {item.coverage !== null ? `${item.coverage}%` : 'N/A'}
                            </TableCell>
                            <TableCell>
                              <RiskBadge level={item.criticality} />
                            </TableCell>
                            <TableCell className="text-right">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleGenerateTests(item.className)}
                              >
                                <FlaskConical className="mr-2 h-3 w-3" />
                                Generate tests
                              </Button>
                            </TableCell>
                          </TableRow>
                        );
                      })
                    ) : (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                          {recommendations.length === 0 ? (
                            <div>
                              <p className="mb-2">No recommendations available</p>
                              <p className="text-xs">Try refreshing or selecting a different repository/strategy</p>
                            </div>
                          ) : (
                            `No classes found matching "${searchTerm}"`
                          )}
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-muted-foreground">
                  Showing {filteredData.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0} -{' '}
                  {Math.min(currentPage * itemsPerPage, filteredData.length)} of{' '}
                  {filteredData.length}
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm">
                    Page {currentPage} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
