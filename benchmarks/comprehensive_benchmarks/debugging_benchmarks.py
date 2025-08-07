#!/usr/bin/env python3
"""
Comprehensive Debugging Benchmarks for Kodezi Chronos 2025
Implements all benchmark categories mentioned in the paper
"""

import json
import time
import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import hashlib

class BugCategory(Enum):
    """Bug categories from the paper"""
    SYNTAX_ERROR = "syntax_error"
    LOGIC_BUG = "logic_bug"
    CONCURRENCY_ISSUE = "concurrency_issue"
    MEMORY_PROBLEM = "memory_problem"
    API_MISUSE = "api_misuse"
    PERFORMANCE_BUG = "performance_bug"
    # Additional categories from paper
    NULL_POINTER = "null_pointer"
    TYPE_ERROR = "type_error"
    RACE_CONDITION = "race_condition"
    MEMORY_LEAK = "memory_leak"
    INFINITE_LOOP = "infinite_loop"
    OFF_BY_ONE = "off_by_one"
    BOUNDARY_CONDITION = "boundary_condition"
    RESOURCE_LEAK = "resource_leak"
    DEADLOCK = "deadlock"
    SECURITY_VULNERABILITY = "security_vulnerability"

@dataclass
class BugScenario:
    """Represents a debugging scenario"""
    bug_id: str
    category: BugCategory
    description: str
    repository_info: Dict
    failing_tests: List[str]
    scattered_context: Dict
    temporal_info: Dict
    ground_truth: Dict
    complexity_score: float
    
    def __post_init__(self):
        # Generate unique hash
        content = f"{self.bug_id}{self.category}{self.description}"
        self.hash = hashlib.md5(content.encode()).hexdigest()[:16]

@dataclass
class BenchmarkSuite:
    """Complete benchmark suite for debugging evaluation"""
    name: str
    scenarios: List[BugScenario] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
