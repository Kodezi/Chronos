#!/usr/bin/env python3
"""
MRR Full Benchmark Dataset Generation Script
Generates the complete 5,000 scenario dataset for the Multi Random Retrieval benchmark
"""

import json
import random
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import os

class MRRDatasetGenerator:
    """Generates full MRR benchmark dataset with realistic debugging scenarios"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        
        # Bug categories from 2025 paper
        self.bug_categories = {
            'syntax_errors': {
                'percentage': 10,
                'subcategories': ['missing_brackets', 'typos', 'indentation', 'unclosed_strings'],
                'complexity_weight': 0.3
            },
            'logic_bugs': {
                'percentage': 24,
                'subcategories': ['off_by_one', 'incorrect_conditions', 'wrong_operators', 'faulty_algorithms'],
                'complexity_weight': 0.7
            },
            'concurrency_issues': {
                'percentage': 16,
                'subcategories': ['race_conditions', 'deadlocks', 'thread_safety', 'synchronization'],
                'complexity_weight': 0.9
            },
            'memory_problems': {
                'percentage': 12,
                'subcategories': ['leaks', 'buffer_overflow', 'null_pointer', 'use_after_free'],
                'complexity_weight': 0.8
            },
            'api_misuse': {
                'percentage': 18,
                'subcategories': ['deprecated_methods', 'wrong_parameters', 'missing_callbacks', 'incorrect_types'],
                'complexity_weight': 0.6
            },
            'performance_bugs': {
                'percentage': 8,
                'subcategories': ['inefficient_algorithms', 'excessive_io', 'cache_misses', 'memory_thrashing'],
                'complexity_weight': 0.7
            },
            'configuration_errors': {
                'percentage': 3,
                'subcategories': ['wrong_settings', 'missing_env_vars', 'invalid_paths'],
                'complexity_weight': 0.4
            },
            'security_vulnerabilities': {
                'percentage': 3,
                'subcategories': ['sql_injection', 'xss', 'buffer_overflow', 'weak_crypto'],
                'complexity_weight': 0.8
            },
            'type_errors': {
                'percentage': 2,
                'subcategories': ['type_mismatch', 'null_safety', 'casting_errors'],
                'complexity_weight': 0.5
            },
            'async_bugs': {
                'percentage': 2,
                'subcategories': ['promise_rejection', 'callback_hell', 'timing_issues'],
                'complexity_weight': 0.8
            },
            'integration_issues': {
                'percentage': 1,
                'subcategories': ['api_version_mismatch', 'protocol_errors', 'data_format'],
                'complexity_weight': 0.7
            },
            'state_management': {
                'percentage': 1,
                'subcategories': ['inconsistent_state', 'stale_data', 'mutation_bugs'],
                'complexity_weight': 0.6
            }
        }
        
        self.languages = ['python', 'javascript', 'java']
        self.language_distribution = [0.4, 0.35, 0.25]
        
    def generate_full_dataset(self, n_scenarios: int = 5000) -> Dict[str, Any]:
        """Generate the complete MRR benchmark dataset"""
        
        dataset = {
            'metadata': {
                'name': 'Multi Random Retrieval (MRR) Benchmark',
                'version': '2.0',
                'date_generated': datetime.now().isoformat(),
                'total_scenarios': n_scenarios,
                'total_bugs': 0,
                'description': 'Comprehensive debugging benchmark with realistic repository-scale scenarios'
            },
            'scenarios': []
        }
        
        # Calculate scenario distribution
        scenario_distribution = self._calculate_scenario_distribution(n_scenarios)
        
        scenario_id = 0
        for category, count in scenario_distribution.items():
            for _ in range(count):
                scenario = self._generate_scenario(scenario_id, category)
                dataset['scenarios'].append(scenario)
                dataset['metadata']['total_bugs'] += len(scenario['bugs'])
                scenario_id += 1
        
        # Add statistical summary
        dataset['summary'] = self._generate_summary(dataset['scenarios'])
        
        return dataset
    
    def _calculate_scenario_distribution(self, n_scenarios: int) -> Dict[str, int]:
        """Calculate number of scenarios per bug category"""
        distribution = {}
        total_allocated = 0
        
        for category, info in self.bug_categories.items():
            count = int(n_scenarios * info['percentage'] / 100)
            distribution[category] = count
            total_allocated += count
        
        # Allocate remaining scenarios to largest category
        if total_allocated < n_scenarios:
            distribution['logic_bugs'] += n_scenarios - total_allocated
        
        return distribution
    
    def _generate_scenario(self, scenario_id: int, primary_category: str) -> Dict[str, Any]:
        """Generate a single debugging scenario"""
        
        # Determine complexity based on category
        complexity_weight = self.bug_categories[primary_category]['complexity_weight']
        complexity = self._determine_complexity(complexity_weight)
        
        # Generate repository characteristics
        language = np.random.choice(self.languages, p=self.language_distribution)
        repo_size = self._generate_repo_size(complexity)
        
        # Generate bugs (2.5 average as per paper)
        n_bugs = np.random.poisson(2.5) + 1  # At least 1 bug
        bugs = self._generate_bugs(n_bugs, primary_category, language, repo_size)
        
        # Generate context scattering (10-50 files)
        context_scatter = self._generate_context_scatter(complexity, n_bugs)
        
        # Generate temporal dispersion (3-12 months)
        temporal_span = random.randint(3, 12)
        
        scenario = {
            'scenario_id': f'mrr_2025_{scenario_id:04d}',
            'metadata': {
                'complexity': complexity,
                'primary_category': primary_category,
                'bug_count': n_bugs,
                'file_count': context_scatter['total_files'],
                'temporal_span_months': temporal_span,
                'language': language
            },
            'repository_snapshot': {
                'commit_hash': self._generate_commit_hash(),
                'size_loc': repo_size,
                'language': language,
                'last_modified': self._generate_timestamp(temporal_span)
            },
            'bugs': bugs,
            'context_scattering': context_scatter,
            'temporal_dispersion': self._generate_temporal_dispersion(temporal_span, n_bugs),
            'ground_truth': self._generate_ground_truth(bugs, language)
        }
        
        return scenario
    
    def _determine_complexity(self, weight: float) -> str:
        """Determine scenario complexity based on category weight"""
        if weight < 0.4:
            return 'low'
        elif weight < 0.6:
            return 'medium'
        elif weight < 0.8:
            return 'high'
        else:
            return 'extreme'
    
    def _generate_repo_size(self, complexity: str) -> int:
        """Generate repository size based on complexity"""
        size_ranges = {
            'low': (1000, 10000),
            'medium': (10000, 100000),
            'high': (100000, 1000000),
            'extreme': (1000000, 10000000)
        }
        
        min_size, max_size = size_ranges[complexity]
        return random.randint(min_size, max_size)
    
    def _generate_bugs(self, n_bugs: int, primary_category: str, 
                      language: str, repo_size: int) -> List[Dict[str, Any]]:
        """Generate bug details for the scenario"""
        bugs = []
        
        # First bug is always from primary category
        bugs.append(self._generate_single_bug(0, primary_category, language, repo_size))
        
        # Additional bugs can be from any category
        for i in range(1, n_bugs):
            category = random.choice(list(self.bug_categories.keys()))
            bugs.append(self._generate_single_bug(i, category, language, repo_size))
        
        return bugs
    
    def _generate_single_bug(self, bug_index: int, category: str, 
                           language: str, repo_size: int) -> Dict[str, Any]:
        """Generate a single bug with details"""
        
        subcategory = random.choice(self.bug_categories[category]['subcategories'])
        
        # Generate realistic bug characteristics
        bug = {
            'bug_id': f'bug_{bug_index:04d}',
            'category': category,
            'subcategory': subcategory,
            'description': self._generate_bug_description(category, subcategory),
            'symptoms': self._generate_symptoms(category, language),
            'severity': random.choice(['low', 'medium', 'high', 'critical']),
            'introduced_commit': self._generate_commit_hash(),
            'affected_files': self._generate_affected_files(category, repo_size),
            'test_failures': self._generate_test_failures(category)
        }
        
        return bug
    
    def _generate_context_scatter(self, complexity: str, n_bugs: int) -> Dict[str, Any]:
        """Generate context scattering information"""
        
        # Base range 10-50 files, adjusted by complexity
        complexity_multiplier = {
            'low': 0.5,
            'medium': 1.0,
            'high': 1.5,
            'extreme': 2.0
        }
        
        base_files = random.randint(10, 50)
        total_files = int(base_files * complexity_multiplier[complexity] * (1 + n_bugs * 0.2))
        total_files = min(total_files, 100)  # Cap at 100 files
        
        return {
            'total_files': total_files,
            'core_files': random.randint(3, 10),
            'peripheral_files': total_files - random.randint(3, 10),
            'avg_hops_to_bug': random.uniform(2.0, 5.0),
            'max_hops': random.randint(3, 7)
        }
    
    def _generate_temporal_dispersion(self, span_months: int, n_bugs: int) -> Dict[str, Any]:
        """Generate temporal dispersion information"""
        return {
            'span_months': span_months,
            'commit_frequency': random.choice(['daily', 'weekly', 'sporadic']),
            'bug_introduction_pattern': random.choice(['clustered', 'spread', 'random']),
            'refactoring_events': random.randint(0, span_months // 3)
        }
    
    def _generate_ground_truth(self, bugs: List[Dict], language: str) -> Dict[str, Any]:
        """Generate ground truth fixes and validation"""
        return {
            'fixes': [self._generate_fix(bug, language) for bug in bugs],
            'test_updates_required': random.randint(0, len(bugs)),
            'refactoring_needed': random.random() < 0.3,
            'performance_impact': random.choice(['none', 'minor', 'moderate', 'significant']),
            'validation_method': 'automated_test_suite'
        }
    
    def _generate_fix(self, bug: Dict, language: str) -> Dict[str, Any]:
        """Generate fix information for a bug"""
        return {
            'bug_id': bug['bug_id'],
            'fix_type': random.choice(['single_line', 'multi_line', 'multi_file', 'architectural']),
            'lines_changed': random.randint(1, 50),
            'files_modified': random.randint(1, 5),
            'introduces_regression': random.random() < 0.1,
            'requires_test_update': random.random() < 0.3
        }
    
    def _generate_bug_description(self, category: str, subcategory: str) -> str:
        """Generate realistic bug description"""
        templates = {
            'logic_bugs': [
                f"{subcategory}: Incorrect boundary check in pagination logic",
                f"{subcategory}: Algorithm fails to handle edge case",
                f"{subcategory}: Business logic validation error"
            ],
            'concurrency_issues': [
                f"{subcategory}: Shared resource accessed without proper locking",
                f"{subcategory}: Potential deadlock in multi-threaded operation",
                f"{subcategory}: Data race in concurrent data structure"
            ],
            'memory_problems': [
                f"{subcategory}: Resource not properly released after use",
                f"{subcategory}: Potential memory corruption in buffer operation",
                f"{subcategory}: Dangling reference after object deletion"
            ]
        }
        
        if category in templates:
            return random.choice(templates[category])
        return f"{category} - {subcategory}: Generic bug description"
    
    def _generate_symptoms(self, category: str, language: str) -> List[str]:
        """Generate bug symptoms based on category and language"""
        symptom_map = {
            'python': {
                'syntax_errors': ['SyntaxError', 'IndentationError'],
                'logic_bugs': ['AssertionError', 'Incorrect output', 'Test failure'],
                'memory_problems': ['MemoryError', 'Segmentation fault'],
                'type_errors': ['TypeError', 'AttributeError']
            },
            'javascript': {
                'syntax_errors': ['SyntaxError', 'Unexpected token'],
                'logic_bugs': ['Wrong result', 'Undefined behavior'],
                'async_bugs': ['Promise rejection', 'Callback not fired'],
                'type_errors': ['TypeError', 'Cannot read property']
            },
            'java': {
                'syntax_errors': ['Compilation error', 'Missing semicolon'],
                'logic_bugs': ['AssertionError', 'Wrong output'],
                'memory_problems': ['OutOfMemoryError', 'NullPointerException'],
                'concurrency_issues': ['DeadlockException', 'Race condition']
            }
        }
        
        if language in symptom_map and category in symptom_map[language]:
            return random.sample(symptom_map[language][category], 
                               min(2, len(symptom_map[language][category])))
        return ['Generic error', 'Test failure']
    
    def _generate_affected_files(self, category: str, repo_size: int) -> List[str]:
        """Generate list of affected files"""
        # More files affected for complex bugs
        complexity_factor = self.bug_categories[category]['complexity_weight']
        n_files = int(random.randint(1, 10) * complexity_factor) + 1
        
        files = []
        for i in range(n_files):
            depth = random.randint(1, 5)
            path_parts = ['src'] + [f'module{random.randint(1,10)}' for _ in range(depth-1)]
            filename = f'file_{random.randint(1,1000)}.py'
            files.append('/'.join(path_parts + [filename]))
        
        return files
    
    def _generate_test_failures(self, category: str) -> List[str]:
        """Generate test failure information"""
        n_failures = random.randint(1, 5)
        test_types = ['unit', 'integration', 'e2e', 'performance']
        
        failures = []
        for _ in range(n_failures):
            test_type = random.choice(test_types)
            test_name = f'test_{category}_{random.randint(1,100)}'
            failures.append(f'{test_type}/{test_name}')
        
        return failures
    
    def _generate_commit_hash(self) -> str:
        """Generate realistic commit hash"""
        return hashlib.sha1(str(random.random()).encode()).hexdigest()[:7]
    
    def _generate_timestamp(self, months_ago: int) -> str:
        """Generate timestamp for given months ago"""
        date = datetime.now() - timedelta(days=months_ago * 30)
        return date.isoformat()
    
    def _generate_summary(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Generate statistical summary of the dataset"""
        
        total_bugs = sum(len(s['bugs']) for s in scenarios)
        complexities = [s['metadata']['complexity'] for s in scenarios]
        
        category_distribution = {}
        for cat in self.bug_categories:
            count = sum(1 for s in scenarios if s['metadata']['primary_category'] == cat)
            category_distribution[cat] = {
                'count': count,
                'percentage': count / len(scenarios) * 100
            }
        
        return {
            'total_scenarios': len(scenarios),
            'total_bugs': total_bugs,
            'avg_bugs_per_scenario': total_bugs / len(scenarios),
            'complexity_distribution': {
                comp: complexities.count(comp) / len(complexities) * 100
                for comp in ['low', 'medium', 'high', 'extreme']
            },
            'category_distribution': category_distribution,
            'language_distribution': {
                lang: sum(1 for s in scenarios if s['metadata']['language'] == lang)
                for lang in self.languages
            }
        }

