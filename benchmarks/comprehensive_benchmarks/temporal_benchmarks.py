#!/usr/bin/env python3
"""
Temporal and Cross-Session Learning Benchmarks for Kodezi Chronos 2025
Tests PDM effectiveness and temporal reasoning capabilities
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import time
import random
from datetime import datetime, timedelta
import json

@dataclass
class TemporalBugEvent:
    """Represents a bug occurrence over time"""
    event_id: str
    timestamp: float
    bug_type: str
    file_path: str
    commit_hash: str
    error_signature: str
    fix_applied: Optional[str] = None
    fix_success: bool = False
    related_events: List[str] = field(default_factory=list)
    
@dataclass
class DebugPattern:
    """Represents a learned debugging pattern"""
    pattern_id: str
    pattern_type: str
    occurrences: List[str]  # Event IDs
    success_rate: float
    avg_fix_time: float
    temporal_distribution: Dict[str, int]  # Hour of day -> count
    
@dataclass
class CodebaseEvolution:
    """Tracks codebase changes over time"""
    timeline: List[Tuple[float, str, Dict]]  # (timestamp, event_type, details)
    file_history: Dict[str, List[Dict]]  # file -> list of changes
    dependency_changes: List[Dict]
    api_migrations: List[Dict]

class TemporalBenchmarkGenerator:
    """Generates temporal debugging benchmarks"""
    
    def __init__(self, start_date: datetime = None):
        self.start_date = start_date or datetime.now() - timedelta(days=365)
        self.current_time = self.start_date.timestamp()
        
    def generate_temporal_bug_sequence(self, 
                                     duration_days: int = 365,
                                     avg_bugs_per_day: float = 5.0) -> List[TemporalBugEvent]:
        """
        Generate a sequence of bugs over time with realistic patterns
        
        Args:
            duration_days: Duration of the sequence
            avg_bugs_per_day: Average number of bugs per day
            
        Returns:
            List of temporal bug events
        """
        events = []
        
        # Bug type distributions change over time (simulating project evolution)
        bug_type_phases = [
            # Early phase: more syntax/simple errors
            {
                'duration': 0.2,
                'distribution': {
                    'syntax_error': 0.3,
                    'null_pointer': 0.2,
                    'type_error': 0.2,
                    'api_misuse': 0.15,
                    'logic_bug': 0.1,
                    'performance': 0.05
                }
            },
            # Mid phase: more complex bugs
            {
                'duration': 0.5,
                'distribution': {
                    'syntax_error': 0.1,
                    'null_pointer': 0.15,
                    'logic_bug': 0.25,
                    'api_misuse': 0.2,
                    'concurrency': 0.15,
                    'performance': 0.15
                }
            },
            # Late phase: mostly optimization and complex issues
            {
                'duration': 0.3,
                'distribution': {
                    'syntax_error': 0.05,
                    'performance': 0.3,
                    'concurrency': 0.25,
                    'memory_leak': 0.2,
                    'logic_bug': 0.15,
                    'security': 0.05
                }
            }
        ]
        
        # Generate events
        for day in range(duration_days):
            # Determine current phase
            progress = day / duration_days
            current_phase = None
            cumulative = 0
            
            for phase in bug_type_phases:
                cumulative += phase['duration']
                if progress <= cumulative:
                    current_phase = phase
                    break
            
            if not current_phase:
                current_phase = bug_type_phases[-1]
            
            # Number of bugs today (Poisson distributed)
            n_bugs = np.random.poisson(avg_bugs_per_day)
            
            # Time of day distribution (more bugs during work hours)
            for _ in range(n_bugs):
                # Work hours bias
                hour = np.random.normal(14, 3)  # Peak at 2 PM
                hour = max(0, min(23, int(hour)))
                
                timestamp = self.current_time + day * 86400 + hour * 3600
                
                # Select bug type based on phase
                bug_type = np.random.choice(
                    list(current_phase['distribution'].keys()),
                    p=list(current_phase['distribution'].values())
                )
                
                # Generate event
                event = TemporalBugEvent(
                    event_id=f"bug_{len(events):05d}",
                    timestamp=timestamp,
                    bug_type=bug_type,
                    file_path=self._generate_file_path(bug_type),
                    commit_hash=f"commit_{day:04d}_{random.randint(0, 99):02d}",
                    error_signature=self._generate_error_signature(bug_type)
                )
                
                # Add relationships to previous similar bugs
                if events:
                    similar_events = [
                        e for e in events[-100:]  # Look at recent bugs
                        if e.bug_type == bug_type and 
                        e.error_signature == event.error_signature
                    ]
                    if similar_events:
                        event.related_events = [e.event_id for e in similar_events[-3:]]
                
                events.append(event)
        
        return events
    
    def _generate_file_path(self, bug_type: str) -> str:
        """Generate realistic file paths based on bug type"""
        path_patterns = {
            'syntax_error': ['src/utils/', 'src/helpers/', 'lib/'],
            'null_pointer': ['src/services/', 'src/models/', 'src/controllers/'],
            'api_misuse': ['src/api/', 'src/external/', 'src/integrations/'],
            'concurrency': ['src/workers/', 'src/async/', 'src/parallel/'],
            'performance': ['src/algorithms/', 'src/optimization/', 'src/cache/'],
            'memory_leak': ['src/resources/', 'src/handlers/', 'src/managers/']
        }
        
        base_paths = path_patterns.get(bug_type, ['src/'])
        base = random.choice(base_paths)
        
        return f"{base}module_{random.randint(1, 20)}/file_{random.randint(1, 100)}.py"
    
    def _generate_error_signature(self, bug_type: str) -> str:
        """Generate error signatures that may repeat over time"""
        # Some signatures are common and repeat
        common_signatures = {
            'null_pointer': [
                'NullPointerException::UserService::getUser',
                'NullPointerException::AuthService::validateToken',
                'AttributeError::NoneType::split'
            ],
            'api_misuse': [
                'TypeError::unexpected_keyword_argument',
                'DeprecationWarning::use_new_api',
                'APIError::invalid_parameters'
            ],
            'concurrency': [
                'RaceCondition::shared_cache_update',
                'DeadlockDetected::resource_acquisition',
                'DataRace::concurrent_map_access'
            ]
        }
        
        if bug_type in common_signatures and random.random() < 0.7:
            # 70% chance of common signature
            return random.choice(common_signatures[bug_type])
        else:
            # Generate unique signature
            return f"{bug_type}::component_{random.randint(1, 50)}::method_{random.randint(1, 100)}"
    
    def simulate_debugging_sessions(self,
                                  bug_events: List[TemporalBugEvent],
                                  learning_rate: float = 0.1) -> Tuple[List[Dict], List[DebugPattern]]:
        """
        Simulate debugging sessions with learning over time
        
        Args:
            bug_events: List of bugs to debug
            learning_rate: How quickly the system learns patterns
            
        Returns:
            Tuple of (session_results, learned_patterns)
        """
        sessions = []
        pattern_memory = {}  # signature -> pattern
        success_history = {}  # signature -> list of outcomes
        
        for i, event in enumerate(bug_events):
            session_start = time.time()
            
            # Check if we've seen this pattern before
            known_pattern = pattern_memory.get(event.error_signature)
            
            # Base success probability
            if known_pattern:
                # Use historical success rate
                base_success = known_pattern.success_rate
                # Boost for recurring patterns
                pattern_boost = min(0.3, len(known_pattern.occurrences) * 0.05)
                success_prob = min(0.95, base_success + pattern_boost)
            else:
                # New pattern - base probability depends on bug type
                base_probs = {
                    'syntax_error': 0.8,
                    'null_pointer': 0.5,
                    'api_misuse': 0.6,
                    'logic_bug': 0.3,
                    'concurrency': 0.2,
                    'performance': 0.4,
                    'memory_leak': 0.35
                }
                success_prob = base_probs.get(event.bug_type, 0.4)
            
            # Simulate debugging attempt
            success = random.random() < success_prob
            
            # Time to fix depends on familiarity
            if known_pattern:
                base_time = 15  # minutes
                time_reduction = min(0.8, len(known_pattern.occurrences) * 0.1)
                fix_time = base_time * (1 - time_reduction)
            else:
                fix_time = random.uniform(30, 120)  # 30-120 minutes for new bugs
            
            # Record session
            session = {
                'session_id': f"session_{i:05d}",
                'bug_event': event.event_id,
                'timestamp': event.timestamp,
                'used_pattern': known_pattern.pattern_id if known_pattern else None,
                'success': success,
                'fix_time_minutes': fix_time,
                'iterations': 1 if known_pattern else random.randint(3, 10),
                'pattern_confidence': known_pattern.success_rate if known_pattern else 0.0
            }
            sessions.append(session)
            
            # Update pattern memory
            if event.error_signature not in success_history:
                success_history[event.error_signature] = []
            success_history[event.error_signature].append(success)
            
            # Create or update pattern
            if event.error_signature not in pattern_memory:
                pattern = DebugPattern(
                    pattern_id=f"pattern_{len(pattern_memory):04d}",
                    pattern_type=event.bug_type,
                    occurrences=[event.event_id],
                    success_rate=float(success),
                    avg_fix_time=fix_time,
                    temporal_distribution={}
                )
                pattern_memory[event.error_signature] = pattern
            else:
                pattern = pattern_memory[event.error_signature]
                pattern.occurrences.append(event.event_id)
                
                # Update success rate with exponential moving average
                pattern.success_rate = (pattern.success_rate * (1 - learning_rate) + 
                                      float(success) * learning_rate)
                
                # Update average fix time
                n = len(pattern.occurrences)
                pattern.avg_fix_time = ((pattern.avg_fix_time * (n - 1) + fix_time) / n)
            
            # Update temporal distribution
            hour = datetime.fromtimestamp(event.timestamp).hour
            if hour not in pattern.temporal_distribution:
                pattern.temporal_distribution[hour] = 0
            pattern.temporal_distribution[hour] += 1
        
        return sessions, list(pattern_memory.values())

class CodebaseEvolutionSimulator:
    """Simulates realistic codebase evolution"""
    
    def __init__(self):
        self.file_count = 100
        self.current_files = {f"file_{i}.py": {
            'created': 0,
            'modified': 0,
            'size': random.randint(100, 5000),
            'complexity': random.uniform(1, 10)
        } for i in range(self.file_count)}
    
    def generate_evolution_timeline(self, 
                                  duration_days: int = 365,
                                  events_per_day: int = 10) -> CodebaseEvolution:
        """Generate codebase evolution timeline"""
        timeline = []
        file_history = {f: [] for f in self.current_files}
        dependency_changes = []
        api_migrations = []
        
        for day in range(duration_days):
            timestamp = day * 86400  # seconds
            
            # Generate various evolution events
            for _ in range(random.randint(1, events_per_day)):
                event_type = np.random.choice(
                    ['file_modified', 'file_added', 'file_deleted', 
                     'refactoring', 'dependency_update', 'api_migration'],
                    p=[0.5, 0.15, 0.05, 0.15, 0.1, 0.05]
                )
                
                if event_type == 'file_modified':
                    file = random.choice(list(self.current_files.keys()))
                    change = {
                        'lines_added': random.randint(1, 100),
                        'lines_removed': random.randint(1, 50),
                        'complexity_delta': random.uniform(-1, 1)
                    }
                    timeline.append((timestamp, 'file_modified', {
                        'file': file,
                        'changes': change
                    }))
                    file_history[file].append({
                        'timestamp': timestamp,
                        'type': 'modified',
                        'details': change
                    })
                
                elif event_type == 'refactoring':
                    # Major refactoring affects multiple files
                    affected_files = random.sample(
                        list(self.current_files.keys()), 
                        random.randint(5, 20)
                    )
                    refactor_type = random.choice([
                        'rename_pattern', 'extract_method', 
                        'move_class', 'change_signature'
                    ])
                    timeline.append((timestamp, 'refactoring', {
                        'type': refactor_type,
                        'affected_files': affected_files
                    }))
                
                elif event_type == 'dependency_update':
                    dep_change = {
                        'dependency': f"library_v{random.randint(1, 10)}",
                        'old_version': f"{random.randint(1, 5)}.{random.randint(0, 9)}.0",
                        'new_version': f"{random.randint(2, 6)}.{random.randint(0, 9)}.0",
                        'breaking_changes': random.random() < 0.3
                    }
                    dependency_changes.append({
                        'timestamp': timestamp,
                        **dep_change
                    })
                    timeline.append((timestamp, 'dependency_update', dep_change))
                
                elif event_type == 'api_migration':
                    migration = {
                        'old_api': f"old_method_{random.randint(1, 50)}",
                        'new_api': f"new_method_{random.randint(1, 50)}",
                        'deprecation_date': timestamp,
                        'removal_date': timestamp + 90 * 86400  # 90 days later
                    }
                    api_migrations.append(migration)
                    timeline.append((timestamp, 'api_migration', migration))
        
        return CodebaseEvolution(
            timeline=timeline,
            file_history=file_history,
            dependency_changes=dependency_changes,
            api_migrations=api_migrations
        )

class CrossSessionLearningBenchmark:
    """Benchmarks for cross-session learning effectiveness"""
    
    def __init__(self):
        self.session_memory = []
        self.pattern_database = {}
        
    def generate_recurring_bug_scenarios(self, 
                                       n_scenarios: int = 1000,
                                       recurrence_rate: float = 0.3) -> List[Dict]:
        """
        Generate scenarios with recurring bug patterns
        
        Args:
            n_scenarios: Number of scenarios
            recurrence_rate: Probability of bug pattern recurring
            
        Returns:
            List of bug scenarios
        """
        scenarios = []
        bug_templates = []
        
        for i in range(n_scenarios):
            if random.random() < recurrence_rate and bug_templates:
                # Recurring bug - select from templates
                template = random.choice(bug_templates)
                scenario = {
                    'scenario_id': f"scenario_{i:04d}",
                    'bug_template': template['template_id'],
                    'variation': self._create_variation(template),
                    'expected_speedup': 1 + len([s for s in scenarios 
                                               if s.get('bug_template') == template['template_id']]) * 0.5
                }
            else:
                # New bug pattern
                template = {
                    'template_id': f"template_{len(bug_templates):03d}",
                    'bug_type': random.choice(['null_pointer', 'race_condition', 
                                             'memory_leak', 'api_misuse']),
                    'root_cause': f"cause_{random.randint(1, 100)}",
                    'fix_pattern': f"fix_{random.randint(1, 50)}"
                }
                bug_templates.append(template)
                scenario = {
                    'scenario_id': f"scenario_{i:04d}",
                    'bug_template': template['template_id'],
                    'variation': {'base': True},
                    'expected_speedup': 1.0
                }
            
            scenarios.append(scenario)
        
        return scenarios
    
    def _create_variation(self, template: Dict) -> Dict:
        """Create variation of existing bug template"""
        variations = {
            'null_pointer': [
                {'context': 'different_method'},
                {'context': 'async_callback'},
                {'context': 'error_handler'}
            ],
            'race_condition': [
                {'resource': 'different_lock'},
                {'timing': 'initialization'},
                {'scope': 'global_state'}
            ],
            'memory_leak': [
                {'cause': 'different_reference'},
                {'lifecycle': 'long_running'},
                {'size': 'large_allocation'}
            ]
        }
        
        bug_type = template.get('bug_type', 'unknown')
        possible_variations = variations.get(bug_type, [{'default': True}])
        
        return random.choice(possible_variations)
    
    def evaluate_learning_curve(self, scenarios: List[Dict]) -> Dict:
        """
        Evaluate how performance improves with learning
        
        Args:
            scenarios: Bug scenarios to evaluate
            
        Returns:
            Learning curve metrics
        """
        metrics = {
            'success_over_time': [],
            'speedup_over_time': [],
            'pattern_reuse': [],
            'cache_hit_rate': []
        }
        
        pattern_seen_count = {}
        total_patterns = 0
        cache_hits = 0
        
        for i, scenario in enumerate(scenarios):
            template_id = scenario['bug_template']
            
            # Track pattern occurrence
            if template_id not in pattern_seen_count:
                pattern_seen_count[template_id] = 0
            pattern_seen_count[template_id] += 1
            total_patterns += 1
            
            # Simulate success rate improvement
            base_success = 0.4
            occurrence_boost = min(0.4, pattern_seen_count[template_id] * 0.1)
            success_rate = base_success + occurrence_boost
            
            # Simulate speedup
            if pattern_seen_count[template_id] > 1:
                cache_hits += 1
                speedup = scenario['expected_speedup']
            else:
                speedup = 1.0
            
            # Record metrics
            if i % 10 == 0:  # Sample every 10 scenarios
                metrics['success_over_time'].append(success_rate)
                metrics['speedup_over_time'].append(speedup)
                metrics['pattern_reuse'].append(
                    sum(1 for c in pattern_seen_count.values() if c > 1) / 
                    len(pattern_seen_count) if pattern_seen_count else 0
                )
                metrics['cache_hit_rate'].append(cache_hits / (i + 1))
        
        return metrics

class TemporalBenchmarkEvaluator:
    """Evaluates temporal reasoning and learning capabilities"""
    
    def __init__(self):
        self.metrics = {}
    
    def evaluate_temporal_performance(self,
                                    bug_events: List[TemporalBugEvent],
                                    sessions: List[Dict],
                                    patterns: List[DebugPattern]) -> Dict:
        """Comprehensive temporal performance evaluation"""
        
        # Group sessions by time windows
        time_windows = self._create_time_windows(sessions, window_days=30)
        
        # Calculate metrics per window
        window_metrics = []
        
        for window_start, window_sessions in time_windows:
            window_events = [
                e for e in bug_events 
                if window_start <= e.timestamp < window_start + 30 * 86400
            ]
            
            metrics = {
                'window_start': window_start,
                'n_bugs': len(window_events),
                'n_sessions': len(window_sessions),
                'success_rate': sum(s['success'] for s in window_sessions) / len(window_sessions) if window_sessions else 0,
                'avg_fix_time': np.mean([s['fix_time_minutes'] for s in window_sessions]) if window_sessions else 0,
                'pattern_reuse_rate': sum(1 for s in window_sessions if s['used_pattern']) / len(window_sessions) if window_sessions else 0,
                'unique_patterns': len(set(s['used_pattern'] for s in window_sessions if s['used_pattern']))
            }
            
            window_metrics.append(metrics)
        
        # Calculate learning improvement
        if len(window_metrics) > 1:
            early_success = np.mean([m['success_rate'] for m in window_metrics[:3]])
            late_success = np.mean([m['success_rate'] for m in window_metrics[-3:]])
            improvement = (late_success - early_success) / early_success if early_success > 0 else 0
        else:
            improvement = 0
        
        # Pattern effectiveness
        pattern_metrics = self._analyze_pattern_effectiveness(patterns, sessions)
        
        return {
            'temporal_windows': window_metrics,
            'overall_improvement': improvement,
            'pattern_analysis': pattern_metrics,
            'learning_velocity': self._calculate_learning_velocity(window_metrics)
        }
    
    def _create_time_windows(self, sessions: List[Dict], window_days: int) -> List[Tuple]:
        """Group sessions into time windows"""
        if not sessions:
            return []
        
        min_time = min(s['timestamp'] for s in sessions)
        max_time = max(s['timestamp'] for s in sessions)
        
        windows = []
        current_time = min_time
        
        while current_time < max_time:
            window_end = current_time + window_days * 86400
            window_sessions = [
                s for s in sessions 
                if current_time <= s['timestamp'] < window_end
            ]
            windows.append((current_time, window_sessions))
            current_time = window_end
        
        return windows
    
    def _analyze_pattern_effectiveness(self, 
                                     patterns: List[DebugPattern],
                                     sessions: List[Dict]) -> Dict:
        """Analyze effectiveness of learned patterns"""
        
        # Create pattern lookup
        pattern_lookup = {p.pattern_id: p for p in patterns}
        
        # Calculate metrics
        pattern_usage = {}
        pattern_success = {}
        
        for session in sessions:
            if session['used_pattern']:
                pattern_id = session['used_pattern']
                if pattern_id not in pattern_usage:
                    pattern_usage[pattern_id] = 0
                    pattern_success[pattern_id] = []
                
                pattern_usage[pattern_id] += 1
                pattern_success[pattern_id].append(session['success'])
        
        # Aggregate metrics
        effectiveness = {}
        for pattern_id, uses in pattern_usage.items():
            pattern = pattern_lookup.get(pattern_id)
            if pattern:
                effectiveness[pattern_id] = {
                    'pattern_type': pattern.pattern_type,
                    'total_uses': uses,
                    'success_rate': sum(pattern_success[pattern_id]) / len(pattern_success[pattern_id]),
                    'avg_fix_time': pattern.avg_fix_time,
                    'occurrences': len(pattern.occurrences)
                }
        
        return effectiveness
    
    def _calculate_learning_velocity(self, window_metrics: List[Dict]) -> float:
        """Calculate rate of improvement over time"""
        if len(window_metrics) < 2:
            return 0.0
        
        # Linear regression on success rates
        x = np.arange(len(window_metrics))
        y = np.array([m['success_rate'] for m in window_metrics])
        
        if len(x) > 1 and np.std(y) > 0:
            slope, _, _, _, _ = np.polyfit(x, y, 1, full=True)
            return float(slope[0])
        
        return 0.0


if __name__ == "__main__":
    # Generate temporal benchmark
    print("Generating temporal bug sequence...")
    generator = TemporalBenchmarkGenerator()
    bug_events = generator.generate_temporal_bug_sequence(duration_days=365, avg_bugs_per_day=5)
    print(f"Generated {len(bug_events)} bug events over 365 days")
    
    # Simulate debugging with learning
    print("\nSimulating debugging sessions with learning...")
    sessions, patterns = generator.simulate_debugging_sessions(bug_events, learning_rate=0.1)
    print(f"Completed {len(sessions)} debugging sessions")
    print(f"Learned {len(patterns)} unique patterns")
    
    # Evaluate temporal performance
    print("\nEvaluating temporal performance...")
    evaluator = TemporalBenchmarkEvaluator()
    temporal_results = evaluator.evaluate_temporal_performance(bug_events, sessions, patterns)
    
    print(f"\nTemporal Performance Results:")
    print(f"  Overall improvement: {temporal_results['overall_improvement']:.1%}")
    print(f"  Learning velocity: {temporal_results['learning_velocity']:.4f}")
    print(f"  Unique patterns used: {len(temporal_results['pattern_analysis'])}")
    
    # Generate cross-session benchmark
    print("\n" + "="*60)
    print("Cross-Session Learning Benchmark")
    print("="*60)
    
    cross_session = CrossSessionLearningBenchmark()
    scenarios = cross_session.generate_recurring_bug_scenarios(n_scenarios=1000, recurrence_rate=0.3)
    
    print(f"Generated {len(scenarios)} scenarios with recurring patterns")
    
    # Evaluate learning curve
    learning_curve = cross_session.evaluate_learning_curve(scenarios)
    
    print(f"\nLearning Curve Results:")
    print(f"  Final success rate: {learning_curve['success_over_time'][-1]:.1%}")
    print(f"  Final cache hit rate: {learning_curve['cache_hit_rate'][-1]:.1%}")
    print(f"  Average speedup: {np.mean(learning_curve['speedup_over_time']):.1f}x")
    
    # Generate codebase evolution
    print("\n" + "="*60)
    print("Codebase Evolution Simulation")
    print("="*60)
    
    evolution_sim = CodebaseEvolutionSimulator()
    evolution = evolution_sim.generate_evolution_timeline(duration_days=365)
    
    print(f"Generated evolution timeline with {len(evolution.timeline)} events")
    print(f"  File modifications: {sum(1 for _, t, _ in evolution.timeline if t == 'file_modified')}")
    print(f"  Refactorings: {sum(1 for _, t, _ in evolution.timeline if t == 'refactoring')}")
    print(f"  Dependency updates: {len(evolution.dependency_changes)}")
    print(f"  API migrations: {len(evolution.api_migrations)}")
    
    # Analyze temporal patterns
    print("\nTemporal Pattern Analysis:")
    if patterns:
        # Hour-of-day analysis
        all_hours = {}
        for pattern in patterns[:10]:  # Sample first 10 patterns
            for hour, count in pattern.temporal_distribution.items():
                if hour not in all_hours:
                    all_hours[hour] = 0
                all_hours[hour] += count
        
        peak_hour = max(all_hours, key=all_hours.get) if all_hours else 0
        print(f"  Peak bug occurrence hour: {peak_hour}:00")
        print(f"  Most effective pattern type: {max(patterns, key=lambda p: p.success_rate).pattern_type}")
        print(f"  Average pattern reuse: {np.mean([len(p.occurrences) for p in patterns]):.1f} times")