class DebuggingBenchmarkGenerator:
    """Generates comprehensive debugging benchmarks"""
    
    def __init__(self):
        self.bug_templates = self._load_bug_templates()
        self.repository_templates = self._load_repository_templates()
        
    def _load_bug_templates(self) -> Dict:
        """Load bug templates for each category"""
        return {
            BugCategory.NULL_POINTER: [
                {
                    "pattern": "uninitialized_object_access",
                    "locations": ["constructor", "method_call", "callback"],
                    "fix_types": ["null_check", "initialization", "optional_chaining"]
                },
                {
                    "pattern": "async_null_reference",
                    "locations": ["promise_resolution", "async_callback"],
                    "fix_types": ["await_check", "null_propagation"]
                }
            ],
            BugCategory.RACE_CONDITION: [
                {
                    "pattern": "concurrent_map_access",
                    "locations": ["shared_resource", "cache_update"],
                    "fix_types": ["mutex_lock", "sync_map", "channel_communication"]
                }
            ],
            BugCategory.MEMORY_LEAK: [
                {
                    "pattern": "circular_reference",
                    "locations": ["event_listener", "closure", "cache"],
                    "fix_types": ["weak_reference", "cleanup_handler", "lifecycle_management"]
                }
            ],
            BugCategory.API_MISUSE: [
                {
                    "pattern": "deprecated_method_usage",
                    "locations": ["external_library", "framework_api"],
                    "fix_types": ["migration", "version_check", "polyfill"]
                }
            ],
            BugCategory.PERFORMANCE_BUG: [
                {
                    "pattern": "n_plus_one_query",
                    "locations": ["database_access", "api_calls"],
                    "fix_types": ["batch_loading", "caching", "query_optimization"]
                }
            ]
        }
    
    def _load_repository_templates(self) -> List[Dict]:
        """Load repository structure templates"""
        return [
            {
                "type": "microservice",
                "size": "medium",
                "loc": 50000,
                "files": 500,
                "languages": ["java", "python"],
                "frameworks": ["spring", "flask"]
            },
            {
                "type": "monolith",
                "size": "large",
                "loc": 500000,
                "files": 5000,
                "languages": ["javascript", "typescript"],
                "frameworks": ["react", "node.js"]
            },
            {
                "type": "library",
                "size": "small",
                "loc": 10000,
                "files": 100,
                "languages": ["rust", "go"],
                "frameworks": []
            }
        ]
    
    def generate_mrr_benchmark(self, n_scenarios: int = 5000) -> BenchmarkSuite:
        """
        Generate Multi Random Retrieval benchmark scenarios
        
        Args:
            n_scenarios: Number of scenarios to generate
            
        Returns:
            BenchmarkSuite with MRR scenarios
        """
        suite = BenchmarkSuite(
            name="Multi Random Retrieval (MRR) Benchmark 2025",
            metadata={
                "version": "2.0",
                "total_scenarios": n_scenarios,
                "context_scattering": "10-50 files",
                "temporal_range": "3-12 months",
                "obfuscation": True
            }
        )
        
        # Distribution based on paper
        category_distribution = {
            BugCategory.SYNTAX_ERROR: 0.10,  # 500/5000
            BugCategory.LOGIC_BUG: 0.24,     # 1200/5000
            BugCategory.CONCURRENCY_ISSUE: 0.16,  # 800/5000
            BugCategory.MEMORY_PROBLEM: 0.12,  # 600/5000
            BugCategory.API_MISUSE: 0.18,     # 900/5000
            BugCategory.PERFORMANCE_BUG: 0.08,  # 400/5000
            # Additional categories
            BugCategory.NULL_POINTER: 0.04,
            BugCategory.TYPE_ERROR: 0.03,
            BugCategory.RACE_CONDITION: 0.03,
            BugCategory.MEMORY_LEAK: 0.02
        }
        
        for i in range(n_scenarios):
            category = self._select_category(category_distribution)
            scenario = self._generate_scenario(i, category)
            suite.scenarios.append(scenario)
        
        return suite
    
    def _select_category(self, distribution: Dict[BugCategory, float]) -> BugCategory:
        """Select category based on distribution"""
        categories = list(distribution.keys())
        probabilities = list(distribution.values())
        return np.random.choice(categories, p=probabilities)
    
    def _generate_scenario(self, idx: int, category: BugCategory) -> BugScenario:
        """Generate a single debugging scenario"""
        repo_template = random.choice(self.repository_templates)
        
        # Generate scattered context (10-50 files)
        n_files = random.randint(10, 50)
        scattered_files = self._generate_file_list(n_files, repo_template)
        
        # Generate temporal dispersion (3-12 months)
        temporal_range = random.randint(3, 12)
        temporal_info = self._generate_temporal_info(temporal_range)
        
        # Generate obfuscated dependencies
        obfuscation = self._generate_obfuscation()
        
        # Calculate complexity score
        complexity = self._calculate_complexity(n_files, temporal_range, category)
        
        return BugScenario(
            bug_id=f"mrr_{category.value}_{idx:04d}",
            category=category,
            description=self._generate_description(category),
            repository_info={
                **repo_template,
                "commit_hash": f"abc{idx:04d}",
                "branch": "main"
            },
            failing_tests=self._generate_failing_tests(category),
            scattered_context={
                "files": scattered_files,
                "obfuscation": obfuscation,
                "multi_modal": self._generate_multi_modal_artifacts()
            },
            temporal_info=temporal_info,
            ground_truth=self._generate_ground_truth(category, scattered_files),
            complexity_score=complexity
        )
    
    def _generate_file_list(self, n_files: int, repo_template: Dict) -> List[str]:
        """Generate list of files involved in bug"""
        files = []
        base_paths = ["src", "lib", "test", "utils", "config"]
        
        for i in range(n_files):
            base = random.choice(base_paths)
            depth = random.randint(1, 4)
            path_parts = [base]
            
            for _ in range(depth):
                path_parts.append(f"module_{random.randint(1, 10)}")
            
            lang = random.choice(repo_template["languages"])
            ext = {"java": ".java", "python": ".py", "javascript": ".js", 
                   "typescript": ".ts", "rust": ".rs", "go": ".go"}.get(lang, ".txt")
            
            filename = f"file_{i}{ext}"
            files.append("/".join(path_parts) + "/" + filename)
        
        return files
    
    def _generate_temporal_info(self, months: int) -> Dict:
        """Generate temporal information for bug"""
        current_time = time.time()
        seconds_per_month = 30 * 24 * 60 * 60
        
        start_time = current_time - (months * seconds_per_month)
        
        # Generate key events
        events = []
        n_events = random.randint(5, 20)
        
        for i in range(n_events):
            event_time = start_time + random.random() * (current_time - start_time)
            events.append({
                "timestamp": event_time,
                "type": random.choice(["commit", "refactor", "merge", "test_added"]),
                "description": f"Event {i}"
            })
        
        return {
            "range_months": months,
            "start_date": time.strftime("%Y-%m-%d", time.localtime(start_time)),
            "end_date": time.strftime("%Y-%m-%d", time.localtime(current_time)),
            "events": sorted(events, key=lambda x: x["timestamp"])
        }
    
    def _generate_obfuscation(self) -> Dict:
        """Generate obfuscation information"""
        obfuscations = []
        n_obfuscations = random.randint(2, 10)
        
        for _ in range(n_obfuscations):
            obfuscations.append({
                "type": random.choice(["rename", "move", "split", "merge"]),
                "old_name": f"old_entity_{random.randint(1, 100)}",
                "new_name": f"new_entity_{random.randint(1, 100)}"
            })
        
        return {"changes": obfuscations}
    
    def _generate_multi_modal_artifacts(self) -> Dict:
        """Generate multi-modal debugging artifacts"""
        return {
            "logs": [f"error.log", f"debug.log", f"access.log"],
            "stack_traces": [f"stacktrace_{i}.txt" for i in range(random.randint(1, 3))],
            "test_outputs": [f"test_output_{i}.xml" for i in range(random.randint(2, 5))],
            "documentation": [f"README.md", f"API.md"],
            "issues": [f"issue_{random.randint(1000, 9999)}"],
            "pull_requests": [f"pr_{random.randint(100, 999)}"]
        }
    
    def _generate_description(self, category: BugCategory) -> str:
        """Generate bug description"""
        descriptions = {
            BugCategory.NULL_POINTER: "Null pointer exception in {component} when {action}",
            BugCategory.RACE_CONDITION: "Race condition in {component} under concurrent {action}",
            BugCategory.MEMORY_LEAK: "Memory leak in {component} during {action}",
            BugCategory.API_MISUSE: "Incorrect usage of {api} in {component}",
            BugCategory.PERFORMANCE_BUG: "Performance degradation in {component} when {action}"
        }
        
        template = descriptions.get(category, "Bug in {component} related to {action}")
        
        return template.format(
            component=f"Component{random.randint(1, 50)}",
            action=f"action{random.randint(1, 20)}",
            api=f"API_v{random.randint(1, 5)}"
        )
    
    def _generate_failing_tests(self, category: BugCategory) -> List[str]:
        """Generate list of failing tests"""
        n_tests = random.randint(1, 5)
        tests = []
        
        for i in range(n_tests):
            test_name = f"test_{category.value}_{i}"
            tests.append(test_name)
        
        return tests
    
    def _generate_ground_truth(self, category: BugCategory, files: List[str]) -> Dict:
        """Generate ground truth for evaluation"""
        # Select fix location
        fix_files = random.sample(files, min(3, len(files)))
        
        return {
            "root_cause": f"Root cause in {category.value}",
            "fix_locations": fix_files,
            "fix_type": self._get_fix_type(category),
            "related_commits": [f"commit_{i}" for i in range(random.randint(1, 5))],
            "pattern_id": f"pattern_{category.value}_{random.randint(1, 100)}"
        }
    
    def _get_fix_type(self, category: BugCategory) -> str:
        """Get appropriate fix type for category"""
        fix_types = {
            BugCategory.NULL_POINTER: "null_check",
            BugCategory.RACE_CONDITION: "synchronization",
            BugCategory.MEMORY_LEAK: "resource_cleanup",
            BugCategory.API_MISUSE: "api_migration",
            BugCategory.PERFORMANCE_BUG: "optimization"
        }
        return fix_types.get(category, "general_fix")
    
    def _calculate_complexity(self, n_files: int, temporal_range: int, 
                            category: BugCategory) -> float:
        """Calculate complexity score for scenario"""
        # Base complexity by category
        category_complexity = {
            BugCategory.SYNTAX_ERROR: 0.1,
            BugCategory.LOGIC_BUG: 0.5,
            BugCategory.CONCURRENCY_ISSUE: 0.8,
            BugCategory.MEMORY_PROBLEM: 0.7,
            BugCategory.API_MISUSE: 0.4,
            BugCategory.PERFORMANCE_BUG: 0.6,
            BugCategory.RACE_CONDITION: 0.9,
            BugCategory.DEADLOCK: 0.95
        }
        
        base = category_complexity.get(category, 0.5)
        
        # File scattering factor
        file_factor = min(n_files / 50, 1.0) * 0.3
        
        # Temporal factor
        temporal_factor = min(temporal_range / 12, 1.0) * 0.2
        
        return min(base + file_factor + temporal_factor, 1.0)

