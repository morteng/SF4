"""
Metrics Collector for Meta Cycles System

Tracks and manages performance metrics for all cycles
Maintains historical data for analysis and reporting
"""

import time
from dataclasses import dataclass
from typing import Dict, List
import json
from pathlib import Path

@dataclass
class CycleMetrics:
    cycle_name: str
    start_time: float
    end_time: float = 0.0
    duration: float = 0.0
    success: bool = False
    error_count: int = 0
    dependencies: List[str] = None
    resource_usage: Dict[str, float] = None
    warnings: List[str] = None
    performance_score: float = 0.0
    transition_from: str = None
    transition_to: str = None
    metadata: Dict[str, str] = None
    cpu_usage: List[float] = None
    memory_usage: List[float] = None
    disk_io: Dict[str, float] = None
    network_usage: Dict[str, float] = None
    task_count: int = 0
    completed_tasks: int = 0
    efficiency_ratio: float = 0.0
    quality_score: float = 0.0
    complexity_score: float = 0.0

class MetricsCollector:
    def __init__(self, config_file: str = "meta_cycles/metrics_config.json"):
        """Initialize metrics collector with configuration
        
        Args:
            config_file: Path to JSON configuration file containing resource limits
                        and performance thresholds
        """
        self.metrics_history = []
        self.current_cycle = None
        self.metrics_file = Path("meta_cycles/metrics_history.json")
        self.config_file = Path(config_file)
        
        # Default configuration
        self.resource_limits = {
            'cpu': 0.9,  # 90% CPU usage
            'memory': 2048,  # 2048 MB
            'disk': 1024,  # 1024 MB
            'time': 3600  # 1 hour
        }
        self.performance_thresholds = {
            'duration': 300,  # 5 minutes
            'error_count': 3,
            'warning_count': 5
        }
        self.score_weights = {
            'time': 0.25,
            'error': 0.25,
            'resource': 0.20,
            'task': 0.15,
            'quality': 0.15
        }
        
        # Load configuration if exists
        self._load_config()
        
    def start_cycle(self, cycle_name: str, dependencies: List[str] = None):
        """Start tracking metrics for a new cycle"""
        self.current_cycle = CycleMetrics(
            cycle_name=cycle_name,
            start_time=time.time(),
            dependencies=dependencies,
            resource_usage={}
        )
        
    def end_cycle(self, success: bool = True, next_cycle: str = None):
        """Finalize metrics for the current cycle with performance analysis"""
        if self.current_cycle:
            # Validate transition
            if next_cycle:
                if not next_cycle.startswith("meta_cycles/") or not next_cycle.endswith(".aiderscript"):
                    raise ValueError(f"Invalid cycle transition target: {next_cycle}")
                
                # Verify cycle exists
                cycle_path = Path(next_cycle)
                if not cycle_path.exists():
                    raise FileNotFoundError(f"Target cycle not found: {next_cycle}")
            self.current_cycle.end_time = time.time()
            self.current_cycle.duration = self.current_cycle.end_time - self.current_cycle.start_time
            self.current_cycle.success = success
            
            # Calculate performance score
            self.current_cycle.performance_score = self._calculate_performance_score()
            
            # Record transition if next cycle is provided
            if next_cycle:
                self.current_cycle.transition_to = next_cycle
                
            self.metrics_history.append(self.current_cycle)
            self._save_metrics()
            self.current_cycle = None
            
    def _calculate_performance_score(self) -> float:
        """Calculate a comprehensive performance score based on multiple metrics
        
        Returns:
            float: Performance score between 0-100
            
        Raises:
            ValueError: If score weights don't sum to 1.0
        """
        if not self.current_cycle:
            return 0.0
            
        # Validate score weights
        total_weight = sum(self.score_weights.values())
        if not math.isclose(total_weight, 1.0, rel_tol=1e-5):
            raise ValueError(f"Score weights must sum to 1.0, got {total_weight}")
            
        # Calculate component scores
        time_score = self._calculate_time_score()
        error_score = self._calculate_error_score()
        resource_score = self._calculate_resource_score()
        task_score = self._calculate_task_score()
        quality_score = self._calculate_quality_score()
        
        # Combine scores with weighted factors
        final_score = (
            (time_score * self.score_weights['time']) +
            (error_score * self.score_weights['error']) +
            (resource_score * self.score_weights['resource']) +
            (task_score * self.score_weights['task']) +
            (quality_score * self.score_weights['quality'])
        )
        
        return max(0, min(100, final_score))  # Ensure score stays between 0-100

    def _calculate_time_score(self) -> float:
        """Calculate score based on time metrics"""
        score = 100.0
        if self.current_cycle.duration > self.performance_thresholds['duration']:
            duration_penalty = (self.current_cycle.duration - self.performance_thresholds['duration']) / 60
            score -= min(30, duration_penalty * 2)  # Max 30 points deduction
        return score

    def _calculate_error_score(self) -> float:
        """Calculate score based on errors and warnings"""
        score = 100.0
        # Deduct points for errors
        score -= min(30, self.current_cycle.error_count * 10)  # 10 points per error, max 30
        # Deduct points for warnings
        if self.current_cycle.warnings:
            score -= min(20, len(self.current_cycle.warnings) * 2)  # 2 points per warning, max 20
        return score

    def _calculate_resource_score(self) -> float:
        """Calculate score based on resource usage"""
        if not self.current_cycle.resource_usage:
            return 100.0
            
        score = 100.0
        for resource, usage in self.current_cycle.resource_usage.items():
            if resource in self.resource_limits:
                if usage > self.resource_limits[resource]:
                    penalty = (usage - self.resource_limits[resource]) / self.resource_limits[resource] * 10
                    score -= min(20, penalty)  # Max 20 points deduction per resource
        return score

    def _calculate_task_score(self) -> float:
        """Calculate score based on task completion"""
        if self.current_cycle.task_count == 0:
            return 100.0
            
        completion_ratio = self.current_cycle.completed_tasks / self.current_cycle.task_count
        return 100.0 * completion_ratio

    def _calculate_quality_score(self) -> float:
        """Calculate score based on quality metrics"""
        if not self.current_cycle.quality_score:
            return 100.0
        return min(100, max(0, self.current_cycle.quality_score))
            
    def record_error(self):
        """Increment error count for current cycle"""
        if self.current_cycle:
            self.current_cycle.error_count += 1
            
    def record_resource_usage(self, resource_name: str, value: float):
        """Track resource usage metrics with validation"""
        if self.current_cycle:
            if resource_name in self.resource_limits:
                if value > self.resource_limits[resource_name]:
                    self.record_warning(f"Resource {resource_name} exceeded limit: {value} > {self.resource_limits[resource_name]}")
            self.current_cycle.resource_usage[resource_name] = value
            
    def record_warning(self, message: str):
        """Record a warning message for the current cycle"""
        if self.current_cycle:
            if self.current_cycle.warnings is None:
                self.current_cycle.warnings = []
            self.current_cycle.warnings.append(message)
            
    def get_cycle_metrics(self, cycle_name: str) -> List[CycleMetrics]:
        """Get historical metrics for a specific cycle"""
        return [m for m in self.metrics_history if m.cycle_name == cycle_name]
    
    def get_all_metrics(self) -> List[CycleMetrics]:
        """Get all historical metrics"""
        return self.metrics_history
    
    def _save_metrics(self):
        """Save metrics to JSON file with validation and backup
        
        Raises:
            IOError: If metrics file cannot be written
        """
        try:
            # Create backup if file exists
            if self.metrics_file.exists():
                backup_file = self.metrics_file.with_suffix('.bak')
                self.metrics_file.rename(backup_file)
                
            # Write new metrics
            metrics_data = [self._validate_metrics(m.__dict__) for m in self.metrics_history]
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
                
        except (IOError, OSError) as e:
            raise IOError(f"Failed to save metrics: {str(e)}")

    def _validate_metrics(self, metrics: dict) -> dict:
        """Validate and clean metrics data before saving"""
        # Ensure required fields are present
        required_fields = ['cycle_name', 'start_time', 'end_time', 'duration']
        for field in required_fields:
            if field not in metrics:
                metrics[field] = 0.0
                
        # Clean up resource usage data
        if 'resource_usage' in metrics and metrics['resource_usage'] is None:
            metrics['resource_usage'] = {}
            
        # Calculate derived metrics if missing
        if 'duration' not in metrics or metrics['duration'] == 0:
            if 'start_time' in metrics and 'end_time' in metrics:
                metrics['duration'] = metrics['end_time'] - metrics['start_time']
                
        return metrics

    def export_metrics(self, format: str = 'json', file_path: str = None) -> str:
        """Export metrics in specified format (json/csv)"""
        if not file_path:
            file_path = f"meta_cycles/metrics_export_{int(time.time())}.{format}"
            
        metrics_data = [m.__dict__ for m in self.metrics_history]
        
        if format == 'json':
            with open(file_path, 'w') as f:
                json.dump(metrics_data, f, indent=2)
        elif format == 'csv':
            import csv
            # Get all possible field names
            fieldnames = set()
            for metric in metrics_data:
                fieldnames.update(metric.keys())
                
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                writer.writerows(metrics_data)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
        return file_path
            
    def _load_config(self):
        """Load configuration from JSON file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.resource_limits = config.get('resource_limits', self.resource_limits)
                    self.performance_thresholds = config.get('performance_thresholds', self.performance_thresholds)
                    self.score_weights = config.get('score_weights', self.score_weights)
            except json.JSONDecodeError:
                self.record_warning("Invalid configuration file format, using defaults")
                
    def load_metrics(self):
        """Load metrics from JSON file with error handling
        
        Raises:
            IOError: If metrics file cannot be read
            json.JSONDecodeError: If metrics file is corrupted
        """
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.metrics_history = [CycleMetrics(**m) for m in data]
            except (IOError, json.JSONDecodeError) as e:
                raise IOError(f"Failed to load metrics: {str(e)}")

# Global metrics collector instance
metrics_collector = MetricsCollector()

# Load existing metrics on startup
metrics_collector.load_metrics()
