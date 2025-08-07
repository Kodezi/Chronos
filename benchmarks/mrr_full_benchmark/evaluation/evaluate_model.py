#!/usr/bin/env python3
"""
Kodezi Chronos MRR Benchmark Evaluation Framework
Comprehensive evaluation suite for debugging-first language models
"""

import json
import time
import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import tempfile
import shutil


@dataclass
class EvaluationResult:
    """Result of evaluating a single bug case"""
    bug_id: str
    category: str
    success: bool
    root_cause_found: bool
    fix_applied: bool
    test_passed: bool
    no_regression: bool
    iterations: int
    time_taken: float
    tokens_used: int
    memory_used_mb: float
    files_retrieved: List[str]
    files_modified: List[str]
    error_message: Optional[str] = None


@dataclass
class ModelPerformance:
    """Overall model performance metrics"""
    model_name: str
    total_cases: int
    successful_fixes: int
    root_cause_accuracy: float
    avg_iterations: float
    avg_time_seconds: float
    avg_tokens: float
    avg_memory_mb: float
    precision_at_k: Dict[int, float]
    recall_at_k: Dict[int, float]
    mean_reciprocal_rank: float
    category_performance: Dict[str, Dict[str, float]]
    difficulty_performance: Dict[str, Dict[str, float]]


