import { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ServiceStatus } from '@/components/common/ServiceStatus';
import { useToast } from '@/hooks/use-toast';
import { useRepository } from '@/context/RepositoryContext';
import { useListRepositories, useRunPreprocessingPipeline, useTrainMLModel, useMLFeatures } from '@/hooks/useApi';
import api from '@/lib/api/client';
import {
  GitBranch,
  Plus,
  Trash2,
  Copy,
  RefreshCw,
  Info,
  Play,
  Loader2,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

interface Repository {
  id: string;
  name: string;
  url: string;
  platform: 'github' | 'gitlab';
  branch: string;
  webhookUrl?: string;
}

interface ServiceHealthState {
  name: string;
  status: 'healthy' | 'unhealthy' | 'loading';
  version?: string;
}

export default function Settings() {
  const { toast } = useToast();
  const { repositories: contextRepos, addRepository, removeRepository } = useRepository();
  const { data: apiRepos, isLoading: isLoadingRepos, refetch: refetchRepos } = useListRepositories();
  const [addRepoDialogOpen, setAddRepoDialogOpen] = useState(false);
  const [newRepoUrl, setNewRepoUrl] = useState('');
  const [newRepoPlatform, setNewRepoPlatform] = useState<'github' | 'gitlab'>('github');
  const [services, setServices] = useState<ServiceHealthState[]>([
    { name: 'Collection Service (S1)', status: 'loading', version: '1.0.0' },
    { name: 'Static Analysis (S2)', status: 'loading', version: '1.0.0' },
    { name: 'Test History (S3)', status: 'loading', version: '1.0.0' },
    { name: 'Preprocessing (S4)', status: 'loading', version: '1.0.0' },
    { name: 'ML Service (S5)', status: 'loading', version: '1.0.0' },
    { name: 'Prioritization Engine (S6)', status: 'loading', version: '1.0.0' },
    { name: 'Test Scaffolder (S7)', status: 'loading', version: '1.0.0' },
  ]);
  
  // Transform API repositories to Settings format
  const repositories = useMemo(() => {
    const repos: Repository[] = [];
    
    // Add repositories from API
    if (apiRepos?.repositories) {
      apiRepos.repositories.forEach((repo: any) => {
        const platform = repo.source === 'gitlab' ? 'gitlab' : 'github';
        repos.push({
          id: repo.id,
          name: repo.name || repo.full_name || repo.id,
          url: repo.url || `https://${platform}.com/${repo.full_name || repo.name}`,
          platform: platform,
          branch: repo.default_branch || 'main',
          webhookUrl: `https://api.prioritest.dev/webhooks/${repo.id}`, // Placeholder
        });
      });
    }
    
    // Add repositories from context that aren't in API
    contextRepos.forEach((repo) => {
      if (!repos.find(r => r.id === repo.id)) {
        const url = repo.url || `https://github.com/${repo.name}`;
        const platform = url.includes('gitlab') ? 'gitlab' : 'github';
        repos.push({
          id: repo.id,
          name: repo.name,
          url: url,
          platform: platform,
          branch: 'main',
          webhookUrl: `https://api.prioritest.dev/webhooks/${repo.id}`, // Placeholder
        });
      }
    });
    
    return repos;
  }, [apiRepos, contextRepos]);

  // Real health check using API
  const checkAllServicesHealth = async () => {
    try {
      const healthResults = await api.checkAllHealth();
      setServices((prev) =>
        prev.map((service, index) => {
          const serviceKey = ['s1', 's2', 's3', 's4', 's5', 's6', 's7'][index];
          const result = healthResults[serviceKey];
          if (result) {
            return {
              ...service,
              status: result.status === 'healthy' ? 'healthy' : 'unhealthy',
              version: result.version || '1.0.0',
            };
          } else {
            return {
              ...service,
              status: 'unhealthy' as const,
              version: '1.0.0',
            };
          }
        })
      );
    } catch (error) {
      console.error('Health check failed:', error);
      setServices((prev) =>
        prev.map((service) => ({ ...service, status: 'unhealthy' as const }))
      );
    }
  };

  useEffect(() => {
    checkAllServicesHealth();
  }, []);

  const handleRefreshHealth = async () => {
    setServices((prev) => prev.map((s) => ({ ...s, status: 'loading' as const })));
    await checkAllServicesHealth();
    toast({
      title: 'Status updated',
      description: 'Service health statuses have been refreshed',
    });
  };

  const handleCopyWebhook = (webhookUrl: string) => {
    navigator.clipboard.writeText(webhookUrl);
    toast({
      title: 'URL copied',
      description: 'Webhook URL has been copied to clipboard',
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

    try {
      // Extract repo name from URL
      const cleanUrl = newRepoUrl
        .replace(/https?:\/\//, '')
        .replace(/(github|gitlab)\.com\//, '')
        .replace(/\.git$/, '')
        .trim();

      const urlParts = cleanUrl.split('/').filter(Boolean);
      let repoName: string;
      let repoId: string;

      if (urlParts.length >= 2) {
        repoName = urlParts.slice(0, 2).join('/');
        repoId = `${newRepoPlatform}_${urlParts.slice(0, 2).join('_')}`;
      } else if (urlParts.length === 1) {
        repoName = urlParts[0];
        repoId = urlParts[0];
      } else {
        throw new Error('Invalid URL format');
      }

      // Add to context (which will register with S1)
      addRepository({
        id: repoId,
        name: repoName,
        url: newRepoUrl,
      });

      setAddRepoDialogOpen(false);
      setNewRepoUrl('');
      refetchRepos();

      toast({
        title: 'Repository added',
        description: `Repository "${repoName}" has been added.`,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to add repository. Please check the URL format.',
        variant: 'destructive',
      });
    }
  };

  const handleRemoveRepository = async (id: string) => {
    try {
      // Delete from S1 database
      await api.deleteRepository(id);
      
      // Remove from local context (frontend state)
      removeRepository(id);
      
      toast({
        title: 'Repository removed',
        description: 'Repository has been successfully removed from the database.',
        variant: 'default',
      });
      
      // Refresh the repository list
      refetchRepos();
    } catch (error) {
      console.error('Error deleting repository:', error);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to delete repository',
        variant: 'destructive',
      });
    }
  };


  // S4 - Preprocessing Pipeline
  const runPreprocessingMutation = useRunPreprocessingPipeline();
  
  const handleRunPreprocessing = async () => {
    try {
      await runPreprocessingMutation.mutateAsync();
      toast({
        title: 'Pipeline started',
        description: 'Preprocessing pipeline is running in background',
        variant: 'default',
      });
    } catch (error) {
      toast({
        title: 'Pipeline failed',
        description: error instanceof Error ? error.message : 'Failed to start pipeline',
        variant: 'destructive',
      });
    }
  };

  // S5 - ML Service
  const trainMLMutation = useTrainMLModel();
  const { data: mlFeatures, isLoading: isLoadingFeatures } = useMLFeatures();
  
  const handleTrainML = async () => {
    try {
      const result = await trainMLMutation.mutateAsync();
      toast({
        title: result.status === 'success' ? 'Model trained' : 'Training failed',
        description: result.message,
        variant: result.status === 'success' ? 'default' : 'destructive',
      });
    } catch (error) {
      toast({
        title: 'Training failed',
        description: error instanceof Error ? error.message : 'Failed to train model',
        variant: 'destructive',
      });
    }
  };

  // Components for S4/S5
  const RunPreprocessingButton = () => (
    <Button
      onClick={handleRunPreprocessing}
      disabled={runPreprocessingMutation.isPending}
      variant="outline"
    >
      {runPreprocessingMutation.isPending ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Running...
        </>
      ) : (
        <>
          <Play className="mr-2 h-4 w-4" />
          Run Pipeline
        </>
      )}
    </Button>
  );

  const TrainMLModelButton = () => (
    <Button
      onClick={handleTrainML}
      disabled={trainMLMutation.isPending}
      variant="outline"
    >
      {trainMLMutation.isPending ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Training...
        </>
      ) : (
        <>
          <Play className="mr-2 h-4 w-4" />
          Train Model
        </>
      )}
    </Button>
  );

  const MLFeaturesDisplay = () => (
    <div className="rounded-lg border border-border p-4">
      <div className="flex items-center justify-between mb-2">
        <p className="font-medium text-sm">ML Features</p>
        {isLoadingFeatures ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : mlFeatures ? (
          <CheckCircle2 className="h-4 w-4 text-success" />
        ) : (
          <AlertCircle className="h-4 w-4 text-muted-foreground" />
        )}
      </div>
      {isLoadingFeatures ? (
        <p className="text-sm text-muted-foreground">Loading features...</p>
      ) : mlFeatures ? (
        <div>
          <p className="text-sm text-muted-foreground">
            {mlFeatures.count} features available
          </p>
          <div className="mt-2 max-h-32 overflow-y-auto">
            <div className="flex flex-wrap gap-1">
              {mlFeatures.features.slice(0, 10).map((feature, i) => (
                <Badge key={i} variant="outline" className="text-xs">
                  {feature}
                </Badge>
              ))}
              {mlFeatures.features.length > 10 && (
                <Badge variant="outline" className="text-xs">
                  +{mlFeatures.features.length - 10} more
                </Badge>
              )}
            </div>
          </div>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          No features loaded. Train the model first.
        </p>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          PRIORITEST platform configuration
        </p>
      </div>

      <Tabs defaultValue="repositories" className="space-y-6">
        <TabsList>
          <TabsTrigger value="repositories">Repositories</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
        </TabsList>

        {/* Repositories Tab */}
        <TabsContent value="repositories" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Repository Configuration</CardTitle>
                  <CardDescription>
                    Manage Git repositories connected to PRIORITEST
                  </CardDescription>
                </div>
                <Dialog open={addRepoDialogOpen} onOpenChange={setAddRepoDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Add Repository
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add Repository</DialogTitle>
                      <DialogDescription>
                        Add a new Git repository to PRIORITEST for analysis
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="platform">Platform</Label>
                        <Select value={newRepoPlatform} onValueChange={(value: 'github' | 'gitlab') => setNewRepoPlatform(value)}>
                          <SelectTrigger id="platform">
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
                          placeholder="https://github.com/owner/repo"
                          value={newRepoUrl}
                          onChange={(e) => setNewRepoUrl(e.target.value)}
                        />
                        <p className="text-xs text-muted-foreground">
                          Enter the full repository URL (e.g., https://github.com/owner/repo)
                        </p>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setAddRepoDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={handleAddRepository}>
                        Add Repository
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              {isLoadingRepos ? (
                <div className="text-center py-8 text-muted-foreground">
                  <RefreshCw className="h-6 w-6 mx-auto mb-2 animate-spin" />
                  <p>Loading repositories...</p>
                </div>
              ) : repositories.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Info className="h-6 w-6 mx-auto mb-2" />
                  <p>No repositories configured</p>
                  <p className="text-xs mt-1">Add a repository to get started</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {repositories.map((repo) => (
                  <div
                    key={repo.id}
                    className="flex items-center justify-between rounded-lg border border-border p-4"
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                        <GitBranch className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium">{repo.name}</p>
                        <p className="text-sm text-muted-foreground">{repo.url}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Branch: {repo.branch} • Platform: {repo.platform}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCopyWebhook(repo.webhookUrl)}
                      >
                        <Copy className="mr-2 h-4 w-4" />
                        Webhook
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRemoveRepository(repo.id)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Integrations Tab */}
        <TabsContent value="integrations" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Service Status</CardTitle>
                  <CardDescription>
                    Health status of PRIORITEST microservices
                  </CardDescription>
                </div>
                <Button variant="outline" onClick={handleRefreshHealth}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                {services.map((service) => (
                  <ServiceStatus
                    key={service.name}
                    name={service.name}
                    status={service.status}
                    version={service.version}
                  />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* S4 - Preprocessing Pipeline */}
          <Card>
            <CardHeader>
              <CardTitle>S4 - Feature Preprocessing</CardTitle>
              <CardDescription>
                Prepare and normalize features for Machine Learning
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-border p-4">
                <div>
                  <p className="font-medium">Run Preprocessing Pipeline</p>
                  <p className="text-sm text-muted-foreground">
                    Combine S2 metrics and S3 coverage data into ML-ready features
                  </p>
                </div>
                <RunPreprocessingButton />
              </div>
            </CardContent>
          </Card>

          {/* S5 - ML Service */}
          <Card>
            <CardHeader>
              <CardTitle>S5 - ML Service</CardTitle>
              <CardDescription>
                Train and use ML models for risk prediction
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-border p-4">
                <div>
                  <p className="font-medium">Train ML Model</p>
                  <p className="text-sm text-muted-foreground">
                    Train the risk prediction model from S4 features
                  </p>
                </div>
                <TrainMLModelButton />
              </div>
              <MLFeaturesDisplay />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
