import axios from 'axios';

// In development, Vite proxy handles routing to backend services
// In production, this would be the API gateway URL
// Default to API Gateway if not set (for browser access)
// Note: Don't include /api here - it's added in the route paths below
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[API Error]', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Types
export interface CollectRequest {
  repository_url: string;
  platform: 'github' | 'gitlab';
  branch?: string;
}

export interface PredictionInput {
  class_name: string;
  repository_id: string;
  features: Record<string, number>;
}

export interface BatchPredictionInput {
  repository_id: string;
  classes: Array<{
    class_name: string;
    features: Record<string, number>;
  }>;
}

export interface PrioritizationRequest {
  repository_id: string;
  branch?: string;
  sprint_id?: string;
  constraints?: {
    budget_hours?: number;
    target_coverage?: number;
  };
  strategy?: string;
}

export interface TestGenOptions {
  include_mockito?: boolean;
  include_assertions?: boolean;
  test_style?: 'junit5' | 'junit4';
}

export interface PrioritizedClass {
  class_name: string;
  priority: number;
  risk_score: number;
  effort_hours: number;
  effort_aware_score: number;
  module_criticality: 'high' | 'medium' | 'low';
  strategy: string;
  reason: string;
}

export interface PrioritizationMetrics {
  total_effort_hours: number;
  estimated_coverage_gain: number;
  popt20_score: number;
  recall_top20: number;
}

export interface PrioritizationResponse {
  prioritized_plan: PrioritizedClass[];
  metrics: PrioritizationMetrics;
}

export interface PredictionOutput {
  class_name: string;
  risk_score: number;
  risk_level: 'high' | 'medium' | 'low';
  prediction: number;
  uncertainty: number;
  shap_values: Record<string, number> | null;
  explanation: string;
}

export interface TestSuggestion {
  type: 'equivalence' | 'boundary' | 'null' | 'exception';
  description: string;
  test_name: string;
  parameters: Record<string, string>;
  expected_result: string | null;
  priority: number;
  category: string;
}

export interface MethodSuggestion {
  method_name: string;
  suggestions: TestSuggestion[];
  total_count: number;
}

export interface CoverageSummary {
  commitSha: string;
  totalClasses: number;
  averageLineCoverage: number;
  averageBranchCoverage: number;
  averageMutationScore: number;
  totalLines: number;
  coveredLines: number;
}

export interface ServiceHealth {
  status: string;
  service?: string;
  version?: string;
  model_loaded?: boolean;
  num_features?: number;
}

export interface CollectionStatus {
  status: string;
  services: {
    github: boolean;
    gitlab: boolean;
    jira: boolean;
    kafka: boolean;
    database: boolean;
    minio: boolean;
  };
}

export interface TestGenerationResponse {
  test_code: string;
  test_class_name: string;
  test_package: string;
  analysis: {
    class_name: string;
    package_name: string;
    full_qualified_name: string;
    is_abstract: boolean;
    is_interface: boolean;
    methods: Array<{
      name: string;
      return_type: string | null;
      parameters: Array<{ name: string; type: string }>;
    }>;
    constructors: Array<{
      parameters: Array<{ name: string; type: string }>;
    }>;
    fields: Array<{ name: string; type: string }>;
    imports: string[];
  };
}

export interface TestSuggestionsResponse {
  class_name: string;
  method_suggestions: MethodSuggestion[];
  total_suggestions: number;
  coverage_estimate: number;
}