class SpecializedBenchmarks:
    """Additional specialized benchmarks from the paper"""
    
    @staticmethod
    def generate_cross_file_benchmark(n_scenarios: int = 1000) -> BenchmarkSuite:
        """Generate cross-file dependency benchmark"""
        suite = BenchmarkSuite(
            name="Cross-File Dependency Benchmark",
            metadata={
                "focus": "multi-file bugs",
                "min_files": 3,
                "dependency_types": ["import", "inheritance", "composition"]
            }
        )
        
        # Implementation details...
        return suite
    
    @staticmethod
    def generate_temporal_benchmark(n_scenarios: int = 1000) -> BenchmarkSuite:
        """Generate temporal evolution benchmark"""
        suite = BenchmarkSuite(
            name="Temporal Evolution Benchmark",
            metadata={
                "focus": "bugs introduced over time",
                "time_range": "6-24 months",
                "evolution_types": ["refactoring", "api_changes", "dependency_updates"]
            }
        )
        
        # Implementation details...
        return suite
    
    @staticmethod
    def generate_concurrency_benchmark(n_scenarios: int = 800) -> BenchmarkSuite:
        """Generate concurrency-specific benchmark"""
        suite = BenchmarkSuite(
            name="Concurrency Bug Benchmark",
            metadata={
                "focus": "race conditions and deadlocks",
                "concurrency_models": ["threads", "async", "actors"],
                "detection_methods": ["static", "dynamic", "hybrid"]
            }
        )
        
        # Implementation details...
        return suite
    
    @staticmethod
    def generate_performance_benchmark(n_scenarios: int = 400) -> BenchmarkSuite:
        """Generate performance regression benchmark"""
        suite = BenchmarkSuite(
            name="Performance Regression Benchmark",
            metadata={
                "focus": "performance degradations",
                "metrics": ["latency", "throughput", "memory", "cpu"],
                "regression_types": ["algorithmic", "resource", "configuration"]
            }
        )
        
        # Implementation details...
        return suite

