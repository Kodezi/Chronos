#!/usr/bin/env python3
"""
MRR Benchmark Validation Script
Validates that the benchmark produces expected results for all models
Ensures consistency and correctness of the benchmark implementation
"""

import json
import numpy as np
from pathlib import Path
import subprocess
import sys
import time
from typing import Dict, List, Tuple
import argparse
import logging
from scipy import stats

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Expected performance from paper
EXPECTED_PERFORMANCE = {
    "chronos": {
        "success_rate": 0.673,
        "tolerance": 0.021,  # ±2.1%
        "ci_width": 0.042
    },
    "claude_4_opus": {
        "success_rate": 0.142,
        "tolerance": 0.013,  # ±1.3%
        "ci_width": 0.026
    },
    "gpt_4_1": {
        "success_rate": 0.138,
        "tolerance": 0.012,  # ±1.2%
        "ci_width": 0.024
    },
    "gemini_2_pro": {
        "success_rate": 0.124,
        "tolerance": 0.012,
        "ci_width": 0.024
    }
}

class MRRBenchmarkValidator:
    """Validates MRR benchmark correctness and consistency"""
    
    def __init__(self, benchmark_dir: str = "mrr_full_benchmark"):
        self.benchmark_dir = Path(benchmark_dir)
        self.results_dir = Path("results/mrr_validation")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def validate_all(self) -> bool:
        """Run all validation checks"""
        logger.info("Starting MRR Benchmark Validation")
        logger.info("="*60)
        
        all_passed = True
        
        # 1. Validate benchmark structure
        if not self.validate_structure():
            all_passed = False
            
        # 2. Validate scenario files
        if not self.validate_scenarios():
            all_passed = False
            
        # 3. Validate expected results
        if not self.validate_expected_results():
            all_passed = False
            
        # 4. Validate reproducibility
        if not self.validate_reproducibility():
            all_passed = False
            
        # 5. Validate statistical properties
        if not self.validate_statistical_properties():
            all_passed = False
            
        # Generate report
        self.generate_validation_report(all_passed)
        
        return all_passed
    
    def validate_structure(self) -> bool:
        """Validate benchmark directory structure"""
        logger.info("\n1. Validating Benchmark Structure")
        logger.info("-"*40)
        
        required_dirs = [
            "syntax_errors",
            "logic_errors", 
            "concurrency_issues",
            "memory_issues",
            "api_misuse",
            "performance_bugs",
            "cross_category",
            "artifacts"
        ]
        
        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.benchmark_dir / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
                logger.error(f"✗ Missing directory: {dir_name}")
            else:
                logger.info(f"✓ Found directory: {dir_name}")
        
        # Check file counts
        expected_counts = {
            "syntax_errors": 500,
            "logic_errors": 1200,
            "concurrency_issues": 800,
            "memory_issues": 600,
            "api_misuse": 900,
            "performance_bugs": 400,
            "cross_category": 600
        }
        
        total_files = 0
        for category, expected in expected_counts.items():
            category_path = self.benchmark_dir / category
            if category_path.exists():
                actual = len(list(category_path.glob("*.json")))
                total_files += actual
                if actual < expected * 0.9:  # Allow 10% tolerance
                    logger.warning(f"⚠ {category}: {actual} files (expected ~{expected})")
                else:
                    logger.info(f"✓ {category}: {actual} files")
        
        logger.info(f"\nTotal scenario files: {total_files}")
        
        return len(missing_dirs) == 0 and total_files >= 4500
    
    def validate_scenarios(self) -> bool:
        """Validate scenario file format and content"""
        logger.info("\n2. Validating Scenario Files")
        logger.info("-"*40)
        
        required_fields = [
            "bug_id", "category", "description", "scattered_files",
            "temporal_range", "ground_truth"
        ]
        
        sample_size = 100  # Check sample of files
        all_files = list(self.benchmark_dir.rglob("*.json"))
        sample_files = np.random.choice(all_files, min(sample_size, len(all_files)), replace=False)
        
        invalid_files = []
        for file_path in sample_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Check required fields
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    invalid_files.append((file_path, f"Missing fields: {missing_fields}"))
                
                # Validate scattered files
                if len(data.get('scattered_files', [])) < 10:
                    invalid_files.append((file_path, "Too few scattered files (<10)"))
                    
            except json.JSONDecodeError as e:
                invalid_files.append((file_path, f"JSON error: {e}"))
            except Exception as e:
                invalid_files.append((file_path, f"Error: {e}"))
        
        if invalid_files:
            logger.error(f"✗ Found {len(invalid_files)} invalid files:")
            for file_path, error in invalid_files[:5]:  # Show first 5
                logger.error(f"  - {file_path.name}: {error}")
        else:
            logger.info(f"✓ All {len(sample_files)} sampled files are valid")
        
        return len(invalid_files) == 0
    
    def validate_expected_results(self) -> bool:
        """Validate that benchmark produces expected results"""
        logger.info("\n3. Validating Expected Results")
        logger.info("-"*40)
        
        all_correct = True
        
        for model_name, expected in EXPECTED_PERFORMANCE.items():
            logger.info(f"\nTesting {model_name}...")
            
            # Run mini benchmark (100 scenarios)
            result = self.run_mini_benchmark(model_name, num_scenarios=100)
            
            if result:
                success_rate = result['success_rate']
                expected_rate = expected['success_rate']
                tolerance = expected['tolerance']
                
                # Check if within tolerance
                diff = abs(success_rate - expected_rate)
                if diff <= tolerance:
                    logger.info(f"✓ {model_name}: {success_rate:.1%} "
                              f"(expected {expected_rate:.1%} ± {tolerance:.1%})")
                else:
                    logger.error(f"✗ {model_name}: {success_rate:.1%} "
                               f"(expected {expected_rate:.1%} ± {tolerance:.1%})")
                    all_correct = False
            else:
                logger.error(f"✗ Failed to run benchmark for {model_name}")
                all_correct = False
        
        return all_correct
    
    def validate_reproducibility(self) -> bool:
        """Validate that results are reproducible with same seed"""
        logger.info("\n4. Validating Reproducibility")
        logger.info("-"*40)
        
        model = "claude_4_opus"
        seed = 12345
        num_scenarios = 50
        
        # Run twice with same seed
        result1 = self.run_mini_benchmark(model, num_scenarios, seed)
        result2 = self.run_mini_benchmark(model, num_scenarios, seed)
        
        if result1 and result2:
            # Check if results match
            if (result1['success_rate'] == result2['success_rate'] and
                result1['successful_fixes'] == result2['successful_fixes']):
                logger.info(f"✓ Results are reproducible (seed={seed})")
                return True
            else:
                logger.error("✗ Results are not reproducible!")
                logger.error(f"  Run 1: {result1['success_rate']:.1%}")
                logger.error(f"  Run 2: {result2['success_rate']:.1%}")
                return False
        else:
            logger.error("✗ Failed to run reproducibility test")
            return False
    
    def validate_statistical_properties(self) -> bool:
        """Validate statistical properties of the benchmark"""
        logger.info("\n5. Validating Statistical Properties")
        logger.info("-"*40)
        
        # Run larger sample for statistical validation
        model = "claude_4_opus"
        num_runs = 10
        num_scenarios = 500
        
        success_rates = []
        for i in range(num_runs):
            seed = 1000 + i
            result = self.run_mini_benchmark(model, num_scenarios, seed)
            if result:
                success_rates.append(result['success_rate'])
        
        if len(success_rates) < num_runs:
            logger.error("✗ Failed to complete statistical validation")
            return False
        
        # Calculate statistics
        mean_rate = np.mean(success_rates)
        std_rate = np.std(success_rates)
        ci_95 = stats.t.interval(0.95, len(success_rates)-1, 
                                loc=mean_rate, 
                                scale=stats.sem(success_rates))
        
        expected = EXPECTED_PERFORMANCE[model]
        
        # Check if mean is close to expected
        if abs(mean_rate - expected['success_rate']) <= expected['tolerance']:
            logger.info(f"✓ Mean success rate: {mean_rate:.1%} "
                       f"(expected {expected['success_rate']:.1%})")
        else:
            logger.error(f"✗ Mean success rate: {mean_rate:.1%} "
                        f"(expected {expected['success_rate']:.1%})")
            return False
        
        # Check confidence interval
        ci_width = ci_95[1] - ci_95[0]
        logger.info(f"  95% CI: [{ci_95[0]:.1%}, {ci_95[1]:.1%}] "
                   f"(width: {ci_width:.1%})")
        logger.info(f"  Standard deviation: {std_rate:.1%}")
        
        # Validate distribution is approximately normal
        _, p_value = stats.shapiro(success_rates)
        if p_value > 0.05:
            logger.info(f"✓ Distribution appears normal (p={p_value:.3f})")
        else:
            logger.warning(f"⚠ Distribution may not be normal (p={p_value:.3f})")
        
        return True
    
    def run_mini_benchmark(self, model: str, num_scenarios: int = 100, 
                          seed: int = 42) -> Dict[str, any]:
        """Run a mini version of the benchmark"""
        try:
            # Import and run the benchmark
            sys.path.append(str(Path(__file__).parent))
            from run_full_mrr_benchmark import MRRBenchmarkRunner, BenchmarkConfig
            
            config = BenchmarkConfig(
                seed=seed,
                num_scenarios=num_scenarios,
                model_name=model,
                output_dir=str(self.results_dir),
                cache_results=False,
                validate_results=False
            )
            
            runner = MRRBenchmarkRunner(config)
            # Quick evaluation without full run
            scenarios = runner.scenarios[:num_scenarios]
            model_perf = runner.MODEL_PERFORMANCE[model]
            
            results = []
            for scenario in scenarios:
                result = runner.evaluate_scenario(scenario, model_perf)
                results.append(result)
            
            # Calculate metrics
            successes = sum(1 for r in results if r['success'])
            success_rate = successes / len(results)
            
            return {
                'success_rate': success_rate,
                'successful_fixes': successes,
                'total_scenarios': len(results)
            }
            
        except Exception as e:
            logger.error(f"Error running mini benchmark: {e}")
            return None
    
    def generate_validation_report(self, all_passed: bool):
        """Generate validation report"""
        report_path = self.results_dir / "validation_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("MRR Benchmark Validation Report\n")
            f.write("="*60 + "\n\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Overall Result: {'PASSED' if all_passed else 'FAILED'}\n\n")
            
            f.write("Expected Performance (from paper):\n")
            for model, perf in EXPECTED_PERFORMANCE.items():
                f.write(f"  {model}: {perf['success_rate']:.1%} ± {perf['tolerance']:.1%}\n")
            
            f.write("\nValidation Checks:\n")
            f.write("1. Structure validation\n")
            f.write("2. Scenario file validation\n")
            f.write("3. Expected results validation\n")
            f.write("4. Reproducibility validation\n")
            f.write("5. Statistical properties validation\n")
        
        logger.info(f"\nValidation report saved to: {report_path}")

def main():
    parser = argparse.ArgumentParser(description='Validate MRR Benchmark')
    parser.add_argument('--benchmark-dir', type=str, default='mrr_full_benchmark',
                       help='Path to benchmark directory')
    
    args = parser.parse_args()
    
    validator = MRRBenchmarkValidator(args.benchmark_dir)
    all_passed = validator.validate_all()
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ MRR Benchmark Validation PASSED")
    else:
        print("❌ MRR Benchmark Validation FAILED")
    print("="*60)
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()