// Re-export types from API client
export type {
  CollectRequest,
  PredictionInput,
  BatchPredictionInput,
  PrioritizationRequest,
  TestGenOptions,
  PrioritizedClass,
  PrioritizationMetrics,
  PrioritizationResponse,
  PredictionOutput,
  TestSuggestion,
  MethodSuggestion,
  CoverageSummary,
  ServiceHealth,
  CollectionStatus,
  TestGenerationResponse,
  TestSuggestionsResponse,
} from '@/lib/api/client';

// Additional UI-specific types
export interface KPIData {
  label: string;
  value: string | number;
  trend?: number;
  trendLabel?: string;
  icon: string;
  color?: 'default' | 'success' | 'warning' | 'danger';
}

export interface CoverageDataPoint {
  date: string;
  lineCoverage: number;
  branchCoverage: number;
  mutationCoverage: number;
}

export interface RiskDistribution {
  bucket: string;
  count: number;
  range: [number, number];
}

export interface TopPriorityClass {
  className: string;
  riskScore: number;
  riskLevel: 'high' | 'medium' | 'low';
  module: string;
}

export interface Repository {
  id: string;
  name: string;
  platform: 'github' | 'gitlab';
  url: string;
  branch: string;
  lastSync?: string;
}

export interface NavigationItem {
  label: string;
  href: string;
  icon: string;
  badge?: number;
}

export type PrioritizationStrategy = 
  | 'maximize_popt20'
  | 'top_k_coverage'
  | 'budget_optimization'
  | 'risk_first'
  | 'effort_aware';

export const STRATEGY_LABELS: Record<PrioritizationStrategy, string> = {
  maximize_popt20: 'Maximiser POPT20',
  top_k_coverage: 'Top K Couverture',
  budget_optimization: 'Optimisation Budget',
  risk_first: 'Risque en Premier',
  effort_aware: 'Effort Conscient',
};
