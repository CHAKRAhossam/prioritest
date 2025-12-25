import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api/client';

interface Repository {
  id: string;
  name: string;
  url?: string; // Full repository URL (e.g., https://github.com/owner/repo)
}

interface RepositoryContextType {
  selectedRepo: string;
  setSelectedRepo: (repo: string) => void;
  selectedBranch: string;
  setSelectedBranch: (branch: string) => void;
  repositories: Repository[];
  addRepository: (repo: Repository) => void;
  removeRepository: (repoId: string) => void;
}

// No default repositories - all repositories come from the database

const RepositoryContext = createContext<RepositoryContextType | undefined>(undefined);

const STORAGE_KEY = 'prioritest_repositories';
const SELECTED_REPO_KEY = 'prioritest_selected_repo';
const SELECTED_BRANCH_KEY = 'prioritest_selected_branch';

// Load repositories from localStorage (no static defaults)
const loadRepositories = (): Repository[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      return parsed;
    }
  } catch (error) {
    console.warn('Failed to load repositories from localStorage:', error);
  }
  return [];
};

// Save repositories to localStorage (save all, no filtering)
const saveRepositories = (repos: Repository[]) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(repos));
  } catch (error) {
    console.warn('Failed to save repositories to localStorage:', error);
  }
};

// Filter out fake/test repositories
const isFakeRepository = (repo: Repository): boolean => {
  const id = repo.id.toLowerCase();
  const name = repo.name.toLowerCase();
  
  // Filter out repositories with suspicious patterns
  const fakePatterns = [
    'marketplace',
    'chakrahossam',
    'com.example',
    'offline.fallback',
    'mock',
    'test_repo',
    'fake',
    '.repository', // Ends with .Repository (like "github_CHAKRAhossam_MarketPlace.Repository")
  ];
  
  return fakePatterns.some(pattern => id.includes(pattern) || name.includes(pattern));
};

