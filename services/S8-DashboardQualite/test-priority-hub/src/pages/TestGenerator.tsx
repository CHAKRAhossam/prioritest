import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { useRepository } from '@/context/RepositoryContext';
import api from '@/lib/api/client';
import {
  Play,
  FlaskConical,
  Lightbulb,
  Copy,
  Download,
  FileCode,
  FolderTree,
  CheckSquare,
  Bug,
  Loader2,
  GitBranch,
  Info,
} from 'lucide-react';

const defaultJavaCode = `package com.example.service;

import java.util.List;
import java.util.Optional;

public class UserService {
    
    private final UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public Optional<User> findById(Long id) {
        if (id == null || id <= 0) {
            throw new IllegalArgumentException("ID must be positive");
        }
        return userRepository.findById(id);
    }
    
    public User create(String name, String email) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Name cannot be empty");
        }
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("Invalid email");
        }
        User user = new User(name, email);
        return userRepository.save(user);
    }
    
    public List<User> findAll() {
        return userRepository.findAll();
    }
    
    public void delete(Long id) {
        if (id == null) {
            throw new IllegalArgumentException("ID cannot be null");
        }
        userRepository.deleteById(id);
    }
}`;

const mockGeneratedTest = `package com.example.service.test;

import org.junit.jupiter.api.*;
import org.mockito.*;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
@DisplayName("Tests pour com.example.service.UserService")
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @BeforeEach
    void setUp() {
        // Setup initial pour chaque test
    }

    @Nested
    @DisplayName("Tests pour findById")
    class FindByIdTests {
        
        @Test
        @DisplayName("Devrait retourner un utilisateur quand l'ID existe")
        void shouldReturnUserWhenIdExists() {
            // Given
            Long id = 1L;
            User expectedUser = new User("John", "john@example.com");
            when(userRepository.findById(id)).thenReturn(Optional.of(expectedUser));
            
            // When
            Optional<User> result = userService.findById(id);
            
            // Then
            assertTrue(result.isPresent());
            assertEquals(expectedUser, result.get());
            verify(userRepository).findById(id);
        }
        
        @Test
        @DisplayName("Devrait lancer une exception quand l'ID est null")
        void shouldThrowExceptionWhenIdIsNull() {
            // When & Then
            assertThrows(IllegalArgumentException.class, 
                () -> userService.findById(null));
        }
        
        @Test
        @DisplayName("Devrait lancer une exception quand l'ID est négatif")
        void shouldThrowExceptionWhenIdIsNegative() {
            // When & Then
            assertThrows(IllegalArgumentException.class, 
                () -> userService.findById(-1L));
        }
    }

    @Nested
    @DisplayName("Tests pour create")
    class CreateTests {
        
        @Test
        @DisplayName("Devrait créer un utilisateur avec des données valides")
        void shouldCreateUserWithValidData() {
            // Given
            String name = "John";
            String email = "john@example.com";
            User newUser = new User(name, email);
            when(userRepository.save(any(User.class))).thenReturn(newUser);
            
            // When
            User result = userService.create(name, email);
            
            // Then
            assertNotNull(result);
            assertEquals(name, result.getName());
            assertEquals(email, result.getEmail());
        }
    }
}`;

interface ClassAnalysis {
  className: string;
  packageName: string;
  methods: Array<{
    name: string;
    returnType: string;
    parameters: Array<{ name: string; type: string }>;
  }>;
  fields: Array<{ name: string; type: string }>;
  constructors: Array<{ parameters: Array<{ name: string; type: string }> }>;
}

interface TestSuggestion {
  methodName: string;
  testName: string;
  type: string;
  description: string;
  priority: number;
  checked: boolean;
}

const mockAnalysis: ClassAnalysis = {
  className: 'UserService',
  packageName: 'com.example.service',
  methods: [
    { name: 'findById', returnType: 'Optional<User>', parameters: [{ name: 'id', type: 'Long' }] },
    { name: 'create', returnType: 'User', parameters: [{ name: 'name', type: 'String' }, { name: 'email', type: 'String' }] },
    { name: 'findAll', returnType: 'List<User>', parameters: [] },
    { name: 'delete', returnType: 'void', parameters: [{ name: 'id', type: 'Long' }] },
  ],
  fields: [{ name: 'userRepository', type: 'UserRepository' }],
  constructors: [{ parameters: [{ name: 'userRepository', type: 'UserRepository' }] }],
};