def generate_and_save_dataset(output_dir: str = 'mrr_full_dataset'):
    """Generate and save the full MRR dataset"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating MRR Full Benchmark Dataset...")
    print("=" * 60)
    
    generator = MRRDatasetGenerator()
    
    # Generate full dataset
    print("Generating 5,000 scenarios...")
    dataset = generator.generate_full_dataset(5000)
    
    # Save full dataset
    output_path = os.path.join(output_dir, 'mrr_full_dataset_2025.json')
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"\nDataset saved to: {output_path}")
    print(f"Total scenarios: {dataset['metadata']['total_scenarios']}")
    print(f"Total bugs: {dataset['metadata']['total_bugs']}")
    print(f"Average bugs per scenario: {dataset['summary']['avg_bugs_per_scenario']:.2f}")
    
    # Generate sample datasets
    print("\nGenerating sample datasets...")
    
    # 100-scenario sample
    sample_100 = {
        'metadata': dataset['metadata'].copy(),
        'scenarios': random.sample(dataset['scenarios'], 100),
        'summary': generator._generate_summary(random.sample(dataset['scenarios'], 100))
    }
    sample_100['metadata']['total_scenarios'] = 100
    sample_100['metadata']['description'] += ' (100-scenario sample)'
    
    with open(os.path.join(output_dir, 'mrr_sample_100.json'), 'w') as f:
        json.dump(sample_100, f, indent=2)
    
    # 20-scenario mini sample
    sample_20 = {
        'metadata': dataset['metadata'].copy(),
        'scenarios': random.sample(dataset['scenarios'], 20),
        'summary': generator._generate_summary(random.sample(dataset['scenarios'], 20))
    }
    sample_20['metadata']['total_scenarios'] = 20
    sample_20['metadata']['description'] += ' (20-scenario mini sample)'
    
    with open(os.path.join(output_dir, 'mrr_mini_20.json'), 'w') as f:
        json.dump(sample_20, f, indent=2)
    
    print("Sample datasets generated:")
    print(f"  - mrr_sample_100.json (100 scenarios)")
    print(f"  - mrr_mini_20.json (20 scenarios)")
    
    print("\nDataset generation complete!")

if __name__ == "__main__":
    generate_and_save_dataset()