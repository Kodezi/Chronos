#!/usr/bin/env python3
"""
Advanced metrics for MRR benchmark evaluation
Includes specialized metrics for debugging-specific evaluation
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import statistics


@dataclass
class RetrievalMetrics:
    """Metrics for context retrieval evaluation"""
    precision_at_k: Dict[int, float]
    recall_at_k: Dict[int, float]
    mean_reciprocal_rank: float
    average_precision: float
    ndcg_at_k: Dict[int, float]
    context_efficiency: float
    retrieval_coverage: float


@dataclass
class DebuggingMetrics:
    """Metrics specific to debugging performance"""
    fix_success_rate: float
    root_cause_accuracy: float
    fix_precision: float
    fix_recall: float
    semantic_correctness: float
    syntactic_correctness: float
    regression_rate: float
    avg_fix_iterations: float
    first_attempt_success_rate: float


@dataclass
class EfficiencyMetrics:
    """Metrics for computational efficiency"""
    avg_time_seconds: float
    avg_tokens_per_bug: float
    avg_memory_mb: float
    tokens_per_successful_fix: float
    time_per_successful_fix: float
    context_tokens_ratio: float


class MetricsCalculator:
    """Advanced metrics calculator for debugging evaluation"""
    
    @staticmethod
    def calculate_retrieval_metrics(results: List[Dict[str, Any]]) -> RetrievalMetrics:
        """Calculate comprehensive retrieval metrics"""
        k_values = [1, 3, 5, 10, 20, 50]
        
        precision_at_k = {}
        recall_at_k = {}
        ndcg_at_k = {}
        
        for k in k_values:
            precisions = []
            recalls = []
            ndcgs = []
            
            for result in results:
                retrieved = result.get('files_retrieved', [])
                relevant = set(result.get('files_modified', []))
                must_find = set(result.get('must_find_files', []))
                
                if len(retrieved) >= k and relevant:
                    # Precision@K
                    relevant_in_k = sum(1 for f in retrieved[:k] if f in relevant)
                    precisions.append(relevant_in_k / k)
                    
                    # Recall@K
                    recalls.append(relevant_in_k / len(relevant))
                    
                    # NDCG@K
                    ndcg = MetricsCalculator._calculate_ndcg(retrieved[:k], relevant, k)
                    ndcgs.append(ndcg)
            
            precision_at_k[k] = np.mean(precisions) if precisions else 0.0
            recall_at_k[k] = np.mean(recalls) if recalls else 0.0
            ndcg_at_k[k] = np.mean(ndcgs) if ndcgs else 0.0
        
        # Mean Reciprocal Rank
        mrr = MetricsCalculator._calculate_mrr(results)
        
        # Average Precision
        avg_precision = MetricsCalculator._calculate_average_precision(results)
        
        # Context Efficiency
        context_efficiency = MetricsCalculator._calculate_context_efficiency(results)
        
        # Retrieval Coverage
        retrieval_coverage = MetricsCalculator._calculate_retrieval_coverage(results)
        
        return RetrievalMetrics(
            precision_at_k=precision_at_k,
            recall_at_k=recall_at_k,
            mean_reciprocal_rank=mrr,
            average_precision=avg_precision,
            ndcg_at_k=ndcg_at_k,
            context_efficiency=context_efficiency,
            retrieval_coverage=retrieval_coverage
        )
    
    @staticmethod
    def calculate_debugging_metrics(results: List[Dict[str, Any]]) -> DebuggingMetrics:
        """Calculate debugging-specific metrics"""
        total = len(results)
        if total == 0:
            return DebuggingMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Success metrics
        successful_fixes = sum(1 for r in results if r.get('success', False))
        fix_success_rate = successful_fixes / total
        
        # Root cause accuracy
        root_cause_found = sum(1 for r in results if r.get('root_cause_found', False))
        root_cause_accuracy = root_cause_found / total
        
        # Fix quality metrics
        fix_metrics = MetricsCalculator._calculate_fix_quality_metrics(results)
        
        # Regression rate
        regressions = sum(1 for r in results 
                         if r.get('fix_applied', False) and not r.get('no_regression', True))
        fixes_applied = sum(1 for r in results if r.get('fix_applied', False))
        regression_rate = regressions / fixes_applied if fixes_applied > 0 else 0.0
        
        # Iteration metrics
        iterations = [r.get('iterations', 0) for r in results if r.get('iterations', 0) > 0]
        avg_fix_iterations = np.mean(iterations) if iterations else 0.0
        
        # First attempt success
        first_attempt_success = sum(1 for r in results 
                                  if r.get('success', False) and r.get('iterations', 0) == 1)
        first_attempt_success_rate = first_attempt_success / successful_fixes if successful_fixes > 0 else 0.0
        
        return DebuggingMetrics(
            fix_success_rate=fix_success_rate,
            root_cause_accuracy=root_cause_accuracy,
            fix_precision=fix_metrics['precision'],
            fix_recall=fix_metrics['recall'],
            semantic_correctness=fix_metrics['semantic_correctness'],
            syntactic_correctness=fix_metrics['syntactic_correctness'],
            regression_rate=regression_rate,
            avg_fix_iterations=avg_fix_iterations,
            first_attempt_success_rate=first_attempt_success_rate
        )
    
    @staticmethod
    def calculate_efficiency_metrics(results: List[Dict[str, Any]]) -> EfficiencyMetrics:
        """Calculate computational efficiency metrics"""
        # Time metrics
        times = [r.get('time_taken', 0) for r in results if r.get('time_taken', 0) > 0]
        avg_time = np.mean(times) if times else 0.0
        
        # Token metrics
        tokens = [r.get('tokens_used', 0) for r in results if r.get('tokens_used', 0) > 0]
        avg_tokens = np.mean(tokens) if tokens else 0.0
        
        # Memory metrics
        memory = [r.get('memory_used_mb', 0) for r in results if r.get('memory_used_mb', 0) > 0]
        avg_memory = np.mean(memory) if memory else 0.0
        
        # Efficiency for successful fixes
        successful_results = [r for r in results if r.get('success', False)]
        
        if successful_results:
            tokens_per_success = np.mean([r.get('tokens_used', 0) for r in successful_results])
            time_per_success = np.mean([r.get('time_taken', 0) for r in successful_results])
        else:
            tokens_per_success = 0.0
            time_per_success = 0.0
        
        # Context tokens ratio
        context_ratios = []
        for r in results:
            total_tokens = r.get('tokens_used', 0)
            context_tokens = r.get('context_tokens', 0)
            if total_tokens > 0:
                context_ratios.append(context_tokens / total_tokens)
        
        context_tokens_ratio = np.mean(context_ratios) if context_ratios else 0.0
        
        return EfficiencyMetrics(
            avg_time_seconds=avg_time,
            avg_tokens_per_bug=avg_tokens,
            avg_memory_mb=avg_memory,
            tokens_per_successful_fix=tokens_per_success,
            time_per_successful_fix=time_per_success,
            context_tokens_ratio=context_tokens_ratio
        )
    
    @staticmethod
    def calculate_category_metrics(results: List[Dict[str, Any]], 
                                 categories: List[str]) -> Dict[str, Dict[str, float]]:
        """Calculate metrics broken down by bug category"""
        category_metrics = {}
        
        for category in categories:
            category_results = [r for r in results if r.get('category') == category]
            
            if category_results:
                category_metrics[category] = {
                    'count': len(category_results),
                    'success_rate': sum(1 for r in category_results if r.get('success', False)) / len(category_results),
                    'avg_time': np.mean([r.get('time_taken', 0) for r in category_results]),
                    'avg_iterations': np.mean([r.get('iterations', 0) for r in category_results if r.get('iterations', 0) > 0]),
                    'root_cause_accuracy': sum(1 for r in category_results if r.get('root_cause_found', False)) / len(category_results)
                }
            else:
                category_metrics[category] = {
                    'count': 0,
                    'success_rate': 0.0,
                    'avg_time': 0.0,
                    'avg_iterations': 0.0,
                    'root_cause_accuracy': 0.0
                }
        
        return category_metrics
    
    @staticmethod
    def calculate_difficulty_metrics(results: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Calculate metrics broken down by difficulty level"""
        difficulties = ['easy', 'medium', 'hard']
        difficulty_metrics = {}
        
        for difficulty in difficulties:
            diff_results = [r for r in results if r.get('difficulty') == difficulty]
            
            if diff_results:
                difficulty_metrics[difficulty] = {
                    'count': len(diff_results),
                    'success_rate': sum(1 for r in diff_results if r.get('success', False)) / len(diff_results),
                    'avg_time': np.mean([r.get('time_taken', 0) for r in diff_results]),
                    'avg_tokens': np.mean([r.get('tokens_used', 0) for r in diff_results])
                }
            else:
                difficulty_metrics[difficulty] = {
                    'count': 0,
                    'success_rate': 0.0,
                    'avg_time': 0.0,
                    'avg_tokens': 0.0
                }
        
        return difficulty_metrics
    
    @staticmethod
    def calculate_temporal_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate metrics related to temporal aspects of debugging"""
        temporal_metrics = {}
        
        # Success rate vs temporal spread
        temporal_spreads = defaultdict(list)
        for r in results:
            spread_days = r.get('temporal_spread_days', 0)
            spread_bucket = spread_days // 30  # Group by months
            temporal_spreads[spread_bucket].append(r.get('success', False))
        
        temporal_success_by_spread = {}
        for bucket, successes in temporal_spreads.items():
            temporal_success_by_spread[f"{bucket}-{bucket+1}_months"] = sum(successes) / len(successes)
        
        temporal_metrics['success_by_temporal_spread'] = temporal_success_by_spread
        
        # Average refactorings in successful vs failed cases
        successful_refactorings = [r.get('refactoring_count', 0) for r in results if r.get('success', False)]
        failed_refactorings = [r.get('refactoring_count', 0) for r in results if not r.get('success', False)]
        
        temporal_metrics['avg_refactorings_successful'] = np.mean(successful_refactorings) if successful_refactorings else 0.0
        temporal_metrics['avg_refactorings_failed'] = np.mean(failed_refactorings) if failed_refactorings else 0.0
        
        return temporal_metrics
    
    # Helper methods
    @staticmethod
    def _calculate_ndcg(retrieved: List[str], relevant: set, k: int) -> float:
        """Calculate Normalized Discounted Cumulative Gain"""
        dcg = 0.0
        for i, file in enumerate(retrieved[:k]):
            if file in relevant:
                dcg += 1.0 / np.log2(i + 2)  # i+2 because positions start at 1
        
        # Ideal DCG (all relevant files at top)
        idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(relevant), k)))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    @staticmethod
    def _calculate_mrr(results: List[Dict[str, Any]]) -> float:
        """Calculate Mean Reciprocal Rank"""
        reciprocal_ranks = []
        
        for result in results:
            retrieved = result.get('files_retrieved', [])
            relevant = set(result.get('files_modified', []))
            
            if retrieved and relevant:
                for rank, file in enumerate(retrieved, 1):
                    if file in relevant:
                        reciprocal_ranks.append(1.0 / rank)
                        break
                else:
                    reciprocal_ranks.append(0.0)
        
        return np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
    
    @staticmethod
    def _calculate_average_precision(results: List[Dict[str, Any]]) -> float:
        """Calculate Average Precision across all queries"""
        avg_precisions = []
        
        for result in results:
            retrieved = result.get('files_retrieved', [])
            relevant = set(result.get('files_modified', []))
            
            if retrieved and relevant:
                precisions = []
                relevant_count = 0
                
                for i, file in enumerate(retrieved):
                    if file in relevant:
                        relevant_count += 1
                        precisions.append(relevant_count / (i + 1))
                
                if precisions:
                    avg_precisions.append(np.mean(precisions))
                else:
                    avg_precisions.append(0.0)
        
        return np.mean(avg_precisions) if avg_precisions else 0.0
    
    @staticmethod
    def _calculate_context_efficiency(results: List[Dict[str, Any]]) -> float:
        """Calculate how efficiently context is used"""
        efficiencies = []
        
        for result in results:
            retrieved = result.get('files_retrieved', [])
            relevant = set(result.get('files_modified', []))
            
            if retrieved:
                relevant_retrieved = sum(1 for f in retrieved if f in relevant)
                efficiencies.append(relevant_retrieved / len(retrieved))
        
        return np.mean(efficiencies) if efficiencies else 0.0
    
    @staticmethod
    def _calculate_retrieval_coverage(results: List[Dict[str, Any]]) -> float:
        """Calculate how well retrieval covers necessary files"""
        coverages = []
        
        for result in results:
            must_find = set(result.get('must_find_files', []))
            retrieved = set(result.get('files_retrieved', []))
            
            if must_find:
                found = must_find.intersection(retrieved)
                coverages.append(len(found) / len(must_find))
        
        return np.mean(coverages) if coverages else 0.0
    
    @staticmethod
    def _calculate_fix_quality_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate metrics for fix quality"""
        metrics = {
            'precision': 0.0,
            'recall': 0.0,
            'semantic_correctness': 0.0,
            'syntactic_correctness': 0.0
        }
        
        # Calculate based on available data
        fixes_with_ground_truth = [r for r in results 
                                  if r.get('fix_applied') and r.get('ground_truth_fix')]
        
        if fixes_with_ground_truth:
            # These would require more sophisticated analysis in practice
            # For now, use simplified metrics
            correct_fixes = sum(1 for r in fixes_with_ground_truth 
                              if r.get('fix_matches_ground_truth', False))
            
            metrics['precision'] = correct_fixes / len(fixes_with_ground_truth)
            metrics['recall'] = correct_fixes / len(results)
            
            # Syntactic correctness (no syntax errors after fix)
            syntactic_correct = sum(1 for r in results 
                                  if r.get('fix_applied') and r.get('no_syntax_errors', True))
            fixes_applied = sum(1 for r in results if r.get('fix_applied'))
            
            if fixes_applied > 0:
                metrics['syntactic_correctness'] = syntactic_correct / fixes_applied
            
            # Semantic correctness (tests pass)
            semantic_correct = sum(1 for r in results 
                                 if r.get('fix_applied') and r.get('test_passed', False))
            
            if fixes_applied > 0:
                metrics['semantic_correctness'] = semantic_correct / fixes_applied
        
        return metrics


