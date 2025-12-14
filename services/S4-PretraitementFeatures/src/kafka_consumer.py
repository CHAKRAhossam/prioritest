"""
Kafka consumer for S4 - Consumes code.metrics from S2 (AnalyseStatique)
Stores metrics in memory/database for feature engineering
"""
import os
import json
import threading
import logging
from typing import Dict, List, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeMetricsConsumer:
    """Consumes code metrics from Kafka topic published by S2"""
    
    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        topic: str = "code.metrics",
        group_id: str = "s4-pretraitement-features"
    ):
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"
        )
        self.topic = topic
        self.group_id = group_id
        self.consumer = None
        self.running = False
        self.metrics_store: Dict[str, Dict] = {}  # key: (repo_id, commit_sha, class_name)
        self._lock = threading.Lock()
        
    def connect(self):
        """Connect to Kafka"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
            logger.info(f"Subscribed to topic: {self.topic}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False
    
    def process_message(self, message):
        """Process a single code metrics message from S2"""
        try:
            data = message.value
            
            # Extract key fields
            repo_id = data.get('repository_id', '')
            commit_sha = data.get('commit_sha', '')
            class_name = data.get('class_name', '')
            file_path = data.get('file_path', '')
            timestamp = data.get('timestamp', '')
            
            # Extract metrics
            metrics = data.get('metrics', {})
            loc = metrics.get('loc', 0)
            cyclomatic_complexity = metrics.get('cyclomatic_complexity', 0)
            
            # Extract CK metrics
            ck_metrics = metrics.get('ck_metrics', {})
            wmc = ck_metrics.get('wmc', 0)
            dit = ck_metrics.get('dit', 0)
            noc = ck_metrics.get('noc', 0)
            cbo = ck_metrics.get('cbo', 0)
            rfc = ck_metrics.get('rfc', 0)
            lcom = ck_metrics.get('lcom', 0)
            
            # Store in memory
            key = f"{repo_id}|{commit_sha}|{class_name}"
            with self._lock:
                self.metrics_store[key] = {
                    'repository_id': repo_id,
                    'commit_sha': commit_sha,
                    'class_name': class_name,
                    'file_path': file_path,
                    'timestamp': timestamp,
                    'loc': loc,
                    'cyclomatic_complexity': cyclomatic_complexity,
                    'wmc': wmc,
                    'dit': dit,
                    'noc': noc,
                    'cbo': cbo,
                    'rfc': rfc,
                    'lcom': lcom
                }
            
            logger.debug(f"Processed metrics for {class_name} in {repo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    def consume_batch(self, max_messages: int = 1000, timeout_ms: int = 5000) -> int:
        """Consume a batch of messages and return count"""
        if not self.consumer:
            if not self.connect():
                return 0
        
        count = 0
        try:
            # Poll for messages
            messages = self.consumer.poll(timeout_ms=timeout_ms, max_records=max_messages)
            
            for topic_partition, records in messages.items():
                for record in records:
                    if self.process_message(record):
                        count += 1
            
            logger.info(f"Consumed {count} code metrics messages")
            
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
        
        return count
    
    def start_background_consumer(self):
        """Start consuming in background thread"""
        self.running = True
        thread = threading.Thread(target=self._consume_loop, daemon=True)
        thread.start()
        logger.info("Started background Kafka consumer")
        return thread
    
    def _consume_loop(self):
        """Background consumer loop"""
        if not self.connect():
            logger.error("Failed to start consumer loop - cannot connect to Kafka")
            return
        
        while self.running:
            try:
                for message in self.consumer:
                    if not self.running:
                        break
                    self.process_message(message)
            except Exception as e:
                logger.error(f"Consumer loop error: {e}")
                if self.running:
                    import time
                    time.sleep(5)  # Wait before reconnecting
    
    def stop(self):
        """Stop the consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer stopped")
    
    def get_metrics_dataframe(self) -> pd.DataFrame:
        """Get all stored metrics as a DataFrame"""
        with self._lock:
            if not self.metrics_store:
                return pd.DataFrame()
            return pd.DataFrame(list(self.metrics_store.values()))
    
    def get_metrics_for_commit(self, repo_id: str, commit_sha: str) -> pd.DataFrame:
        """Get metrics for a specific commit"""
        with self._lock:
            results = []
            prefix = f"{repo_id}|{commit_sha}|"
            for key, value in self.metrics_store.items():
                if key.startswith(prefix):
                    results.append(value)
            return pd.DataFrame(results) if results else pd.DataFrame()
    
    def get_metrics_count(self) -> int:
        """Get count of stored metrics"""
        with self._lock:
            return len(self.metrics_store)


# Global consumer instance
_consumer_instance: Optional[CodeMetricsConsumer] = None


def get_consumer() -> CodeMetricsConsumer:
    """Get or create the global consumer instance"""
    global _consumer_instance
    if _consumer_instance is None:
        _consumer_instance = CodeMetricsConsumer()
    return _consumer_instance


def init_consumer():
    """Initialize and start the background consumer"""
    consumer = get_consumer()
    consumer.start_background_consumer()
    return consumer


if __name__ == "__main__":
    # Test the consumer
    consumer = CodeMetricsConsumer(bootstrap_servers="localhost:9092")
    
    print("Consuming code metrics from Kafka...")
    count = consumer.consume_batch(max_messages=100, timeout_ms=10000)
    print(f"Consumed {count} messages")
    
    df = consumer.get_metrics_dataframe()
    if not df.empty:
        print(f"\nMetrics DataFrame ({len(df)} rows):")
        print(df.head())
    else:
        print("\nNo metrics found in topic")
    
    consumer.stop()
