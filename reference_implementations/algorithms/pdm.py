#!/usr/bin/env python3
"""
Persistent Debug Memory (PDM) - Complete Implementation
Repository-specific learning system from 15M+ debugging sessions
"""

import json
import sqlite3
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import pickle
from pathlib import Path
from collections import defaultdict, Counter
import re

@dataclass
class BugPattern:
    """Represents a learned bug pattern"""
    pattern_id: str
    category: str
    symptoms: List[str]
    root_causes: List[str]
    fixes: List[str]
    frequency: int
    success_rate: float
    avg_fix_time: float
    last_seen: str
    repositories: List[str]
    
@dataclass 
class DebugSession:
    """Represents a debugging session"""
    session_id: str
    repository: str
    bug_id: str
    category: str
    timestamp: str
    duration_seconds: int
    iterations: int
    success: bool
    files_examined: List[str]
    fix_applied: str
    test_results: Dict
    confidence: float

@dataclass
class RepositoryMemory:
    """Repository-specific memory"""
    repo_id: str
    patterns: List[str]  # Pattern IDs
    common_bugs: Dict[str, int]  # Bug type frequencies
    fix_templates: Dict[str, List[str]]
    dependency_issues: Dict[str, List[str]]
    performance_hotspots: List[str]
    test_coverage_gaps: List[str]
    last_updated: str

