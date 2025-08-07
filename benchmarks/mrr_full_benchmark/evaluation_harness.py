#!/usr/bin/env python3
"""
MRR Benchmark Evaluation Harness
Complete evaluation framework for the Multi Random Retrieval benchmark
"""

import json
import time
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import subprocess
import tempfile
import os
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
import traceback

class DebugOutcome(Enum):
    """Possible outcomes of a debugging attempt"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"

@dataclass
class DebugAttempt:
    """Single debugging attempt result"""
    bug_id: str
    outcome: DebugOutcome
    iterations: int
    time_seconds: float
    files_retrieved: List[str]
    files_modified: List[str]
    tests_passed: List[str]
    tests_failed: List[str]
    error_message: Optional[str] = None
    
@dataclass
class EvaluationResult:
    """Complete evaluation result for a model"""
    model_name: str
    scenario_results: Dict[str, List[DebugAttempt]]
    overall_metrics: Dict[str, float]
    category_metrics: Dict[str, Dict[str, float]]
    retrieval_metrics: Dict[str, float]
    timing_metrics: Dict[str, float]

class MRREvaluationHarness:
    """Main evaluation harness for MRR benchmark"""
    
    def __init__(self, dataset_path: str, timeout_seconds: int = 600):
        """
        Initialize evaluation harness
        
        Args:
            dataset_path: Path to MRR dataset JSON
            timeout_seconds: Maximum time per bug (default 10 minutes)
        """
        self.dataset_path = dataset_path
        self.timeout_seconds = timeout_seconds
        self.dataset = self._load_dataset()
        
    def _load_dataset(self) -> Dict[str, Any]:
        """Load MRR dataset from file"""
        with open(self.dataset_path, 'r') as f:
            return json.load(f)
    
    def evaluate_model(self, model_interface, model_name: str, 
                      scenarios: Optional[List[str]] = None,
                      parallel: bool = True) -> EvaluationResult:
        """
        Evaluate a model on the MRR benchmark
        
        Args:
            model_interface: Model interface with debug() method
            model_name: Name of the model
            scenarios: List of scenario IDs to evaluate (None = all)
            parallel: Whether to run scenarios in parallel
            
        Returns:
            Complete evaluation results
        """
        print(f"\nEvaluating {model_name} on MRR Benchmark")
        print("=" * 60)
        
        # Select scenarios to evaluate
        if scenarios is None:
            scenarios_to_eval = self.dataset['scenarios']
        else:
            scenarios_to_eval = [s for s in self.dataset['scenarios'] 
                               if s['scenario_id'] in scenarios]
        
        print(f"Evaluating {len(scenarios_to_eval)} scenarios")
        
        # Run evaluation
        start_time = time.time()
        
        if parallel:
            results = self._evaluate_parallel(model_interface, scenarios_to_eval)
        else:
            results = self._evaluate_sequential(model_interface, scenarios_to_eval)
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        overall_metrics = self._calculate_overall_metrics(results)
        category_metrics = self._calculate_category_metrics(results, scenarios_to_eval)
        retrieval_metrics = self._calculate_retrieval_metrics(results, scenarios_to_eval)
        timing_metrics = self._calculate_timing_metrics(results, total_time)
        
        # Create evaluation result
        evaluation_result = EvaluationResult(
            model_name=model_name,
            scenario_results=results,
            overall_metrics=overall_metrics,
            category_metrics=category_metrics,
            retrieval_metrics=retrieval_metrics,
            timing_metrics=timing_metrics
        )
        
        # Print summary
        self._print_summary(evaluation_result)
        
        return evaluation_result
    
    def _evaluate_sequential(self, model_interface, 
                           scenarios: List[Dict]) -> Dict[str, List[DebugAttempt]]:
        """Evaluate scenarios sequentially"""
        results = {}
        
        for i, scenario in enumerate(scenarios):
            print(f"\n[{i+1}/{len(scenarios)}] Evaluating {scenario['scenario_id']}...")
            scenario_results = self._evaluate_scenario(model_interface, scenario)
            results[scenario['scenario_id']] = scenario_results
            
            # Print progress
            successes = sum(1 for r in scenario_results if r.outcome == DebugOutcome.SUCCESS)
            print(f"  Bugs fixed: {successes}/{len(scenario_results)}")
        
        return results
    
    def _evaluate_parallel(self, model_interface, 
                         scenarios: List[Dict]) -> Dict[str, List[DebugAttempt]]:
        """Evaluate scenarios in parallel"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all scenarios
            future_to_scenario = {
                executor.submit(self._evaluate_scenario, model_interface, scenario): scenario
                for scenario in scenarios
            }
            
            # Process completed scenarios
            for i, future in enumerate(concurrent.futures.as_completed(future_to_scenario)):
                scenario = future_to_scenario[future]
                try:
                    scenario_results = future.result()
                    results[scenario['scenario_id']] = scenario_results
                    
                    # Print progress
                    successes = sum(1 for r in scenario_results 
                                  if r.outcome == DebugOutcome.SUCCESS)
                    print(f"[{i+1}/{len(scenarios)}] {scenario['scenario_id']}: "
                          f"{successes}/{len(scenario_results)} bugs fixed")
                          
                except Exception as e:
                    print(f"Error evaluating {scenario['scenario_id']}: {str(e)}")
                    results[scenario['scenario_id']] = []
        
        return results
    
    def _evaluate_scenario(self, model_interface, scenario: Dict) -> List[DebugAttempt]:
        """Evaluate a single scenario with multiple bugs"""
        scenario_results = []
        
        # Create temporary repository snapshot
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = self._setup_repository(scenario, temp_dir)
            
            # Evaluate each bug
            for bug in scenario['bugs']:
                attempt = self._evaluate_bug(model_interface, bug, scenario, repo_path)
                scenario_results.append(attempt)
        
        return scenario_results
    
    def _evaluate_bug(self, model_interface, bug: Dict, 
                     scenario: Dict, repo_path: str) -> DebugAttempt:
        """Evaluate model performance on a single bug"""
        start_time = time.time()
        
        try:
            # Prepare bug context
            bug_context = {
                'bug_id': bug['bug_id'],
                'description': bug['description'],
                'symptoms': bug['symptoms'],
                'repository_path': repo_path,
                'repository_metadata': scenario['repository_snapshot'],
                'context_hints': scenario['context_scattering']
            }
            
            # Call model interface
            result = model_interface.debug(
                bug_context=bug_context,
                max_iterations=10,
                timeout=self.timeout_seconds
            )
            
            # Validate fix
            validation = self._validate_fix(result, bug, repo_path)
            
            # Determine outcome
            if validation['all_tests_pass']:
                outcome = DebugOutcome.SUCCESS
            elif validation['root_cause_found']:
                outcome = DebugOutcome.PARTIAL
            elif result.get('timeout', False):
                outcome = DebugOutcome.TIMEOUT
            else:
                outcome = DebugOutcome.FAILED
            
            return DebugAttempt(
                bug_id=bug['bug_id'],
                outcome=outcome,
                iterations=result.get('iterations', 0),
                time_seconds=time.time() - start_time,
                files_retrieved=result.get('files_retrieved', []),
                files_modified=result.get('files_modified', []),
                tests_passed=validation['tests_passed'],
                tests_failed=validation['tests_failed'],
                error_message=result.get('error_message')
            )
            
        except Exception as e:
            return DebugAttempt(
                bug_id=bug['bug_id'],
                outcome=DebugOutcome.ERROR,
                iterations=0,
                time_seconds=time.time() - start_time,
                files_retrieved=[],
                files_modified=[],
                tests_passed=[],
                tests_failed=[],
                error_message=str(e)
            )
    
    def _setup_repository(self, scenario: Dict, temp_dir: str) -> str:
        """Setup temporary repository for evaluation"""
        # In real implementation, this would:
        # 1. Clone repository at specific commit
        # 2. Set up test environment
        # 3. Verify initial state
        
        # For now, return mock path
        repo_path = os.path.join(temp_dir, 'repo')
        os.makedirs(repo_path)
        return repo_path
    
    def _validate_fix(self, result: Dict, bug: Dict, repo_path: str) -> Dict[str, Any]:
        """Validate that fix actually resolves the bug"""
        # In real implementation, this would:
        # 1. Apply proposed fix
        # 2. Run test suite
        # 3. Check for regressions
        # 4. Verify bug symptoms are gone
        
        # Mock validation for now
        validation = {
            'all_tests_pass': result.get('success', False),
            'root_cause_found': result.get('root_cause_identified', False),
            'tests_passed': bug.get('test_failures', []) if result.get('success') else [],
            'tests_failed': [] if result.get('success') else bug.get('test_failures', []),
            'no_regressions': True
        }
        
        return validation
    
    def _calculate_overall_metrics(self, results: Dict[str, List[DebugAttempt]]) -> Dict[str, float]:
        """Calculate overall metrics across all scenarios"""
        all_attempts = []
        for scenario_results in results.values():
            all_attempts.extend(scenario_results)
        
        if not all_attempts:
            return {}
        
        total_bugs = len(all_attempts)
        successes = sum(1 for a in all_attempts if a.outcome == DebugOutcome.SUCCESS)
        partials = sum(1 for a in all_attempts if a.outcome == DebugOutcome.PARTIAL)
        
        avg_iterations = np.mean([a.iterations for a in all_attempts if a.iterations > 0])
        avg_time = np.mean([a.time_seconds for a in all_attempts])
        
        return {
            'debug_success_rate': successes / total_bugs * 100,
            'partial_success_rate': partials / total_bugs * 100,
            'total_bugs_evaluated': total_bugs,
            'avg_iterations': avg_iterations,
            'avg_time_seconds': avg_time,
            'timeout_rate': sum(1 for a in all_attempts if a.outcome == DebugOutcome.TIMEOUT) / total_bugs * 100,
            'error_rate': sum(1 for a in all_attempts if a.outcome == DebugOutcome.ERROR) / total_bugs * 100
        }
    
    def _calculate_category_metrics(self, results: Dict[str, List[DebugAttempt]], 
                                  scenarios: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Calculate metrics by bug category"""
        # Build mapping of bug_id to category
        bug_to_category = {}
        for scenario in scenarios:
            for bug in scenario['bugs']:
                bug_to_category[bug['bug_id']] = bug['category']
        
        # Group attempts by category
        category_attempts = {}
        for scenario_results in results.values():
            for attempt in scenario_results:
                category = bug_to_category.get(attempt.bug_id, 'unknown')
                if category not in category_attempts:
                    category_attempts[category] = []
                category_attempts[category].append(attempt)
        
        # Calculate metrics per category
        category_metrics = {}
        for category, attempts in category_attempts.items():
            successes = sum(1 for a in attempts if a.outcome == DebugOutcome.SUCCESS)
            category_metrics[category] = {
                'success_rate': successes / len(attempts) * 100 if attempts else 0,
                'avg_iterations': np.mean([a.iterations for a in attempts if a.iterations > 0]),
                'avg_time': np.mean([a.time_seconds for a in attempts]),
                'total_bugs': len(attempts)
            }
        
        return category_metrics
    
    def _calculate_retrieval_metrics(self, results: Dict[str, List[DebugAttempt]], 
                                   scenarios: List[Dict]) -> Dict[str, float]:
        """Calculate retrieval performance metrics"""
        # Build ground truth mapping
        bug_to_ground_truth = {}
        for scenario in scenarios:
            for bug in scenario['bugs']:
                bug_to_ground_truth[bug['bug_id']] = set(bug['affected_files'])
        
        precisions = []
        recalls = []
        mrrs = []
        
        for scenario_results in results.values():
            for attempt in scenario_results:
                if attempt.files_retrieved:
                    ground_truth = bug_to_ground_truth.get(attempt.bug_id, set())
                    retrieved = set(attempt.files_retrieved[:10])  # P@10
                    
                    if ground_truth:
                        precision = len(retrieved & ground_truth) / len(retrieved) if retrieved else 0
                        recall = len(retrieved & ground_truth) / len(ground_truth)
                        
                        # Calculate MRR
                        for i, file in enumerate(attempt.files_retrieved):
                            if file in ground_truth:
                                mrrs.append(1 / (i + 1))
                                break
                        else:
                            mrrs.append(0)
                        
                        precisions.append(precision)
                        recalls.append(recall)
        
        return {
            'precision_at_10': np.mean(precisions) * 100 if precisions else 0,
            'recall_at_10': np.mean(recalls) * 100 if recalls else 0,
            'mean_reciprocal_rank': np.mean(mrrs) if mrrs else 0,
            'avg_files_retrieved': np.mean([len(a.files_retrieved) for a in all_attempts 
                                           for all_attempts in results.values()])
        }
    
    def _calculate_timing_metrics(self, results: Dict[str, List[DebugAttempt]], 
                                total_time: float) -> Dict[str, float]:
        """Calculate timing and efficiency metrics"""
        all_attempts = []
        for scenario_results in results.values():
            all_attempts.extend(scenario_results)
        
        successful_attempts = [a for a in all_attempts if a.outcome == DebugOutcome.SUCCESS]
        
        return {
            'total_evaluation_time': total_time,
            'avg_time_per_bug': np.mean([a.time_seconds for a in all_attempts]),
            'avg_time_per_success': np.mean([a.time_seconds for a in successful_attempts]) if successful_attempts else 0,
            'bugs_per_minute': len(all_attempts) / (total_time / 60),
            'successes_per_hour': len(successful_attempts) / (total_time / 3600)
        }
    
    def _print_summary(self, result: EvaluationResult):
        """Print evaluation summary"""
        print("\n" + "=" * 60)
        print(f"EVALUATION SUMMARY - {result.model_name}")
        print("=" * 60)
        
        # Overall metrics
        print("\nOverall Performance:")
        print(f"  Debug Success Rate: {result.overall_metrics.get('debug_success_rate', 0):.1f}%")
        print(f"  Partial Success Rate: {result.overall_metrics.get('partial_success_rate', 0):.1f}%")
        print(f"  Average Iterations: {result.overall_metrics.get('avg_iterations', 0):.1f}")
        print(f"  Average Time: {result.overall_metrics.get('avg_time_seconds', 0):.1f}s")
        
        # Category breakdown
        print("\nPerformance by Category:")
        for category in ['syntax_errors', 'logic_bugs', 'concurrency_issues', 
                        'memory_problems', 'api_misuse', 'performance_bugs']:
            if category in result.category_metrics:
                metrics = result.category_metrics[category]
                print(f"  {category}: {metrics['success_rate']:.1f}% "
                      f"({metrics['total_bugs']} bugs)")
        
        # Retrieval metrics
        print("\nRetrieval Performance:")
        print(f"  Precision@10: {result.retrieval_metrics.get('precision_at_10', 0):.1f}%")
        print(f"  Recall@10: {result.retrieval_metrics.get('recall_at_10', 0):.1f}%")
        print(f"  MRR: {result.retrieval_metrics.get('mean_reciprocal_rank', 0):.3f}")
        
        print("\n" + "=" * 60)

def save_evaluation_results(result: EvaluationResult, output_path: str):
    """Save evaluation results to JSON file"""
    
    # Convert to serializable format
    serializable_result = {
        'model_name': result.model_name,
        'timestamp': datetime.now().isoformat(),
        'overall_metrics': result.overall_metrics,
        'category_metrics': result.category_metrics,
        'retrieval_metrics': result.retrieval_metrics,
        'timing_metrics': result.timing_metrics,
        'detailed_results': {}
    }
    
    # Add detailed results
    for scenario_id, attempts in result.scenario_results.items():
        serializable_result['detailed_results'][scenario_id] = [
            {
                'bug_id': a.bug_id,
                'outcome': a.outcome.value,
                'iterations': a.iterations,
                'time_seconds': a.time_seconds,
                'files_retrieved': a.files_retrieved,
                'files_modified': a.files_modified,
                'tests_passed': a.tests_passed,
                'tests_failed': a.tests_failed,
                'error_message': a.error_message
            }
            for a in attempts
        ]
    
    with open(output_path, 'w') as f:
        json.dump(serializable_result, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")

# Example usage
if __name__ == "__main__":
    # Example model interface
    class MockChronosInterface:
        def debug(self, bug_context, max_iterations=10, timeout=600):
            # Simulate Chronos 2025 performance
            import random
            
            success = random.random() < 0.673  # 67.3% success rate
            
            return {
                'success': success,
                'iterations': random.randint(1, 15) if success else random.randint(1, 5),
                'files_retrieved': [f'file_{i}.py' for i in range(random.randint(5, 20))],
                'files_modified': [f'file_{i}.py' for i in range(random.randint(1, 5))],
                'root_cause_identified': success or random.random() < 0.3
            }
    
    # Run evaluation
    harness = MRREvaluationHarness('mrr_mini_20.json')
    model = MockChronosInterface()
    
    result = harness.evaluate_model(model, 'Kodezi Chronos 2025', parallel=False)
    save_evaluation_results(result, 'chronos_2025_evaluation.json')