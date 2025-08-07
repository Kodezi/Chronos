"""
Kodezi Chronos Benchmark Evaluation Metrics

Core metrics for evaluating debugging model performance.
These metrics are used in the Chronos paper to compare model capabilities.
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class DebugOutcome(Enum):
    """Possible outcomes of a debugging attempt"""
    SUCCESS = "success"  # Bug fixed, all tests pass
    PARTIAL = "partial"  # Root cause found but fix incomplete
    FAILED = "failed"    # Unable to fix the bug
    TIMEOUT = "timeout"  # Exceeded time/iteration limit


@dataclass
class DebugAttempt:
    """Single debugging attempt by a model"""
    bug_id: str
    model_name: str
    outcome: DebugOutcome
    iterations: int
    time_seconds: float
    files_examined: List[str]
    files_modified: List[str]
    root_cause_found: bool
    test_results: Dict[str, bool]
    context_retrieved: List[str]
    

class DebugMetrics:
    """Core metrics for debugging evaluation"""
    
    @staticmethod
    def debug_success_rate(attempts: List[DebugAttempt]) -> float:
        """
        Calculate percentage of successfully fixed bugs.
        This is the primary metric reported in the paper.
        """
        if not attempts:
            return 0.0
        
        successes = sum(1 for a in attempts if a.outcome == DebugOutcome.SUCCESS)
        return (successes / len(attempts)) * 100
    
    @staticmethod
    def root_cause_accuracy(attempts: List[DebugAttempt]) -> float:
        """
        Calculate percentage where root cause was correctly identified,
        regardless of whether fix was successful.
        """
        if not attempts:
            return 0.0
        
        root_causes_found = sum(1 for a in attempts if a.root_cause_found)
        return (root_causes_found / len(attempts)) * 100
    
    @staticmethod
    def average_fix_cycles(attempts: List[DebugAttempt]) -> float:
        """
        Calculate average number of iterations needed to fix bugs.
        Only counts successful attempts.
        """
        successful = [a for a in attempts if a.outcome == DebugOutcome.SUCCESS]
        if not successful:
            return float('inf')
        
        return np.mean([a.iterations for a in successful])
    
    @staticmethod
    def fix_cycle_distribution(attempts: List[DebugAttempt]) -> Dict[int, float]:
        """
        Distribution of iteration counts for successful fixes.
        Helps understand debugging efficiency.
        """
        successful = [a for a in attempts if a.outcome == DebugOutcome.SUCCESS]
        if not successful:
            return {}
        
        distribution = {}
        for i in range(1, 11):  # 1-10 iterations
            count = sum(1 for a in successful if a.iterations == i)
            distribution[i] = (count / len(successful)) * 100
        
        # Group 11+ iterations
        over_10 = sum(1 for a in successful if a.iterations > 10)
        if over_10 > 0:
            distribution['11+'] = (over_10 / len(successful)) * 100
        
        return distribution
    
    @staticmethod
    def average_time_to_fix(attempts: List[DebugAttempt]) -> Dict[str, float]:
        """
        Calculate average time metrics.
        Returns overall average and by outcome type.
        """
        if not attempts:
            return {'overall': 0.0}
        
        results = {
            'overall': np.mean([a.time_seconds for a in attempts]),
            'successful': 0.0,
            'failed': 0.0
        }
        
        successful = [a for a in attempts if a.outcome == DebugOutcome.SUCCESS]
        failed = [a for a in attempts if a.outcome == DebugOutcome.FAILED]
        
        if successful:
            results['successful'] = np.mean([a.time_seconds for a in successful])
        if failed:
            results['failed'] = np.mean([a.time_seconds for a in failed])
        
        return results
    
    @staticmethod
    def category_performance(attempts: List[DebugAttempt], 
                           bug_categories: Dict[str, str]) -> Dict[str, Dict[str, float]]:
        """
        Calculate performance metrics broken down by bug category.
        bug_categories maps bug_id to category name.
        """
        category_attempts = {}
        
        # Group attempts by category
        for attempt in attempts:
            category = bug_categories.get(attempt.bug_id, 'unknown')
            if category not in category_attempts:
                category_attempts[category] = []
            category_attempts[category].append(attempt)
        
        # Calculate metrics per category
        results = {}
        for category, cat_attempts in category_attempts.items():
            results[category] = {
                'success_rate': DebugMetrics.debug_success_rate(cat_attempts),
                'avg_iterations': DebugMetrics.average_fix_cycles(cat_attempts),
                'avg_time': np.mean([a.time_seconds for a in cat_attempts]),
                'count': len(cat_attempts)
            }
        
        return results


class RetrievalMetrics:
    """Metrics specific to retrieval performance in debugging"""
    
    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: List[str], k: int = 10) -> float:
        """
        Calculate precision@k for retrieved context.
        Measures what fraction of retrieved items are relevant.
        """
        if not retrieved or k <= 0:
            return 0.0
        
        retrieved_k = retrieved[:k]
        relevant_set = set(relevant)
        
        relevant_retrieved = sum(1 for item in retrieved_k if item in relevant_set)
        return relevant_retrieved / min(len(retrieved_k), k)
    
    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: List[str], k: int = 10) -> float:
        """
        Calculate recall@k for retrieved context.
        Measures what fraction of relevant items were retrieved.
        """
        if not relevant or k <= 0:
            return 0.0
        
        retrieved_k = set(retrieved[:k])
        relevant_set = set(relevant)
        
        relevant_retrieved = len(retrieved_k.intersection(relevant_set))
        return relevant_retrieved / len(relevant_set)
    
    @staticmethod
    def mean_reciprocal_rank(retrieved: List[str], relevant: List[str]) -> float:
        """
        Calculate MRR - average of reciprocal ranks of first relevant item.
        """
        relevant_set = set(relevant)
        
        for i, item in enumerate(retrieved):
            if item in relevant_set:
                return 1.0 / (i + 1)
        
        return 0.0
    
    @staticmethod
    def context_efficiency(retrieved: List[str], relevant: List[str], 
                         used: List[str]) -> float:
        """
        Measures how efficiently the model uses retrieved context.
        Ratio of used relevant items to total retrieved items.
        """
        if not retrieved:
            return 0.0
        
        relevant_set = set(relevant)
        used_set = set(used)
        
        used_relevant = len(used_set.intersection(relevant_set))
        return used_relevant / len(retrieved)


class StatisticalAnalysis:
    """Statistical tests for comparing model performance"""
    
    @staticmethod
    def confidence_interval(values: List[float], confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for a metric"""
        if not values:
            return (0.0, 0.0)
        
        mean = np.mean(values)
        std_err = np.std(values) / np.sqrt(len(values))
        
        # Using t-distribution for small samples
        from scipy import stats
        df = len(values) - 1
        t_val = stats.t.ppf((1 + confidence) / 2, df)
        
        margin = t_val * std_err
        return (mean - margin, mean + margin)
    
    @staticmethod
    def compare_models(model1_results: List[float], 
                      model2_results: List[float]) -> Dict[str, Any]:
        """
        Perform statistical comparison between two models.
        Returns t-statistic, p-value, and effect size.
        """
        from scipy import stats
        
        if not model1_results or not model2_results:
            return {'error': 'Insufficient data'}
        
        # Perform independent t-test
        t_stat, p_value = stats.ttest_ind(model1_results, model2_results)
        
        # Calculate Cohen's d effect size
        pooled_std = np.sqrt((np.std(model1_results)**2 + np.std(model2_results)**2) / 2)
        cohens_d = (np.mean(model1_results) - np.mean(model2_results)) / pooled_std
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'significant': p_value < 0.05,
            'effect_size': 'large' if abs(cohens_d) > 0.8 else 'medium' if abs(cohens_d) > 0.5 else 'small'
        }