const mockSuggestions: TestSuggestion[] = [
  { methodName: 'findById', testName: 'testFindById_WithValidId', type: 'equivalence', description: 'Test with a valid existing ID', priority: 1, checked: false },
  { methodName: 'findById', testName: 'testFindById_WithNullId', type: 'null', description: 'Test with a null ID', priority: 1, checked: false },
  { methodName: 'findById', testName: 'testFindById_WithNegativeId', type: 'boundary', description: 'Test with a negative ID', priority: 2, checked: false },
  { methodName: 'findById', testName: 'testFindById_WithZeroId', type: 'boundary', description: 'Test with ID = 0', priority: 2, checked: false },
  { methodName: 'create', testName: 'testCreate_WithValidData', type: 'equivalence', description: 'Test with valid data', priority: 1, checked: false },
  { methodName: 'create', testName: 'testCreate_WithNullName', type: 'null', description: 'Test with a null name', priority: 1, checked: false },
  { methodName: 'create', testName: 'testCreate_WithInvalidEmail', type: 'exception', description: 'Test with an invalid email', priority: 1, checked: false },
  { methodName: 'delete', testName: 'testDelete_WithValidId', type: 'equivalence', description: 'Test deletion with a valid ID', priority: 1, checked: false },
  { methodName: 'delete', testName: 'testDelete_WithNullId', type: 'null', description: 'Test deletion with null ID', priority: 1, checked: false },
];

// Map PIT mutators to our mutation types
const mapMutatorToType = (mutator: string): string | null => {
  if (!mutator) return null;
  const mutatorLower = mutator.toLowerCase();
  
  if (mutatorLower.includes('conditionalsboundary') || mutatorLower.includes('boundary')) {
    return 'Conditionals Boundary';
  }
  if (mutatorLower.includes('negate') || mutatorLower.includes('invert')) {
    return 'Negate Conditionals';
  }
  if (mutatorLower.includes('removeconditionals') || mutatorLower.includes('removeconditional')) {
    return 'Remove Conditionals';
  }
  if (mutatorLower.includes('returnvals') || mutatorLower.includes('returnvalue')) {
    return 'Return Values';
  }
  if (mutatorLower.includes('voidmethod') || mutatorLower.includes('voidcall')) {
    return 'Void Method Calls';
  }
  if (mutatorLower.includes('constructor') || mutatorLower.includes('construct')) {
    return 'Constructor Calls';
  }
  if (mutatorLower.includes('argument') || mutatorLower.includes('propagate')) {
    return 'Argument Propagation';
  }
  return null;
};

interface MutationChecklistItem {
  id: number;
  mutation: string;
  description: string;
  covered: boolean;
  total?: number;
  killed?: number;
  survived?: number;
}

const defaultMutationChecklist: MutationChecklistItem[] = [
  { id: 1, mutation: 'Conditionals Boundary', description: 'Modify boundary conditions (< vs <=)', covered: false },
  { id: 2, mutation: 'Negate Conditionals', description: 'Invert boolean conditions', covered: false },
  { id: 3, mutation: 'Remove Conditionals', description: 'Remove if conditions', covered: false },
  { id: 4, mutation: 'Return Values', description: 'Modify return values', covered: false },
  { id: 5, mutation: 'Void Method Calls', description: 'Remove void method calls', covered: false },
  { id: 6, mutation: 'Constructor Calls', description: 'Modify constructor calls', covered: false },
  { id: 7, mutation: 'Argument Propagation', description: 'Propagate input arguments', covered: false },
];

