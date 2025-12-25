import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { RepositoryProvider } from "@/context/RepositoryContext";
import Dashboard from "./pages/Dashboard";
import Recommendations from "./pages/Recommendations";
import Coverage from "./pages/Coverage";
import Risks from "./pages/Risks";
import Trends from "./pages/Trends";
import Impact from "./pages/Impact";
import Debt from "./pages/Debt";
import Flaky from "./pages/Flaky";
import TestGenerator from "./pages/TestGenerator";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <RepositoryProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/recommendations" element={<Recommendations />} />
              <Route path="/coverage" element={<Coverage />} />
              <Route path="/risks" element={<Risks />} />
              <Route path="/trends" element={<Trends />} />
              <Route path="/impact" element={<Impact />} />
              <Route path="/debt" element={<Debt />} />
              <Route path="/flaky" element={<Flaky />} />
              <Route path="/test-generator" element={<TestGenerator />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </RepositoryProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