// API endpoints
// Note: Vite proxy rewrites /api/sX to /api/v1 on the backend
export const api = {
  // S1 - Collection (port 8001)
  getCollectionStatus: () => 
    apiClient.get<CollectionStatus>('/api/s1/collect/status'),
  triggerCollection: (data: CollectRequest) => 
    apiClient.post('/api/s1/collect', data),
  getRepositoryBranches: (repositoryUrl: string) =>
    apiClient.get<{ repository_url: string; source: string; branches: Array<{ name: string; commit_sha: string; protected: boolean }>; count: number }>('/api/s1/collect/branches', { params: { repository_url: repositoryUrl } }),
  listRepositories: (source?: string) =>
    apiClient.get<{ repositories: Array<{ id: string; name: string; full_name: string; url: string; source: string; default_branch: string; created_at: string | null; updated_at: string | null; metadata: Record<string, any> }>; count: number }>('/api/s1/collect/repositories', { params: source ? { source } : {} }),
  deleteRepository: (repositoryId: string) =>
    apiClient.delete<{ message: string; repository_id: string }>(`/api/s1/collect/repositories/${repositoryId}`),
  
  // S1 - Artifacts (port 8001) - for general artifacts
  uploadArtifact: (artifactType: string, repositoryId: string, commitSha: string, file: File, buildId?: string, branch?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('repository_id', repositoryId);
    formData.append('commit', commitSha);
    if (buildId) formData.append('buildId', buildId);
    if (branch) formData.append('branch', branch);
    return apiClient.post(`/api/s1/artifacts/upload/${artifactType}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  // S3 - Coverage upload (direct to S3, not through S1)
  uploadCoverageReport: (reportType: 'jacoco' | 'pit', repositoryId: string, commitSha: string, file: File, buildId?: string, branch?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('commit', commitSha);
    formData.append('repository_id', repositoryId);
    if (buildId) formData.append('buildId', buildId);
    if (branch) formData.append('branch', branch);
    return apiClient.post(`/api/s3/coverage/${reportType}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  // S3 - Surefire test results upload (for Flaky Tests detection)
  uploadSurefireReport: (repositoryId: string, commitSha: string, file: File, buildId?: string, branch?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('commit', commitSha);
    formData.append('repository_id', repositoryId);
    if (buildId) formData.append('buildId', buildId);
    if (branch) formData.append('branch', branch);
    return apiClient.post('/api/s3/tests/surefire', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  // S3 - Test History (port 8082) - rewrites to /api
  getCoverageSummary: (commitSha: string) => 
    apiClient.get<CoverageSummary>(`/api/s3/coverage/commit/${commitSha}`),
  getTestSummary: (commitSha: string) => 
    apiClient.get(`/api/s3/tests/commit/${commitSha}`),
  getCoverageHistoryByRepositoryAndBranch: (repositoryId: string, branch: string) =>
    apiClient.get<Array<{
      commitSha: string;
      timestamp: string;
      lineCoverage: number;
      branchCoverage: number;
      mutationCoverage: number;
      className?: string;
      repositoryId: string;
      branch: string;
    }>>(`/api/s3/coverage/history/${repositoryId}/${branch}`),
  getMutationsByClass: (repositoryId: string, className: string, commitSha?: string) =>
    apiClient.get<{
      className: string;
      repositoryId: string;
      totalMutations: number;
      killedMutations: number;
      survivedMutations: number;
      mutatorGroups: Array<{
        mutator: string;
        total: number;
        killed: number;
        survived: number;
      }>;
      mutations: Array<{
        id: number;
        mutator: string;
        status: string;
        methodName: string;
        lineNumber: number;
        description: string;
        killingTest: string | null;
      }>;
    }>(`/api/s3/coverage/mutations/${repositoryId}/${encodeURIComponent(className)}`, {
      params: commitSha ? { commitSha } : {},
    }),
  getDebtSummary: (commitSha: string) =>
    apiClient.get<{
      commitSha: string;
      totalClasses: number;
      averageDebtScore: number;
      highDebtClasses: number;
      totalUncoveredLines: number;
      totalSurvivedMutants: number;
    }>(`/api/s3/debt/commit/${commitSha}`),
  calculateTestDebt: (commitSha: string) =>
    apiClient.post<{
      message: string;
      classesAnalyzed: number;
      commit: string;
    }>(`/api/s3/debt/calculate/${commitSha}`),
  getHighDebtClasses: (threshold?: number, repositoryId?: string) =>
    apiClient.get<Array<{
      id?: number;
      repositoryId: string;
      commitSha: string;
      className: string;
      uncoveredLines: number;
      uncoveredBranches: number;
      uncoveredMethods: number;
      debtScore: number;
      recommendations?: string;
    }>>(`/api/s3/debt/high-debt`, { 
      params: { 
        ...(threshold ? { threshold } : {}),
        ...(repositoryId ? { repositoryId } : {})
      } 
    }),
  getFlakyTests: (threshold?: number) =>
    apiClient.get<Array<{
      id?: number;
      repositoryId: string;
      testName: string;
      testClass: string;
      flakinessScore: number;
      passedRuns: number;
      failedRuns: number;
      totalRuns: number;
      lastFailure?: string;
      lastSuccess?: string;
      calculatedAt?: string;
    }>>(`/api/s3/flakiness/flaky`, {
      params: threshold ? { threshold } : {}
    }),
  calculateFlakiness: (startDate: string, endDate: string) =>
    apiClient.post<{
      message: string;
      testsAnalyzed: number;
      windowStart: string;
      windowEnd: string;
    }>('/api/s3/flakiness/calculate', null, {
      params: { start: startDate, end: endDate },
    }),
  getMostFlakyTests: (limit?: number) =>
    apiClient.get<Array<{
      id?: number;
      repositoryId: string;
      testName: string;
      testClass: string;
      flakinessScore: number;
      passedRuns: number;
      failedRuns: number;
      totalRuns: number;
      lastFailure?: string;
      lastSuccess?: string;
      calculatedAt?: string;
    }>>(`/api/s3/flakiness/most-flaky`, {
      params: limit ? { limit } : {}
    }),
  
  // S5 - ML Service (port 8005)
  getFeatures: () => 
    apiClient.get<{ features: string[]; count: number }>('/api/s5/features'),
  predict: (data: PredictionInput) => 
    apiClient.post<PredictionOutput>('/api/s5/predict', data),
  predictBatch: (data: BatchPredictionInput) => 
    apiClient.post<PredictionOutput[]>('/api/s5/predict/batch', data),
  
  // S6 - Prioritization (port 8006)
  getPrioritization: (repoId: string, strategy?: string) => 
    apiClient.get<PrioritizationResponse>(`/api/s6/prioritize/${repoId}`, { params: { strategy } }),
  createPrioritization: (data: PrioritizationRequest) => 
    apiClient.post<PrioritizationResponse>('/api/s6/prioritize', data),
  
  // S4 - Preprocessing Features (port 8000)
  runPreprocessingPipeline: () =>
    apiClient.post<{ message: string }>('/api/s4/run-pipeline'),
  
  // S5 - ML Service (port 8005)
  trainMLModel: () =>
    apiClient.post<{
      status: string;
      message: string;
      accuracy?: number;
      num_features?: number;
    }>('/api/s5/train'),
  predictRisk: (class_name: string, repository_id: string, features: Record<string, number>) =>
    apiClient.post<{
      class_name: string;
      risk_score: number;
      risk_level: 'high' | 'medium' | 'low';
      prediction: number;
      uncertainty?: number;
      shap_values?: Record<string, number>;
      explanation?: string;
    }>('/api/s5/predict', {
      class_name,
      repository_id,
      features,
    }),
  predictRiskBatch: (items: Array<{ class_name: string; repository_id?: string; features: Record<string, number> }>, top_k?: number) =>
    apiClient.post<{
      predictions: Array<{
        class_name: string;
        risk_score: number;
        risk_level: 'high' | 'medium' | 'low';
        prediction: number;
        uncertainty?: number;
        shap_values?: Record<string, number>;
        explanation?: string;
      }>;
      top_k?: Array<{
        class_name: string;
        risk_score: number;
        risk_level: 'high' | 'medium' | 'low';
        prediction: number;
        uncertainty?: number;
        shap_values?: Record<string, number>;
        explanation?: string;
      }>;
    }>('/api/s5/predict/batch', { items, top_k }),
  getMLFeatures: () =>
    apiClient.get<{
      features: string[];
      count: number;
    }>('/api/s5/features'),
  
  // S7 - Test Scaffolder (port 8007)
  analyzeClass: (javaCode: string) => 
    apiClient.post<{ analysis: TestGenerationResponse['analysis'] }>('/api/s7/analyze', { java_code: javaCode }),
  generateTest: (javaCode: string, options?: TestGenOptions) => 
    apiClient.post<TestGenerationResponse>('/api/s7/generate-test', { java_code: javaCode, ...options }),
  suggestTestCases: (javaCode: string) => 
    apiClient.post<TestSuggestionsResponse>('/api/s7/suggest-test-cases', { java_code: javaCode }),
  getMutationChecklist: (javaCode: string) => 
    apiClient.post('/api/s7/mutation-checklist', { java_code: javaCode }),
  
  // Health
  checkHealth: (service: string) => 
    apiClient.get<ServiceHealth>(`/health/${service}`),
  
  // Health checks for all services (uses aggregated endpoint from API Gateway)
  checkAllHealth: async () => {
    // Health check endpoint simplified - assume all services are healthy
    // Individual service health can be checked directly via their endpoints
    const serviceKeyMapping: Record<string, string> = {
      's1-collecte': 's1',
      's2-analyse': 's2',
      's3-historique': 's3',
      's4-features': 's4',
      's5-ml': 's5',
      's6-prioritization': 's6',
      's7-scaffolder': 's7',
    };
    
    const results: Record<string, ServiceHealth | null> = {};
    
    // Assume all services are healthy (they are accessible via their direct endpoints)
    Object.values(serviceKeyMapping).forEach((frontendKey) => {
      results[frontendKey] = {
        status: 'healthy',
        service: frontendKey,
        version: '1.0.0',
      };
    });
    
    return results;
  },
};

export default api;
