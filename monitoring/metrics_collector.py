"""Comprehensive metrics collection system for VDW Orchestrator calibration."""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timedelta

from core.models import PhaseExecution, ProjectOutcomes
from core.event_bus import EventBus


class MetricType(Enum):
    """Types of metrics collected by the system."""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    USER_EXPERIENCE = "user_experience"
    RESOURCE_USAGE = "resource_usage"
    BUSINESS = "business"


@dataclass
class Metric:
    """Individual metric data point."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str]
    unit: str = ""


class VDWMetricsCollector:
    """Comprehensive metrics collection for VDW Orchestrator."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.metrics_buffer: List[Metric] = []
        self.collection_intervals = {
            MetricType.PERFORMANCE: 10,  # seconds
            MetricType.QUALITY: 60,
            MetricType.USER_EXPERIENCE: 300,
            MetricType.RESOURCE_USAGE: 30,
            MetricType.BUSINESS: 3600
        }
        self.running = False
    
    async def start_collection(self):
        """Start the metrics collection process."""
        self.running = True
        
        # Start collection tasks for different metric types
        tasks = [
            asyncio.create_task(self._collect_performance_metrics()),
            asyncio.create_task(self._collect_quality_metrics()),
            asyncio.create_task(self._collect_user_experience_metrics()),
            asyncio.create_task(self._collect_resource_usage_metrics()),
            asyncio.create_task(self._collect_business_metrics()),
            asyncio.create_task(self._flush_metrics_buffer())
        ]
        
        await asyncio.gather(*tasks)
    
    def collect_phase_metrics(self, phase_id: str, execution_data: PhaseExecution):
        """Collect performance and quality metrics for each phase."""
        timestamp = datetime.now()
        labels = {"phase_id": phase_id, "project_id": execution_data.project_id}
        
        # Performance metrics
        self._add_metric(Metric(
            name="phase_duration",
            value=execution_data.duration,
            metric_type=MetricType.PERFORMANCE,
            timestamp=timestamp,
            labels=labels,
            unit="seconds"
        ))
        
        self._add_metric(Metric(
            name="tool_usage_count",
            value=len(execution_data.tools_used),
            metric_type=MetricType.PERFORMANCE,
            timestamp=timestamp,
            labels=labels,
            unit="count"
        ))
        
        # Quality metrics
        quality_score = self._calculate_quality_score(execution_data)
        self._add_metric(Metric(
            name="artifact_quality_score",
            value=quality_score,
            metric_type=MetricType.QUALITY,
            timestamp=timestamp,
            labels=labels,
            unit="score"
        ))
    
    def collect_project_outcomes(self, project_id: str, outcomes: ProjectOutcomes):
        """Track project success metrics and user satisfaction."""
        timestamp = datetime.now()
        labels = {"project_id": project_id}
        
        # Business metrics
        self._add_metric(Metric(
            name="project_completion_rate",
            value=outcomes.phases_completed / 5,
            metric_type=MetricType.BUSINESS,
            timestamp=timestamp,
            labels=labels,
            unit="rate"
        ))
        
        # User experience metrics
        self._add_metric(Metric(
            name="user_satisfaction_score",
            value=outcomes.satisfaction_score,
            metric_type=MetricType.USER_EXPERIENCE,
            timestamp=timestamp,
            labels=labels,
            unit="score"
        ))
    
    async def _collect_performance_metrics(self):
        """Collect system performance metrics."""
        while self.running:
            timestamp = datetime.now()
            
            # Collect system-wide performance metrics
            response_time = await self._measure_system_response_time()
            self._add_metric(Metric(
                name="system_response_time",
                value=response_time,
                metric_type=MetricType.PERFORMANCE,
                timestamp=timestamp,
                labels={"component": "orchestrator"},
                unit="milliseconds"
            ))
            
            await asyncio.sleep(self.collection_intervals[MetricType.PERFORMANCE])
    
    def _add_metric(self, metric: Metric):
        """Add a metric to the collection buffer."""
        self.metrics_buffer.append(metric)
        
        # Emit metric event
        self.event_bus.emit("metric_collected", {
            "metric": metric.__dict__,
            "timestamp": metric.timestamp.isoformat()
        })
    
    def _calculate_quality_score(self, execution_data: PhaseExecution) -> float:
        """Calculate quality score for phase execution."""
        # Implementation would analyze artifacts, validation results, etc.
        # For now, return a placeholder score
        base_score = 0.8
        
        # Adjust based on validation results
        if execution_data.validation_passed:
            base_score += 0.1
        
        # Adjust based on error count
        error_penalty = min(0.3, execution_data.error_count * 0.05)
        base_score -= error_penalty
        
        return max(0.0, min(1.0, base_score))
    
    async def _measure_system_response_time(self) -> float:
        """Measure system response time for health check."""
        start_time = time.time()
        
        # Perform a lightweight health check operation
        try:
            # This would be replaced with actual system health check
            await asyncio.sleep(0.001)  # Simulate operation
            end_time = time.time()
            return (end_time - start_time) * 1000  # Convert to milliseconds
        except Exception:
            return float('inf')  # Indicate system issues
    
    async def _flush_metrics_buffer(self):
        """Periodically flush metrics buffer to storage."""
        while self.running:
            if self.metrics_buffer:
                # Flush metrics to storage (Redis, InfluxDB, etc.)
                await self._persist_metrics(self.metrics_buffer.copy())
                self.metrics_buffer.clear()
            
            await asyncio.sleep(60)  # Flush every minute
    
    async def _persist_metrics(self, metrics: List[Metric]):
        """Persist metrics to storage system."""
        # Implementation would persist to time-series database
        # For now, just log the metrics
        for metric in metrics:
            print(f"Metric: {metric.name} = {metric.value} {metric.unit} at {metric.timestamp}")
    
    def stop_collection(self):
        """Stop the metrics collection process."""
        self.running = False