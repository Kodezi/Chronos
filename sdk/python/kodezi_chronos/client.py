"""
Kodezi Chronos Client Implementation
"""

import os
import json
import time
from typing import Dict, List, Optional, Union, Any
import requests
import aiohttp
import asyncio
from datetime import datetime

from .models import (
    DebugRequest, DebugResponse, InputType, DebugStatus,
    BatchDebugRequest, BatchDebugResponse, JobStatus
)
from .exceptions import (
    ChronosException, AuthenticationError, RateLimitError,
    DebugTimeoutError, ValidationError
)


class ChronosClient:
    """Synchronous client for Kodezi Chronos API"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 base_url: str = "https://api.kodezi.com/chronos/v1",
                 timeout: int = 600,
                 max_retries: int = 3):
        """
        Initialize Chronos client
        
        Args:
            api_key: API key for authentication (can also use CHRONOS_API_KEY env var)
            base_url: Base URL for Chronos API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key or os.getenv("CHRONOS_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key required. Set CHRONOS_API_KEY or pass api_key parameter")
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "kodezi-chronos-python/2025.1.0"
        })
    
    def debug(self, 
              error_input: Union[str, Dict],
              input_type: InputType,
              metadata: Optional[Dict[str, Any]] = None,
              wait_for_result: bool = True) -> DebugResponse:
        """
        Submit a debugging request
        
        Args:
            error_input: Error information (stack trace, log, etc.)
            input_type: Type of input (InputType enum)
            metadata: Additional metadata
            wait_for_result: Wait for result (True) or return job ID (False)
            
        Returns:
            DebugResponse with results or job information
        """
        request = DebugRequest(
            error_input=error_input,
            input_type=input_type,
            metadata=metadata or {}
        )
        
        endpoint = "/debug" if wait_for_result else "/debug/async"
        response = self._make_request("POST", endpoint, data=request.dict())
        
        if wait_for_result:
            return DebugResponse(**response)
        else:
            # For async, poll for results
            job_id = response["job_id"]
            return self._wait_for_job(job_id)
    
    def debug_batch(self, issues: List[Dict[str, Any]]) -> BatchDebugResponse:
        """
        Debug multiple issues in batch
        
        Args:
            issues: List of issues to debug
            
        Returns:
            BatchDebugResponse with results for all issues
        """
        request = BatchDebugRequest(issues=issues)
        response = self._make_request("POST", "/debug/batch", data=request.dict())
        return BatchDebugResponse(**response)
    
    def get_job_status(self, job_id: str) -> JobStatus:
        """
        Get status of async debugging job
        
        Args:
            job_id: Job ID from async debug request
            
        Returns:
            JobStatus with current status and results if complete
        """
        response = self._make_request("GET", f"/debug/status/{job_id}")
        return JobStatus(**response)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get debugging statistics"""
        return self._make_request("GET", "/stats")
    
    def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        return self._make_request("GET", "/health")
    
    def _make_request(self, method: str, endpoint: str, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with retries"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    response = self.session.get(url, timeout=self.timeout)
                else:
                    response = self.session.post(
                        url, 
                        json=data, 
                        timeout=self.timeout
                    )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 202:
                    return response.json()  # Async accepted
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 429:
                    # Rate limited - check headers and wait
                    retry_after = int(response.headers.get("X-RateLimit-Reset", 60))
                    if attempt < self.max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds")
                else:
                    error_data = response.json()
                    raise ChronosException(f"API error: {error_data.get('error', 'Unknown error')}")
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise DebugTimeoutError("Request timed out")
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise ChronosException(f"Request failed: {str(e)}")
        
        raise ChronosException("Max retries exceeded")
    
    def _wait_for_job(self, job_id: str, poll_interval: int = 2) -> DebugResponse:
        """Wait for async job to complete"""
        start_time = time.time()
        
        while True:
            if time.time() - start_time > self.timeout:
                raise DebugTimeoutError(f"Job {job_id} timed out")
            
            status = self.get_job_status(job_id)
            
            if status.status == "completed":
                return DebugResponse(**status.result)
            elif status.status == "failed":
                raise ChronosException(f"Debug job failed: {status.error}")
            
            time.sleep(poll_interval)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


class AsyncChronosClient:
    """Asynchronous client for Kodezi Chronos API"""
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 base_url: str = "https://api.kodezi.com/chronos/v1",
                 timeout: int = 600,
                 max_retries: int = 3):
        """Initialize async Chronos client"""
        self.api_key = api_key or os.getenv("CHRONOS_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key required")
        
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "kodezi-chronos-python/2025.1.0"
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def debug(self,
                   error_input: Union[str, Dict],
                   input_type: InputType,
                   metadata: Optional[Dict[str, Any]] = None,
                   wait_for_result: bool = True) -> DebugResponse:
        """Async debug request"""
        request = DebugRequest(
            error_input=error_input,
            input_type=input_type,
            metadata=metadata or {}
        )
        
        endpoint = "/debug" if wait_for_result else "/debug/async"
        response = await self._make_request("POST", endpoint, data=request.dict())
        
        if wait_for_result:
            return DebugResponse(**response)
        else:
            job_id = response["job_id"]
            return await self._wait_for_job(job_id)
    
    async def debug_batch(self, issues: List[Dict[str, Any]]) -> BatchDebugResponse:
        """Async batch debug"""
        request = BatchDebugRequest(issues=issues)
        response = await self._make_request("POST", "/debug/batch", data=request.dict())
        return BatchDebugResponse(**response)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get debugging statistics"""
        return await self._make_request("GET", "/stats")
    
    async def _make_request(self, method: str, endpoint: str,
                          data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make async HTTP request with retries"""
        if not self.session:
            raise ChronosException("Session not initialized. Use 'async with' context manager")
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    async with self.session.get(url) as response:
                        return await self._handle_response(response, attempt)
                else:
                    async with self.session.post(url, json=data) as response:
                        return await self._handle_response(response, attempt)
                        
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise DebugTimeoutError("Request timed out")
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise ChronosException(f"Request failed: {str(e)}")
        
        raise ChronosException("Max retries exceeded")
    
    async def _handle_response(self, response: aiohttp.ClientResponse, 
                             attempt: int) -> Dict[str, Any]:
        """Handle API response"""
        if response.status in (200, 202):
            return await response.json()
        elif response.status == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status == 429:
            retry_after = int(response.headers.get("X-RateLimit-Reset", 60))
            if attempt < self.max_retries - 1:
                await asyncio.sleep(retry_after)
                raise  # Retry
            raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after}s")
        else:
            error_data = await response.json()
            raise ChronosException(f"API error: {error_data.get('error', 'Unknown')}")
    
    async def _wait_for_job(self, job_id: str, poll_interval: int = 2) -> DebugResponse:
        """Wait for async job completion"""
        start_time = time.time()
        
        while True:
            if time.time() - start_time > self.timeout.total:
                raise DebugTimeoutError(f"Job {job_id} timed out")
            
            response = await self._make_request("GET", f"/debug/status/{job_id}")
            status = JobStatus(**response)
            
            if status.status == "completed":
                return DebugResponse(**status.result)
            elif status.status == "failed":
                raise ChronosException(f"Debug job failed: {status.error}")
            
            await asyncio.sleep(poll_interval)