def generate_metrics_report(results: List[Dict[str, Any]], 
                          categories: List[str],
                          output_file: str):
    """Generate comprehensive metrics report"""
    # Calculate all metrics
    retrieval_metrics = MetricsCalculator.calculate_retrieval_metrics(results)
    debugging_metrics = MetricsCalculator.calculate_debugging_metrics(results)
    efficiency_metrics = MetricsCalculator.calculate_efficiency_metrics(results)
    category_metrics = MetricsCalculator.calculate_category_metrics(results, categories)
    difficulty_metrics = MetricsCalculator.calculate_difficulty_metrics(results)
    temporal_metrics = MetricsCalculator.calculate_temporal_metrics(results)
    
    # Generate report
    report = f"""# MRR Benchmark Detailed Metrics Report

## Retrieval Metrics
- Mean Reciprocal Rank: {retrieval_metrics.mean_reciprocal_rank:.4f}
- Average Precision: {retrieval_metrics.average_precision:.4f}
- Context Efficiency: {retrieval_metrics.context_efficiency:.4f}
- Retrieval Coverage: {retrieval_metrics.retrieval_coverage:.4f}

### Precision@K
"""
    
    for k, p in sorted(retrieval_metrics.precision_at_k.items()):
        report += f"- P@{k}: {p:.4f}\n"
    
    report += "\n### Recall@K\n"
    for k, r in sorted(retrieval_metrics.recall_at_k.items()):
        report += f"- R@{k}: {r:.4f}\n"
    
    report += "\n### NDCG@K\n"
    for k, n in sorted(retrieval_metrics.ndcg_at_k.items()):
        report += f"- NDCG@{k}: {n:.4f}\n"
    
    report += f"""
## Debugging Metrics
- Fix Success Rate: {debugging_metrics.fix_success_rate:.2%}
- Root Cause Accuracy: {debugging_metrics.root_cause_accuracy:.2%}
- Fix Precision: {debugging_metrics.fix_precision:.2%}
- Fix Recall: {debugging_metrics.fix_recall:.2%}
- Semantic Correctness: {debugging_metrics.semantic_correctness:.2%}
- Syntactic Correctness: {debugging_metrics.syntactic_correctness:.2%}
- Regression Rate: {debugging_metrics.regression_rate:.2%}
- Average Fix Iterations: {debugging_metrics.avg_fix_iterations:.2f}
- First Attempt Success Rate: {debugging_metrics.first_attempt_success_rate:.2%}

## Efficiency Metrics
- Average Time: {efficiency_metrics.avg_time_seconds:.2f}s
- Average Tokens: {efficiency_metrics.avg_tokens_per_bug:,.0f}
- Average Memory: {efficiency_metrics.avg_memory_mb:.2f} MB
- Tokens per Successful Fix: {efficiency_metrics.tokens_per_successful_fix:,.0f}
- Time per Successful Fix: {efficiency_metrics.time_per_successful_fix:.2f}s
- Context Tokens Ratio: {efficiency_metrics.context_tokens_ratio:.2%}

## Performance by Category
"""
    
    for category, metrics in category_metrics.items():
        report += f"\n### {category}\n"
        report += f"- Count: {metrics['count']}\n"
        report += f"- Success Rate: {metrics['success_rate']:.2%}\n"
        report += f"- Avg Time: {metrics['avg_time']:.2f}s\n"
        report += f"- Avg Iterations: {metrics['avg_iterations']:.2f}\n"
        report += f"- Root Cause Accuracy: {metrics['root_cause_accuracy']:.2%}\n"
    
    report += "\n## Performance by Difficulty\n"
    for difficulty, metrics in difficulty_metrics.items():
        report += f"\n### {difficulty.capitalize()}\n"
        report += f"- Count: {metrics['count']}\n"
        report += f"- Success Rate: {metrics['success_rate']:.2%}\n"
        report += f"- Avg Time: {metrics['avg_time']:.2f}s\n"
        report += f"- Avg Tokens: {metrics['avg_tokens']:,.0f}\n"
    
    report += "\n## Temporal Analysis\n"
    report += "### Success Rate by Temporal Spread\n"
    for spread, rate in temporal_metrics['success_by_temporal_spread'].items():
        report += f"- {spread}: {rate:.2%}\n"
    
    report += f"\n- Avg Refactorings (Successful): {temporal_metrics['avg_refactorings_successful']:.2f}\n"
    report += f"- Avg Refactorings (Failed): {temporal_metrics['avg_refactorings_failed']:.2f}\n"
    
    # Save report
    with open(output_file, 'w') as f:
        f.write(report)
    
    return report