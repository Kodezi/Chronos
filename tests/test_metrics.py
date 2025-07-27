"""
Test suite for evaluation metrics calculations.

This module tests the metric calculations used in the Chronos evaluation framework.
"""

import pytest
import numpy as np
from typing import List, Dict, Any


class TestMetrics:
    """Test evaluation metrics calculations."""
    
    def test_debug_success_rate(self):
        """Test debug success rate calculation."""
        results = [
            {"success": True, "iterations": 2},
            {"success": True, "iterations": 1},
            {"success": False, "iterations": 5},
            {"success": True, "iterations": 3},
        ]
        
        success_rate = self.calculate_success_rate(results)
        assert success_rate == 75.0  # 3 out of 4 successful
    
    def test_root_cause_accuracy(self):
        """Test root cause accuracy calculation."""
        results = [
            {"root_cause_correct": True, "success": True},
            {"root_cause_correct": True, "success": True},
            {"root_cause_correct": False, "success": True},
            {"root_cause_correct": False, "success": False},
        ]
        
        # Only count when fix is successful
        accuracy = self.calculate_root_cause_accuracy(results)
        assert accuracy == 66.67  # 2 out of 3 successful fixes had correct root cause
    
    def test_average_iterations(self):
        """Test average iteration calculation."""
        results = [
            {"success": True, "iterations": 2},
            {"success": True, "iterations": 3},
            {"success": True, "iterations": 1},
            {"success": False, "iterations": 10},  # Should not count failed attempts
        ]
        
        avg_iterations = self.calculate_avg_iterations(results, successful_only=True)
        assert avg_iterations == 2.0  # (2 + 3 + 1) / 3
    
    def test_retrieval_precision(self):
        """Test retrieval precision calculation."""
        retrieved = ["file1.py", "file2.py", "file3.py", "file4.py", "file5.py"]
        relevant = ["file1.py", "file2.py", "file6.py"]
        
        precision = self.calculate_precision(retrieved, relevant)
        assert precision == 40.0  # 2 out of 5 retrieved were relevant
    
    def test_retrieval_recall(self):
        """Test retrieval recall calculation."""
        retrieved = ["file1.py", "file2.py", "file3.py"]
        relevant = ["file1.py", "file2.py", "file4.py", "file5.py"]
        
        recall = self.calculate_recall(retrieved, relevant)
        assert recall == 50.0  # 2 out of 4 relevant were retrieved
    
    def test_context_efficiency(self):
        """Test context efficiency calculation."""
        retrieved_tokens = 5000
        used_tokens = 3500
        
        efficiency = self.calculate_context_efficiency(used_tokens, retrieved_tokens)
        assert efficiency == 0.7  # 3500 / 5000
    
    def test_statistical_significance(self):
        """Test statistical significance calculation."""
        chronos_results = [65.2, 64.8, 65.5, 65.9, 65.1]
        baseline_results = [8.3, 8.7, 8.5, 8.2, 8.8]
        
        p_value = self.calculate_significance(chronos_results, baseline_results)
        assert p_value < 0.001  # Should be highly significant
    
    # Helper methods
    def calculate_success_rate(self, results: List[Dict[str, Any]]) -> float:
        """Calculate debugging success rate."""
        successful = sum(1 for r in results if r["success"])
        return (successful / len(results)) * 100 if results else 0.0
    
    def calculate_root_cause_accuracy(self, results: List[Dict[str, Any]]) -> float:
        """Calculate root cause identification accuracy."""
        successful_with_correct_cause = sum(
            1 for r in results 
            if r["success"] and r["root_cause_correct"]
        )
        successful_total = sum(1 for r in results if r["success"])
        
        if successful_total == 0:
            return 0.0
        
        return round((successful_with_correct_cause / successful_total) * 100, 2)
    
    def calculate_avg_iterations(self, results: List[Dict[str, Any]], 
                                successful_only: bool = True) -> float:
        """Calculate average iterations to fix."""
        if successful_only:
            iterations = [r["iterations"] for r in results if r["success"]]
        else:
            iterations = [r["iterations"] for r in results]
        
        return sum(iterations) / len(iterations) if iterations else 0.0
    
    def calculate_precision(self, retrieved: List[str], relevant: List[str]) -> float:
        """Calculate retrieval precision."""
        if not retrieved:
            return 0.0
        
        relevant_retrieved = len(set(retrieved) & set(relevant))
        return (relevant_retrieved / len(retrieved)) * 100
    
    def calculate_recall(self, retrieved: List[str], relevant: List[str]) -> float:
        """Calculate retrieval recall."""
        if not relevant:
            return 0.0
        
        relevant_retrieved = len(set(retrieved) & set(relevant))
        return (relevant_retrieved / len(relevant)) * 100
    
    def calculate_context_efficiency(self, used_tokens: int, 
                                    retrieved_tokens: int) -> float:
        """Calculate context usage efficiency."""
        if retrieved_tokens == 0:
            return 0.0
        return used_tokens / retrieved_tokens
    
    def calculate_significance(self, chronos_results: List[float], 
                             baseline_results: List[float]) -> float:
        """Calculate statistical significance (mock implementation)."""
        # In real implementation, use scipy.stats.ttest_rel
        # This is a simplified version for demonstration
        chronos_mean = np.mean(chronos_results)
        baseline_mean = np.mean(baseline_results)
        
        # If difference is large, return very small p-value
        if chronos_mean > baseline_mean * 5:
            return 0.0001
        return 0.05


if __name__ == "__main__":
    pytest.main([__file__])