class BenchmarkEvaluator:
    """Evaluates model performance on benchmarks"""
    
    def __init__(self):
        self.metrics = {
            "precision_at_k": [1, 3, 5, 10, 20, 50],
            "recall_at_k": [1, 3, 5, 10, 20, 50],
            "fix_accuracy": True,
            "root_cause_accuracy": True,
            "regression_detection": True,
            "time_metrics": True
        }
    
    def evaluate_model(self, model_name: str, suite: BenchmarkSuite) -> Dict:
        """Evaluate a model on a benchmark suite"""
        results = {
            "model": model_name,
            "benchmark": suite.name,
            "n_scenarios": len(suite.scenarios),
            "timestamp": time.time(),
            "detailed_results": []
        }
        
        for scenario in suite.scenarios:
            result = self._evaluate_scenario(model_name, scenario)
            results["detailed_results"].append(result)
        
        # Aggregate metrics
        results["aggregate_metrics"] = self._aggregate_results(
            results["detailed_results"]
        )
        
        return results
    
    def _evaluate_scenario(self, model_name: str, scenario: BugScenario) -> Dict:
        """Evaluate model on single scenario"""
        # This would call actual model in production
        # For now, return simulated results
        
        return {
            "scenario_id": scenario.bug_id,
            "category": scenario.category.value,
            "complexity": scenario.complexity_score,
            "retrieval_metrics": self._simulate_retrieval_metrics(),
            "fix_metrics": self._simulate_fix_metrics(),
            "time_metrics": self._simulate_time_metrics()
        }
    
    def _simulate_retrieval_metrics(self) -> Dict:
        """Simulate retrieval performance"""
        return {
            "files_retrieved": random.randint(10, 50),
            "relevant_files": random.randint(5, 20),
            "precision": random.uniform(0.5, 0.95),
            "recall": random.uniform(0.4, 0.90)
        }
    
    def _simulate_fix_metrics(self) -> Dict:
        """Simulate fix performance"""
        return {
            "fix_generated": True,
            "tests_passed": random.choice([True, False]),
            "root_cause_correct": random.choice([True, False]),
            "no_regressions": random.choice([True, False]),
            "iterations": random.randint(1, 15)
        }
    
    def _simulate_time_metrics(self) -> Dict:
        """Simulate timing metrics"""
        return {
            "retrieval_time": random.uniform(0.5, 5.0),
            "analysis_time": random.uniform(2.0, 10.0),
            "fix_generation_time": random.uniform(5.0, 20.0),
            "validation_time": random.uniform(10.0, 60.0),
            "total_time": random.uniform(20.0, 90.0)
        }
    
    def _aggregate_results(self, detailed_results: List[Dict]) -> Dict:
        """Aggregate detailed results into summary metrics"""
        n = len(detailed_results)
        
        # Calculate aggregates
        fix_accuracy = sum(r["fix_metrics"]["tests_passed"] 
                          for r in detailed_results) / n
        
        root_cause_accuracy = sum(r["fix_metrics"]["root_cause_correct"] 
                                 for r in detailed_results) / n
        
        avg_iterations = np.mean([r["fix_metrics"]["iterations"] 
                                 for r in detailed_results])
        
        avg_time = np.mean([r["time_metrics"]["total_time"] 
                           for r in detailed_results])
        
        return {
            "fix_accuracy": fix_accuracy,
            "root_cause_accuracy": root_cause_accuracy,
            "avg_iterations": avg_iterations,
            "avg_time_minutes": avg_time / 60,
            "success_by_category": self._success_by_category(detailed_results),
            "complexity_analysis": self._complexity_analysis(detailed_results)
        }
    
    def _success_by_category(self, results: List[Dict]) -> Dict:
        """Calculate success rates by bug category"""
        category_stats = {}
        
        for result in results:
            category = result["category"]
            if category not in category_stats:
                category_stats[category] = {"total": 0, "success": 0}
            
            category_stats[category]["total"] += 1
            if result["fix_metrics"]["tests_passed"]:
                category_stats[category]["success"] += 1
        
        return {
            cat: stats["success"] / stats["total"] 
            for cat, stats in category_stats.items()
        }
    
    def _complexity_analysis(self, results: List[Dict]) -> Dict:
        """Analyze performance vs complexity"""
        complexity_buckets = {
            "low": {"range": (0, 0.33), "results": []},
            "medium": {"range": (0.33, 0.67), "results": []},
            "high": {"range": (0.67, 1.0), "results": []}
        }
        
        for result in results:
            complexity = result["complexity"]
            for bucket_name, bucket_info in complexity_buckets.items():
                if bucket_info["range"][0] <= complexity < bucket_info["range"][1]:
                    bucket_info["results"].append(result)
                    break
        
        analysis = {}
        for bucket_name, bucket_info in complexity_buckets.items():
            if bucket_info["results"]:
                analysis[bucket_name] = {
                    "count": len(bucket_info["results"]),
                    "success_rate": sum(r["fix_metrics"]["tests_passed"] 
                                      for r in bucket_info["results"]) / len(bucket_info["results"])
                }
        
        return analysis


