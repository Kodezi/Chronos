"""
Multi-Random Retrieval (MRR) Benchmark Specific Metrics

Specialized metrics for evaluating performance on the MRR benchmark,
which tests debugging capabilities with scattered context.
"""

import numpy as np
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class MRRTestCase:
    """Single MRR test case with scattered context"""
    bug_id: str
    scattered_files: List[str]  # All files containing relevant context
    critical_files: List[str]   # Files that must be found for successful fix
    time_span_days: int         # How far back in history the bug spans
    refactoring_count: int      # Number of refactorings since bug introduced
    cross_file_dependencies: int # Number of files that must be understood together


@dataclass 
class MRRAttempt:
    """Model's attempt at solving an MRR test case"""
    bug_id: str
    model_name: str
    retrieved_files: List[str]
    examined_files: List[str]
    modified_files: List[str]
    retrieval_order: List[Tuple[str, int]]  # (file, iteration_number)
    commits_examined: List[str]
    time_range_examined_days: int
    success: bool
    iterations: int
    

class MRRMetrics:
    """Metrics specific to Multi-Random Retrieval benchmark"""
    
    @staticmethod
    def scattered_context_recall(attempt: MRRAttempt, test_case: MRRTestCase) -> float:
        """
        Measures how well the model found scattered context.
        Different from standard recall - weighs critical files higher.
        """
        retrieved_set = set(attempt.retrieved_files)
        
        # Critical files are worth 2x
        critical_found = sum(1 for f in test_case.critical_files if f in retrieved_set)
        other_relevant = test_case.scattered_files
        other_found = sum(1 for f in other_relevant 
                         if f in retrieved_set and f not in test_case.critical_files)
        
        total_weight = len(test_case.critical_files) * 2 + len(other_relevant)
        if total_weight == 0:
            return 0.0
            
        found_weight = critical_found * 2 + other_found
        return found_weight / total_weight
    
    @staticmethod
    def temporal_coverage(attempt: MRRAttempt, test_case: MRRTestCase) -> float:
        """
        Measures how well the model covered the temporal span of the bug.
        Important for bugs that span months of development.
        """
        if test_case.time_span_days == 0:
            return 1.0
            
        coverage_ratio = attempt.time_range_examined_days / test_case.time_span_days
        return min(coverage_ratio, 1.0)  # Cap at 100%
    
    @staticmethod
    def cross_file_comprehension(attempt: MRRAttempt, test_case: MRRTestCase) -> float:
        """
        Measures if model understood cross-file dependencies.
        Checks if related files were examined close together.
        """
        if test_case.cross_file_dependencies <= 1:
            return 1.0
            
        # Group files by when they were retrieved
        retrieval_groups = {}
        for file, iteration in attempt.retrieval_order:
            if iteration not in retrieval_groups:
                retrieval_groups[iteration] = []
            retrieval_groups[iteration].append(file)
        
        # Check if dependent files were retrieved in same or adjacent iterations
        dependent_files = set(test_case.critical_files)
        comprehension_score = 0.0
        
        for iteration, files in retrieval_groups.items():
            files_set = set(files)
            
            # Check this iteration and adjacent ones
            for adj in [iteration - 1, iteration, iteration + 1]:
                if adj in retrieval_groups:
                    files_set.update(retrieval_groups[adj])
            
            # How many dependent files are grouped together?
            found_together = len(files_set.intersection(dependent_files))
            if found_together > 1:
                comprehension_score += found_together / len(dependent_files)
        
        return min(comprehension_score, 1.0)
    
    @staticmethod
    def refactoring_resilience(attempt: MRRAttempt, test_case: MRRTestCase) -> float:
        """
        Measures model's ability to handle refactored code.
        Higher score if model still finds relevant context despite refactoring.
        """
        if test_case.refactoring_count == 0:
            return 1.0
            
        # Base score on successful retrieval despite refactoring
        base_score = MRRMetrics.scattered_context_recall(attempt, test_case)
        
        # Penalty based on refactoring count (diminishing impact)
        refactoring_penalty = 1.0 / (1.0 + np.log1p(test_case.refactoring_count))
        
        return base_score * refactoring_penalty
    
    @staticmethod
    def retrieval_efficiency(attempt: MRRAttempt, test_case: MRRTestCase) -> float:
        """
        Measures how efficiently the model found necessary files.
        Ratio of relevant files to total files examined.
        """
        if not attempt.examined_files:
            return 0.0
            
        relevant_files = set(test_case.scattered_files)
        examined_relevant = len(set(attempt.examined_files).intersection(relevant_files))
        
        return examined_relevant / len(attempt.examined_files)
    
    @staticmethod
    def iterative_improvement(attempts: List[MRRAttempt]) -> Dict[int, float]:
        """
        Analyzes how retrieval improves over iterations.
        Shows learning/adaptation capability.
        """
        max_iterations = max(a.iterations for a in attempts)
        improvement_by_iteration = {}
        
        for i in range(1, max_iterations + 1):
            # Get attempts that reached this iteration
            attempts_at_i = [a for a in attempts if a.iterations >= i]
            if not attempts_at_i:
                continue
                
            # Calculate success rate at this iteration
            successes_at_i = sum(1 for a in attempts_at_i 
                               if a.success and a.iterations == i)
            improvement_by_iteration[i] = successes_at_i / len(attempts_at_i)
        
        return improvement_by_iteration


