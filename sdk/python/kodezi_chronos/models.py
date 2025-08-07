"""
Data models for Kodezi Chronos SDK
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator


class InputType(str, Enum):
    """Types of debugging inputs"""
    STACK_TRACE = "stack_trace"
    ERROR_LOG = "error_log"
    TEST_OUTPUT = "test_output"
    CI_CD_LOG = "ci_cd_log"
    PERFORMANCE_PROFILE = "performance_profile"
    USER_REPORT = "user_report"
    MONITORING_ALERT = "monitoring_alert"
    API_RESPONSE = "api_response"
    CODE_REVIEW = "code_review"
    DEBUGGER_OUTPUT = "debugger_output"


class DebugStatus(str, Enum):
    """Status of debugging operation"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CodeChange(BaseModel):
    """Represents a code change in a file"""
    file_path: str
    line_number: int
    change_type: str  # add, modify, delete
    original_code: Optional[str] = None
    new_code: Optional[str] = None
    reason: str


class ValidationResult(BaseModel):
    """Test validation results"""
    tests_pass: bool
    coverage_change: float
    performance_impact: Dict[str, str]
    regression_detected: bool = False
    failed_tests: List[str] = Field(default_factory=list)


class DebugRequest(BaseModel):
    """Request model for debugging"""
    error_input: Union[str, Dict[str, Any]]
    input_type: InputType
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('error_input')
    def validate_error_input(cls, v, values):
        """Validate error input based on type"""
        input_type = values.get('input_type')
        
        if input_type in [InputType.STACK_TRACE, InputType.ERROR_LOG, InputType.CI_CD_LOG]:
            if not isinstance(v, str):
                raise ValueError(f"{input_type} requires string input")
        elif input_type in [InputType.TEST_OUTPUT, InputType.PERFORMANCE_PROFILE]:
            if not isinstance(v, (dict, str)):
                raise ValueError(f"{input_type} requires dict or string input")
        
        return v


class DebugResponse(BaseModel):
    """Response model for debugging"""
    session_id: str
    success: bool
    total_time: float
    iterations: int
    error_info: Optional[Dict[str, Any]] = None
    fix: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    validation: Optional[ValidationResult] = None
    statistics: Optional[Dict[str, Any]] = None
    
    @property
    def confidence(self) -> float:
        """Get confidence score"""
        if self.fix and 'confidence' in self.fix:
            return self.fix['confidence']
        return 0.0
    
    @property
    def files_changed(self) -> List[str]:
        """Get list of changed files"""
        if self.fix and 'files' in self.fix:
            return list(self.fix['files'].keys())
        return []


class BatchDebugRequest(BaseModel):
    """Request for batch debugging"""
    issues: List[Dict[str, Any]]
    
    @validator('issues')
    def validate_issues(cls, v):
        """Validate each issue has required fields"""
        for issue in v:
            if 'error_input' not in issue:
                raise ValueError("Each issue must have 'error_input'")
            if 'input_type' not in issue:
                raise ValueError("Each issue must have 'input_type'")
        return v


class BatchDebugResponse(BaseModel):
    """Response for batch debugging"""
    total: int
    successful: int
    results: List[Dict[str, Any]]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        return self.successful / self.total if self.total > 0 else 0


class JobStatus(BaseModel):
    """Status of async debugging job"""
    job_id: str
    status: DebugStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if job is complete"""
        return self.status in [DebugStatus.COMPLETED, DebugStatus.FAILED]
    
    @property
    def duration(self) -> Optional[float]:
        """Get job duration in seconds"""
        if self.created_at and self.completed_at:
            return (self.completed_at - self.created_at).total_seconds()
        return None


class SystemStats(BaseModel):
    """System statistics"""
    total_sessions: int
    success_rate: str
    average_iterations: float
    cache_hit_rate: str
    memory_sessions: int
    system_uptime: str
    
    @property
    def success_rate_float(self) -> float:
        """Get success rate as float"""
        return float(self.success_rate.rstrip('%')) / 100
    
    @property
    def cache_hit_rate_float(self) -> float:
        """Get cache hit rate as float"""
        return float(self.cache_hit_rate.rstrip('%')) / 100


class HealthStatus(BaseModel):
    """System health status"""
    status: str
    chronos: bool
    layers: Dict[str, str]
    statistics: Dict[str, Any]
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return (self.status == "healthy" and 
                all(status == "ready" for status in self.layers.values()))