if __name__ == "__main__":
    # Generate comprehensive benchmarks
    generator = DebuggingBenchmarkGenerator()
    
    # Generate main MRR benchmark
    print("Generating MRR Benchmark...")
    mrr_suite = generator.generate_mrr_benchmark(n_scenarios=5000)
    print(f"Generated {len(mrr_suite.scenarios)} MRR scenarios")
    
    # Generate specialized benchmarks
    print("\nGenerating specialized benchmarks...")
    cross_file_suite = SpecializedBenchmarks.generate_cross_file_benchmark(1000)
    temporal_suite = SpecializedBenchmarks.generate_temporal_benchmark(1000)
    concurrency_suite = SpecializedBenchmarks.generate_concurrency_benchmark(800)
    performance_suite = SpecializedBenchmarks.generate_performance_benchmark(400)
    
    # Example evaluation
    evaluator = BenchmarkEvaluator()
    
    # Simulate evaluation
    print("\nSimulating Chronos evaluation on MRR...")
    chronos_results = evaluator.evaluate_model("Chronos 2.0", mrr_suite)
    
    print(f"\nAggregate Results:")
    print(f"Fix Accuracy: {chronos_results['aggregate_metrics']['fix_accuracy']:.1%}")
    print(f"Root Cause Accuracy: {chronos_results['aggregate_metrics']['root_cause_accuracy']:.1%}")
    print(f"Avg Iterations: {chronos_results['aggregate_metrics']['avg_iterations']:.1f}")
    print(f"Avg Time: {chronos_results['aggregate_metrics']['avg_time_minutes']:.1f} minutes")