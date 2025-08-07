#!/usr/bin/env python3
"""
Enhanced metrics for MRR benchmark evaluation
Includes context efficiency, obfuscation resistance, and compositional retrieval metrics
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import statistics
import json


@dataclass
class EnhancedRetrievalMetrics:
    """Enhanced metrics for multi-modal retrieval evaluation"""
    # Standard metrics
    precision_at_k: Dict[int, float]
    recall_at_k: Dict[int, float]
    mean_reciprocal_rank: float
    
    # Enhanced metrics
    context_efficiency: float  # Ratio of used vs retrieved tokens
    compositional_success_rate: float  # Success following implicit paths
    obfuscation_resistance: float  # Success despite refactorings
    multi_modal_integration: float  # Usage of logs/docs/tests
    retrieval_path_accuracy: float  # Following correct retrieval paths
    
    # Detailed breakdowns
    artifact_usage: Dict[str, float]  # Usage by artifact type
    path_type_success: Dict[str, float]  # Success by path type


@dataclass
class TokenEfficiencyMetrics:
    """Metrics for token usage efficiency"""
    total_tokens_retrieved: int
    tokens_used_in_solution: int
    efficiency_ratio: float
    redundancy_rate: float
    precision_of_usage: float
    
    # Breakdowns
    tokens_by_file_relevance: Dict[str, int]
    tokens_by_artifact_type: Dict[str, int]


class EnhancedMetricsCalculator:
    """Advanced metrics calculator for enhanced MRR benchmark"""
    
    @staticmethod
    def calculate_context_efficiency(results: List[Dict[str, Any]]) -> TokenEfficiencyMetrics:
        """Calculate detailed context efficiency metrics"""
        total_retrieved = 0
        total_used = 0
        tokens_by_relevance = defaultdict(int)
        tokens_by_artifact = defaultdict(int)
        
        for result in results:
            # Count tokens retrieved
            for file_info in result.get('scattered_context', []):
                file_tokens = file_info.get('tokens', 0)
                total_retrieved += file_tokens
                tokens_by_relevance[file_info.get('relevance', 'unknown')] += file_tokens
            
            # Count tokens from artifacts
            artifacts = result.get('artifacts', {})
            for artifact_type, artifact_list in artifacts.items():
                for artifact in artifact_list:
                    artifact_tokens = artifact.get('tokens', 100)  # Default estimate
                    total_retrieved += artifact_tokens
                    tokens_by_artifact[artifact_type] += artifact_tokens
            
            # Count tokens actually used in solution
            files_modified = set(result.get('files_modified', []))
            for file_info in result.get('scattered_context', []):
                if file_info['file_path'] in files_modified:
                    total_used += file_info.get('tokens', 0)
            
            # Add tokens from used artifacts
            used_artifacts = result.get('artifacts_used_in_solution', [])
            for artifact_id in used_artifacts:
                total_used += 100  # Estimate
        
        efficiency_ratio = total_used / total_retrieved if total_retrieved > 0 else 0
        redundancy_rate = 1 - efficiency_ratio
        
        # Calculate precision of usage (how many retrieved files were actually useful)
        files_retrieved = sum(len(r.get('files_retrieved', [])) for r in results)
        files_used = sum(len(r.get('files_modified', [])) for r in results)
        precision_of_usage = files_used / files_retrieved if files_retrieved > 0 else 0
        
        return TokenEfficiencyMetrics(
            total_tokens_retrieved=total_retrieved,
            tokens_used_in_solution=total_used,
            efficiency_ratio=efficiency_ratio,
            redundancy_rate=redundancy_rate,
            precision_of_usage=precision_of_usage,
            tokens_by_file_relevance=dict(tokens_by_relevance),
            tokens_by_artifact_type=dict(tokens_by_artifact)
        )
    
    @staticmethod
    def calculate_compositional_retrieval_metrics(results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate metrics for compositional retrieval success"""
        total_compositional_paths = 0
        successful_compositional_paths = 0
        path_type_counts = defaultdict(int)
        path_type_success = defaultdict(int)
        
        for result in results:
            retrieval_paths = result.get('retrieval_paths', {})
            
            # Check compositional paths
            compositional_paths = retrieval_paths.get('compositional', [])
            for path in compositional_paths:
                total_compositional_paths += 1
                path_type_counts['compositional'] += 1
                
                # Check if model followed this path
                if EnhancedMetricsCalculator._check_path_followed(path, result):
                    successful_compositional_paths += 1
                    path_type_success['compositional'] += 1
            
            # Check explicit paths
            explicit_paths = retrieval_paths.get('explicit', [])
            for path in explicit_paths:
                path_type_counts['explicit'] += 1
                if EnhancedMetricsCalculator._check_simple_path_followed(path, result):
                    path_type_success['explicit'] += 1
            
            # Check implicit paths
            implicit_paths = retrieval_paths.get('implicit', [])
            for path in implicit_paths:
                path_type_counts['implicit'] += 1
                if EnhancedMetricsCalculator._check_implicit_path_followed(path, result):
                    path_type_success['implicit'] += 1
        
        # Calculate success rates by path type
        path_success_rates = {}
        for path_type, count in path_type_counts.items():
            success_count = path_type_success.get(path_type, 0)
            path_success_rates[path_type] = success_count / count if count > 0 else 0
        
        compositional_success_rate = (successful_compositional_paths / total_compositional_paths 
                                    if total_compositional_paths > 0 else 0)
        
        return {
            'compositional_success_rate': compositional_success_rate,
            'path_type_success_rates': path_success_rates,
            'avg_path_depth': EnhancedMetricsCalculator._calculate_avg_path_depth(results),
            'correct_path_ratio': EnhancedMetricsCalculator._calculate_correct_path_ratio(results)
        }
    
    @staticmethod
    def calculate_obfuscation_resistance(results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate how well models handle obfuscated dependencies"""
        total_obfuscated_cases = 0
        successful_despite_obfuscation = 0
        obfuscation_level_success = defaultdict(lambda: {'total': 0, 'success': 0})
        
        for result in results:
            obfuscation = result.get('obfuscation', {})
            if obfuscation:
                total_obfuscated_cases += 1
                level = obfuscation.get('obfuscation_level', 'unknown')
                obfuscation_level_success[level]['total'] += 1
                
                # Check if model succeeded despite obfuscation
                if result.get('success', False):
                    successful_despite_obfuscation += 1
                    obfuscation_level_success[level]['success'] += 1
                
                # Check specific obfuscation handling
                refactorings = obfuscation.get('refactorings', [])
                handled_refactorings = EnhancedMetricsCalculator._count_handled_refactorings(
                    refactorings, result
                )
        
        # Calculate resistance scores
        overall_resistance = (successful_despite_obfuscation / total_obfuscated_cases 
                            if total_obfuscated_cases > 0 else 0)
        
        level_resistance = {}
        for level, counts in obfuscation_level_success.items():
            if counts['total'] > 0:
                level_resistance[level] = counts['success'] / counts['total']
        
        return {
            'overall_resistance': overall_resistance,
            'resistance_by_level': level_resistance,
            'refactoring_handling_rate': EnhancedMetricsCalculator._calculate_refactoring_handling_rate(results)
        }
    
    @staticmethod
    def calculate_multi_modal_integration(results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate how well models integrate multiple artifact types"""
        artifact_type_usage = defaultdict(lambda: {'available': 0, 'used': 0})
        multi_modal_cases = 0
        successful_multi_modal = 0
        
        for result in results:
            artifacts = result.get('artifacts', {})
            artifacts_used = set(result.get('artifacts_used_in_solution', []))
            
            # Count available vs used artifacts by type
            artifact_types_available = set()
            for artifact_type, artifact_list in artifacts.items():
                if artifact_list:
                    artifact_types_available.add(artifact_type)
                    artifact_type_usage[artifact_type]['available'] += len(artifact_list)
                    
                    # Count used artifacts of this type
                    used_count = sum(1 for a in artifact_list 
                                   if a.get('path', '') in artifacts_used)
                    artifact_type_usage[artifact_type]['used'] += used_count
            
            # Check if this is a multi-modal case (multiple artifact types available)
            if len(artifact_types_available) > 1:
                multi_modal_cases += 1
                
                # Check if solution used multiple types
                types_used = set()
                for artifact_path in artifacts_used:
                    for artifact_type, artifact_list in artifacts.items():
                        if any(a.get('path', '') == artifact_path for a in artifact_list):
                            types_used.add(artifact_type)
                
                if len(types_used) > 1 and result.get('success', False):
                    successful_multi_modal += 1
        
        # Calculate usage rates by artifact type
        artifact_usage_rates = {}
        for artifact_type, counts in artifact_type_usage.items():
            if counts['available'] > 0:
                artifact_usage_rates[artifact_type] = counts['used'] / counts['available']
        
        multi_modal_success_rate = (successful_multi_modal / multi_modal_cases 
                                  if multi_modal_cases > 0 else 0)
        
        return {
            'multi_modal_success_rate': multi_modal_success_rate,
            'artifact_usage_rates': artifact_usage_rates,
            'avg_artifact_types_used': EnhancedMetricsCalculator._calculate_avg_artifact_types(results),
            'cross_modal_correlation': EnhancedMetricsCalculator._calculate_cross_modal_correlation(results)
        }
    
    @staticmethod
    def calculate_enhanced_retrieval_metrics(results: List[Dict[str, Any]]) -> EnhancedRetrievalMetrics:
        """Calculate all enhanced retrieval metrics"""
        # Calculate standard metrics (reuse from original metrics.py)
        standard_metrics = {
            'precision_at_k': EnhancedMetricsCalculator._calculate_precision_at_k(results),
            'recall_at_k': EnhancedMetricsCalculator._calculate_recall_at_k(results),
            'mean_reciprocal_rank': EnhancedMetricsCalculator._calculate_mrr(results)
        }
        
        # Calculate enhanced metrics
        context_efficiency = EnhancedMetricsCalculator.calculate_context_efficiency(results)
        compositional_metrics = EnhancedMetricsCalculator.calculate_compositional_retrieval_metrics(results)
        obfuscation_metrics = EnhancedMetricsCalculator.calculate_obfuscation_resistance(results)
        multi_modal_metrics = EnhancedMetricsCalculator.calculate_multi_modal_integration(results)
        
        # Calculate retrieval path accuracy
        path_accuracy = EnhancedMetricsCalculator._calculate_retrieval_path_accuracy(results)
        
        # Compile artifact usage breakdown
        artifact_usage = multi_modal_metrics['artifact_usage_rates']
        
        # Compile path type success breakdown
        path_type_success = compositional_metrics['path_type_success_rates']
        
        return EnhancedRetrievalMetrics(
            precision_at_k=standard_metrics['precision_at_k'],
            recall_at_k=standard_metrics['recall_at_k'],
            mean_reciprocal_rank=standard_metrics['mean_reciprocal_rank'],
            context_efficiency=context_efficiency.efficiency_ratio,
            compositional_success_rate=compositional_metrics['compositional_success_rate'],
            obfuscation_resistance=obfuscation_metrics['overall_resistance'],
            multi_modal_integration=multi_modal_metrics['multi_modal_success_rate'],
            retrieval_path_accuracy=path_accuracy,
            artifact_usage=artifact_usage,
            path_type_success=path_type_success
        )
    
    # Helper methods
    
    @staticmethod
    def _check_path_followed(path: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Check if a compositional path was followed"""
        retrieved_files = result.get('files_retrieved', [])
        path_files = [path['start']] + path.get('path', [])
        
        # Check if files were retrieved in roughly the correct order
        retrieved_indices = []
        for path_file in path_files:
            if path_file in retrieved_files:
                retrieved_indices.append(retrieved_files.index(path_file))
            else:
                return False
        
        # Check if indices are in increasing order (allowing some flexibility)
        return retrieved_indices == sorted(retrieved_indices)
    
    @staticmethod
    def _check_simple_path_followed(path: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Check if a simple explicit path was followed"""
        retrieved_files = set(result.get('files_retrieved', []))
        return path['from'] in retrieved_files and path['to'] in retrieved_files
    
    @staticmethod
    def _check_implicit_path_followed(path: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Check if an implicit path was discovered"""
        # Check if both endpoints were retrieved and evidence was found
        retrieved_files = set(result.get('files_retrieved', []))
        evidence_found = path.get('evidence', '') in str(result.get('analysis', ''))
        
        return (path['from'] in retrieved_files and 
                path['to'] in retrieved_files and 
                (evidence_found or path.get('confidence', 0) < 0.7))
    
    @staticmethod
    def _calculate_avg_path_depth(results: List[Dict[str, Any]]) -> float:
        """Calculate average depth of retrieval paths"""
        depths = []
        for result in results:
            paths = result.get('retrieval_paths', {}).get('compositional', [])
            for path in paths:
                depths.append(len(path.get('path', [])) + 1)
        
        return np.mean(depths) if depths else 0
    
    @staticmethod
    def _calculate_correct_path_ratio(results: List[Dict[str, Any]]) -> float:
        """Calculate ratio of correct paths followed"""
        total_paths = 0
        correct_paths = 0
        
        for result in results:
            if result.get('success', False):
                paths = result.get('retrieval_paths', {})
                for path_type in ['explicit', 'implicit', 'compositional']:
                    total_paths += len(paths.get(path_type, []))
                    # Simple heuristic: successful results likely followed correct paths
                    correct_paths += len(paths.get(path_type, [])) * 0.8
        
        return correct_paths / total_paths if total_paths > 0 else 0
    
    @staticmethod
    def _count_handled_refactorings(refactorings: List[Dict], result: Dict[str, Any]) -> int:
        """Count how many refactorings were correctly handled"""
        handled = 0
        for refactoring in refactorings:
            # Check if model correctly mapped old to new names
            if (refactoring['original'] in str(result.get('analysis', '')) or
                refactoring['current'] in str(result.get('files_modified', []))):
                handled += 1
        return handled
    
    @staticmethod
    def _calculate_refactoring_handling_rate(results: List[Dict[str, Any]]) -> float:
        """Calculate overall refactoring handling rate"""
        total_refactorings = 0
        handled_refactorings = 0
        
        for result in results:
            refactorings = result.get('obfuscation', {}).get('refactorings', [])
            total_refactorings += len(refactorings)
            handled_refactorings += EnhancedMetricsCalculator._count_handled_refactorings(
                refactorings, result
            )
        
        return handled_refactorings / total_refactorings if total_refactorings > 0 else 0
    
    @staticmethod
    def _calculate_avg_artifact_types(results: List[Dict[str, Any]]) -> float:
        """Calculate average number of artifact types used per bug"""
        artifact_type_counts = []
        
        for result in results:
            artifacts_used = set(result.get('artifacts_used_in_solution', []))
            if artifacts_used:
                # Count unique artifact types used
                types_used = set()
                for artifact_path in artifacts_used:
                    # Extract type from path (e.g., "artifacts/logs/..." -> "logs")
                    parts = artifact_path.split('/')
                    if len(parts) > 1 and parts[0] == 'artifacts':
                        types_used.add(parts[1])
                artifact_type_counts.append(len(types_used))
        
        return np.mean(artifact_type_counts) if artifact_type_counts else 0
    
    @staticmethod
    def _calculate_cross_modal_correlation(results: List[Dict[str, Any]]) -> float:
        """Calculate correlation between using multiple artifact types and success"""
        multi_modal_usage = []
        success_indicators = []
        
        for result in results:
            # Count artifact types used
            artifacts_used = set(result.get('artifacts_used_in_solution', []))
            types_used = set()
            for artifact_path in artifacts_used:
                parts = artifact_path.split('/')
                if len(parts) > 1 and parts[0] == 'artifacts':
                    types_used.add(parts[1])
            
            multi_modal_usage.append(len(types_used))
            success_indicators.append(1 if result.get('success', False) else 0)
        
        if len(multi_modal_usage) > 1:
            return np.corrcoef(multi_modal_usage, success_indicators)[0, 1]
        return 0
    
    @staticmethod
    def _calculate_retrieval_path_accuracy(results: List[Dict[str, Any]]) -> float:
        """Calculate accuracy of following defined retrieval paths"""
        total_required_paths = 0
        correctly_followed_paths = 0
        
        for result in results:
            paths = result.get('retrieval_paths', {}).get('compositional', [])
            for path in paths:
                if path.get('required_for_fix', False):
                    total_required_paths += 1
                    if EnhancedMetricsCalculator._check_path_followed(path, result):
                        correctly_followed_paths += 1
        
        return correctly_followed_paths / total_required_paths if total_required_paths > 0 else 0
    
    # Standard metrics calculations (simplified versions)
    
    @staticmethod
    def _calculate_precision_at_k(results: List[Dict[str, Any]]) -> Dict[int, float]:
        """Calculate precision@k for different k values"""
        k_values = [1, 5, 10, 20, 50]
        precision_at_k = {}
        
        for k in k_values:
            precisions = []
            for result in results:
                retrieved = result.get('files_retrieved', [])[:k]
                relevant = set(result.get('files_modified', []))
                
                if retrieved:
                    precision = len(set(retrieved) & relevant) / len(retrieved)
                    precisions.append(precision)
            
            precision_at_k[k] = np.mean(precisions) if precisions else 0
        
        return precision_at_k
    
    @staticmethod
    def _calculate_recall_at_k(results: List[Dict[str, Any]]) -> Dict[int, float]:
        """Calculate recall@k for different k values"""
        k_values = [1, 5, 10, 20, 50]
        recall_at_k = {}
        
        for k in k_values:
            recalls = []
            for result in results:
                retrieved = set(result.get('files_retrieved', [])[:k])
                relevant = set(result.get('files_modified', []))
                
                if relevant:
                    recall = len(retrieved & relevant) / len(relevant)
                    recalls.append(recall)
            
            recall_at_k[k] = np.mean(recalls) if recalls else 0
        
        return recall_at_k
    
    @staticmethod
    def _calculate_mrr(results: List[Dict[str, Any]]) -> float:
        """Calculate Mean Reciprocal Rank"""
        reciprocal_ranks = []
        
        for result in results:
            retrieved = result.get('files_retrieved', [])
            relevant = set(result.get('files_modified', []))
            
            for i, file in enumerate(retrieved):
                if file in relevant:
                    reciprocal_ranks.append(1.0 / (i + 1))
                    break
            else:
                reciprocal_ranks.append(0)
        
        return np.mean(reciprocal_ranks) if reciprocal_ranks else 0


def generate_enhanced_metrics_report(results: List[Dict[str, Any]], output_file: str):
    """Generate comprehensive enhanced metrics report"""
    # Calculate all enhanced metrics
    enhanced_retrieval = EnhancedMetricsCalculator.calculate_enhanced_retrieval_metrics(results)
    context_efficiency = EnhancedMetricsCalculator.calculate_context_efficiency(results)
    compositional_metrics = EnhancedMetricsCalculator.calculate_compositional_retrieval_metrics(results)
    obfuscation_metrics = EnhancedMetricsCalculator.calculate_obfuscation_resistance(results)
    multi_modal_metrics = EnhancedMetricsCalculator.calculate_multi_modal_integration(results)
    
    # Generate report
    report = f"""# Enhanced MRR Benchmark Metrics Report

## Context Efficiency Metrics
- **Total Tokens Retrieved**: {context_efficiency.total_tokens_retrieved:,}
- **Tokens Used in Solution**: {context_efficiency.tokens_used_in_solution:,}
- **Efficiency Ratio**: {context_efficiency.efficiency_ratio:.2%}
- **Redundancy Rate**: {context_efficiency.redundancy_rate:.2%}
- **Precision of Usage**: {context_efficiency.precision_of_usage:.2%}

### Token Distribution by Relevance
"""
    
    for relevance, tokens in context_efficiency.tokens_by_file_relevance.items():
        report += f"- {relevance}: {tokens:,} tokens\n"
    
    report += "\n### Token Distribution by Artifact Type\n"
    for artifact_type, tokens in context_efficiency.tokens_by_artifact_type.items():
        report += f"- {artifact_type}: {tokens:,} tokens\n"
    
    report += f"""
## Compositional Retrieval Metrics
- **Compositional Success Rate**: {compositional_metrics['compositional_success_rate']:.2%}
- **Average Path Depth**: {compositional_metrics['avg_path_depth']:.1f}
- **Correct Path Ratio**: {compositional_metrics['correct_path_ratio']:.2%}

### Success Rate by Path Type
"""
    
    for path_type, success_rate in compositional_metrics['path_type_success_rates'].items():
        report += f"- {path_type}: {success_rate:.2%}\n"
    
    report += f"""
## Obfuscation Resistance Metrics
- **Overall Resistance**: {obfuscation_metrics['overall_resistance']:.2%}
- **Refactoring Handling Rate**: {obfuscation_metrics['refactoring_handling_rate']:.2%}

### Resistance by Obfuscation Level
"""
    
    for level, resistance in obfuscation_metrics['resistance_by_level'].items():
        report += f"- {level}: {resistance:.2%}\n"
    
    report += f"""
## Multi-Modal Integration Metrics
- **Multi-Modal Success Rate**: {multi_modal_metrics['multi_modal_success_rate']:.2%}
- **Average Artifact Types Used**: {multi_modal_metrics['avg_artifact_types_used']:.1f}
- **Cross-Modal Correlation**: {multi_modal_metrics['cross_modal_correlation']:.3f}

### Artifact Usage Rates
"""
    
    for artifact_type, usage_rate in multi_modal_metrics['artifact_usage_rates'].items():
        report += f"- {artifact_type}: {usage_rate:.2%}\n"
    
    report += f"""
## Enhanced Retrieval Summary
- **Mean Reciprocal Rank**: {enhanced_retrieval.mean_reciprocal_rank:.3f}
- **Context Efficiency**: {enhanced_retrieval.context_efficiency:.2%}
- **Compositional Success**: {enhanced_retrieval.compositional_success_rate:.2%}
- **Obfuscation Resistance**: {enhanced_retrieval.obfuscation_resistance:.2%}
- **Multi-Modal Integration**: {enhanced_retrieval.multi_modal_integration:.2%}
- **Retrieval Path Accuracy**: {enhanced_retrieval.retrieval_path_accuracy:.2%}

### Precision@K
"""
    
    for k, precision in sorted(enhanced_retrieval.precision_at_k.items()):
        report += f"- P@{k}: {precision:.3f}\n"
    
    report += "\n### Recall@K\n"
    for k, recall in sorted(enhanced_retrieval.recall_at_k.items()):
        report += f"- R@{k}: {recall:.3f}\n"
    
    # Save report
    with open(output_file, 'w') as f:
        f.write(report)
    
    return report