def calculate_mrr_metrics(test_results: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate Multi-Random Retrieval benchmark metrics.
    This is the primary evaluation used in the Chronos paper.
    """
    metrics = {
        'precision_at_10': [],
        'recall_at_10': [],
        'fix_accuracy': [],
        'context_efficiency': []
    }
    
    for result in test_results:
        retrieved = result['retrieved_files']
        relevant = result['ground_truth']['relevant_files']
        used = result.get('files_modified', [])
        
        metrics['precision_at_10'].append(
            RetrievalMetrics.precision_at_k(retrieved, relevant, k=10)
        )
        metrics['recall_at_10'].append(
            RetrievalMetrics.recall_at_k(retrieved, relevant, k=10)
        )
        metrics['fix_accuracy'].append(
            1.0 if result['outcome'] == 'success' else 0.0
        )
        metrics['context_efficiency'].append(
            RetrievalMetrics.context_efficiency(retrieved, relevant, used)
        )
    
    # Return averages
    return {
        metric: np.mean(values) * 100  # Convert to percentage
        for metric, values in metrics.items()
    }


def generate_evaluation_report(results: Dict[str, List[DebugAttempt]], 
                             bug_categories: Dict[str, str]) -> Dict[str, Any]:
    """Generate comprehensive evaluation report comparing models"""
    report = {}
    
    for model_name, attempts in results.items():
        model_report = {
            'overall_metrics': {
                'debug_success_rate': DebugMetrics.debug_success_rate(attempts),
                'root_cause_accuracy': DebugMetrics.root_cause_accuracy(attempts),
                'average_fix_cycles': DebugMetrics.average_fix_cycles(attempts),
                'fix_cycle_distribution': DebugMetrics.fix_cycle_distribution(attempts),
                'average_time': DebugMetrics.average_time_to_fix(attempts)
            },
            'category_performance': DebugMetrics.category_performance(attempts, bug_categories),
            'total_attempts': len(attempts)
        }
        report[model_name] = model_report
    
    # Add statistical comparisons if multiple models
    if len(results) > 1:
        report['statistical_comparisons'] = {}
        model_names = list(results.keys())
        
        for i in range(len(model_names)):
            for j in range(i + 1, len(model_names)):
                model1, model2 = model_names[i], model_names[j]
                
                # Extract success rates for comparison
                model1_successes = [
                    1.0 if a.outcome == DebugOutcome.SUCCESS else 0.0 
                    for a in results[model1]
                ]
                model2_successes = [
                    1.0 if a.outcome == DebugOutcome.SUCCESS else 0.0 
                    for a in results[model2]
                ]
                
                comparison_key = f"{model1}_vs_{model2}"
                report['statistical_comparisons'][comparison_key] = \
                    StatisticalAnalysis.compare_models(model1_successes, model2_successes)
    
    return report


# Example usage for testing
if __name__ == "__main__":
    # This would be used with actual evaluation data
    print("Chronos Evaluation Metrics Module")
    print("Use with run_evaluation.py to evaluate debugging models")
    print("\nKey metrics:")
    print("- Debug Success Rate: % of bugs successfully fixed")
    print("- Root Cause Accuracy: % where root cause identified")  
    print("- Average Fix Cycles: Iterations needed to fix")
    print("- Retrieval Precision/Recall: Context finding accuracy")
    print("- Context Efficiency: How well retrieved context is used")