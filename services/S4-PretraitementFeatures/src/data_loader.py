"""
Data loader for S4 - loads real data from PostgreSQL/TimescaleDB
Combines data from S1 (commits), S2 (CK metrics via Kafka/Feast), and S3 (test metrics)
"""
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from typing import Optional
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Kafka consumer for S2 metrics
try:
    from src.kafka_consumer import get_consumer, CodeMetricsConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger.warning("Kafka consumer not available - S2 metrics will not be loaded")


class RealDataLoader:
    """Loads real data from PostgreSQL and S3 API"""
    
    def __init__(self, database_url: Optional[str] = None, s3_api_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "postgresql://prioritest:prioritest@postgres:5432/prioritest"
        )
        self.s3_api_url = s3_api_url or os.getenv(
            "S3_API_URL",
            "http://historique-tests:8081"
        )
        self.engine = None
        
    def connect(self):
        """Connect to database"""
        try:
            self.engine = create_engine(self.database_url)
            logger.info("Connected to database")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def load_commits(self) -> pd.DataFrame:
        """Load commits from S1 (commits table)"""
        if not self.engine:
            self.connect()
        
        query = text("""
            SELECT 
                c.id as commit_id,
                c.commit_sha,
                c.repository_id,
                c.commit_message,
                c.author_email,
                c.author_name,
                c.timestamp as commit_date,
                c.metadata_json->>'branch' as branch,
                c.metadata_json->>'source' as source,
                json_array_length(COALESCE(c.files_changed, '[]'::json)) as files_changed_count,
                COALESCE(
                    (SELECT SUM((f->>'additions')::int) 
                     FROM json_array_elements(c.files_changed) f),
                    0
                ) as lines_added,
                COALESCE(
                    (SELECT SUM((f->>'deletions')::int) 
                     FROM json_array_elements(c.files_changed) f),
                    0
                ) as lines_deleted
            FROM commits c
            WHERE c.timestamp IS NOT NULL
            ORDER BY c.timestamp ASC
        """)
        
        try:
            df = pd.read_sql(query, self.engine)
            logger.info(f"Loaded {len(df)} commits from database")
            return df
        except Exception as e:
            logger.warning(f"Error loading commits: {e}. Returning empty DataFrame")
            return pd.DataFrame()
    
    def load_test_metrics(self, repository_ids: Optional[list] = None) -> pd.DataFrame:
        """Load test metrics from S3 (test_coverage table)"""
        if not self.engine:
            self.connect()
        
        # Build query with optional repository filter
        base_query = """
            SELECT 
                tc.id,
                tc.repository_id,
                tc.commit_sha,
                tc.class_name,
                tc.file_path,
                tc.package_name,
                tc.line_coverage,
                tc.branch_coverage,
                tc.method_coverage,
                tc.instruction_coverage,
                tc.mutation_score,
                tc.lines_covered,
                tc.lines_missed,
                tc.timestamp,
                tc.build_id,
                tc.branch
            FROM test_coverage tc
            WHERE tc.timestamp IS NOT NULL
        """
        
        if repository_ids:
            repo_filter = "', '".join(repository_ids)
            base_query += f" AND tc.repository_id IN ('{repo_filter}')"
        
        base_query += " ORDER BY tc.timestamp ASC"
        
        try:
            df = pd.read_sql(text(base_query), self.engine)
            logger.info(f"Loaded {len(df)} test coverage records from database")
            return df
        except Exception as e:
            logger.warning(f"Error loading test metrics: {e}. Returning empty DataFrame")
            return pd.DataFrame()
    
    def load_test_results(self, repository_ids: Optional[list] = None) -> pd.DataFrame:
        """Load test results from S3 (test_result table)"""
        if not self.engine:
            self.connect()
        
        base_query = """
            SELECT 
                tr.id,
                tr.repository_id,
                tr.commit_sha,
                tr.test_name,
                tr.test_class as class_name,
                tr.status,
                tr.execution_time as duration_ms,
                tr.error_message,
                tr.timestamp
            FROM test_result tr
            WHERE tr.timestamp IS NOT NULL
        """
        
        if repository_ids:
            repo_filter = "', '".join(repository_ids)
            base_query += f" AND tr.repository_id IN ('{repo_filter}')"
        
        base_query += " ORDER BY tr.timestamp ASC"
        
        try:
            df = pd.read_sql(text(base_query), self.engine)
            logger.info(f"Loaded {len(df)} test results from database")
            return df
        except Exception as e:
            logger.warning(f"Error loading test results: {e}. Returning empty DataFrame")
            return pd.DataFrame()
    
    def load_code_metrics_from_kafka(self, timeout_ms: int = 10000) -> pd.DataFrame:
        """Load code metrics from S2 via Kafka topic"""
        if not KAFKA_AVAILABLE:
            logger.warning("Kafka consumer not available")
            return pd.DataFrame()
        
        try:
            consumer = get_consumer()
            
            # Consume available messages
            count = consumer.consume_batch(max_messages=5000, timeout_ms=timeout_ms)
            logger.info(f"Consumed {count} code metrics from Kafka")
            
            # Get as DataFrame
            df = consumer.get_metrics_dataframe()
            
            if not df.empty:
                logger.info(f"Loaded {len(df)} code metrics from S2 (Kafka)")
            else:
                logger.info("No code metrics available in Kafka topic")
            
            return df
            
        except Exception as e:
            logger.warning(f"Error loading code metrics from Kafka: {e}")
            return pd.DataFrame()
    
    def aggregate_test_metrics_by_class(self, test_metrics_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate test metrics by class and commit"""
        if test_metrics_df.empty:
            return pd.DataFrame()
        
        # Group by repository, commit, and class
        aggregated = test_metrics_df.groupby([
            'repository_id', 'commit_sha', 'class_name'
        ]).agg({
            'line_coverage': 'mean',
            'branch_coverage': 'mean',
            'method_coverage': 'mean',
            'instruction_coverage': 'mean',
            'mutation_score': 'mean',
            'lines_covered': 'sum',
            'lines_missed': 'sum',
            'timestamp': 'max'  # Latest timestamp for this class in this commit
        }).reset_index()
        
        return aggregated
    
    def aggregate_test_results_by_class(self, test_results_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate test results by class and commit"""
        if test_results_df.empty:
            return pd.DataFrame()
        
        # Group by repository, commit, and class
        aggregated = test_results_df.groupby([
            'repository_id', 'commit_sha', 'class_name'
        ]).agg({
            'status': lambda x: (x == 'PASSED').sum(),  # Count passed tests
            'duration_ms': 'sum',  # Total test duration
            'timestamp': 'max'
        }).reset_index()
        
        aggregated['tests_passed'] = aggregated['status']
        aggregated['total_test_duration_ms'] = aggregated['duration_ms']
        aggregated = aggregated.drop(columns=['status', 'duration_ms'])
        
        return aggregated
    
    def combine_data(
        self, 
        commits_df: pd.DataFrame,
        test_metrics_df: pd.DataFrame,
        test_results_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Combine commits, test metrics, and test results into a single dataset
        Creates one row per (repository_id, commit_sha, class_name) combination
        """
        if commits_df.empty:
            logger.warning("No commits found. Cannot combine data.")
            return pd.DataFrame()
        
        # Start with commits
        df = commits_df.copy()
        
        # Convert commit_date to datetime if not already
        if 'commit_date' in df.columns:
            df['commit_date'] = pd.to_datetime(df['commit_date'])
        
        # Aggregate test metrics by class and commit
        test_metrics_agg = self.aggregate_test_metrics_by_class(test_metrics_df)
        test_results_agg = self.aggregate_test_results_by_class(test_results_df)
        
        # Merge test metrics (left join on repository_id + commit_sha)
        # Note: We'll need to handle class_name matching later
        # For now, we'll merge at commit level and then expand per class
        if not test_metrics_agg.empty:
            # Get unique classes per commit
            commit_classes = test_metrics_agg.groupby(['repository_id', 'commit_sha']).agg({
                'class_name': lambda x: list(x),
                'line_coverage': 'mean',  # Average coverage across all classes in commit
                'branch_coverage': 'mean',
                'method_coverage': 'mean',
                'mutation_score': 'mean'
            }).reset_index()
            
            commit_classes.columns = [
                'repository_id', 'commit_sha', 'classes', 
                'avg_line_coverage', 'avg_branch_coverage', 
                'avg_method_coverage', 'avg_mutation_score'
            ]
            
            df = df.merge(commit_classes, on=['repository_id', 'commit_sha'], how='left')
        else:
            df['classes'] = None
            df['avg_line_coverage'] = np.nan
            df['avg_branch_coverage'] = np.nan
            df['avg_method_coverage'] = np.nan
            df['avg_mutation_score'] = np.nan
        
        # Merge test results
        if not test_results_agg.empty:
            commit_test_results = test_results_agg.groupby(['repository_id', 'commit_sha']).agg({
                'tests_passed': 'sum',
                'total_test_duration_ms': 'sum'
            }).reset_index()
            
            df = df.merge(commit_test_results, on=['repository_id', 'commit_sha'], how='left')
        else:
            df['tests_passed'] = 0
            df['total_test_duration_ms'] = 0
        
        # Calculate derived features from commits
        df['lines_modified'] = df['lines_added'].fillna(0) + df['lines_deleted'].fillna(0)
        
        # Create target variable (simplified: 1 if low coverage, 0 otherwise)
        # In real scenario, this would be based on actual bug/issue data
        df['target'] = (df['avg_line_coverage'].fillna(0) < 0.5).astype(int)
        
        # Fill missing values for numeric columns
        numeric_cols = ['avg_line_coverage', 'avg_branch_coverage', 'avg_method_coverage', 
                       'avg_mutation_score', 'tests_passed', 'total_test_duration_ms',
                       'lines_modified', 'files_changed_count']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # Add complexity placeholder (would come from S2 in real scenario)
        # For now, use lines_modified as proxy
        df['complexity'] = df['lines_modified'].clip(upper=500) / 50.0
        
        # Add author_type placeholder (would come from commit analysis)
        df['author_type'] = 'Unknown'
        
        # Add file_type placeholder
        df['file_type'] = '.java'  # Default for Java projects
        
        # Convert 'classes' list to count (number of classes) - avoid unhashable list issue
        if 'classes' in df.columns:
            df['num_classes'] = df['classes'].apply(lambda x: len(x) if isinstance(x, list) else 0)
            df = df.drop(columns=['classes'])
        
        # Drop other problematic columns that can't be processed by sklearn
        cols_to_drop = ['commit_sha', 'commit_message', 'branch', 'source']
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
        
        logger.info(f"Combined dataset: {len(df)} rows")
        return df
    
    def merge_code_metrics(self, df: pd.DataFrame, code_metrics_df: pd.DataFrame) -> pd.DataFrame:
        """Merge S2 code metrics into the main dataframe"""
        if code_metrics_df.empty:
            logger.info("No code metrics to merge - using placeholders")
            return df
        
        # Aggregate code metrics by repository_id and commit_sha
        code_agg = code_metrics_df.groupby(['repository_id', 'commit_sha']).agg({
            'loc': 'sum',
            'cyclomatic_complexity': 'mean',
            'wmc': 'sum',
            'dit': 'max',
            'noc': 'sum',
            'cbo': 'mean',
            'rfc': 'mean',
            'lcom': 'mean'
        }).reset_index()
        
        code_agg.columns = [
            'repository_id', 'commit_sha',
            's2_loc', 's2_cyclomatic_complexity', 's2_wmc', 
            's2_dit', 's2_noc', 's2_cbo', 's2_rfc', 's2_lcom'
        ]
        
        # Merge with main dataframe
        df = df.merge(code_agg, on=['repository_id', 'commit_sha'], how='left')
        
        # Fill NaN with 0 for S2 metrics
        s2_cols = ['s2_loc', 's2_cyclomatic_complexity', 's2_wmc', 
                   's2_dit', 's2_noc', 's2_cbo', 's2_rfc', 's2_lcom']
        for col in s2_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        logger.info(f"Merged S2 code metrics: {len(code_agg)} commit aggregations")
        return df
    
    def load_real_data(self) -> pd.DataFrame:
        """
        Main method to load all real data and combine into dataset
        """
        logger.info("Loading real data from database...")
        
        # Load commits from S1
        commits_df = self.load_commits()
        
        if commits_df.empty:
            logger.warning("No commits found in database. Cannot proceed with real data.")
            return pd.DataFrame()
        
        # Get unique repository IDs
        repository_ids = commits_df['repository_id'].unique().tolist()
        logger.info(f"Found {len(repository_ids)} repositories: {repository_ids}")
        
        # Load test metrics from S3
        test_metrics_df = self.load_test_metrics(repository_ids)
        
        # Load test results from S3
        test_results_df = self.load_test_results(repository_ids)
        
        # Load code metrics from S2 (Kafka)
        code_metrics_df = self.load_code_metrics_from_kafka()
        
        # Combine S1 + S3 data
        combined_df = self.combine_data(commits_df, test_metrics_df, test_results_df)
        
        if combined_df is None or combined_df.empty:
            logger.warning("Combined data is empty")
            return pd.DataFrame()
        
        # Merge S2 code metrics
        if not code_metrics_df.empty:
            # Need to add commit_sha back temporarily for merging
            commits_with_sha = commits_df[['commit_id', 'repository_id', 'commit_sha']].copy()
            combined_df = combined_df.merge(
                commits_with_sha[['commit_id', 'commit_sha']], 
                on='commit_id', 
                how='left'
            )
            combined_df = self.merge_code_metrics(combined_df, code_metrics_df)
            # Drop commit_sha again
            combined_df = combined_df.drop(columns=['commit_sha'], errors='ignore')
        
        return combined_df
