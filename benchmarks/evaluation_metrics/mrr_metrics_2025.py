#!/usr/bin/env python3
"""
Multi Random Retrieval (MRR) Metrics for Kodezi Chronos 2025
Implements comprehensive evaluation metrics for debugging-specific retrieval
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json
from scipy import stats

@dataclass
class MRRResult:
    """Results from Multi Random Retrieval evaluation"""
    precision_at_k: Dict[int, float]
    recall_at_k: Dict[int, float]
    fix_accuracy: float
    context_efficiency: float
    cross_file_hit_rate: float
    debug_cycles: int
    time_to_fix: float
    regression_avoided: float
    confidence_interval: float

class MRRMetrics:
    """
    Multi Random Retrieval metrics for debugging evaluation
    Implements the 2025 MRR benchmark methodology
    """
    
    def __init__(self, k_values: List[int] = [1, 2, 3, 5, 10, 20, 50]):
        self.k_values = k_values
        self.confidence_level = 0.95  # 95% CI
        
    def calculate_precision_at_k(self, 
                                retrieved: List[str], 
                                relevant: List[str], 
                                k: int) -> float:
        """
        Calculate precision@k for retrieval evaluation
        
        Args:
            retrieved: List of retrieved items in order
            relevant: List of relevant items
            k: Top-k cutoff
            
        Returns:
            Precision@k score
        """
        if k == 0:
            return 0.0
            
        retrieved_k = retrieved[:k]
        relevant_in_k = sum(1 for item in retrieved_k if item in relevant)
        
        return relevant_in_k / k
    
    def calculate_recall_at_k(self, 
                             retrieved: List[str], 
                             relevant: List[str], 
                             k: int) -> float:
        """
        Calculate recall@k for retrieval evaluation
        
        Args:
            retrieved: List of retrieved items in order
            relevant: List of relevant items  
            k: Top-k cutoff
            
        Returns:
            Recall@k score
        """
        if len(relevant) == 0:
            return 0.0
            
        retrieved_k = retrieved[:k]
        relevant_in_k = sum(1 for item in retrieved_k if item in relevant)
        
        return relevant_in_k / len(relevant)
    
    def calculate_context_efficiency(self,
                                   used_tokens: int,
                                   retrieved_tokens: int) -> float:
        """
        Calculate context efficiency (ratio of used vs retrieved tokens)
        
        Args:
            used_tokens: Number of tokens actually used in the fix
            retrieved_tokens: Total number of tokens retrieved
            
        Returns:
            Efficiency score (0-1)
        """
        if retrieved_tokens == 0:
            return 0.0
            
        return min(used_tokens / retrieved_tokens, 1.0)
    
    def calculate_mrr_score(self,
                           queries: List[Dict],
                           retrievals: List[Dict]) -> float:
        """
        Calculate Mean Reciprocal Rank for debugging queries
        
        Args:
            queries: List of debugging queries
            retrievals: List of retrieval results
            
        Returns:
            MRR score
        """
        reciprocal_ranks = []
        
        for query, retrieval in zip(queries, retrievals):
            relevant = query['relevant_files']
            retrieved = retrieval['retrieved_files']
            
            # Find rank of first relevant item
            for rank, item in enumerate(retrieved, 1):
                if item in relevant:
                    reciprocal_ranks.append(1.0 / rank)
                    break
            else:
                reciprocal_ranks.append(0.0)
        
        return np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
    
    def calculate_cross_file_hit_rate(self,
                                     bug_dependencies: List[List[str]],
                                     retrieved_files: List[List[str]]) -> float:
        """
        Calculate hit rate for cross-file dependencies
        
        Args:
            bug_dependencies: List of file dependencies for each bug
            retrieved_files: List of retrieved files for each bug
            
        Returns:
            Cross-file hit rate (0-1)
        """
        hits = 0
        total = 0
        
        for deps, retrieved in zip(bug_dependencies, retrieved_files):
            if len(deps) > 1:  # Cross-file bug
                total += 1
                # Check if all dependencies were retrieved
                if all(dep in retrieved for dep in deps):
                    hits += 1
        
        return hits / total if total > 0 else 0.0
    
    def calculate_confidence_interval(self,
                                    successes: int,
                                    total: int) -> float:
        """
        Calculate Wilson score confidence interval for success rate
        
        Args:
            successes: Number of successful fixes
            total: Total number of attempts
            
        Returns:
            Margin of error for 95% CI
        """
        if total == 0:
            return 0.0
            
        p = successes / total
        z = stats.norm.ppf((1 + self.confidence_level) / 2)
        
        denominator = 1 + z**2 / total
        center = (p + z**2 / (2 * total)) / denominator
        margin = z * np.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
        
        return margin
    
    def calculate_agr_complexity(self,
                               traversal_paths: List[List[int]]) -> Dict:
        """
        Verify O(k log d) complexity for AGR traversal
        
        Args:
            traversal_paths: List of k-hop counts for each query
            
        Returns:
            Complexity analysis results
        """
        k_values = []
        node_counts = []
        
        for path in traversal_paths:
            for k, nodes in enumerate(path, 1):
                k_values.append(k)
                node_counts.append(nodes)
        
        # Fit to k log d model
        k_array = np.array(k_values)
        counts_array = np.array(node_counts)
        
        # Approximate average degree
        d_estimate = np.mean(counts_array[k_array == 1])
        
        # Expected counts under O(k log d)
        expected = k_array * np.log(d_estimate)
        
        # Calculate R-squared
        ss_res = np.sum((counts_array - expected) ** 2)
        ss_tot = np.sum((counts_array - np.mean(counts_array)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'complexity_verified': r_squared > 0.8,
            'r_squared': r_squared,
            'average_degree': d_estimate
        }
    
    def evaluate_debugging_scenario(self,
                                  scenario: Dict,
                                  model_output: Dict) -> MRRResult:
        """
        Evaluate a single debugging scenario
        
        Args:
            scenario: Debugging scenario with ground truth
            model_output: Model's retrieval and fix attempt
            
        Returns:
            MRRResult with all metrics
        """
        # Calculate precision/recall at different k values
        precision_at_k = {}
        recall_at_k = {}
        
        for k in self.k_values:
            precision_at_k[k] = self.calculate_precision_at_k(
                model_output['retrieved_files'],
                scenario['relevant_files'],
                k
            )
            recall_at_k[k] = self.calculate_recall_at_k(
                model_output['retrieved_files'],
                scenario['relevant_files'],
                k
            )
        
        # Calculate other metrics
        context_efficiency = self.calculate_context_efficiency(
            model_output.get('used_tokens', 0),
            model_output.get('retrieved_tokens', 1)
        )
        
        fix_accuracy = float(model_output.get('tests_passed', False))
        
        debug_cycles = model_output.get('iterations', 1)
        time_to_fix = model_output.get('time_minutes', 0.0)
        
        regression_avoided = float(not model_output.get('introduced_regression', False))
        
        # Cross-file hit rate (simplified for single scenario)
        cross_file_hit = 1.0 if len(scenario['relevant_files']) > 1 and \
                        all(f in model_output['retrieved_files'] for f in scenario['relevant_files']) \
                        else 0.0
        
        return MRRResult(
            precision_at_k=precision_at_k,
            recall_at_k=recall_at_k,
            fix_accuracy=fix_accuracy,
            context_efficiency=context_efficiency,
            cross_file_hit_rate=cross_file_hit,
            debug_cycles=debug_cycles,
            time_to_fix=time_to_fix,
            regression_avoided=regression_avoided,
            confidence_interval=0.0  # Calculated over multiple scenarios
        )
    
    def aggregate_results(self, results: List[MRRResult]) -> Dict:
        """
        Aggregate results from multiple debugging scenarios
        
        Args:
            results: List of MRRResult objects
            
        Returns:
            Aggregated metrics with confidence intervals
        """
        n = len(results)
        if n == 0:
            return {}
        
        # Aggregate precision/recall
        avg_precision = {}
        avg_recall = {}
        
        for k in self.k_values:
            precisions = [r.precision_at_k[k] for r in results]
            recalls = [r.recall_at_k[k] for r in results]
            
            avg_precision[k] = {
                'mean': np.mean(precisions),
                'std': np.std(precisions),
                'ci': stats.sem(precisions) * stats.t.ppf((1 + self.confidence_level) / 2, n - 1)
            }
            
            avg_recall[k] = {
                'mean': np.mean(recalls),
                'std': np.std(recalls),
                'ci': stats.sem(recalls) * stats.t.ppf((1 + self.confidence_level) / 2, n - 1)
            }
        
        # Calculate fix accuracy with CI
        fix_successes = sum(r.fix_accuracy for r in results)
        fix_accuracy_ci = self.calculate_confidence_interval(fix_successes, n)
        
        return {
            'n_scenarios': n,
            'precision_at_k': avg_precision,
            'recall_at_k': avg_recall,
            'fix_accuracy': {
                'mean': fix_successes / n,
                'ci': fix_accuracy_ci
            },
            'context_efficiency': {
                'mean': np.mean([r.context_efficiency for r in results]),
                'std': np.std([r.context_efficiency for r in results])
            },
            'cross_file_hit_rate': {
                'mean': np.mean([r.cross_file_hit_rate for r in results])
            },
            'avg_debug_cycles': {
                'mean': np.mean([r.debug_cycles for r in results]),
                'std': np.std([r.debug_cycles for r in results])
            },
            'avg_time_to_fix': {
                'mean': np.mean([r.time_to_fix for r in results]),
                'std': np.std([r.time_to_fix for r in results])
            },
            'regression_avoidance': {
                'mean': np.mean([r.regression_avoided for r in results])
            }
        }

def compare_models_mrr(model_results: Dict[str, List[MRRResult]]) -> Dict:
    """
    Compare multiple models on MRR benchmark with statistical significance
    
    Args:
        model_results: Dictionary mapping model names to lists of results
        
    Returns:
        Comparison metrics with Cohen's d effect sizes
    """
    metrics = MRRMetrics()
    aggregated = {}
    
    # Aggregate results for each model
    for model_name, results in model_results.items():
        aggregated[model_name] = metrics.aggregate_results(results)
    
    # Calculate Cohen's d for Chronos vs others
    if 'Chronos' in model_results:
        chronos_fixes = [r.fix_accuracy for r in model_results['Chronos']]
        
        for model_name, results in model_results.items():
            if model_name != 'Chronos':
                other_fixes = [r.fix_accuracy for r in results]
                
                # Cohen's d calculation
                n1, n2 = len(chronos_fixes), len(other_fixes)
                var1 = np.var(chronos_fixes, ddof=1)
                var2 = np.var(other_fixes, ddof=1)
                
                pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
                
                if pooled_sd > 0:
                    cohens_d = abs(np.mean(chronos_fixes) - np.mean(other_fixes)) / pooled_sd
                    aggregated[model_name]['cohens_d_vs_chronos'] = cohens_d
    
    return aggregated

if __name__ == "__main__":
    # Example usage
    metrics = MRRMetrics()
    
    # Sample scenario
    scenario = {
        'bug_id': 'test-001',
        'relevant_files': ['auth.py', 'utils.py', 'config.yml', 'test_auth.py'],
        'scattered_files': list(range(50))  # 50 files in repo
    }
    
    # Sample model output
    model_output = {
        'retrieved_files': ['auth.py', 'main.py', 'utils.py', 'config.yml', 
                          'test_auth.py', 'db.py', 'cache.py'],
        'retrieved_tokens': 15000,
        'used_tokens': 3500,
        'tests_passed': True,
        'iterations': 7,
        'time_minutes': 42.3,
        'introduced_regression': False
    }
    
    result = metrics.evaluate_debugging_scenario(scenario, model_output)
    
    print(f"Fix Accuracy: {result.fix_accuracy}")
    print(f"Context Efficiency: {result.context_efficiency:.2%}")
    print(f"Precision@3: {result.precision_at_k[3]:.2%}")
    print(f"Recall@3: {result.recall_at_k[3]:.2%}")