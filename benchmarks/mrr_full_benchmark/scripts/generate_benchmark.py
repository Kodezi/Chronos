#!/usr/bin/env python3
"""
Generate the complete Kodezi Chronos MRR Benchmark with 5000 bug cases.
This creates realistic debugging scenarios with scattered context.
"""

import json
import os
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple


class BugGenerator:
    """Generate realistic bug scenarios for the MRR benchmark"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.bug_counter = 0
        
        # Templates for different bug types
        self.syntax_templates = self._load_syntax_templates()
        self.logic_templates = self._load_logic_templates()
        self.concurrency_templates = self._load_concurrency_templates()
        self.memory_templates = self._load_memory_templates()
        self.api_templates = self._load_api_templates()
        self.performance_templates = self._load_performance_templates()
        
    def generate_all_bugs(self):
        """Generate all 5000 bug files"""
        print("Starting MRR Benchmark generation...")
        
        # Generate each category
        categories = [
            ("syntax_errors", 500, self.generate_syntax_error),
            ("logic_errors", 1200, self.generate_logic_error),
            ("concurrency_issues", 800, self.generate_concurrency_bug),
            ("memory_issues", 600, self.generate_memory_bug),
            ("api_misuse", 900, self.generate_api_bug),
            ("performance_bugs", 400, self.generate_performance_bug),
            ("cross_category", 600, self.generate_cross_category_bug)
        ]
        
        for category_name, count, generator_func in categories:
            print(f"\nGenerating {count} {category_name}...")
            category_path = self.base_path / category_name
            category_path.mkdir(exist_ok=True)
            
            for i in range(count):
                bug_id = f"mrr_{category_name}_{i+1:04d}"
                bug_data = generator_func(bug_id, category_name)
                
                # Save bug file
                file_path = category_path / f"{bug_id}.json"
                with open(file_path, 'w') as f:
                    json.dump(bug_data, f, indent=2)
                
                if (i + 1) % 100 == 0:
                    print(f"  Generated {i + 1}/{count} {category_name}")
            
            print(f"✓ Completed {category_name}")
        
        print("\n✓ Generated all 5000 bug files!")
        self._create_summary_file()
    
    def generate_syntax_error(self, bug_id: str, category: str) -> Dict[str, Any]:
        """Generate a syntax error bug"""
        languages = ["python", "javascript", "java"]
        language = random.choice(languages)
        difficulty = random.choice(["easy", "medium", "hard"])
        
        # Language-specific syntax errors
        if language == "python":
            error_types = [
                ("missing_colon", "SyntaxError: invalid syntax", "Missing colon after if/for/while/def"),
                ("indentation", "IndentationError: unexpected indent", "Incorrect indentation"),
                ("missing_bracket", "SyntaxError: unexpected EOF while parsing", "Missing closing bracket"),
                ("invalid_syntax", "SyntaxError: invalid syntax", "Invalid operator or keyword usage")
            ]
        elif language == "javascript":
            error_types = [
                ("missing_brace", "SyntaxError: Unexpected end of input", "Missing closing brace"),
                ("missing_semicolon", "SyntaxError: Unexpected identifier", "Missing semicolon"),
                ("invalid_token", "SyntaxError: Unexpected token", "Invalid character or operator"),
                ("missing_paren", "SyntaxError: missing ) after argument list", "Missing parenthesis")
            ]
        else:  # java
            error_types = [
                ("missing_semicolon", "error: ';' expected", "Missing semicolon"),
                ("unclosed_string", "error: unclosed string literal", "Missing closing quote"),
                ("illegal_start", "error: illegal start of expression", "Invalid expression syntax"),
                ("missing_brace", "error: reached end of file while parsing", "Missing closing brace")
            ]
        
        error_type, error_msg, description = random.choice(error_types)
        
        # Generate scattered context
        scattered_files = self._generate_scattered_context(bug_id, 10, 20)
        
        return {
            "bug_id": bug_id,
            "category": category,
            "subcategory": error_type,
            "difficulty": difficulty,
            "language": language,
            "repository": self._generate_repo_info(difficulty),
            "description": f"{description} causing {error_msg}",
            "symptoms": [
                error_msg,
                f"Build fails with syntax error",
                f"IDE shows red underline at line {random.randint(10, 200)}"
            ],
            "error_location": {
                "file": scattered_files[0]["file_path"],
                "line": random.randint(10, 200),
                "column": random.randint(1, 80)
            },
            "scattered_context": scattered_files,
            "temporal_info": self._generate_temporal_info(),
            "ground_truth": {
                "root_cause": description,
                "fix_type": "syntax_correction",
                "files_modified": 1,
                "fix_description": f"Add missing {error_type.replace('_', ' ')}",
                "test_command": f"pytest tests/" if language == "python" else "npm test"
            },
            "evaluation_criteria": {
                "must_find_files": [scattered_files[0]["file_path"]],
                "should_find_files": [f["file_path"] for f in scattered_files[1:3]],
                "test_must_pass": True,
                "no_regressions": True,
                "time_limit_seconds": 300
            }
        }
    
    def generate_logic_error(self, bug_id: str, category: str) -> Dict[str, Any]:
        """Generate a logic error bug"""
        languages = ["python", "javascript", "java"]
        language = random.choice(languages)
        difficulty = random.choice(["easy"] * 2 + ["medium"] * 3 + ["hard"])
        
        logic_errors = [
            {
                "type": "off_by_one",
                "description": "Off-by-one error in loop boundary",
                "symptoms": ["Last element not processed", "Array index out of bounds"],
                "fix": "Change loop condition from < to <="
            },
            {
                "type": "incorrect_operator",
                "description": "Wrong comparison operator used",
                "symptoms": ["Incorrect filtering results", "Boundary conditions fail"],
                "fix": "Change operator (e.g., > to >=, == to !=)"
            },
            {
                "type": "wrong_variable",
                "description": "Using wrong variable in calculation",
                "symptoms": ["Incorrect computation results", "Unit tests fail"],
                "fix": "Use correct variable name"
            },
            {
                "type": "missing_condition",
                "description": "Missing edge case handling",
                "symptoms": ["Fails for empty input", "Null/undefined errors"],
                "fix": "Add condition to handle edge case"
            },
            {
                "type": "incorrect_order",
                "description": "Operations performed in wrong order",
                "symptoms": ["Incorrect results", "Precedence issues"],
                "fix": "Reorder operations"
            }
        ]
        
        error_info = random.choice(logic_errors)
        scattered_files = self._generate_scattered_context(bug_id, 15, 30)
        
        return {
            "bug_id": bug_id,
            "category": category,
            "subcategory": error_info["type"],
            "difficulty": difficulty,
            "language": language,
            "repository": self._generate_repo_info(difficulty),
            "description": error_info["description"],
            "symptoms": error_info["symptoms"] + [
                f"Test '{self._generate_test_name()}' fails",
                "Incorrect output for certain inputs"
            ],
            "error_location": {
                "file": scattered_files[0]["file_path"],
                "function": self._generate_function_name(),
                "approximate_line": random.randint(50, 300)
            },
            "scattered_context": scattered_files,
            "temporal_info": self._generate_temporal_info(),
            "test_data": {
                "failing_input": self._generate_test_input(language),
                "expected_output": self._generate_expected_output(language),
                "actual_output": self._generate_actual_output(language)
            },
            "ground_truth": {
                "root_cause": error_info["description"],
                "fix_type": "logic_correction",
                "fix_description": error_info["fix"],
                "files_modified": 1,
                "complexity": "low" if difficulty == "easy" else "medium"
            },
            "evaluation_criteria": {
                "must_find_files": [scattered_files[0]["file_path"]],
                "should_find_files": [f["file_path"] for f in scattered_files[1:5]],
                "test_must_pass": True,
                "preserve_functionality": True
            }
        }
    
    def generate_concurrency_bug(self, bug_id: str, category: str) -> Dict[str, Any]:
        """Generate a concurrency bug"""
        languages = ["python", "java", "javascript"]
        language = random.choice(languages)
        difficulty = random.choice(["medium", "hard", "hard"])  # Concurrency is usually harder
        
        concurrency_bugs = [
            {
                "type": "race_condition",
                "description": "Race condition in shared resource access",
                "symptoms": ["Intermittent failures", "Data corruption under load"],
                "fix": "Add proper synchronization"
            },
            {
                "type": "deadlock",
                "description": "Deadlock between multiple threads",
                "symptoms": ["System hangs", "Threads waiting indefinitely"],
                "fix": "Fix lock ordering"
            },
            {
                "type": "missing_synchronization",
                "description": "Missing synchronization on shared data",
                "symptoms": ["Inconsistent state", "Lost updates"],
                "fix": "Add mutex/lock"
            },
            {
                "type": "atomicity_violation",
                "description": "Non-atomic operation on shared variable",
                "symptoms": ["Counter incorrect under concurrency", "State corruption"],
                "fix": "Use atomic operations"
            }
        ]
        
        bug_info = random.choice(concurrency_bugs)
        scattered_files = self._generate_scattered_context(bug_id, 20, 40)
        
        return {
            "bug_id": bug_id,
            "category": category,
            "subcategory": bug_info["type"],
            "difficulty": difficulty,
            "language": language,
            "repository": self._generate_repo_info(difficulty),
            "description": bug_info["description"],
            "symptoms": bug_info["symptoms"] + [
                "Only occurs under high load",
                f"Fails in {random.randint(1, 10)}% of runs"
            ],
            "concurrency_details": {
                "threads_involved": random.randint(2, 5),
                "shared_resources": self._generate_resource_names(),
                "synchronization_primitives": ["mutex", "semaphore", "lock"],
                "failure_rate": f"{random.randint(1, 30)}%"
            },
            "scattered_context": scattered_files,
            "temporal_info": self._generate_temporal_info(),
            "ground_truth": {
                "root_cause": bug_info["description"],
                "fix_type": "synchronization",
                "fix_description": bug_info["fix"],
                "files_modified": random.randint(2, 4),
                "requires_refactoring": difficulty == "hard"
            },
            "reproduction": {
                "min_threads": random.randint(10, 50),
                "iterations": random.randint(1000, 10000),
                "timing_sensitive": True
            },
            "evaluation_criteria": {
                "must_find_files": [f["file_path"] for f in scattered_files[:3]],
                "thread_safety_required": True,
                "performance_impact": "minimal"
            }
        }
    
    def generate_memory_bug(self, bug_id: str, category: str) -> Dict[str, Any]:
        """Generate a memory-related bug"""
        languages = ["javascript", "java", "python"]
        language = random.choice(languages)
        difficulty = random.choice(["easy", "medium", "medium", "hard"])
        
        memory_bugs = {
            "javascript": [
                {
                    "type": "memory_leak",
                    "description": "Event listeners not removed causing memory leak",
                    "symptoms": ["Memory usage grows over time", "Browser becomes slow"],
                    "fix": "Remove event listeners on cleanup"
                },
                {
                    "type": "circular_reference",
                    "description": "Circular references preventing garbage collection",
                    "symptoms": ["Objects not garbage collected", "Memory usage high"],
                    "fix": "Break circular references"
                }
            ],
            "java": [
                {
                    "type": "null_pointer",
                    "description": "NullPointerException in method call",
                    "symptoms": ["NPE thrown at runtime", "Application crashes"],
                    "fix": "Add null check before access"
                },
                {
                    "type": "resource_leak",
                    "description": "Resources not closed properly",
                    "symptoms": ["File handles exhausted", "Database connections leak"],
                    "fix": "Use try-with-resources or finally block"
                }
            ],
            "python": [
                {
                    "type": "reference_leak",
                    "description": "Unintended references keeping objects alive",
                    "symptoms": ["Memory not freed", "Slow garbage collection"],
                    "fix": "Clear references explicitly"
                },
                {
                    "type": "attribute_error",
                    "description": "AttributeError on None object",
                    "symptoms": ["'NoneType' has no attribute X", "Crashes on edge cases"],
                    "fix": "Add proper None checking"
                }
            ]
        }
        
        bug_info = random.choice(memory_bugs[language])
        scattered_files = self._generate_scattered_context(bug_id, 15, 35)
        
        return {
            "bug_id": bug_id,
            "category": category,
            "subcategory": bug_info["type"],
            "difficulty": difficulty,
            "language": language,
            "repository": self._generate_repo_info(difficulty),
            "description": bug_info["description"],
            "symptoms": bug_info["symptoms"],
            "memory_profile": {
                "initial_memory_mb": random.randint(50, 200),
                "leak_rate_mb_per_hour": random.randint(10, 100),
                "crash_threshold_mb": random.randint(1000, 4000)
            },
            "scattered_context": scattered_files,
            "temporal_info": self._generate_temporal_info(),
            "ground_truth": {
                "root_cause": bug_info["description"],
                "fix_type": "memory_management",
                "fix_description": bug_info["fix"],
                "files_modified": random.randint(1, 3)
            },
            "evaluation_criteria": {
                "memory_leak_fixed": True,
                "no_performance_regression": True,
                "backward_compatible": True
            }
        }
    
    def generate_api_bug(self, bug_id: str, category: str) -> Dict[str, Any]:
        """Generate an API misuse bug"""
        languages = ["python", "javascript", "java"]
        language = random.choice(languages)
        difficulty = random.choice(["easy", "medium", "medium", "hard"])
        
        api_bugs = [
            {
                "type": "deprecated_method",
                "description": "Using deprecated API method",
                "symptoms": ["Deprecation warnings", "Method will be removed in next version"],
                "fix": "Migrate to new API"
            },
            {
                "type": "incorrect_parameters",
                "description": "Wrong parameter order or type",
                "symptoms": ["API returns error", "Unexpected behavior"],
                "fix": "Fix parameter usage"
            },
            {
                "type": "missing_error_handling",
                "description": "No error handling for API failures",
                "symptoms": ["Unhandled exceptions", "App crashes on API errors"],
                "fix": "Add proper error handling"
            },
            {
                "type": "api_version_mismatch",
                "description": "Code expects different API version",
                "symptoms": ["Method not found", "Different response format"],
                "fix": "Update to match API version"
            },
            {
                "type": "rate_limit_violation",
                "description": "Exceeding API rate limits",
                "symptoms": ["429 errors", "Requests blocked"],
                "fix": "Implement rate limiting"
            }
        ]
        
        bug_info = random.choice(api_bugs)
        scattered_files = self._generate_scattered_context(bug_id, 20, 45)
        
        # Generate API-specific context
        api_name = random.choice(["stripe", "aws-sdk", "googleapis", "twilio", "sendgrid"])
        old_version = f"{random.randint(1,3)}.{random.randint(0,20)}.{random.randint(0,30)}"
        new_version = f"{random.randint(4,6)}.{random.randint(0,20)}.{random.randint(0,30)}"
        
        return {
            "bug_id": bug_id,
            "category": category,
            "subcategory": bug_info["type"],
            "difficulty": difficulty,
            "language": language,
            "repository": self._generate_repo_info(difficulty),
            "description": bug_info["description"],
            "symptoms": bug_info["symptoms"],
            "api_details": {
                "api_name": api_name,
                "old_version": old_version,
                "new_version": new_version,
                "breaking_changes": bug_info["type"] in ["deprecated_method", "api_version_mismatch"]
            },
            "scattered_context": scattered_files,
            "temporal_info": self._generate_temporal_info(),
            "migration_info": {
                "documentation_url": f"https://docs.{api_name}.com/migration/{old_version}-to-{new_version}",
                "affected_methods": self._generate_method_names(3, 6),
                "estimated_effort": f"{random.randint(2, 8)} hours"
            },
            "ground_truth": {
                "root_cause": bug_info["description"],
                "fix_type": "api_migration",
                "fix_description": bug_info["fix"],
                "files_modified": random.randint(3, 8),
                "requires_testing": True
            },
            "evaluation_criteria": {
                "api_calls_updated": True,
                "tests_updated": True,
                "backward_compatibility_handled": difficulty == "hard"
            }
        }
    
    def generate_performance_bug(self, bug_id: str, category: str) -> Dict[str, Any]:
        """Generate a performance bug"""
        languages = ["python", "javascript", "java"]
        language = random.choice(languages)
        difficulty = random.choice(["medium", "hard", "hard"])  # Performance bugs are usually complex
        
        performance_bugs = [
            {
                "type": "n_plus_one_query",
                "description": "N+1 query problem in database access",
                "symptoms": ["Slow page load", "Database CPU high", "Many similar queries"],
                "fix": "Use eager loading or batch queries"
            },
            {
                "type": "inefficient_algorithm",
                "description": "O(n²) algorithm where O(n) is possible",
                "symptoms": ["Exponential slowdown with data size", "CPU usage high"],
                "fix": "Use more efficient algorithm"
            },
            {
                "type": "memory_bloat",
                "description": "Loading entire dataset into memory",
                "symptoms": ["High memory usage", "OOM on large datasets"],
                "fix": "Use streaming or pagination"
            },
            {
                "type": "blocking_io",
                "description": "Synchronous I/O blocking event loop",
                "symptoms": ["UI freezes", "Poor responsiveness"],
                "fix": "Use async I/O"
            },
            {
                "type": "missing_cache",
                "description": "Repeatedly computing expensive operations",
                "symptoms": ["Same calculations repeated", "CPU waste"],
                "fix": "Add caching layer"
            }
        ]
        
        bug_info = random.choice(performance_bugs)
        scattered_files = self._generate_scattered_context(bug_id, 25, 50)
        
        return {
            "bug_id": bug_id,
            "category": category,
            "subcategory": bug_info["type"],
            "difficulty": difficulty,
            "language": language,
            "repository": self._generate_repo_info(difficulty),
            "description": bug_info["description"],
            "symptoms": bug_info["symptoms"],
            "performance_metrics": {
                "baseline_response_time_ms": random.randint(50, 200),
                "degraded_response_time_ms": random.randint(2000, 10000),
                "data_size_threshold": random.randint(1000, 10000),
                "cpu_usage_percent": random.randint(80, 100),
                "memory_usage_mb": random.randint(500, 4000)
            },
            "scattered_context": scattered_files,
            "temporal_info": self._generate_temporal_info(),
            "profiling_data": {
                "hotspot_methods": self._generate_method_names(3, 5),
                "bottleneck_operations": ["database_query", "serialization", "network_io"],
                "scaling_factor": f"O(n^{random.randint(2, 3)})"
            },
            "ground_truth": {
                "root_cause": bug_info["description"],
                "fix_type": "performance_optimization",
                "fix_description": bug_info["fix"],
                "files_modified": random.randint(2, 6),
                "performance_improvement": f"{random.randint(70, 95)}%"
            },
            "evaluation_criteria": {
                "performance_improved": True,
                "functionality_preserved": True,
                "scalability_tested": True
            }
        }
    
    def generate_cross_category_bug(self, bug_id: str, category: str) -> Dict[str, Any]:
        """Generate a complex bug spanning multiple categories"""
        languages = ["python", "javascript", "java"]
        language = random.choice(languages)
        difficulty = "hard"  # Cross-category bugs are always complex
        
        # Combine multiple bug types
        categories_combo = random.choice([
            ["memory", "concurrency"],
            ["api", "performance"],
            ["logic", "memory"],
            ["concurrency", "performance"],
            ["api", "concurrency"]
        ])
        
        scattered_files = self._generate_scattered_context(bug_id, 30, 50)
        
        bug_description = {
            ("memory", "concurrency"): {
                "description": "Memory leak in concurrent connection pool",
                "symptoms": ["Memory grows under load", "Connections not released", "OOM after days"],
                "root_cause": "Race condition in connection cleanup prevents garbage collection"
            },
            ("api", "performance"): {
                "description": "API migration causes performance regression",
                "symptoms": ["10x slower after upgrade", "Timeouts on large requests"],
                "root_cause": "New API version removed batch endpoints, causing N+1 requests"
            },
            ("logic", "memory"): {
                "description": "Logic error causes unbounded cache growth",
                "symptoms": ["Memory usage increases", "Cache hit rate decreases"],
                "root_cause": "Cache key generation bug creates unique keys for same data"
            },
            ("concurrency", "performance"): {
                "description": "Lock contention causes performance degradation",
                "symptoms": ["Response times spike under load", "CPU mostly idle"],
                "root_cause": "Overly broad lock scope creates bottleneck"
            },
            ("api", "concurrency"): {
                "description": "API client not thread-safe causing data corruption",
                "symptoms": ["Intermittent wrong responses", "Authentication failures"],
                "root_cause": "Shared client instance mutates state without synchronization"
            }
        }
        
        combo_key = tuple(categories_combo)
        bug_info = bug_description.get(combo_key, bug_description[("memory", "concurrency")])
        
        return {
            "bug_id": bug_id,
            "category": category,
            "subcategories": categories_combo,
            "difficulty": difficulty,
            "language": language,
            "repository": self._generate_repo_info(difficulty),
            "description": bug_info["description"],
            "symptoms": bug_info["symptoms"],
            "complexity_factors": {
                "interacting_components": random.randint(4, 8),
                "abstraction_layers": random.randint(3, 5),
                "temporal_spread_months": random.randint(6, 12),
                "developers_involved": random.randint(3, 7)
            },
            "scattered_context": scattered_files,
            "temporal_info": self._generate_temporal_info(min_months=6),
            "interaction_pattern": {
                "trigger_sequence": self._generate_trigger_sequence(),
                "failure_conditions": self._generate_failure_conditions(),
                "environmental_factors": ["load", "data_size", "concurrency_level"]
            },
            "ground_truth": {
                "root_cause": bug_info["root_cause"],
                "fix_type": "multi_component",
                "fix_complexity": "high",
                "files_modified": random.randint(5, 12),
                "requires_architecture_change": random.choice([True, False]),
                "fix_phases": [
                    "Immediate mitigation",
                    "Root cause fix",
                    "Preventive measures"
                ]
            },
            "evaluation_criteria": {
                "all_symptoms_resolved": True,
                "no_new_issues_introduced": True,
                "performance_acceptable": True,
                "thread_safe": True,
                "properly_tested": True
            }
        }
    
    # Helper methods
    def _generate_scattered_context(self, bug_id: str, min_files: int, max_files: int) -> List[Dict[str, Any]]:
        """Generate scattered context files with different relevance levels"""
        num_files = random.randint(min_files, max_files)
        files = []
        
        # Define file patterns for different components
        component_patterns = [
            ("core", ["service", "handler", "processor", "manager"]),
            ("api", ["controller", "endpoint", "route", "resource"]),
            ("data", ["model", "entity", "repository", "dao"]),
            ("utils", ["helper", "util", "common", "shared"]),
            ("config", ["config", "settings", "constants", "env"]),
            ("test", ["test", "spec", "fixture", "mock"])
        ]
        
        for i in range(num_files):
            component, patterns = random.choice(component_patterns)
            pattern = random.choice(patterns)
            
            relevance = "critical" if i < 2 else "high" if i < 5 else "medium" if i < 10 else "low"
            
            file_info = {
                "file_path": f"src/{component}/{pattern}_{random.randint(1, 99)}.{self._get_extension(random.choice(['python', 'javascript', 'java']))}",
                "relevance": relevance,
                "relationship": random.choice(["imports", "calls", "extends", "implements", "uses", "tests"]),
                "key_elements": self._generate_key_elements(),
                "last_modified": self._generate_date_offset(random.randint(1, 180))
            }
            
            if relevance in ["critical", "high"]:
                file_info["specific_issue"] = self._generate_specific_issue()
            
            files.append(file_info)
        
        return files
    
    def _generate_repo_info(self, difficulty: str) -> Dict[str, Any]:
        """Generate repository information based on difficulty"""
        if difficulty == "easy":
            size = random.choice(["small", "small", "medium"])
        elif difficulty == "medium":
            size = random.choice(["small", "medium", "medium", "large"])
        else:
            size = random.choice(["medium", "large", "large", "enterprise"])
        
        size_specs = {
            "small": {"files": random.randint(50, 200), "loc": random.randint(5000, 10000)},
            "medium": {"files": random.randint(200, 1000), "loc": random.randint(10000, 100000)},
            "large": {"files": random.randint(1000, 5000), "loc": random.randint(100000, 1000000)},
            "enterprise": {"files": random.randint(5000, 20000), "loc": random.randint(1000000, 5000000)}
        }
        
        specs = size_specs[size]
        
        return {
            "size_category": size,
            "files": specs["files"],
            "loc": specs["loc"],
            "age_months": random.randint(6, 60),
            "contributors": random.randint(1, 50),
            "languages": self._generate_language_distribution(),
            "frameworks": self._generate_frameworks()
        }
    
    def _generate_temporal_info(self, min_months: int = 3) -> Dict[str, Any]:
        """Generate temporal information for bug context"""
        return {
            "bug_introduced": self._generate_date_offset(random.randint(min_months * 30, 365)),
            "last_modified": self._generate_date_offset(random.randint(1, 30)),
            "refactoring_events": random.randint(0, 5),
            "related_commits": self._generate_commit_hashes(random.randint(3, 10)),
            "temporal_spread_days": random.randint(min_months * 30, 365)
        }
    
    def _generate_test_name(self) -> str:
        """Generate a realistic test name"""
        prefixes = ["test", "should", "verify", "ensure", "check"]
        operations = ["create", "update", "delete", "process", "validate", "calculate", "handle"]
        subjects = ["user", "order", "payment", "data", "request", "response", "item"]
        conditions = ["with_valid_input", "with_invalid_data", "when_empty", "under_load"]
        
        return f"{random.choice(prefixes)}_{random.choice(operations)}_{random.choice(subjects)}_{random.choice(conditions)}"
    
    def _generate_function_name(self) -> str:
        """Generate a function name"""
        verbs = ["get", "set", "process", "handle", "calculate", "validate", "update", "create"]
        nouns = ["data", "user", "order", "result", "response", "request", "item", "value"]
        return f"{random.choice(verbs)}{random.choice(nouns).capitalize()}"
    
    def _generate_method_names(self, min_count: int, max_count: int) -> List[str]:
        """Generate multiple method names"""
        count = random.randint(min_count, max_count)
        return [self._generate_function_name() for _ in range(count)]
    
    def _generate_resource_names(self) -> List[str]:
        """Generate resource names for concurrency bugs"""
        resources = ["connection_pool", "cache", "user_sessions", "file_handles", "database_locks"]
        return random.sample(resources, random.randint(2, 4))
    
    def _generate_test_input(self, language: str) -> Any:
        """Generate test input based on language"""
        if language == "python":
            return random.choice([
                "[1, 2, 3, 4, 5]",
                "{'key': 'value', 'count': 10}",
                "'test_string_input'",
                "42"
            ])
        elif language == "javascript":
            return random.choice([
                "[1, 2, 3, 4, 5]",
                "{key: 'value', count: 10}",
                "'test string input'",
                "null"
            ])
        else:  # java
            return random.choice([
                "Arrays.asList(1, 2, 3, 4, 5)",
                "new HashMap<String, Object>()",
                '"testInput"',
                "null"
            ])
    
    def _generate_expected_output(self, language: str) -> Any:
        """Generate expected output"""
        return random.choice(["[2, 4, 6, 8, 10]", "15", "true", "{'status': 'success'}", "null"])
    
    def _generate_actual_output(self, language: str) -> Any:
        """Generate actual (incorrect) output"""
        return random.choice(["[2, 4, 6, 8]", "14", "false", "{'status': 'error'}", "NullPointerException"])
    
    def _generate_commit_hashes(self, count: int) -> List[str]:
        """Generate realistic commit hashes"""
        return [hashlib.md5(f"{random.randint(0, 999999)}".encode()).hexdigest()[:8] for _ in range(count)]
    
    def _generate_date_offset(self, days_ago: int) -> str:
        """Generate a date string for given days ago"""
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d")
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        return {"python": "py", "javascript": "js", "java": "java"}[language]
    
    def _generate_key_elements(self) -> List[str]:
        """Generate key code elements in a file"""
        elements = ["class", "function", "variable", "import", "constant", "interface", "enum"]
        return random.sample(elements, random.randint(2, 4))
    
    def _generate_specific_issue(self) -> str:
        """Generate specific issue description"""
        issues = [
            "Contains the failing assertion",
            "Performs the problematic operation",
            "Defines the data structure",
            "Handles the edge case incorrectly",
            "Missing error handling",
            "Incorrect boundary check"
        ]
        return random.choice(issues)
    
    def _generate_language_distribution(self) -> Dict[str, float]:
        """Generate language distribution for repository"""
        primary = random.choice(["python", "javascript", "java"])
        secondary = random.choice([l for l in ["python", "javascript", "java"] if l != primary])
        
        primary_pct = random.randint(60, 85)
        secondary_pct = random.randint(10, 30)
        other_pct = 100 - primary_pct - secondary_pct
        
        return {
            primary: primary_pct / 100,
            secondary: secondary_pct / 100,
            "other": other_pct / 100
        }
    
    def _generate_frameworks(self) -> List[str]:
        """Generate framework list"""
        frameworks_by_language = {
            "python": ["django", "flask", "fastapi", "pytest", "sqlalchemy"],
            "javascript": ["react", "express", "jest", "webpack", "mongoose"],
            "java": ["spring", "junit", "hibernate", "maven", "jackson"]
        }
        
        language = random.choice(list(frameworks_by_language.keys()))
        return random.sample(frameworks_by_language[language], random.randint(2, 4))
    
    def _generate_trigger_sequence(self) -> List[str]:
        """Generate sequence of actions that trigger the bug"""
        actions = [
            "User authenticates",
            "Load increases to 100 requests/second",
            "Cache expires",
            "Database connection drops",
            "Memory usage reaches 80%",
            "Concurrent requests arrive",
            "Large dataset is processed"
        ]
        return random.sample(actions, random.randint(3, 5))
    
    def _generate_failure_conditions(self) -> List[str]:
        """Generate conditions under which bug manifests"""
        conditions = [
            "High concurrency (>50 threads)",
            "Large data size (>10MB)",
            "Slow network conditions",
            "Limited memory (<2GB)",
            "Specific timezone (UTC+X)",
            "After running for >24 hours"
        ]
        return random.sample(conditions, random.randint(2, 4))
    
    def _load_syntax_templates(self) -> List[Dict]:
        """Load syntax error templates"""
        return []  # Templates would be loaded from files in production
    
    def _load_logic_templates(self) -> List[Dict]:
        """Load logic error templates"""
        return []
    
    def _load_concurrency_templates(self) -> List[Dict]:
        """Load concurrency templates"""
        return []
    
    def _load_memory_templates(self) -> List[Dict]:
        """Load memory bug templates"""
        return []
    
    def _load_api_templates(self) -> List[Dict]:
        """Load API bug templates"""
        return []
    
    def _load_performance_templates(self) -> List[Dict]:
        """Load performance bug templates"""
        return []
    
    def _create_summary_file(self):
        """Create a summary file of all generated bugs"""
        summary = {
            "total_bugs": 5000,
            "generation_date": datetime.now().isoformat(),
            "categories": {
                "syntax_errors": 500,
                "logic_errors": 1200,
                "concurrency_issues": 800,
                "memory_issues": 600,
                "api_misuse": 900,
                "performance_bugs": 400,
                "cross_category": 600
            },
            "languages": {
                "python": 0,
                "javascript": 0,
                "java": 0
            },
            "difficulty_distribution": {
                "easy": 0,
                "medium": 0,
                "hard": 0
            }
        }
        
        # Count actual distributions
        for category in ["syntax_errors", "logic_errors", "concurrency_issues", 
                        "memory_issues", "api_misuse", "performance_bugs", "cross_category"]:
            category_path = self.base_path / category
            if category_path.exists():
                for bug_file in category_path.glob("*.json"):
                    with open(bug_file) as f:
                        bug_data = json.load(f)
                        summary["languages"][bug_data["language"]] += 1
                        if "difficulty" in bug_data:
                            summary["difficulty_distribution"][bug_data["difficulty"]] += 1
        
        summary_path = self.base_path / "BENCHMARK_SUMMARY.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nSummary saved to {summary_path}")


def main():
    """Main function to generate the benchmark"""
    base_path = "/Users/ishraqkhan/Chronosss/Chronos/benchmarks/mrr_full_benchmark"
    generator = BugGenerator(base_path)
    generator.generate_all_bugs()


if __name__ == "__main__":
    main()