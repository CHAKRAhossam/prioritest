"""Kafka producer service for publishing events."""
import json
import logging
from typing import Optional
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.cimpl import KafkaException

from src.config import settings
from src.models.events import CommitEvent, IssueEvent, CIArtifactEvent

logger = logging.getLogger(__name__)


class KafkaService:
    """Service for publishing events to Kafka topics."""
    
    def __init__(self):
        """Initialize Kafka producer."""
        self.producer = Producer({
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'client.id': 'collecte-depots-producer',
            'acks': 'all',  # Wait for all replicas
            'retries': 3,
            'max.in.flight.requests.per.connection': 1,
        })
        self._ensure_topics_exist()
    
    def _ensure_topics_exist(self):
        """Ensure Kafka topics exist."""
        admin_client = AdminClient({
            'bootstrap.servers': settings.kafka_bootstrap_servers
        })
        
        topics = [
            NewTopic(settings.kafka_topic_commits, num_partitions=3, replication_factor=1),
            NewTopic(settings.kafka_topic_issues, num_partitions=3, replication_factor=1),
            NewTopic(settings.kafka_topic_artifacts, num_partitions=3, replication_factor=1),
        ]
        
        try:
            futures = admin_client.create_topics(topics)
            for topic, future in futures.items():
                try:
                    future.result()
                    logger.info(f"Topic {topic} created or already exists")
                except KafkaException as e:
                    if "already exists" in str(e).lower():
                        logger.debug(f"Topic {topic} already exists")
                    else:
                        logger.warning(f"Could not create topic {topic}: {e}")
        except Exception as e:
            logger.warning(f"Error ensuring topics exist: {e}")
    
    def _delivery_callback(self, err, msg):
        """Callback for message delivery confirmation."""
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")
    
    def publish_commit(self, event: CommitEvent) -> bool:
        """
        Publish commit event to Kafka.
        
        Args:
            event: CommitEvent to publish
            
        Returns:
            bool: True if published successfully
        """
        try:
            message = event.model_dump_json()
            self.producer.produce(
                settings.kafka_topic_commits,
                key=event.repository_id.encode('utf-8'),
                value=message.encode('utf-8'),
                callback=self._delivery_callback
            )
            self.producer.poll(0)
            logger.info(f"Published commit event {event.event_id} to {settings.kafka_topic_commits}")
            return True
        except Exception as e:
            logger.error(f"Error publishing commit event: {e}")
            return False
    
    def publish_issue(self, event: IssueEvent) -> bool:
        """
        Publish issue event to Kafka.
        
        Args:
            event: IssueEvent to publish
            
        Returns:
            bool: True if published successfully
        """
        try:
            message = event.model_dump_json()
            self.producer.produce(
                settings.kafka_topic_issues,
                key=event.repository_id.encode('utf-8'),
                value=message.encode('utf-8'),
                callback=self._delivery_callback
            )
            self.producer.poll(0)
            logger.info(f"Published issue event {event.event_id} to {settings.kafka_topic_issues}")
            return True
        except Exception as e:
            logger.error(f"Error publishing issue event: {e}")
            return False
    
    def publish_artifact(self, event: CIArtifactEvent) -> bool:
        """
        Publish CI artifact event to Kafka.
        
        Args:
            event: CIArtifactEvent to publish
            
        Returns:
            bool: True if published successfully
        """
        try:
            message = event.model_dump_json()
            self.producer.produce(
                settings.kafka_topic_artifacts,
                key=event.repository_id.encode('utf-8'),
                value=message.encode('utf-8'),
                callback=self._delivery_callback
            )
            self.producer.poll(0)
            logger.info(f"Published artifact event {event.event_id} to {settings.kafka_topic_artifacts}")
            return True
        except Exception as e:
            logger.error(f"Error publishing artifact event: {e}")
            return False
    
    def flush(self, timeout: float = 10.0):
        """Flush pending messages."""
        self.producer.flush(timeout)
    
    def close(self):
        """Close the producer."""
        self.flush()
        logger.info("Kafka producer closed")

