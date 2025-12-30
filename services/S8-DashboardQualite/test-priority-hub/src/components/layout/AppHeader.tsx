import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Calendar, GitBranch, Moon, Sun, User, Settings, LogOut, Loader2 } from 'lucide-react';
import { useRepository } from '@/context/RepositoryContext';
import { useRepositoryBranches } from '@/hooks/useApi';

interface AppHeaderProps {
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
}

const dateRanges = [
  { value: '7', label: 'Last 7 days' },
  { value: '30', label: 'Last 30 days' },
  { value: '90', label: 'Last 90 days' },
  { value: 'custom', label: 'Custom' },
];

export function AppHeader({ theme, onThemeToggle }: AppHeaderProps) {
  const { selectedRepo, setSelectedRepo, selectedBranch, setSelectedBranch, repositories } = useRepository();
  // Ensure repositories is always an array
  const reposArray = Array.isArray(repositories) ? repositories : [];
  // Find repository URL from context
  const currentRepo = reposArray.find(r => r.id === selectedRepo);
  const { data: branches = [], isLoading: branchesLoading } = useRepositoryBranches(selectedRepo, currentRepo?.url);
  const [dateRange, setDateRange] = useState('30');
  
  // Debug: Log available repositories
  useEffect(() => {
    console.log('[Header] Available repositories:', reposArray.length);
  }, [reposArray.length]);
  
  const handleRepoChange = (value: string) => {
    console.log('[Header] Repository changed to:', value);
    if (value && value !== '__empty__') {
      setSelectedRepo(value);
      // Branch will be reset to 'main' by context useEffect
    }
  };
  
  const handleBranchChange = (value: string) => {
    console.log('[Header] Branch changed to:', value);
    setSelectedBranch(value);
  };
  
  // Ensure selected branch is valid when branches load
  useEffect(() => {
    if (branches.length > 0 && !branches.includes(selectedBranch)) {
      // If current branch is not in the list, default to 'main' or first available
      const defaultBranch = branches.includes('main') ? 'main' : branches[0];
      console.log('[Header] Selected branch not available, switching to:', defaultBranch);
      setSelectedBranch(defaultBranch);
    }
  }, [branches, selectedBranch, setSelectedBranch]);

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card/50 px-6">
      {/* Left side - Repository & Branch selectors */}
      <div className="flex items-center gap-4">
        <Select 
          value={selectedRepo || undefined} 
          onValueChange={handleRepoChange} 
          disabled={reposArray.length === 0}
        >
          <SelectTrigger 
            className="w-[250px] bg-background cursor-pointer"
          >
            <SelectValue placeholder={reposArray.length === 0 ? "No repositories" : "Select repository"} />
          </SelectTrigger>
          <SelectContent className="z-[100]" position="popper">
            {reposArray.length === 0 ? (
              <SelectItem value="__empty__" disabled>No repositories available</SelectItem>
            ) : (
              reposArray.map((repo) => (
                <SelectItem key={repo.id} value={repo.id}>
                  {repo.name || repo.id}
                </SelectItem>
              ))
            )}
          </SelectContent>
        </Select>

        <Select value={selectedBranch} onValueChange={handleBranchChange} disabled={branchesLoading || branches.length === 0}>
          <SelectTrigger className="w-[180px] bg-background">
            <GitBranch className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue placeholder={branchesLoading ? "Loading..." : "Branch"} />
          </SelectTrigger>
          <SelectContent>
            {branchesLoading ? (
              <SelectItem value="__loading__" disabled>
                <span className="flex items-center">
                  <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                  Loading...
                </span>
              </SelectItem>
            ) : branches.length > 0 ? (
              branches.map((branch) => (
                <SelectItem key={branch} value={branch}>
                  {branch.length > 15 ? `${branch.substring(0, 12)}...` : branch}
                </SelectItem>
              ))
            ) : (
              <SelectItem value="main" disabled>No branches available</SelectItem>
            )}
          </SelectContent>
        </Select>

        <Select value={dateRange} onValueChange={setDateRange}>
          <SelectTrigger className="w-[180px] bg-background">
            <Calendar className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue placeholder="Période" />
          </SelectTrigger>
          <SelectContent>
            {dateRanges.map((range) => (
              <SelectItem key={range.value} value={range.value}>
                {range.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Right side - Live indicator, theme toggle, user menu */}
      <div className="flex items-center gap-4">
        {/* Live indicator */}
        <div className="live-indicator text-success">
          <span className="text-muted-foreground">Live</span>
        </div>

        {/* Theme toggle */}
        <Button variant="ghost" size="icon" onClick={onThemeToggle}>
          {theme === 'dark' ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </Button>

        {/* User menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-8 w-8 rounded-full">
              <Avatar className="h-8 w-8">
                <AvatarImage src="/placeholder.svg" alt="User" />
                <AvatarFallback className="bg-primary text-primary-foreground">
                  AD
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">Admin</p>
                <p className="text-xs leading-none text-muted-foreground">
                  admin@prioritest.dev
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" />
              <span>Profil</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2 h-4 w-4" />
              <span>Paramètres</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive">
              <LogOut className="mr-2 h-4 w-4" />
              <span>Déconnexion</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