class MRRBenchmarkEvaluator:
    """Main evaluator for the MRR benchmark"""
    
    def __init__(self, benchmark_path: str, output_dir: str):
        self.benchmark_path = Path(benchmark_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Load benchmark metadata
        self.load_benchmark_metadata()
        
        # Initialize metrics storage
        self.results: List[EvaluationResult] = []
        
    def setup_logging(self):
        """Setup evaluation logging"""
        log_file = self.output_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_benchmark_metadata(self):
        """Load benchmark metadata"""
        metadata_path = self.benchmark_path / "BENCHMARK_METADATA.json"
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        self.logger.info(f"Loaded benchmark metadata: {self.metadata['benchmark_info']['name']}")
        
    def evaluate_model(self, model_api, model_name: str, subset_size: Optional[int] = None) -> ModelPerformance:
        """
        Evaluate a model on the benchmark
        
        Args:
            model_api: Model API interface (must implement debug_bug method)
            model_name: Name of the model being evaluated
            subset_size: Optional number of cases to evaluate (for testing)
        """
        self.logger.info(f"Starting evaluation of {model_name}")
        
        # Load bug cases
        bug_cases = self.load_bug_cases(subset_size)
        self.logger.info(f"Loaded {len(bug_cases)} bug cases for evaluation")
        
        # Evaluate each bug case
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for bug_case in bug_cases:
                future = executor.submit(self.evaluate_single_bug, model_api, bug_case)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results.append(result)
                    self.log_progress(len(self.results), len(bug_cases))
                except Exception as e:
                    self.logger.error(f"Error evaluating bug: {e}")
        
        # Calculate overall performance
        performance = self.calculate_performance(model_name)
        
        # Save results
        self.save_results(model_name, performance)
        
        return performance
        
    def load_bug_cases(self, subset_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load bug cases from the benchmark"""
        bug_cases = []
        
        # Load bugs from each category
        for category in self.metadata['categories']:
            category_path = self.benchmark_path / category
            if category_path.exists():
                bug_files = sorted(category_path.glob("*.json"))
                
                # Load subset if specified
                if subset_size:
                    per_category = subset_size // len(self.metadata['categories'])
                    bug_files = bug_files[:per_category]
                
                for bug_file in bug_files:
                    with open(bug_file, 'r') as f:
                        bug_cases.append(json.load(f))
        
        return bug_cases
        
    def evaluate_single_bug(self, model_api, bug_case: Dict[str, Any]) -> EvaluationResult:
        """Evaluate model on a single bug"""
        start_time = time.time()
        bug_id = bug_case['bug_id']
        
        try:
            # Create temporary workspace
            with tempfile.TemporaryDirectory() as workspace:
                workspace_path = Path(workspace)
                
                # Setup test repository (would copy from test_repositories)
                repo_path = self.setup_test_repository(bug_case, workspace_path)
                
                # Run model debugging
                debug_result = model_api.debug_bug(
                    bug_description=bug_case['description'],
                    symptoms=bug_case['symptoms'],
                    repository_path=repo_path,
                    scattered_context=bug_case['scattered_context'],
                    time_limit=bug_case['evaluation_criteria']['time_limit_seconds']
                )
                
                # Evaluate the fix
                evaluation = self.evaluate_fix(bug_case, debug_result, repo_path)
                
                # Create result
                result = EvaluationResult(
                    bug_id=bug_id,
                    category=bug_case['category'],
                    success=evaluation['success'],
                    root_cause_found=evaluation['root_cause_found'],
                    fix_applied=evaluation['fix_applied'],
                    test_passed=evaluation['test_passed'],
                    no_regression=evaluation['no_regression'],
                    iterations=debug_result.get('iterations', 1),
                    time_taken=time.time() - start_time,
                    tokens_used=debug_result.get('tokens_used', 0),
                    memory_used_mb=debug_result.get('memory_used_mb', 0),
                    files_retrieved=debug_result.get('files_retrieved', []),
                    files_modified=debug_result.get('files_modified', [])
                )
                
                return result
                
        except Exception as e:
            self.logger.error(f"Error evaluating bug {bug_id}: {e}")
            return EvaluationResult(
                bug_id=bug_id,
                category=bug_case['category'],
                success=False,
                root_cause_found=False,
                fix_applied=False,
                test_passed=False,
                no_regression=False,
                iterations=0,
                time_taken=time.time() - start_time,
                tokens_used=0,
                memory_used_mb=0,
                files_retrieved=[],
                files_modified=[],
                error_message=str(e)
            )
            
    def setup_test_repository(self, bug_case: Dict[str, Any], workspace: Path) -> Path:
        """Setup test repository for bug evaluation"""
        # In real implementation, would copy from test_repositories
        # For now, create a minimal structure
        repo_path = workspace / "test_repo"
        repo_path.mkdir()
        
        # Create the error file
        error_location = bug_case['error_location']
        error_file = repo_path / error_location['file']
        error_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a simple file with the bug
        error_file.write_text(f"# Bug at line {error_location['line']}\n# TODO: Fix this bug\n")
        
        return repo_path
        
    def evaluate_fix(self, bug_case: Dict[str, Any], debug_result: Dict[str, Any], repo_path: Path) -> Dict[str, bool]:
        """Evaluate if the fix is correct"""
        evaluation = {
            'success': False,
            'root_cause_found': False,
            'fix_applied': False,
            'test_passed': False,
            'no_regression': False
        }
        
        # Check if root cause was identified
        if debug_result.get('root_cause'):
            expected_root_cause = bug_case['ground_truth']['root_cause'].lower()
            actual_root_cause = debug_result['root_cause'].lower()
            evaluation['root_cause_found'] = expected_root_cause in actual_root_cause
        
        # Check if fix was applied
        if debug_result.get('files_modified'):
            evaluation['fix_applied'] = True
            
            # Check if correct files were modified
            must_find_files = set(bug_case['evaluation_criteria']['must_find_files'])
            found_files = set(debug_result.get('files_retrieved', []))
            if must_find_files.issubset(found_files):
                evaluation['success'] = True
        
        # Run tests if available
        if evaluation['fix_applied'] and bug_case['ground_truth'].get('test_command'):
            test_result = self.run_test_command(repo_path, bug_case['ground_truth']['test_command'])
            evaluation['test_passed'] = test_result
            
            # Check for regressions
            if test_result:
                evaluation['no_regression'] = True
        
        return evaluation
        
    def run_test_command(self, repo_path: Path, test_command: str) -> bool:
        """Run test command and return success status"""
        try:
            result = subprocess.run(
                test_command.split(),
                cwd=repo_path,
                capture_output=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception:
            return False
            
    def calculate_performance(self, model_name: str) -> ModelPerformance:
        """Calculate overall performance metrics"""
        if not self.results:
            raise ValueError("No results to calculate performance")
        
        # Basic metrics
        total_cases = len(self.results)
        successful_fixes = sum(1 for r in self.results if r.success)
        root_cause_found = sum(1 for r in self.results if r.root_cause_found)
        
        # Average metrics
        avg_iterations = statistics.mean(r.iterations for r in self.results if r.iterations > 0)
        avg_time = statistics.mean(r.time_taken for r in self.results)
        avg_tokens = statistics.mean(r.tokens_used for r in self.results)
        avg_memory = statistics.mean(r.memory_used_mb for r in self.results)
        
        # Retrieval metrics
        precision_at_k = self.calculate_precision_at_k()
        recall_at_k = self.calculate_recall_at_k()
        mrr = self.calculate_mrr()
        
        # Category performance
        category_performance = self.calculate_category_performance()
        
        # Difficulty performance
        difficulty_performance = self.calculate_difficulty_performance()
        
        return ModelPerformance(
            model_name=model_name,
            total_cases=total_cases,
            successful_fixes=successful_fixes,
            root_cause_accuracy=root_cause_found / total_cases,
            avg_iterations=avg_iterations,
            avg_time_seconds=avg_time,
            avg_tokens=avg_tokens,
            avg_memory_mb=avg_memory,
            precision_at_k=precision_at_k,
            recall_at_k=recall_at_k,
            mean_reciprocal_rank=mrr,
            category_performance=category_performance,
            difficulty_performance=difficulty_performance
        )
        
    def calculate_precision_at_k(self) -> Dict[int, float]:
        """Calculate precision@k for different k values"""
        k_values = [1, 5, 10, 20]
        precision_at_k = {}
        
        for k in k_values:
            precisions = []
            for result in self.results:
                if len(result.files_retrieved) >= k:
                    # Count relevant files in top k
                    relevant_count = sum(1 for f in result.files_retrieved[:k] 
                                       if f in result.files_modified)
                    precisions.append(relevant_count / k)
            
            if precisions:
                precision_at_k[k] = statistics.mean(precisions)
            else:
                precision_at_k[k] = 0.0
                
        return precision_at_k
        
    def calculate_recall_at_k(self) -> Dict[int, float]:
        """Calculate recall@k for different k values"""
        k_values = [1, 5, 10, 20]
        recall_at_k = {}
        
        for k in k_values:
            recalls = []
            for result in self.results:
                if result.files_modified:
                    # Count how many modified files were retrieved in top k
                    retrieved_relevant = sum(1 for f in result.files_retrieved[:k] 
                                           if f in result.files_modified)
                    recalls.append(retrieved_relevant / len(result.files_modified))
            
            if recalls:
                recall_at_k[k] = statistics.mean(recalls)
            else:
                recall_at_k[k] = 0.0
                
        return recall_at_k
        
    def calculate_mrr(self) -> float:
        """Calculate Mean Reciprocal Rank"""
        reciprocal_ranks = []
        
        for result in self.results:
            if result.files_modified and result.files_retrieved:
                # Find rank of first relevant file
                for rank, file in enumerate(result.files_retrieved, 1):
                    if file in result.files_modified:
                        reciprocal_ranks.append(1.0 / rank)
                        break
                else:
                    reciprocal_ranks.append(0.0)
        
        return statistics.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
        
    def calculate_category_performance(self) -> Dict[str, Dict[str, float]]:
        """Calculate performance by category"""
        category_results = {}
        
        for category in self.metadata['categories']:
            category_data = [r for r in self.results if r.category == category]
            if category_data:
                category_results[category] = {
                    'success_rate': sum(1 for r in category_data if r.success) / len(category_data),
                    'avg_time': statistics.mean(r.time_taken for r in category_data),
                    'avg_iterations': statistics.mean(r.iterations for r in category_data if r.iterations > 0)
                }
        
        return category_results
        
    def calculate_difficulty_performance(self) -> Dict[str, Dict[str, float]]:
        """Calculate performance by difficulty level"""
        # Would need difficulty information in bug cases
        # For now, return empty
        return {}
        
    def log_progress(self, completed: int, total: int):
        """Log evaluation progress"""
        progress = (completed / total) * 100
        self.logger.info(f"Progress: {completed}/{total} ({progress:.1f}%)")
        
    def save_results(self, model_name: str, performance: ModelPerformance):
        """Save evaluation results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed results
        results_file = self.output_dir / f"{model_name}_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump([asdict(r) for r in self.results], f, indent=2)
        
        # Save performance summary
        summary_file = self.output_dir / f"{model_name}_performance_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(asdict(performance), f, indent=2)
        
        # Generate report
        self.generate_report(model_name, performance, timestamp)
        
        self.logger.info(f"Results saved to {self.output_dir}")
        
    def generate_report(self, model_name: str, performance: ModelPerformance, timestamp: str):
        """Generate human-readable evaluation report"""
        report_file = self.output_dir / f"{model_name}_report_{timestamp}.md"
        
        report = f"""# Kodezi Chronos MRR Benchmark Evaluation Report

## Model: {model_name}
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Benchmark Version**: {self.metadata['benchmark_info']['version']}

## Overall Performance

- **Total Cases**: {performance.total_cases}
- **Successful Fixes**: {performance.successful_fixes} ({performance.successful_fixes/performance.total_cases*100:.1f}%)
- **Root Cause Accuracy**: {performance.root_cause_accuracy:.3f}
- **Average Iterations**: {performance.avg_iterations:.1f}
- **Average Time**: {performance.avg_time_seconds:.1f}s
- **Average Tokens**: {performance.avg_tokens:,.0f}
- **Average Memory**: {performance.avg_memory_mb:.1f} MB

## Retrieval Metrics

### Precision@K
"""
        for k, precision in performance.precision_at_k.items():
            report += f"- P@{k}: {precision:.3f}\n"
            
        report += "\n### Recall@K\n"
        for k, recall in performance.recall_at_k.items():
            report += f"- R@{k}: {recall:.3f}\n"
            
        report += f"\n- **Mean Reciprocal Rank**: {performance.mean_reciprocal_rank:.3f}\n"
        
        report += "\n## Category Performance\n\n"
        report += "| Category | Success Rate | Avg Time | Avg Iterations |\n"
        report += "|----------|-------------|----------|----------------|\n"
        
        for category, metrics in performance.category_performance.items():
            report += f"| {category} | {metrics['success_rate']:.2%} | {metrics['avg_time']:.1f}s | {metrics['avg_iterations']:.1f} |\n"
        
        report += "\n## Comparison with Baselines\n\n"
        report += "| Model | Success Rate | Root Cause Accuracy | MRR |\n"
        report += "|-------|--------------|-------------------|-----|\n"
        report += f"| {model_name} | {performance.successful_fixes/performance.total_cases:.1%} | {performance.root_cause_accuracy:.3f} | {performance.mean_reciprocal_rank:.3f} |\n"
        
        # Add baseline comparisons from metadata
        for baseline, metrics in self.metadata.get('baseline_performance', {}).items():
            report += f"| {baseline} | {metrics['success_rate']:.1%} | {metrics['root_cause_accuracy']:.3f} | - |\n"
        
        with open(report_file, 'w') as f:
            f.write(report)


class MockModelAPI:
    """Mock model API for testing the evaluation framework"""
    
    def debug_bug(self, bug_description: str, symptoms: List[str], 
                  repository_path: Path, scattered_context: List[Dict],
                  time_limit: int) -> Dict[str, Any]:
        """Mock debugging implementation"""
        # Simulate some debugging work
        time.sleep(0.1)
        
        return {
            'root_cause': 'Mock root cause identification',
            'iterations': 2,
            'tokens_used': 15000,
            'memory_used_mb': 512.0,
            'files_retrieved': [ctx['file_path'] for ctx in scattered_context[:10]],
            'files_modified': [scattered_context[0]['file_path']] if scattered_context else []
        }


def main():
    """Main evaluation entry point"""
    parser = argparse.ArgumentParser(description='Evaluate model on Kodezi Chronos MRR Benchmark')
    parser.add_argument('--model', type=str, required=True, help='Model name to evaluate')
    parser.add_argument('--benchmark-path', type=str, required=True, help='Path to benchmark data')
    parser.add_argument('--output-dir', type=str, required=True, help='Output directory for results')
    parser.add_argument('--subset', type=int, help='Evaluate on subset of cases (for testing)')
    
    args = parser.parse_args()
    
    # Create evaluator
    evaluator = MRRBenchmarkEvaluator(args.benchmark_path, args.output_dir)
    
    # Create model API (would be replaced with actual model)
    model_api = MockModelAPI()
    
    # Run evaluation
    performance = evaluator.evaluate_model(model_api, args.model, args.subset)
    
    # Print summary
    print(f"\nEvaluation Complete!")
    print(f"Success Rate: {performance.successful_fixes}/{performance.total_cases} ({performance.successful_fixes/performance.total_cases*100:.1f}%)")
    print(f"Root Cause Accuracy: {performance.root_cause_accuracy:.3f}")
    print(f"Mean Reciprocal Rank: {performance.mean_reciprocal_rank:.3f}")


if __name__ == "__main__":
    main()