class MRRBenchmarkEvaluator:
    """Complete evaluator for MRR benchmark"""
    
    def __init__(self, test_cases: List[MRRTestCase]):
        self.test_cases = {tc.bug_id: tc for tc in test_cases}
        
    def evaluate_model(self, attempts: List[MRRAttempt]) -> Dict[str, any]:
        """Comprehensive evaluation of model on MRR benchmark"""
        
        results = {
            'overall_metrics': {},
            'detailed_metrics': {},
            'category_breakdown': {},
            'difficulty_analysis': {}
        }
        
        # Overall success rate
        results['overall_metrics']['success_rate'] = \
            sum(1 for a in attempts if a.success) / len(attempts) * 100
        
        # Detailed MRR metrics
        recall_scores = []
        temporal_scores = []
        cross_file_scores = []
        refactoring_scores = []
        efficiency_scores = []
        
        for attempt in attempts:
            test_case = self.test_cases[attempt.bug_id]
            
            recall_scores.append(
                MRRMetrics.scattered_context_recall(attempt, test_case)
            )
            temporal_scores.append(
                MRRMetrics.temporal_coverage(attempt, test_case)
            )
            cross_file_scores.append(
                MRRMetrics.cross_file_comprehension(attempt, test_case)
            )
            refactoring_scores.append(
                MRRMetrics.refactoring_resilience(attempt, test_case)
            )
            efficiency_scores.append(
                MRRMetrics.retrieval_efficiency(attempt, test_case)
            )
        
        results['detailed_metrics'] = {
            'scattered_context_recall': np.mean(recall_scores) * 100,
            'temporal_coverage': np.mean(temporal_scores) * 100,
            'cross_file_comprehension': np.mean(cross_file_scores) * 100,
            'refactoring_resilience': np.mean(refactoring_scores) * 100,
            'retrieval_efficiency': np.mean(efficiency_scores) * 100
        }
        
        # Iterative improvement analysis
        results['iterative_improvement'] = MRRMetrics.iterative_improvement(attempts)
        
        # Break down by difficulty factors
        results['difficulty_analysis'] = self._analyze_by_difficulty(attempts)
        
        return results
    
    def _analyze_by_difficulty(self, attempts: List[MRRAttempt]) -> Dict[str, any]:
        """Analyze performance based on test case difficulty factors"""
        
        analysis = {
            'by_time_span': {},
            'by_file_count': {},
            'by_refactoring': {},
            'by_dependencies': {}
        }
        
        # Group by time span
        time_buckets = [(0, 30), (30, 90), (90, 180), (180, float('inf'))]
        for min_days, max_days in time_buckets:
            bucket_attempts = [
                a for a in attempts 
                if min_days <= self.test_cases[a.bug_id].time_span_days < max_days
            ]
            if bucket_attempts:
                bucket_name = f"{min_days}-{max_days} days" if max_days != float('inf') else f"{min_days}+ days"
                analysis['by_time_span'][bucket_name] = {
                    'success_rate': sum(1 for a in bucket_attempts if a.success) / len(bucket_attempts) * 100,
                    'count': len(bucket_attempts)
                }
        
        # Group by file count
        file_buckets = [(0, 5), (5, 10), (10, 20), (20, float('inf'))]
        for min_files, max_files in file_buckets:
            bucket_attempts = [
                a for a in attempts
                if min_files <= len(self.test_cases[a.bug_id].scattered_files) < max_files
            ]
            if bucket_attempts:
                bucket_name = f"{min_files}-{max_files} files" if max_files != float('inf') else f"{min_files}+ files"
                analysis['by_file_count'][bucket_name] = {
                    'success_rate': sum(1 for a in bucket_attempts if a.success) / len(bucket_attempts) * 100,
                    'count': len(bucket_attempts)
                }
        
        return analysis
    
    def compare_models(self, results_dict: Dict[str, List[MRRAttempt]]) -> Dict[str, any]:
        """Compare multiple models on MRR benchmark"""
        
        comparison = {
            'model_rankings': {},
            'detailed_comparison': {},
            'statistical_significance': {}
        }
        
        # Evaluate each model
        model_results = {}
        for model_name, attempts in results_dict.items():
            model_results[model_name] = self.evaluate_model(attempts)
        
        # Rank models by overall success rate
        rankings = sorted(
            [(name, res['overall_metrics']['success_rate']) 
             for name, res in model_results.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        comparison['model_rankings'] = {
            name: {'rank': i + 1, 'success_rate': rate}
            for i, (name, rate) in enumerate(rankings)
        }
        
        # Detailed metric comparison
        all_metrics = ['scattered_context_recall', 'temporal_coverage', 
                      'cross_file_comprehension', 'refactoring_resilience',
                      'retrieval_efficiency']
        
        for metric in all_metrics:
            comparison['detailed_comparison'][metric] = {
                name: results['detailed_metrics'][metric]
                for name, results in model_results.items()
            }
        
        return comparison


def generate_mrr_report(evaluator: MRRBenchmarkEvaluator,
                       model_attempts: Dict[str, List[MRRAttempt]]) -> str:
    """Generate human-readable MRR benchmark report"""
    
    report_lines = [
        "Multi-Random Retrieval (MRR) Benchmark Results",
        "=" * 50,
        ""
    ]
    
    # Individual model results
    for model_name, attempts in model_attempts.items():
        results = evaluator.evaluate_model(attempts)
        
        report_lines.extend([
            f"Model: {model_name}",
            "-" * 30,
            f"Overall Success Rate: {results['overall_metrics']['success_rate']:.1f}%",
            "",
            "Detailed Metrics:",
            f"  Scattered Context Recall: {results['detailed_metrics']['scattered_context_recall']:.1f}%",
            f"  Temporal Coverage: {results['detailed_metrics']['temporal_coverage']:.1f}%", 
            f"  Cross-File Comprehension: {results['detailed_metrics']['cross_file_comprehension']:.1f}%",
            f"  Refactoring Resilience: {results['detailed_metrics']['refactoring_resilience']:.1f}%",
            f"  Retrieval Efficiency: {results['detailed_metrics']['retrieval_efficiency']:.1f}%",
            ""
        ])
    
    # Model comparison
    if len(model_attempts) > 1:
        comparison = evaluator.compare_models(model_attempts)
        
        report_lines.extend([
            "Model Comparison",
            "=" * 50,
            ""
        ])
        
        for model, ranking in comparison['model_rankings'].items():
            report_lines.append(
                f"#{ranking['rank']} {model}: {ranking['success_rate']:.1f}%"
            )
    
    return "\n".join(report_lines)


# Example usage
if __name__ == "__main__":
    print("MRR Benchmark Metrics Module")
    print("Specialized metrics for Multi-Random Retrieval evaluation")
    print("\nKey MRR metrics:")
    print("- Scattered Context Recall: Finding dispersed relevant files")
    print("- Temporal Coverage: Handling bugs spanning months") 
    print("- Cross-File Comprehension: Understanding file dependencies")
    print("- Refactoring Resilience: Handling renamed/moved code")
    print("- Retrieval Efficiency: Finding files without excess noise")