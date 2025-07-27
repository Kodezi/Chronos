"""
Multi Random Retrieval (MRR) Benchmark Evaluation Metrics

This module implements the core evaluation metrics for the MRR benchmark.
Note: The Kodezi Chronos model is proprietary and only available via Kodezi OS (Q1 2026).
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Any
from dataclasses import dataclass


@dataclass
class RetrievalResult:
    """Container for retrieval results"""
    retrieved_files: List[str]
    retrieved_commits: List[str]
    retrieved_tokens: int
    used_tokens: int
    retrieval_time: float


@dataclass
class DebugResult:
    """Container for debugging results"""
    proposed_fix: str
    fix_location: Dict[str, Any]
    test_results: Dict[str, bool]
    iterations: int
    total_time: float


class MRRMetrics:
    """
    Evaluation metrics for the Multi Random Retrieval benchmark.
    
    Measures:
    - Retrieval Precision@k
    - Retrieval Recall@k
    - Fix Accuracy
    - Context Efficiency
    """
    
    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Calculate precision@k for retrieved artifacts.
        
        Args:
            retrieved: List of retrieved artifact IDs
            relevant: Set of relevant artifact IDs
            k: Cutoff value
            
        Returns:
            Precision@k score
        """
        if k <= 0:
            return 0.0
            
        retrieved_k = retrieved[:k]
        if not retrieved_k:
            return 0.0
            
        relevant_retrieved = sum(1 for item in retrieved_k if item in relevant)
        return relevant_retrieved / len(retrieved_k)
    
    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Calculate recall@k for retrieved artifacts.
        
        Args:
            retrieved: List of retrieved artifact IDs
            relevant: Set of relevant artifact IDs
            k: Cutoff value
            
        Returns:
            Recall@k score
        """
        if not relevant:
            return 1.0  # No relevant items to retrieve
            
        retrieved_k = retrieved[:k]
        relevant_retrieved = sum(1 for item in retrieved_k if item in relevant)
        return relevant_retrieved / len(relevant)
    
    @staticmethod
    def f1_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Calculate F1@k score.
        
        Args:
            retrieved: List of retrieved artifact IDs
            relevant: Set of relevant artifact IDs
            k: Cutoff value
            
        Returns:
            F1@k score
        """
        precision = MRRMetrics.precision_at_k(retrieved, relevant, k)
        recall = MRRMetrics.recall_at_k(retrieved, relevant, k)
        
        if precision + recall == 0:
            return 0.0
            
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def fix_accuracy(test_results: Dict[str, bool], must_pass: List[str]) -> bool:
        """
        Determine if a fix is correct based on test results.
        
        Args:
            test_results: Dict mapping test names to pass/fail
            must_pass: List of tests that must pass
            
        Returns:
            True if all required tests pass
        """
        for test in must_pass:
            if test not in test_results or not test_results[test]:
                return False
        return True
    
    @staticmethod
    def context_efficiency(used_tokens: int, retrieved_tokens: int) -> float:
        """
        Calculate context efficiency (ratio of used to retrieved tokens).
        
        Args:
            used_tokens: Number of tokens actually used in the fix
            retrieved_tokens: Total number of tokens retrieved
            
        Returns:
            Context efficiency score [0, 1]
        """
        if retrieved_tokens == 0:
            return 0.0
        return min(used_tokens / retrieved_tokens, 1.0)
    
    @staticmethod
    def mean_reciprocal_rank(retrieved: List[str], relevant: Set[str]) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR) for a single query.
        
        Args:
            retrieved: Ranked list of retrieved items
            relevant: Set of relevant items
            
        Returns:
            Reciprocal rank score
        """
        for i, item in enumerate(retrieved):
            if item in relevant:
                return 1.0 / (i + 1)
        return 0.0
    
    @staticmethod
    def average_precision(retrieved: List[str], relevant: Set[str]) -> float:
        """
        Calculate Average Precision for a single query.
        
        Args:
            retrieved: Ranked list of retrieved items
            relevant: Set of relevant items
            
        Returns:
            Average precision score
        """
        if not relevant:
            return 0.0
            
        precisions = []
        relevant_found = 0
        
        for i, item in enumerate(retrieved):
            if item in relevant:
                relevant_found += 1
                precision_at_i = relevant_found / (i + 1)
                precisions.append(precision_at_i)
        
        if not precisions:
            return 0.0
            
        return sum(precisions) / len(relevant)


class MRRBenchmarkEvaluator:
    """
    Complete evaluator for the MRR benchmark.
    """
    
    def __init__(self):
        self.metrics = MRRMetrics()
        
    def evaluate_single_task(
        self,
        retrieval_result: RetrievalResult,
        debug_result: DebugResult,
        ground_truth: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Evaluate a single debugging task.
        
        Args:
            retrieval_result: Results from retrieval phase
            debug_result: Results from debugging phase
            ground_truth: Ground truth data
            
        Returns:
            Dict of metric scores
        """
        # Combine files and commits for retrieval evaluation
        retrieved = retrieval_result.retrieved_files + retrieval_result.retrieved_commits
        relevant = set(ground_truth['files_involved'] + ground_truth['commits_relevant'])
        
        # Calculate retrieval metrics
        metrics = {
            'precision_at_5': self.metrics.precision_at_k(retrieved, relevant, 5),
            'precision_at_10': self.metrics.precision_at_k(retrieved, relevant, 10),
            'precision_at_20': self.metrics.precision_at_k(retrieved, relevant, 20),
            'recall_at_5': self.metrics.recall_at_k(retrieved, relevant, 5),
            'recall_at_10': self.metrics.recall_at_k(retrieved, relevant, 10),
            'recall_at_20': self.metrics.recall_at_k(retrieved, relevant, 20),
            'f1_at_10': self.metrics.f1_at_k(retrieved, relevant, 10),
            'mrr': self.metrics.mean_reciprocal_rank(retrieved, relevant),
            'average_precision': self.metrics.average_precision(retrieved, relevant),
        }
        
        # Calculate fix accuracy
        metrics['fix_accuracy'] = float(self.metrics.fix_accuracy(
            debug_result.test_results,
            ground_truth['validation_criteria']['must_pass']
        ))
        
        # Calculate efficiency metrics
        metrics['context_efficiency'] = self.metrics.context_efficiency(
            retrieval_result.used_tokens,
            retrieval_result.retrieved_tokens
        )
        
        # Additional metrics
        metrics['iterations'] = debug_result.iterations
        metrics['time_to_fix'] = debug_result.total_time
        metrics['retrieval_time'] = retrieval_result.retrieval_time
        
        return metrics
    
    def evaluate_benchmark(
        self,
        results: List[Tuple[RetrievalResult, DebugResult, Dict[str, Any]]]
    ) -> Dict[str, float]:
        """
        Evaluate complete benchmark results.
        
        Args:
            results: List of (retrieval_result, debug_result, ground_truth) tuples
            
        Returns:
            Aggregated metrics
        """
        all_metrics = []
        
        for retrieval_result, debug_result, ground_truth in results:
            metrics = self.evaluate_single_task(
                retrieval_result, debug_result, ground_truth
            )
            all_metrics.append(metrics)
        
        # Aggregate metrics
        aggregated = {}
        for key in all_metrics[0].keys():
            values = [m[key] for m in all_metrics]
            aggregated[f'{key}_mean'] = np.mean(values)
            aggregated[f'{key}_std'] = np.std(values)
        
        # Add summary statistics
        fix_accuracies = [m['fix_accuracy'] for m in all_metrics]
        aggregated['total_tasks'] = len(results)
        aggregated['successful_fixes'] = sum(fix_accuracies)
        aggregated['success_rate'] = np.mean(fix_accuracies)
        
        return aggregated


