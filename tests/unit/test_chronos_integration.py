#!/usr/bin/env python3
"""
Unit tests for Chronos integration module
Tests the complete 7-layer architecture
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from pathlib import Path
import json

from chronos_integration import (
    ChronosSystem, ChronosConfig, create_chronos_system,
    InputType, ParsedInput
)
from architecture.multi_source_input import InputType
from architecture.debug_tuned_llm import DebugOutput
from architecture.execution_sandbox import SandboxResult, TestResult
from architecture.explainability_layer import Explanation, CodeChange


class TestChronosIntegration(unittest.TestCase):
    """Test cases for Chronos system integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = ChronosConfig(
            repository_path="/tmp/test_repo",
            use_docker_sandbox=False,
            max_iterations=5,
            confidence_threshold=0.7,
            memory_db_path=":memory:",  # In-memory SQLite
            enable_caching=True,
            log_level="ERROR"  # Reduce noise in tests
        )
        self.chronos = ChronosSystem(self.config)
    
    def test_initialization(self):
        """Test system initialization"""
        # Check all layers initialized
        self.assertIsNotNone(self.chronos.input_layer)
        self.assertIsNotNone(self.chronos.agr)
        self.assertIsNotNone(self.chronos.debug_llm)
        self.assertIsNotNone(self.chronos.orchestrator)
        self.assertIsNotNone(self.chronos.pdm)
        self.assertIsNotNone(self.chronos.sandbox)
        self.assertIsNotNone(self.chronos.explainer)
        
        # Check status
        status = self.chronos.get_system_status()
        self.assertTrue(status['initialized'])
        self.assertEqual(status['layers']['input'], 'ready')
        self.assertEqual(status['config']['repository'], '/tmp/test_repo')
    
    @patch('chronos_integration.ChronosSystem._parse_fix_to_files')
    @patch('architecture.orchestration_controller.OrchestrationController.debug')
    def test_debug_stack_trace(self, mock_orchestrator_debug, mock_parse_fix):
        """Test debugging with stack trace input"""
        # Mock orchestrator response
        mock_debug_session = Mock()
        mock_debug_session.success = True
        mock_debug_session.session_id = "test_123"
        mock_debug_session.iterations = [Mock(confidence=0.85)]
        mock_debug_session.final_fix = "if user is not None:\n    return user.name"
        mock_debug_session.total_time = 2.5
        mock_orchestrator_debug.return_value = mock_debug_session
        
        # Mock fix parsing
        mock_parse_fix.return_value = {
            'user_service.py': "if user is not None:\n    return user.name"
        }
        
        # Test input
        stack_trace = """
TypeError: 'NoneType' object is not subscriptable
  File "user_service.py", line 45, in get_user
    return user['name']
"""
        
        # Run debug
        result = self.chronos.debug(
            error_input=stack_trace,
            input_type=InputType.STACK_TRACE,
            metadata={'test': True}
        )
        
        # Verify results
        self.assertTrue(result['success'])
        self.assertEqual(result['session_id'], 'test_123')
        self.assertIn('fix', result)
        self.assertIn('code', result['fix'])
        self.assertIn('files', result['fix'])
        self.assertEqual(result['fix']['confidence'], 0.85)
    
    @patch('architecture.execution_sandbox.ExecutionSandbox.execute_with_fix')
    @patch('architecture.orchestration_controller.OrchestrationController.debug')
    def test_debug_with_sandbox_validation(self, mock_orchestrator_debug, mock_sandbox_execute):
        """Test debugging with sandbox validation"""
        # Mock orchestrator response
        mock_debug_session = Mock()
        mock_debug_session.success = True
        mock_debug_session.session_id = "test_456"
        mock_debug_session.iterations = [Mock(confidence=0.9)]
        mock_debug_session.final_fix = "fixed code"
        mock_debug_session.total_time = 3.0
        mock_orchestrator_debug.return_value = mock_debug_session
        
        # Mock sandbox result
        mock_sandbox_result = SandboxResult(
            all_tests_pass=True,
            test_results=[
                TestResult("test_user", True, 0.1),
                TestResult("test_login", True, 0.2)
            ],
            total_execution_time=1.5,
            coverage_before=75.0,
            coverage_after=78.0,
            memory_usage={'rss_mb': 100},
            performance_metrics={'cpu_impact': 'negligible'},
            security_violations=[],
            regression_detected=False
        )
        mock_sandbox_execute.return_value = mock_sandbox_result
        
        # Run debug
        result = self.chronos.debug(
            error_input="Test failure",
            input_type=InputType.TEST_OUTPUT,
            metadata={}
        )
        
        # Verify validation results
        self.assertTrue(result['success'])
        self.assertIn('validation', result)
        self.assertTrue(result['validation']['tests_pass'])
        self.assertEqual(result['validation']['coverage_change'], 3.0)
    
    @patch('architecture.explainability_layer.ExplainabilityLayer.generate_explanation')
    @patch('architecture.orchestration_controller.OrchestrationController.debug')
    def test_debug_with_explanation(self, mock_orchestrator_debug, mock_generate_explanation):
        """Test debugging with explanation generation"""
        # Mock orchestrator response
        mock_debug_session = Mock()
        mock_debug_session.success = True
        mock_debug_session.session_id = "test_789"
        mock_debug_session.iterations = [Mock(confidence=0.92)]
        mock_debug_session.final_fix = "fixed code"
        mock_debug_session.total_time = 4.0
        mock_orchestrator_debug.return_value = mock_debug_session
        
        # Mock explanation
        mock_explanation = Explanation(
            summary="Fixed null pointer issue with 92% confidence",
            root_cause="Variable 'user' was null",
            fix_description="Added null check before access",
            code_changes=[
                CodeChange(
                    file_path="user_service.py",
                    line_number=45,
                    change_type="modify",
                    original_code="return user['name']",
                    new_code="if user:\n    return user['name']",
                    reason="Added null safety check"
                )
            ],
            test_implications=["All tests pass"],
            confidence_factors={'overall': 0.92},
            alternative_solutions=["Use Optional type"]
        )
        mock_generate_explanation.return_value = mock_explanation
        
        # Run debug
        result = self.chronos.debug(
            error_input="NullPointerException",
            input_type=InputType.STACK_TRACE,
            metadata={}
        )
        
        # Verify explanation
        self.assertIn('explanation', result)
        self.assertIsNotNone(result['explanation'])
        self.assertIn('Fixed null pointer', result['explanation'])
    
    def test_debug_async(self):
        """Test async debugging interface"""
        async def run_async_test():
            # Mock the orchestrator
            with patch('architecture.orchestration_controller.OrchestrationController.debug') as mock_debug:
                mock_session = Mock()
                mock_session.success = True
                mock_session.session_id = "async_123"
                mock_session.iterations = []
                mock_session.final_fix = "async fix"
                mock_session.total_time = 1.0
                mock_debug.return_value = mock_session
                
                # Run async debug
                result = await self.chronos.debug_async(
                    error_input="Async error",
                    input_type=InputType.ERROR_LOG,
                    metadata={}
                )
                
                # Verify
                self.assertTrue(result['success'])
                self.assertEqual(result['session_id'], 'async_123')
        
        # Run async test
        asyncio.run(run_async_test())
    
    def test_input_parsing_stack_trace(self):
        """Test parsing different input types - stack trace"""
        stack_trace = """
IndexError: list index out of range
  File "processor.py", line 100, in process_batch
    item = items[index]
  File "main.py", line 50, in run
    process_batch(data)
"""
        
        result = self.chronos.debug(
            error_input=stack_trace,
            input_type=InputType.STACK_TRACE,
            metadata={'source': 'test'}
        )
        
        # Should extract error info correctly
        self.assertIn('error_info', result)
        self.assertEqual(result['error_info']['type'], 'index_error')
        self.assertIn('processor.py', result['error_info']['affected_files'])
    
    def test_input_parsing_test_output(self):
        """Test parsing different input types - test output"""
        test_output = {
            "failures": [
                {
                    "test_name": "test_authentication",
                    "error": "AssertionError: Login failed",
                    "stack_trace": "File 'tests/test_auth.py', line 30"
                }
            ],
            "test_suite": "auth_tests",
            "total_tests": 10,
            "passed": 9,
            "failed": 1
        }
        
        result = self.chronos.debug(
            error_input=test_output,
            input_type=InputType.TEST_OUTPUT,
            metadata={'ci': 'github_actions'}
        )
        
        # Should extract test failure info
        self.assertIn('error_info', result)
        self.assertIn('test_authentication', str(result['error_info']))
    
    def test_statistics_tracking(self):
        """Test statistics tracking"""
        initial_stats = self.chronos.orchestrator.get_statistics()
        initial_total = initial_stats['total_sessions']
        
        # Run a debug session
        with patch('architecture.orchestration_controller.OrchestrationController.debug') as mock_debug:
            mock_session = Mock()
            mock_session.success = True
            mock_session.iterations = [Mock(), Mock(), Mock()]  # 3 iterations
            mock_session.session_id = "stats_test"
            mock_session.final_fix = "fix"
            mock_session.total_time = 2.0
            mock_debug.return_value = mock_session
            
            self.chronos.debug(
                error_input="Error",
                input_type=InputType.ERROR_LOG,
                metadata={}
            )
        
        # Check updated statistics
        updated_stats = self.chronos.orchestrator.get_statistics()
        self.assertEqual(updated_stats['total_sessions'], initial_total + 1)
    
    def test_create_chronos_system_factory(self):
        """Test factory function"""
        system = create_chronos_system(
            repository_path="/test/repo",
            use_docker_sandbox=False,
            max_iterations=3
        )
        
        self.assertIsInstance(system, ChronosSystem)
        self.assertEqual(system.config.repository_path, "/test/repo")
        self.assertEqual(system.config.max_iterations, 3)
        self.assertFalse(system.config.use_docker_sandbox)