export default function TestGenerator() {
  const { toast } = useToast();
  const location = useLocation();
  const navigate = useNavigate();
  const { selectedRepo: repoId, selectedBranch, repositories } = useRepository();
  const [javaCode, setJavaCode] = useState(defaultJavaCode);
  const [generatedTest, setGeneratedTest] = useState('');
  const [analysis, setAnalysis] = useState<ClassAnalysis | null>(null);
  const [suggestions, setSuggestions] = useState<TestSuggestion[]>([]);
  const [activeTab, setActiveTab] = useState('test');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [classNameFromNav, setClassNameFromNav] = useState<string | null>(null);
  const [mutationChecklist, setMutationChecklist] = useState<MutationChecklistItem[]>(defaultMutationChecklist);
  const [mutationsData, setMutationsData] = useState<{
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
  } | null>(null);
  
  // Get className and sourceCode from navigation state
  useEffect(() => {
    if (location.state && typeof location.state === 'object' && 'className' in location.state) {
      const navState = location.state as {
        className: string;
        sourceCode?: string;
        filePath?: string;
        repositoryId?: string;
        branch?: string;
      };
      const className = navState.className;
      setClassNameFromNav(className);
      
      // If source code is provided, load it into the editor
      if (navState.sourceCode) {
        setJavaCode(navState.sourceCode);
        toast({
          title: 'Source code loaded',
          description: `Code for ${className} loaded from repository`,
        });
      } else {
        toast({
          title: 'Class selected',
          description: `Generating tests for ${className}. Please paste the source code or use "Fetch from Repository".`,
        });
      }
    }
  }, [location.state, toast]);

  // Load mutations when classNameFromNav or repoId changes
  useEffect(() => {
    const loadMutations = async () => {
      if (!classNameFromNav || !repoId) {
        setMutationChecklist(defaultMutationChecklist);
        setMutationsData(null);
        return;
      }

      try {
        const response = await api.getMutationsByClass(repoId, classNameFromNav);
        const data = response.data;
        setMutationsData(data);

        // Map mutators to mutation types and update checklist
        const updatedChecklist = defaultMutationChecklist.map(item => {
          // Find mutator groups that match this mutation type
          const matchingGroups = data.mutatorGroups.filter((group: { mutator: string; total: number; killed: number; survived: number }) => {
            const mappedType = mapMutatorToType(group.mutator);
            return mappedType === item.mutation;
          });

          if (matchingGroups.length === 0) {
            return { ...item, covered: false };
          }

          // Check if at least one mutation of this type was killed (covered)
          const hasKilled = matchingGroups.some((group: { killed: number }) => group.killed > 0);
          const total = matchingGroups.reduce((sum: number, g: { total: number }) => sum + g.total, 0);
          const killed = matchingGroups.reduce((sum: number, g: { killed: number }) => sum + g.killed, 0);
          const survived = matchingGroups.reduce((sum: number, g: { survived: number }) => sum + g.survived, 0);

          return {
            ...item,
            covered: hasKilled, // Covered if at least one mutation was killed
            total,
            killed,
            survived,
          };
        });

        setMutationChecklist(updatedChecklist);
      } catch (error: unknown) {
        // If no mutations found, use default checklist
        console.warn('No mutations found for class:', classNameFromNav, error);
        setMutationChecklist(defaultMutationChecklist);
        setMutationsData(null);
      }
    };

    loadMutations();
  }, [classNameFromNav, repoId]);

  const handleAnalyze = async () => {
    setIsLoading(true);
    setLoadingAction('analyze');
    try {
      const response = await api.analyzeClass(javaCode);
      // S7 returns { analysis: ClassAnalysis }
      const analysisData = response.data?.analysis || (response.data as any);
      if (analysisData && (analysisData.class_name || analysisData.className)) {
        const mappedAnalysis: ClassAnalysis = {
          className: analysisData.class_name || analysisData.className,
          packageName: analysisData.package_name || analysisData.packageName || '',
          methods: (analysisData.methods || []).map((m: { name: string; return_type?: string; returnType?: string; parameters?: Array<{ name?: string; parameter_name?: string; type?: string; parameter_type?: string }> }) => ({
            name: m.name,
            returnType: m.return_type || m.returnType || 'void',
            parameters: (m.parameters || []).map((p) => ({ 
              name: p.name || p.parameter_name || '', 
              type: p.type || p.parameter_type || '' 
            })),
          })),
          fields: (analysisData.fields || []).map((f: { name?: string; field_name?: string; type?: string; field_type?: string }) => ({ 
            name: f.name || f.field_name || '', 
            type: f.type || f.field_type || '' 
          })),
          constructors: (analysisData.constructors || []).map((c: { parameters?: Array<{ name?: string; parameter_name?: string; type?: string; parameter_type?: string }> }) => ({
            parameters: (c.parameters || []).map((p) => ({ 
              name: p.name || p.parameter_name || '', 
              type: p.type || p.parameter_type || '' 
            })),
          })),
        };
        setAnalysis(mappedAnalysis);
        setActiveTab('analysis');
        toast({
          title: 'Analysis complete',
          description: `Class ${mappedAnalysis.className} analyzed successfully`,
        });
      }
    } catch (error: any) {
      console.error('Analysis error:', error);
      setAnalysis(mockAnalysis);
      setActiveTab('analysis');
      toast({
        title: 'Using mock data',
        description: error.response?.data?.detail || error.message || 'S7 service unavailable, showing example analysis',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
      setLoadingAction(null);
    }
  };

  const handleGenerateTest = async () => {
    setIsLoading(true);
    setLoadingAction('generate');
    try {
      const response = await api.generateTest(javaCode, {
        include_mockito: true,
        include_assertions: true,
        test_style: 'junit5',
      });
      if (response.data?.test_code) {
        setGeneratedTest(response.data.test_code);
        // Also update analysis if available
        if (response.data.analysis) {
          const analysisData = response.data.analysis;
          const mappedAnalysis: ClassAnalysis = {
            className: analysisData.class_name || '',
            packageName: analysisData.package_name || '',
            methods: (analysisData.methods || []).map((m) => ({
              name: m.name,
              returnType: m.return_type || 'void',
              parameters: (m.parameters || []).map((p) => ({ 
                name: p.name || '', 
                type: p.type || '' 
              })),
            })),
            fields: (analysisData.fields || []).map((f) => ({ 
              name: f.name || '', 
              type: f.type || '' 
            })),
            constructors: (analysisData.constructors || []).map((c) => ({
              parameters: (c.parameters || []).map((p) => ({ 
                name: p.name || '', 
                type: p.type || '' 
              })),
            })),
          };
          setAnalysis(mappedAnalysis);
        }
        setActiveTab('test');
        toast({
          title: 'Tests generated',
          description: `Unit tests generated successfully for ${response.data.test_class_name || 'class'}`,
        });
      }
    } catch (error: any) {
      console.error('Generate test error:', error);
      setGeneratedTest(mockGeneratedTest);
      setActiveTab('test');
      toast({
        title: 'Using mock data',
        description: error.response?.data?.detail || error.message || 'S7 service unavailable, showing example tests',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
      setLoadingAction(null);
    }
  };

  const handleSuggestTests = async () => {
    setIsLoading(true);
    setLoadingAction('suggest');
    try {
      const response = await api.suggestTestCases(javaCode);
      if (response.data?.method_suggestions) {
        const allSuggestions: TestSuggestion[] = [];
        response.data.method_suggestions.forEach((ms: { method_name?: string; methodName?: string; suggestions?: Array<{ test_name?: string; testName?: string; type?: string; description?: string; priority?: number }> }) => {
          (ms.suggestions || []).forEach((s) => {
            allSuggestions.push({
              methodName: ms.method_name || ms.methodName || '',
              testName: s.test_name || s.testName || '',
              type: (s.type || 'equivalence') as 'equivalence' | 'boundary' | 'null' | 'exception',
              description: s.description || '',
              priority: s.priority || 1,
              checked: false,
            });
          });
        });
        setSuggestions(allSuggestions);
        setActiveTab('suggestions');
        toast({
          title: 'Suggestions generated',
          description: `${allSuggestions.length} test cases suggested`,
        });
      }
    } catch (error: any) {
      console.error('Suggest tests error:', error);
      setSuggestions(mockSuggestions);
      setActiveTab('suggestions');
      toast({
        title: 'Using mock data',
        description: error.response?.data?.detail || error.message || 'S7 service unavailable, showing example suggestions',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
      setLoadingAction(null);
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(generatedTest);
    toast({
      title: 'Code copied',
      description: 'The code has been copied to clipboard',
    });
  };

  const handleDownload = () => {
    const blob = new Blob([generatedTest], { type: 'text/java' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${analysis?.className || 'Test'}Test.java`;
    link.click();
    URL.revokeObjectURL(url);
    toast({
      title: 'File downloaded',
      description: `${analysis?.className || 'Test'}Test.java`,
    });
  };

  const toggleSuggestion = (index: number) => {
    setSuggestions((prev) =>
      prev.map((s, i) => (i === index ? { ...s, checked: !s.checked } : s))
    );
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'equivalence':
        return 'bg-primary/20 text-primary border-primary/30';
      case 'boundary':
        return 'bg-warning/20 text-warning border-warning/30';
      case 'null':
        return 'bg-destructive/20 text-destructive border-destructive/30';
      case 'exception':
        return 'bg-coverage-mutation/20 text-coverage-mutation border-coverage-mutation/30';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Test Generator</h1>
          <p className="text-muted-foreground">
            Analyze your Java code and generate unit tests automatically
            {classNameFromNav && (
              <span className="ml-2 text-xs text-primary">
                (Class: <code className="bg-muted px-1.5 py-0.5 rounded">{classNameFromNav}</code>)
              </span>
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
      </div>
      
      {/* Info Card - Class from Navigation */}
      {classNameFromNav && (
        <Card className="bg-blue-900/5 border-blue-900/20">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-blue-500 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold mb-1">Class Selected: {classNameFromNav}</h3>
                <p className="text-xs text-muted-foreground mb-2">
                  Please paste the Java source code for <code className="text-xs bg-muted px-1 py-0.5 rounded">{classNameFromNav}</code> in the editor below, or fetch it from the repository.
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    if (!classNameFromNav || !repoId) {
                      toast({
                        title: 'Missing information',
                        description: 'Class name or repository not available',
                        variant: 'destructive',
                      });
                      return;
                    }

                    try {
                      setIsLoading(true);
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
                      const urlMatch = repo.url.match(/(?:github|gitlab)\.com\/([^/]+\/[^/]+)/);
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
                      
                      // Convert package to path
                      const classPath = classNameFromNav.replace(/\./g, '/') + '.java';
                      const shortClassName = classNameFromNav.split('.').pop() || classNameFromNav;
                      
                      let sourceCode: string | null = null;

                      // Try direct paths (GitHub API works for public repos without auth)
                      const sourcePaths = [
                        `src/main/java/${classPath}`,
                        `src/${classPath}`,
                        `${classPath}`,
                      ];

                      for (const path of sourcePaths) {
                        try {
                          if (isGitLab) {
                            const gitlabUrl = `https://gitlab.com/api/v4/projects/${encodeURIComponent(`${owner}/${repoName}`)}/repository/files/${encodeURIComponent(path)}/raw?ref=${branch}`;
                            const response = await fetch(gitlabUrl);
                            if (response.ok) {
                              sourceCode = await response.text();
                              break;
                            }
                          } else {
                            // GitHub API - try raw content first (simpler)
                            const githubUrl = `https://api.github.com/repos/${owner}/${repoName}/contents/${path}?ref=${branch}`;
                            
                            // Try raw content endpoint
                            const rawUrl = `https://raw.githubusercontent.com/${owner}/${repoName}/${branch}/${path}`;
                            const rawResponse = await fetch(rawUrl);
                            if (rawResponse.ok) {
                              sourceCode = await rawResponse.text();
                              break;
                            }
                            
                            // Fallback to JSON API
                            const jsonResponse = await fetch(githubUrl);
                            if (jsonResponse.ok) {
                              const data = await jsonResponse.json();
                              if (data.content && data.encoding === 'base64') {
                                sourceCode = atob(data.content.replace(/\s/g, ''));
                                break;
                              }
                            }
                          }
                        } catch (error) {
                          continue;
                        }
                      }

                      if (sourceCode) {
                        setJavaCode(sourceCode);
                        toast({
                          title: 'Source code fetched',
                          description: `Code for ${classNameFromNav} loaded successfully`,
                        });
                      } else {
                        toast({
                          title: 'Source code not found',
                          description: `Could not find ${classNameFromNav} in repository. Please paste the code manually.`,
                          variant: 'destructive',
                        });
                      }
                    } catch (error: any) {
                      toast({
                        title: 'Error fetching source code',
                        description: error.message || 'Please paste the code manually',
                        variant: 'destructive',
                      });
                    } finally {
                      setIsLoading(false);
                    }
                  }}
                  disabled={isLoading || !classNameFromNav || !repoId}
                >
                  <FileCode className="mr-2 h-4 w-4" />
                  Fetch from Repository
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content - Split View */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left Panel - Code Editor */}
        <Card className="flex flex-col">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <FileCode className="h-4 w-4" />
                Java Source Code
              </CardTitle>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAnalyze}
                  disabled={isLoading}
                >
                  {loadingAction === 'analyze' ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="mr-2 h-4 w-4" />
                  )}
                  Analyze
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSuggestTests}
                  disabled={isLoading}
                >
                  {loadingAction === 'suggest' ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Lightbulb className="mr-2 h-4 w-4" />
                  )}
                  Suggest
                </Button>
                <Button size="sm" onClick={handleGenerateTest} disabled={isLoading}>
                  {loadingAction === 'generate' ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <FlaskConical className="mr-2 h-4 w-4" />
                  )}
                  Generate Tests
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex-1 p-0">
            <div className="h-[600px] border-t border-border">
              <Editor
                height="100%"
                defaultLanguage="java"
                value={javaCode}
                onChange={(value) => setJavaCode(value || '')}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 13,
                  fontFamily: "'JetBrains Mono', monospace",
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  padding: { top: 16 },
                }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Right Panel - Output Tabs */}
        <Card className="flex flex-col">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <div className="flex items-center justify-between">
                  <TabsList>
                    <TabsTrigger value="test" className="flex items-center gap-2">
                      <FlaskConical className="h-4 w-4" />
                      Generated Test
                    </TabsTrigger>
                    <TabsTrigger value="analysis" className="flex items-center gap-2">
                      <FolderTree className="h-4 w-4" />
                      Analysis
                    </TabsTrigger>
                    <TabsTrigger value="suggestions" className="flex items-center gap-2">
                      <CheckSquare className="h-4 w-4" />
                      Suggestions
                    </TabsTrigger>
                    <TabsTrigger value="mutations" className="flex items-center gap-2">
                      <Bug className="h-4 w-4" />
                      Mutations
                    </TabsTrigger>
                  </TabsList>
                  {generatedTest && activeTab === 'test' && (
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" onClick={handleCopyCode}>
                        <Copy className="mr-2 h-4 w-4" />
                        Copy
                      </Button>
                      <Button variant="outline" size="sm" onClick={handleDownload}>
                        <Download className="mr-2 h-4 w-4" />
                        Download
                      </Button>
                    </div>
                  )}
                </div>
              </Tabs>
            </div>
          </CardHeader>
          <CardContent className="flex-1 p-0">
            <Tabs value={activeTab} className="h-full">
              <TabsContent value="test" className="h-[600px] m-0 border-t border-border">
                {generatedTest ? (
                  <Editor
                    height="100%"
                    defaultLanguage="java"
                    value={generatedTest}
                    theme="vs-dark"
                    options={{
                      minimap: { enabled: false },
                      fontSize: 13,
                      fontFamily: "'JetBrains Mono', monospace",
                      lineNumbers: 'on',
                      scrollBeyondLastLine: false,
                      automaticLayout: true,
                      readOnly: true,
                      padding: { top: 16 },
                    }}
                  />
                ) : (
                  <div className="flex h-full items-center justify-center text-muted-foreground">
                    <div className="text-center">
                      <FlaskConical className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Click "Generate Tests" to create unit tests</p>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="analysis" className="h-[600px] m-0 border-t border-border">
                <ScrollArea className="h-full p-4">
                  {analysis ? (
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-lg font-semibold">{analysis.className}</h3>
                        <p className="text-sm text-muted-foreground">{analysis.packageName}</p>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium mb-2">Constructors</h4>
                        <div className="space-y-2">
                          {analysis.constructors.map((ctor, i) => (
                            <div key={i} className="rounded-lg bg-muted/50 p-3 font-mono text-sm">
                              {analysis.className}(
                              {ctor.parameters.map((p) => `${p.type} ${p.name}`).join(', ')})
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium mb-2">Methods ({analysis.methods.length})</h4>
                        <div className="space-y-2">
                          {analysis.methods.map((method, i) => (
                            <div key={i} className="rounded-lg bg-muted/50 p-3">
                              <div className="font-mono text-sm">
                                <span className="text-primary">{method.returnType}</span>{' '}
                                <span className="font-semibold">{method.name}</span>(
                                {method.parameters.map((p) => `${p.type} ${p.name}`).join(', ')})
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium mb-2">Fields ({analysis.fields.length})</h4>
                        <div className="space-y-2">
                          {analysis.fields.map((field, i) => (
                            <div key={i} className="rounded-lg bg-muted/50 p-3 font-mono text-sm">
                              <span className="text-primary">{field.type}</span> {field.name}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex h-full items-center justify-center text-muted-foreground">
                      <div className="text-center">
                        <FolderTree className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Click "Analyze" to see the class structure</p>
                      </div>
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>

              <TabsContent value="suggestions" className="h-[600px] m-0 border-t border-border">
                <ScrollArea className="h-full p-4">
                  {suggestions.length > 0 ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">
                          {suggestions.filter((s) => s.checked).length} / {suggestions.length} selected
                        </p>
                        <Badge variant="outline" className="bg-success/20 text-success">
                          Estimated coverage: 90%
                        </Badge>
                      </div>
                      <div className="space-y-2">
                        {suggestions.map((suggestion, index) => (
                          <div
                            key={index}
                            className="flex items-start gap-3 rounded-lg border border-border p-3 hover:bg-muted/30 transition-colors"
                          >
                            <Checkbox
                              checked={suggestion.checked}
                              onCheckedChange={() => toggleSuggestion(index)}
                            />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="font-mono text-sm font-medium">
                                  {suggestion.testName}
                                </span>
                                <Badge
                                  variant="outline"
                                  className={`text-xs ${getTypeColor(suggestion.type)}`}
                                >
                                  {suggestion.type}
                                </Badge>
                              </div>
                              <p className="text-sm text-muted-foreground">
                                {suggestion.description}
                              </p>
                              <p className="text-xs text-muted-foreground mt-1">
                                Method: {suggestion.methodName} • Priority: {suggestion.priority}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="flex h-full items-center justify-center text-muted-foreground">
                      <div className="text-center">
                        <Lightbulb className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Click "Suggest" to get test case recommendations</p>
                      </div>
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>

              <TabsContent value="mutations" className="h-[600px] m-0 border-t border-border">
                <ScrollArea className="h-full p-4">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-muted-foreground">
                        Mutation checklist to improve coverage score
                      </p>
                      <Badge variant="outline">
                        {mutationChecklist.filter((m) => m.covered).length} / {mutationChecklist.length} covered
                      </Badge>
                    </div>
                    {mutationsData ? (
                      <>
                        <div className="mb-4 p-3 rounded-lg bg-muted/30 border">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">Total Mutations:</span>
                            <span className="font-semibold">{mutationsData.totalMutations}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm mt-2">
                            <span className="text-muted-foreground">Killed:</span>
                            <span className="font-semibold text-success">{mutationsData.killedMutations}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm mt-2">
                            <span className="text-muted-foreground">Survived:</span>
                            <span className="font-semibold text-destructive">{mutationsData.survivedMutations}</span>
                          </div>
                        </div>
                        <div className="space-y-2">
                          {mutationChecklist.map((mutation) => (
                            <div
                              key={mutation.id}
                              className={`flex items-start gap-3 rounded-lg border p-3 ${
                                mutation.covered
                                  ? 'border-success/30 bg-success/5'
                                  : 'border-border bg-muted/30'
                              }`}
                            >
                              <Checkbox checked={mutation.covered} disabled />
                              <div className="flex-1">
                                <p className="font-medium text-sm">{mutation.mutation}</p>
                                <p className="text-sm text-muted-foreground">{mutation.description}</p>
                                {mutation.total !== undefined && mutation.total > 0 && (
                                  <p className="text-xs text-muted-foreground mt-1">
                                    {mutation.killed || 0} killed / {mutation.total} total
                                  </p>
                                )}
                              </div>
                              {mutation.covered ? (
                                <Badge className="bg-success/20 text-success border-success/30">
                                  Covered
                                </Badge>
                              ) : (
                                <Badge variant="outline" className="text-muted-foreground">
                                  {mutation.total !== undefined && mutation.total > 0 ? 'Partially covered' : 'To cover'}
                                </Badge>
                              )}
                            </div>
                          ))}
                        </div>
                      </>
                    ) : (
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground text-center py-4">
                          No mutation testing data available. Upload a PIT report to see mutation coverage.
                        </p>
                        {mutationChecklist.map((mutation) => (
                          <div
                            key={mutation.id}
                            className="flex items-start gap-3 rounded-lg border p-3 border-border bg-muted/30 opacity-50"
                          >
                            <Checkbox checked={false} disabled />
                            <div className="flex-1">
                              <p className="font-medium text-sm">{mutation.mutation}</p>
                              <p className="text-sm text-muted-foreground">{mutation.description}</p>
                            </div>
                            <Badge variant="outline" className="text-muted-foreground">
                              To cover
                            </Badge>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
