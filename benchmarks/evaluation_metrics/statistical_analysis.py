"""
Statistical Analysis for Chronos Benchmark Evaluation

Provides rigorous statistical testing for comparing debugging models.
Used to validate the significance of Chronos's performance improvements.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from scipy import stats
import warnings


@dataclass
class ModelPerformance:
    """Performance data for a single model"""
    model_name: str
    success_rates: List[float]  # Success rate per test case (0 or 1)
    fix_times: List[float]      # Time to fix in seconds
    iterations: List[int]       # Iterations needed per case
    category_results: Dict[str, List[float]]  # Results by bug category


class StatisticalTests:
    """Statistical tests for model comparison"""
    
    @staticmethod
    def bootstrap_confidence_interval(data: List[float], 
                                    confidence: float = 0.95,
                                    n_bootstrap: int = 10000) -> Tuple[float, float, float]:
        """
        Calculate bootstrap confidence interval for any metric.
        Returns (mean, lower_bound, upper_bound)
        """
        if not data:
            return (0.0, 0.0, 0.0)
        
        data_array = np.array(data)
        bootstrap_means = []
        
        # Perform bootstrap sampling
        for _ in range(n_bootstrap):
            sample = np.random.choice(data_array, size=len(data_array), replace=True)
            bootstrap_means.append(np.mean(sample))
        
        # Calculate percentiles
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        mean = np.mean(data)
        lower = np.percentile(bootstrap_means, lower_percentile)
        upper = np.percentile(bootstrap_means, upper_percentile)
        
        return (mean, lower, upper)
    
    @staticmethod
    def paired_permutation_test(model1_results: List[float],
                               model2_results: List[float],
                               n_permutations: int = 10000) -> float:
        """
        Permutation test for paired samples (same test cases).
        Returns p-value for the null hypothesis that models perform equally.
        """
        if len(model1_results) != len(model2_results):
            raise ValueError("Results must be paired (same test cases)")
        
        # Calculate observed difference
        differences = np.array(model1_results) - np.array(model2_results)
        observed_mean_diff = np.mean(differences)
        
        # Permutation test
        permuted_diffs = []
        for _ in range(n_permutations):
            # Randomly flip signs of differences
            signs = np.random.choice([-1, 1], size=len(differences))
            permuted_diff = np.mean(differences * signs)
            permuted_diffs.append(permuted_diff)
        
        # Calculate p-value
        permuted_diffs = np.array(permuted_diffs)
        p_value = np.mean(np.abs(permuted_diffs) >= np.abs(observed_mean_diff))
        
        return p_value
    
    @staticmethod
    def mcnemar_test(model1_results: List[bool], 
                     model2_results: List[bool]) -> Dict[str, float]:
        """
        McNemar's test for paired binary outcomes (success/failure).
        Specifically designed for comparing debugging success rates.
        """
        if len(model1_results) != len(model2_results):
            raise ValueError("Results must be paired")
        
        # Create contingency table
        both_success = sum(1 for m1, m2 in zip(model1_results, model2_results) 
                          if m1 and m2)
        model1_only = sum(1 for m1, m2 in zip(model1_results, model2_results) 
                         if m1 and not m2)
        model2_only = sum(1 for m1, m2 in zip(model1_results, model2_results) 
                         if not m1 and m2)
        both_fail = sum(1 for m1, m2 in zip(model1_results, model2_results) 
                       if not m1 and not m2)
        
        # McNemar's test statistic
        n_discordant = model1_only + model2_only
        if n_discordant == 0:
            return {
                'statistic': 0.0,
                'p_value': 1.0,
                'model1_advantage': 0,
                'model2_advantage': 0
            }
        
        # Use exact binomial test for small samples
        if n_discordant < 20:
            p_value = stats.binom_test(model1_only, n_discordant, 0.5)
        else:
            # Use chi-square approximation for larger samples
            chi2 = (abs(model1_only - model2_only) - 1) ** 2 / n_discordant
            p_value = 1 - stats.chi2.cdf(chi2, df=1)
        
        return {
            'statistic': (model1_only - model2_only) ** 2 / n_discordant,
            'p_value': p_value,
            'model1_advantage': model1_only,
            'model2_advantage': model2_only,
            'both_success': both_success,
            'both_fail': both_fail
        }
    
    @staticmethod
    def effect_size_metrics(model1_results: List[float],
                           model2_results: List[float]) -> Dict[str, float]:
        """
        Calculate various effect size metrics for comparing models.
        """
        model1_array = np.array(model1_results)
        model2_array = np.array(model2_results)
        
        # Cohen's d
        pooled_std = np.sqrt((np.var(model1_array, ddof=1) + 
                             np.var(model2_array, ddof=1)) / 2)
        
        if pooled_std == 0:
            cohens_d = 0.0
        else:
            cohens_d = (np.mean(model1_array) - np.mean(model2_array)) / pooled_std
        
        # Probability of superiority (non-parametric effect size)
        # P(X > Y) where X is model1 and Y is model2
        superiority_count = 0
        total_comparisons = 0
        
        for x in model1_array:
            for y in model2_array:
                total_comparisons += 1
                if x > y:
                    superiority_count += 1
                elif x == y:
                    superiority_count += 0.5  # Tie counts as 0.5
        
        prob_superiority = superiority_count / total_comparisons if total_comparisons > 0 else 0.5
        
        # Relative improvement
        mean1 = np.mean(model1_array)
        mean2 = np.mean(model2_array)
        
        if mean2 == 0:
            relative_improvement = float('inf') if mean1 > 0 else 0.0
        else:
            relative_improvement = (mean1 - mean2) / mean2
        
        return {
            'cohens_d': cohens_d,
            'probability_of_superiority': prob_superiority,
            'relative_improvement': relative_improvement,
            'absolute_improvement': mean1 - mean2,
            'model1_mean': mean1,
            'model2_mean': mean2
        }
    
    @staticmethod
    def multiple_comparison_correction(p_values: List[float], 
                                     method: str = 'bonferroni') -> List[float]:
        """
        Adjust p-values for multiple comparisons.
        Methods: 'bonferroni', 'holm', 'fdr'
        """
        n = len(p_values)
        if n == 0:
            return []
        
        if method == 'bonferroni':
            return [min(p * n, 1.0) for p in p_values]
        
        elif method == 'holm':
            # Holm-Bonferroni method
            sorted_indices = np.argsort(p_values)
            sorted_p = np.array(p_values)[sorted_indices]
            adjusted_p = np.zeros(n)
            
            for i in range(n):
                adjusted_p[sorted_indices[i]] = min(sorted_p[i] * (n - i), 1.0)
                
            # Ensure monotonicity
            for i in range(1, n):
                if adjusted_p[sorted_indices[i]] < adjusted_p[sorted_indices[i-1]]:
                    adjusted_p[sorted_indices[i]] = adjusted_p[sorted_indices[i-1]]
                    
            return adjusted_p.tolist()
        
        elif method == 'fdr':
            # Benjamini-Hochberg FDR
            sorted_indices = np.argsort(p_values)
            sorted_p = np.array(p_values)[sorted_indices]
            adjusted_p = np.zeros(n)
            
            for i in range(n):
                adjusted_p[sorted_indices[i]] = min(
                    sorted_p[i] * n / (i + 1), 1.0
                )
            
            # Ensure monotonicity from end
            for i in range(n-2, -1, -1):
                if adjusted_p[sorted_indices[i]] > adjusted_p[sorted_indices[i+1]]:
                    adjusted_p[sorted_indices[i]] = adjusted_p[sorted_indices[i+1]]
                    
            return adjusted_p.tolist()
        
        else:
            raise ValueError(f"Unknown method: {method}")


class BenchmarkStatisticalAnalysis:
    """Complete statistical analysis for benchmark results"""
    
    def __init__(self, results: Dict[str, ModelPerformance]):
        self.results = results
        self.model_names = list(results.keys())
    
    def pairwise_comparison(self, model1: str, model2: str) -> Dict[str, Any]:
        """Comprehensive pairwise comparison between two models"""
        
        perf1 = self.results[model1]
        perf2 = self.results[model2]
        
        comparison = {
            'models': [model1, model2],
            'success_rate': {},
            'efficiency': {},
            'statistical_tests': {}
        }
        
        # Success rate analysis
        success1 = perf1.success_rates
        success2 = perf2.success_rates
        
        # Bootstrap confidence intervals
        mean1, lower1, upper1 = StatisticalTests.bootstrap_confidence_interval(success1)
        mean2, lower2, upper2 = StatisticalTests.bootstrap_confidence_interval(success2)
        
        comparison['success_rate'] = {
            model1: {
                'mean': mean1 * 100,
                'confidence_interval': [lower1 * 100, upper1 * 100]
            },
            model2: {
                'mean': mean2 * 100,
                'confidence_interval': [lower2 * 100, upper2 * 100]
            }
        }
        
        # Statistical tests
        # McNemar's test for paired binary outcomes
        mcnemar_result = StatisticalTests.mcnemar_test(
            [s == 1.0 for s in success1],
            [s == 1.0 for s in success2]
        )
        
        # Permutation test
        perm_p_value = StatisticalTests.paired_permutation_test(success1, success2)
        
        # Effect sizes
        effect_sizes = StatisticalTests.effect_size_metrics(success1, success2)
        
        comparison['statistical_tests'] = {
            'mcnemar': mcnemar_result,
            'permutation_test_p': perm_p_value,
            'effect_sizes': effect_sizes
        }
        
        # Efficiency comparison (time and iterations)
        if perf1.fix_times and perf2.fix_times:
            time_effect = StatisticalTests.effect_size_metrics(
                perf1.fix_times, perf2.fix_times
            )
            comparison['efficiency']['time'] = time_effect
        
        if perf1.iterations and perf2.iterations:
            iter_effect = StatisticalTests.effect_size_metrics(
                [float(i) for i in perf1.iterations],
                [float(i) for i in perf2.iterations]
            )
            comparison['efficiency']['iterations'] = iter_effect
        
        return comparison
    
    def category_analysis(self) -> Dict[str, Any]:
        """Analyze performance across bug categories"""
        
        category_results = {}
        
        # Get all categories
        all_categories = set()
        for perf in self.results.values():
            all_categories.update(perf.category_results.keys())
        
        for category in all_categories:
            category_results[category] = {}
            
            # Get results for each model in this category
            model_category_results = {}
            for model_name, perf in self.results.items():
                if category in perf.category_results:
                    model_category_results[model_name] = perf.category_results[category]
            
            # Calculate statistics for each model
            for model_name, results in model_category_results.items():
                mean, lower, upper = StatisticalTests.bootstrap_confidence_interval(results)
                category_results[category][model_name] = {
                    'mean': mean * 100,
                    'confidence_interval': [lower * 100, upper * 100],
                    'n_cases': len(results)
                }
        
        return category_results
    
    def full_comparison_matrix(self) -> pd.DataFrame:
        """Create a comparison matrix of all models"""
        
        n_models = len(self.model_names)
        p_values = np.ones((n_models, n_models))
        effect_sizes = np.zeros((n_models, n_models))
        
        # Perform pairwise comparisons
        for i in range(n_models):
            for j in range(i + 1, n_models):
                comparison = self.pairwise_comparison(
                    self.model_names[i], 
                    self.model_names[j]
                )
                
                p_value = comparison['statistical_tests']['permutation_test_p']
                effect_size = comparison['statistical_tests']['effect_sizes']['cohens_d']
                
                p_values[i, j] = p_value
                p_values[j, i] = p_value
                effect_sizes[i, j] = effect_size
                effect_sizes[j, i] = -effect_size
        
        # Create DataFrames
        p_value_df = pd.DataFrame(
            p_values,
            index=self.model_names,
            columns=self.model_names
        )
        
        effect_size_df = pd.DataFrame(
            effect_sizes,
            index=self.model_names,
            columns=self.model_names
        )
        
        return p_value_df, effect_size_df
    
    def generate_report(self) -> str:
        """Generate comprehensive statistical report"""
        
        lines = [
            "Statistical Analysis Report",
            "=" * 50,
            "",
            "Model Performance Summary",
            "-" * 30
        ]
        
        # Overall performance
        for model_name, perf in self.results.items():
            mean, lower, upper = StatisticalTests.bootstrap_confidence_interval(
                perf.success_rates
            )
            lines.append(
                f"{model_name}: {mean*100:.1f}% "
                f"(95% CI: [{lower*100:.1f}%, {upper*100:.1f}%])"
            )
        
        lines.extend(["", "Pairwise Comparisons", "-" * 30])
        
        # Key comparisons (assuming Chronos is one of the models)
        if "kodezi_chronos" in self.results:
            for other_model in self.model_names:
                if other_model != "kodezi_chronos":
                    comparison = self.pairwise_comparison("kodezi_chronos", other_model)
                    
                    p_value = comparison['statistical_tests']['permutation_test_p']
                    effect_size = comparison['statistical_tests']['effect_sizes']['cohens_d']
                    rel_improvement = comparison['statistical_tests']['effect_sizes']['relative_improvement']
                    
                    lines.append(
                        f"\nChronos vs {other_model}:"
                    )
                    lines.append(
                        f"  p-value: {p_value:.4f} "
                        f"({'significant' if p_value < 0.05 else 'not significant'})"
                    )
                    lines.append(
                        f"  Effect size (Cohen's d): {effect_size:.2f}"
                    )
                    lines.append(
                        f"  Relative improvement: {rel_improvement*100:.1f}%"
                    )
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    print("Chronos Benchmark Statistical Analysis Module")
    print("\nProvides:")
    print("- Bootstrap confidence intervals")
    print("- Permutation tests for paired comparisons")
    print("- McNemar's test for binary outcomes")
    print("- Effect size calculations")
    print("- Multiple comparison corrections")
    print("\nUse with evaluation results to validate performance improvements")