def compare_models(baseline_results: Dict[str, float], chronos_results: Dict[str, float]) -> Dict[str, float]:
    """
    Compare Chronos results with baseline models.
    
    Args:
        baseline_results: Baseline model metrics
        chronos_results: Chronos model metrics
        
    Returns:
        Improvement ratios
    """
    improvements = {}
    
    for metric in ['precision_at_10_mean', 'recall_at_10_mean', 'fix_accuracy_mean']:
        if metric in baseline_results and metric in chronos_results:
            baseline = baseline_results[metric]
            chronos = chronos_results[metric]
            
            if baseline > 0:
                improvements[f'{metric}_improvement'] = chronos / baseline
            else:
                improvements[f'{metric}_improvement'] = float('inf')
    
    return improvements


# Example usage (for documentation purposes)
if __name__ == "__main__":
    print("MRR Benchmark Metrics Module")
    print("=" * 50)
    print("This module implements evaluation metrics for the Multi Random Retrieval benchmark.")
    print("\nKey metrics:")
    print("- Retrieval Precision@k")
    print("- Retrieval Recall@k") 
    print("- Fix Accuracy")
    print("- Context Efficiency")
    print("\nNote: Kodezi Chronos achieves:")
    print("- 89.2% Precision@10")
    print("- 84.7% Recall@10")
    print("- 67.3% Fix Accuracy")
    print("- 0.71 Context Efficiency")
    print("\nModel available Q1 2026 via Kodezi OS")