class TestChronosErrorHandling(unittest.TestCase):
    """Test error handling in Chronos system"""
    
    def setUp(self):
        """Set up test environment"""
        self.chronos = create_chronos_system(
            repository_path="/tmp/test",
            use_docker_sandbox=False,
            log_level="ERROR"
        )
    
    def test_invalid_input_type(self):
        """Test handling of invalid input type"""
        # Should handle gracefully and return error
        result = self.chronos.debug(
            error_input="Some error",
            input_type="invalid_type",  # Invalid
            metadata={}
        )
        
        # Should not crash, but indicate failure
        self.assertIn('error_info', result)
    
    @patch('architecture.orchestration_controller.OrchestrationController.debug')
    def test_orchestrator_exception(self, mock_debug):
        """Test handling of orchestrator exceptions"""
        # Mock orchestrator throwing exception
        mock_debug.side_effect = Exception("Orchestrator error")
        
        # Should handle gracefully
        result = self.chronos.debug(
            error_input="Error",
            input_type=InputType.ERROR_LOG,
            metadata={}
        )
        
        # Should indicate failure but not crash
        self.assertFalse(result.get('success', False))
    
    def test_empty_input(self):
        """Test handling of empty input"""
        result = self.chronos.debug(
            error_input="",
            input_type=InputType.STACK_TRACE,
            metadata={}
        )
        
        # Should handle empty input gracefully
        self.assertIsNotNone(result)
        self.assertIn('session_id', result)


if __name__ == '__main__':
    unittest.main()