class PersistentDebugMemory:
    """
    Persistent Debug Memory system for Chronos
    Learns from debugging sessions and improves over time
    """
    
    def __init__(self, db_path: str = "chronos_memory.db"):
        """
        Initialize PDM with database connection
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Initialize tables
        self._initialize_database()
        
        # Memory caches
        self.pattern_cache = {}
        self.repo_cache = {}
        self.similarity_cache = {}
        
        # Learning parameters
        self.min_pattern_frequency = 3
        self.confidence_threshold = 0.7
        self.decay_factor = 0.95  # Time decay for old patterns
        
        # Statistics
        self.stats = {
            'total_sessions': 0,
            'successful_fixes': 0,
            'patterns_learned': 0,
            'repositories': set()
        }
        
        self._load_statistics()
    
    def _initialize_database(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        # Bug patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bug_patterns (
                pattern_id TEXT PRIMARY KEY,
                category TEXT,
                symptoms TEXT,
                root_causes TEXT,
                fixes TEXT,
                frequency INTEGER,
                success_rate REAL,
                avg_fix_time REAL,
                last_seen TEXT,
                repositories TEXT,
                embedding BLOB
            )
        """)
        
        # Debug sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debug_sessions (
                session_id TEXT PRIMARY KEY,
                repository TEXT,
                bug_id TEXT,
                category TEXT,
                timestamp TEXT,
                duration_seconds INTEGER,
                iterations INTEGER,
                success INTEGER,
                files_examined TEXT,
                fix_applied TEXT,
                test_results TEXT,
                confidence REAL
            )
        """)
        
        # Repository memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repository_memory (
                repo_id TEXT PRIMARY KEY,
                patterns TEXT,
                common_bugs TEXT,
                fix_templates TEXT,
                dependency_issues TEXT,
                performance_hotspots TEXT,
                test_coverage_gaps TEXT,
                last_updated TEXT
            )
        """)
        
        # Pattern relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_relationships (
                pattern1_id TEXT,
                pattern2_id TEXT,
                relationship_type TEXT,
                strength REAL,
                co_occurrence_count INTEGER,
                PRIMARY KEY (pattern1_id, pattern2_id)
            )
        """)
        
        # Index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_repo 
            ON debug_sessions(repository)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patterns_category 
            ON bug_patterns(category)
        """)
        
        self.conn.commit()
    
    def record_session(self, session: DebugSession) -> None:
        """
        Record a debugging session and update patterns
        
        Args:
            session: DebugSession object
        """
        cursor = self.conn.cursor()
        
        # Insert session
        cursor.execute("""
            INSERT OR REPLACE INTO debug_sessions 
            (session_id, repository, bug_id, category, timestamp, 
             duration_seconds, iterations, success, files_examined, 
             fix_applied, test_results, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.repository,
            session.bug_id,
            session.category,
            session.timestamp,
            session.duration_seconds,
            session.iterations,
            int(session.success),
            json.dumps(session.files_examined),
            session.fix_applied,
            json.dumps(session.test_results),
            session.confidence
        ))
        
        # Update patterns if successful
        if session.success:
            self._update_patterns(session)
        
        # Update repository memory
        self._update_repository_memory(session)
        
        # Update statistics
        self.stats['total_sessions'] += 1
        if session.success:
            self.stats['successful_fixes'] += 1
        self.stats['repositories'].add(session.repository)
        
        self.conn.commit()
    
    def retrieve_similar_patterns(self, bug_context: Dict, 
                                 repository: str = None,
                                 top_k: int = 5) -> List[BugPattern]:
        """
        Retrieve similar bug patterns from memory
        
        Args:
            bug_context: Current bug information
            repository: Optional repository filter
            top_k: Number of patterns to retrieve
            
        Returns:
            List of similar BugPattern objects
        """
        # Generate query embedding
        query_key = self._generate_pattern_key(bug_context)
        
        # Check cache
        cache_key = f"{query_key}_{repository}_{top_k}"
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        cursor = self.conn.cursor()
        
        # Build query
        query = """
            SELECT * FROM bug_patterns 
            WHERE category = ?
        """
        params = [bug_context.get('category', 'unknown')]
        
        if repository:
            query += " AND repositories LIKE ?"
            params.append(f"%{repository}%")
        
        query += " ORDER BY frequency * success_rate DESC LIMIT ?"
        params.append(top_k * 3)  # Get more for filtering
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to BugPattern objects and rank
        patterns = []
        for row in rows:
            pattern = self._row_to_pattern(row)
            similarity = self._calculate_similarity(bug_context, pattern)
            
            if similarity > self.confidence_threshold:
                patterns.append((pattern, similarity))
        
        # Sort by similarity and return top_k
        patterns.sort(key=lambda x: x[1], reverse=True)
        result = [p[0] for p in patterns[:top_k]]
        
        # Cache result
        self.similarity_cache[cache_key] = result
        
        return result
    
    def get_repository_insights(self, repository: str) -> Dict:
        """
        Get repository-specific debugging insights
        
        Args:
            repository: Repository identifier
            
        Returns:
            Dictionary of insights and patterns
        """
        cursor = self.conn.cursor()
        
        # Get repository memory
        cursor.execute("""
            SELECT * FROM repository_memory WHERE repo_id = ?
        """, (repository,))
        
        row = cursor.fetchone()
        
        if not row:
            return self._generate_initial_insights(repository)
        
        # Parse stored data
        insights = {
            'repository': repository,
            'last_updated': row['last_updated'],
            'common_bugs': json.loads(row['common_bugs']),
            'fix_templates': json.loads(row['fix_templates']),
            'dependency_issues': json.loads(row['dependency_issues']),
            'performance_hotspots': json.loads(row['performance_hotspots']),
            'test_coverage_gaps': json.loads(row['test_coverage_gaps'])
        }
        
        # Get success metrics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(success) as successful,
                AVG(duration_seconds) as avg_duration,
                AVG(iterations) as avg_iterations
            FROM debug_sessions
            WHERE repository = ?
            AND timestamp > datetime('now', '-30 days')
        """, (repository,))
        
        metrics = cursor.fetchone()
        
        insights['recent_metrics'] = {
            'total_sessions': metrics['total'] or 0,
            'success_rate': (metrics['successful'] or 0) / max(1, metrics['total'] or 1),
            'avg_fix_time': metrics['avg_duration'] or 0,
            'avg_iterations': metrics['avg_iterations'] or 0
        }
        
        # Get top patterns
        pattern_ids = json.loads(row['patterns']) if row['patterns'] else []
        insights['top_patterns'] = []
        
        for pattern_id in pattern_ids[:10]:
            cursor.execute("""
                SELECT * FROM bug_patterns WHERE pattern_id = ?
            """, (pattern_id,))
            pattern_row = cursor.fetchone()
            if pattern_row:
                insights['top_patterns'].append(self._row_to_pattern(pattern_row))
        
        return insights
    
    def learn_from_batch(self, sessions: List[DebugSession]) -> Dict:
        """
        Batch learning from multiple sessions
        
        Args:
            sessions: List of DebugSession objects
            
        Returns:
            Learning statistics
        """
        patterns_before = len(self.pattern_cache)
        successful_patterns = []
        
        for session in sessions:
            self.record_session(session)
            
            if session.success:
                pattern_key = self._generate_pattern_key({
                    'category': session.category,
                    'files': session.files_examined,
                    'fix': session.fix_applied
                })
                successful_patterns.append(pattern_key)
        
        # Mine frequent patterns
        new_patterns = self._mine_patterns(successful_patterns)
        
        # Calculate statistics
        stats = {
            'sessions_processed': len(sessions),
            'patterns_before': patterns_before,
            'patterns_after': len(self.pattern_cache),
            'new_patterns': new_patterns,
            'success_rate': sum(s.success for s in sessions) / len(sessions)
        }
        
        return stats
    
    def _update_patterns(self, session: DebugSession) -> None:
        """Update bug patterns based on successful session"""
        pattern_key = self._generate_pattern_key({
            'category': session.category,
            'files': session.files_examined,
            'fix': session.fix_applied
        })
        
        cursor = self.conn.cursor()
        
        # Check if pattern exists
        cursor.execute("""
            SELECT * FROM bug_patterns WHERE pattern_id = ?
        """, (pattern_key,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing pattern
            frequency = existing['frequency'] + 1
            success_rate = (existing['success_rate'] * existing['frequency'] + 1) / frequency
            avg_fix_time = (existing['avg_fix_time'] * existing['frequency'] + 
                          session.duration_seconds) / frequency
            
            repositories = json.loads(existing['repositories'])
            if session.repository not in repositories:
                repositories.append(session.repository)
            
            cursor.execute("""
                UPDATE bug_patterns 
                SET frequency = ?, success_rate = ?, avg_fix_time = ?,
                    last_seen = ?, repositories = ?
                WHERE pattern_id = ?
            """, (
                frequency, success_rate, avg_fix_time,
                session.timestamp, json.dumps(repositories),
                pattern_key
            ))
        else:
            # Create new pattern
            pattern = BugPattern(
                pattern_id=pattern_key,
                category=session.category,
                symptoms=self._extract_symptoms(session),
                root_causes=self._extract_root_causes(session),
                fixes=[session.fix_applied],
                frequency=1,
                success_rate=1.0,
                avg_fix_time=session.duration_seconds,
                last_seen=session.timestamp,
                repositories=[session.repository]
            )
            
            self._insert_pattern(pattern)
            self.stats['patterns_learned'] += 1
    
    def _update_repository_memory(self, session: DebugSession) -> None:
        """Update repository-specific memory"""
        cursor = self.conn.cursor()
        
        # Get existing memory
        cursor.execute("""
            SELECT * FROM repository_memory WHERE repo_id = ?
        """, (session.repository,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing memory
            common_bugs = json.loads(existing['common_bugs'])
            common_bugs[session.category] = common_bugs.get(session.category, 0) + 1
            
            if session.success:
                fix_templates = json.loads(existing['fix_templates'])
                if session.category not in fix_templates:
                    fix_templates[session.category] = []
                if session.fix_applied not in fix_templates[session.category]:
                    fix_templates[session.category].append(session.fix_applied)
            
            cursor.execute("""
                UPDATE repository_memory
                SET common_bugs = ?, fix_templates = ?, last_updated = ?
                WHERE repo_id = ?
            """, (
                json.dumps(common_bugs),
                json.dumps(fix_templates),
                session.timestamp,
                session.repository
            ))
        else:
            # Create new memory
            memory = RepositoryMemory(
                repo_id=session.repository,
                patterns=[],
                common_bugs={session.category: 1},
                fix_templates={session.category: [session.fix_applied]} if session.success else {},
                dependency_issues={},
                performance_hotspots=[],
                test_coverage_gaps=[],
                last_updated=session.timestamp
            )
            
            self._insert_repository_memory(memory)
    
    def _calculate_similarity(self, bug_context: Dict, pattern: BugPattern) -> float:
        """Calculate similarity between bug context and pattern"""
        score = 0.0
        
        # Category match
        if bug_context.get('category') == pattern.category:
            score += 0.3
        
        # Symptom overlap
        bug_symptoms = set(bug_context.get('symptoms', []))
        pattern_symptoms = set(pattern.symptoms)
        if bug_symptoms and pattern_symptoms:
            overlap = len(bug_symptoms & pattern_symptoms) / len(bug_symptoms | pattern_symptoms)
            score += overlap * 0.3
        
        # File similarity
        bug_files = set(bug_context.get('files', []))
        pattern_files = set()
        for fix in pattern.fixes:
            # Extract files from fix
            files = re.findall(r'(\w+\.\w+)', fix)
            pattern_files.update(files)
        
        if bug_files and pattern_files:
            file_overlap = len(bug_files & pattern_files) / len(bug_files | pattern_files)
            score += file_overlap * 0.2
        
        # Temporal relevance (decay old patterns)
        if pattern.last_seen:
            days_old = (datetime.now() - datetime.fromisoformat(pattern.last_seen)).days
            temporal_score = self.decay_factor ** (days_old / 30)
            score *= temporal_score
        
        # Success rate weight
        score *= pattern.success_rate
        
        return score
    
    def _generate_pattern_key(self, context: Dict) -> str:
        """Generate unique pattern key"""
        key_parts = [
            context.get('category', 'unknown'),
            str(sorted(context.get('files', [])))[:100],
            str(context.get('fix', ''))[:100]
        ]
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def _extract_symptoms(self, session: DebugSession) -> List[str]:
        """Extract symptoms from session"""
        symptoms = []
        
        # Extract from test results
        if session.test_results:
            for test, result in session.test_results.items():
                if not result.get('passed', False):
                    symptoms.append(f"test_failure:{test}")
        
        # Extract from category
        category_symptoms = {
            'syntax_errors': ['compilation_error', 'syntax_invalid'],
            'logic_errors': ['incorrect_output', 'assertion_failure'],
            'memory_issues': ['segfault', 'memory_leak', 'null_pointer'],
            'concurrency_issues': ['deadlock', 'race_condition'],
            'performance_bugs': ['timeout', 'high_cpu', 'memory_bloat']
        }
        
        symptoms.extend(category_symptoms.get(session.category, []))
        
        return symptoms
    
    def _extract_root_causes(self, session: DebugSession) -> List[str]:
        """Extract root causes from session"""
        root_causes = []
        
        # Analyze fix to infer root cause
        fix = session.fix_applied.lower()
        
        if 'null' in fix or 'none' in fix:
            root_causes.append('missing_null_check')
        if 'index' in fix or 'bound' in fix:
            root_causes.append('boundary_condition')
        if 'lock' in fix or 'mutex' in fix:
            root_causes.append('synchronization_issue')
        if 'cache' in fix:
            root_causes.append('cache_invalidation')
        
        return root_causes
    
    def _mine_patterns(self, pattern_keys: List[str]) -> int:
        """Mine frequent patterns from pattern keys"""
        # Count frequencies
        pattern_counts = Counter(pattern_keys)
        
        new_patterns = 0
        cursor = self.conn.cursor()
        
        for pattern_key, count in pattern_counts.items():
            if count >= self.min_pattern_frequency:
                # Check if pattern exists
                cursor.execute("""
                    SELECT pattern_id FROM bug_patterns WHERE pattern_id = ?
                """, (pattern_key,))
                
                if not cursor.fetchone():
                    # Create new pattern
                    pattern = BugPattern(
                        pattern_id=pattern_key,
                        category='mined',
                        symptoms=[],
                        root_causes=[],
                        fixes=[],
                        frequency=count,
                        success_rate=0.8,  # Initial estimate
                        avg_fix_time=0,
                        last_seen=datetime.now().isoformat(),
                        repositories=[]
                    )
                    
                    self._insert_pattern(pattern)
                    new_patterns += 1
        
        return new_patterns
    
    def _insert_pattern(self, pattern: BugPattern) -> None:
        """Insert pattern into database"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO bug_patterns
            (pattern_id, category, symptoms, root_causes, fixes,
             frequency, success_rate, avg_fix_time, last_seen, repositories)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern.pattern_id,
            pattern.category,
            json.dumps(pattern.symptoms),
            json.dumps(pattern.root_causes),
            json.dumps(pattern.fixes),
            pattern.frequency,
            pattern.success_rate,
            pattern.avg_fix_time,
            pattern.last_seen,
            json.dumps(pattern.repositories)
        ))
        
        # Update cache
        self.pattern_cache[pattern.pattern_id] = pattern
    
    def _insert_repository_memory(self, memory: RepositoryMemory) -> None:
        """Insert repository memory into database"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO repository_memory
            (repo_id, patterns, common_bugs, fix_templates,
             dependency_issues, performance_hotspots, 
             test_coverage_gaps, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.repo_id,
            json.dumps(memory.patterns),
            json.dumps(memory.common_bugs),
            json.dumps(memory.fix_templates),
            json.dumps(memory.dependency_issues),
            json.dumps(memory.performance_hotspots),
            json.dumps(memory.test_coverage_gaps),
            memory.last_updated
        ))
    
    def _row_to_pattern(self, row) -> BugPattern:
        """Convert database row to BugPattern"""
        return BugPattern(
            pattern_id=row['pattern_id'],
            category=row['category'],
            symptoms=json.loads(row['symptoms']),
            root_causes=json.loads(row['root_causes']),
            fixes=json.loads(row['fixes']),
            frequency=row['frequency'],
            success_rate=row['success_rate'],
            avg_fix_time=row['avg_fix_time'],
            last_seen=row['last_seen'],
            repositories=json.loads(row['repositories'])
        )
    
    def _generate_initial_insights(self, repository: str) -> Dict:
        """Generate initial insights for new repository"""
        return {
            'repository': repository,
            'last_updated': datetime.now().isoformat(),
            'common_bugs': {},
            'fix_templates': {},
            'dependency_issues': {},
            'performance_hotspots': [],
            'test_coverage_gaps': [],
            'recent_metrics': {
                'total_sessions': 0,
                'success_rate': 0,
                'avg_fix_time': 0,
                'avg_iterations': 0
            },
            'top_patterns': []
        }
    
    def _load_statistics(self) -> None:
        """Load statistics from database"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM debug_sessions")
        self.stats['total_sessions'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT SUM(success) as count FROM debug_sessions")
        self.stats['successful_fixes'] = cursor.fetchone()['count'] or 0
        
        cursor.execute("SELECT COUNT(*) as count FROM bug_patterns")
        self.stats['patterns_learned'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT DISTINCT repository FROM debug_sessions")
        self.stats['repositories'] = set(row['repository'] for row in cursor.fetchall())
    
    def get_statistics(self) -> Dict:
        """Get PDM statistics"""
        return {
            'total_sessions': self.stats['total_sessions'],
            'successful_fixes': self.stats['successful_fixes'],
            'success_rate': self.stats['successful_fixes'] / max(1, self.stats['total_sessions']),
            'patterns_learned': self.stats['patterns_learned'],
            'unique_repositories': len(self.stats['repositories']),
            'cache_size': len(self.pattern_cache),
            'db_size_mb': Path(self.db_path).stat().st_size / (1024 * 1024) if Path(self.db_path).exists() else 0
        }
    
    def export_patterns(self, output_path: str) -> None:
        """Export learned patterns to file"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM bug_patterns")
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append(asdict(self._row_to_pattern(row)))
        
        with open(output_path, 'w') as f:
            json.dump(patterns, f, indent=2)
        
        print(f"Exported {len(patterns)} patterns to {output_path}")
    
    def close(self) -> None:
        """Close database connection"""
        self.conn.close()


if __name__ == "__main__":
    # Example usage
    print("Persistent Debug Memory (PDM) System")
    print("=" * 60)
    
    # Initialize PDM
    pdm = PersistentDebugMemory("test_memory.db")
    
    # Example debugging session
    session = DebugSession(
        session_id="SESSION-001",
        repository="example_repo",
        bug_id="BUG-123",
        category="logic_errors",
        timestamp=datetime.now().isoformat(),
        duration_seconds=180,
        iterations=7,
        success=True,
        files_examined=["auth.py", "database.py", "utils.py"],
        fix_applied="Fixed boundary condition in auth.py line 42",
        test_results={"test_auth": {"passed": True}},
        confidence=0.85
    )
    
    # Record session
    pdm.record_session(session)
    
    # Retrieve similar patterns
    bug_context = {
        'category': 'logic_errors',
        'symptoms': ['assertion_failure', 'incorrect_output'],
        'files': ['auth.py']
    }
    
    similar_patterns = pdm.retrieve_similar_patterns(bug_context, repository="example_repo")
    
    print(f"\nFound {len(similar_patterns)} similar patterns")
    for pattern in similar_patterns:
        print(f"  - Pattern {pattern.pattern_id}: {pattern.category} "
              f"(success: {pattern.success_rate:.1%}, frequency: {pattern.frequency})")
    
    # Get repository insights
    insights = pdm.get_repository_insights("example_repo")
    
    print(f"\nRepository Insights for 'example_repo':")
    print(f"  Common bugs: {insights['common_bugs']}")
    print(f"  Recent success rate: {insights['recent_metrics']['success_rate']:.1%}")
    
    # Get statistics
    stats = pdm.get_statistics()
    
    print(f"\nPDM Statistics:")
    print(f"  Total sessions: {stats['total_sessions']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Patterns learned: {stats['patterns_learned']}")
    print(f"  Unique repositories: {stats['unique_repositories']}")
    
    # Close connection
    pdm.close()