export function RepositoryProvider({ children }: { children: ReactNode }) {
  // Load from localStorage on mount
  const [selectedRepo, setSelectedRepo] = useState(() => {
    try {
      return localStorage.getItem(SELECTED_REPO_KEY) || '';
    } catch {
      return '';
    }
  });
  const [selectedBranch, setSelectedBranch] = useState(() => {
    try {
      return localStorage.getItem(SELECTED_BRANCH_KEY) || 'main';
    } catch {
      return 'main';
    }
  });
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch repositories from S1 API on mount
  useEffect(() => {
    const fetchRepositories = async () => {
      try {
        setIsLoading(true);
        const response = await api.listRepositories();
        const dbRepos: Repository[] = response.data.repositories
          .map((r) => ({
            id: r.id,
            name: r.full_name || r.name, // Use full_name (owner/repo) for better display
            url: r.url,
          }))
          .filter((repo) => !isFakeRepository(repo)); // Filter out fake repositories

        // Use only repositories from database (no static defaults)
        setRepositories(dbRepos);
        saveRepositories(dbRepos);
        
        // If no repo is selected and we have repos, select the first one
        const currentSelected = localStorage.getItem(SELECTED_REPO_KEY) || '';
        if (!currentSelected && dbRepos.length > 0) {
          setSelectedRepo(dbRepos[0].id);
        }
      } catch (error) {
        console.warn('[RepositoryContext] Failed to fetch repositories from S1:', error);
        // Fallback to localStorage (but no static defaults)
        const stored = loadRepositories().filter((repo) => !isFakeRepository(repo)); // Filter fake repos
        setRepositories(stored);
        const currentSelected = localStorage.getItem(SELECTED_REPO_KEY) || '';
        if (!currentSelected && stored.length > 0) {
          setSelectedRepo(stored[0].id);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchRepositories();
  }, []);

  // Save selected repo to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(SELECTED_REPO_KEY, selectedRepo);
    } catch (error) {
      console.warn('Failed to save selected repo:', error);
    }
  }, [selectedRepo]);

  // Save selected branch to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(SELECTED_BRANCH_KEY, selectedBranch);
    } catch (error) {
      console.warn('Failed to save selected branch:', error);
    }
  }, [selectedBranch]);

  // Save repositories to localStorage whenever they change
  useEffect(() => {
    saveRepositories(repositories);
  }, [repositories]);

  // Reset branch to 'main' when repository changes
  useEffect(() => {
    setSelectedBranch('main');
  }, [selectedRepo]);
  
  // Validate selected branch when it changes (in case it's no longer available)
  // This will be handled by the component using the branches

  const addRepository = async (repo: Repository) => {
    // Don't add if already exists
    if (repositories.some((r) => r.id === repo.id)) {
      setSelectedRepo(repo.id);
      return;
    }

    // If repo has URL, register it with S1 and trigger full workflow
    if (repo.url) {
      try {
        // Trigger full collection workflow: commits + issues + ci_reports
        // This will:
        // 1. Create repository in S1 database
        // 2. Collect commits and publish to Kafka (repository.commits)
        // 3. S2 will automatically consume Kafka events and analyze code
        // 4. S2 publishes metrics to Kafka/Feast
        // 5. Collect CI/CD artifacts (JaCoCo/PIT) from GitHub Actions
        // 6. S3 will automatically consume Kafka events (ci.artifacts) and process coverage
        // 7. S4, S5, S6 can then use the data for prioritization
        const response = await fetch('/api/s1/collect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            repository_url: repo.url,
            collect_type: 'commits|issues|ci_reports', // Collect commits, issues, and CI/CD artifacts
          }),
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        console.log('[RepositoryContext] Repository collection started:', {
          repoId: repo.id,
          status: result.status,
          message: result.message,
          collectTypes: result.collect_types,
        });
        
        // Note: Collection happens in background. S2 will automatically process commits via Kafka.
        // The workflow: S1 → Kafka → S2 → Kafka/Feast → S4 → S5 → S6 → S8
      } catch (error) {
        console.error('[RepositoryContext] Failed to start repository collection:', error);
        // Continue anyway - add to local state, user can retry later
      }
    }

    // Add to local state
    const updated = [...repositories, repo];
    setRepositories(updated);
    saveRepositories(updated);
    
    // Select the new repository
    setSelectedRepo(repo.id);

    // Refresh repositories from S1 after a short delay to get the new one
    if (repo.url) {
      setTimeout(async () => {
        try {
          const response = await api.listRepositories();
          const dbRepos: Repository[] = response.data.repositories
            .map((r) => ({
              id: r.id,
              name: r.full_name || r.name, // Use full_name (owner/repo) for better display
              url: r.url,
            }))
            .filter((repo) => !isFakeRepository(repo)); // Filter out fake repositories

          // Use only repositories from database
          setRepositories(dbRepos);
          saveRepositories(dbRepos);
        } catch (error) {
          console.warn('[RepositoryContext] Failed to refresh repositories:', error);
        }
      }, 2000);
    }
  };

  const removeRepository = (repoId: string) => {
    // Remove from local state
    const updated = repositories.filter((r) => r.id !== repoId);
    setRepositories(updated);
    saveRepositories(updated);
    
    // If the removed repo was selected, select another one or clear selection
    if (selectedRepo === repoId) {
      if (updated.length > 0) {
        setSelectedRepo(updated[0].id);
      } else {
        setSelectedRepo('');
      }
    }
  };

  return (
    <RepositoryContext.Provider value={{ 
      selectedRepo, 
      setSelectedRepo, 
      selectedBranch,
      setSelectedBranch,
      repositories, 
      addRepository,
      removeRepository
    }}>
      {children}
    </RepositoryContext.Provider>
  );
}

export function useRepository() {
  const context = useContext(RepositoryContext);
  if (context === undefined) {
    throw new Error('useRepository must be used within a RepositoryProvider');
  }
  return context;
}
