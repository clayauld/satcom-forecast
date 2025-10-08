"""
API Error Handling Framework

This module provides comprehensive error handling for API operations,
including retry logic, fallback mechanisms, and error reporting.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories."""
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    DATA_ERROR = "data_error"
    CONFIGURATION_ERROR = "configuration_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    AUTHENTICATION_ERROR = "authentication_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorContext:
    """Context information for an error."""
    operation: str
    coordinates: Optional[tuple] = None
    endpoint: Optional[str] = None
    retry_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    user_agent: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class ErrorInfo:
    """Information about an error."""
    error_type: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    original_exception: Optional[Exception] = None
    retryable: bool = True
    fallback_available: bool = True
    recovery_suggestion: Optional[str] = None


class APIError(Exception):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, error_info: Optional[ErrorInfo] = None):
        super().__init__(message)
        self.error_info = error_info


class RetryableError(APIError):
    """Error that can be retried."""
    pass


class NonRetryableError(APIError):
    """Error that should not be retried."""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded error."""
    pass


class TimeoutError(APIError):
    """Request timeout error."""
    pass


class DataValidationError(APIError):
    """Data validation error."""
    pass


class ErrorHandler:
    """Handles errors with retry logic and fallback mechanisms."""
    
    def __init__(self, 
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 backoff_factor: float = 2.0,
                 jitter: bool = True):
        """
        Initialize error handler.
        
        Args:
            max_retries: Maximum number of retries
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_factor: Exponential backoff factor
            jitter: Whether to add jitter to delays
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.error_stats: Dict[str, int] = {}
        self.error_history: List[ErrorInfo] = []
        
    def classify_error(self, exception: Exception, context: ErrorContext) -> ErrorInfo:
        """
        Classify an error and determine handling strategy.
        
        Args:
            exception: The exception that occurred
            context: Error context information
            
        Returns:
            ErrorInfo object with classification
        """
        error_type = type(exception).__name__
        message = str(exception)
        
        # Determine category and severity
        if isinstance(exception, (ConnectionError, OSError)):
            category = ErrorCategory.NETWORK_ERROR
            severity = ErrorSeverity.MEDIUM
            retryable = True
            fallback_available = True
            recovery_suggestion = "Check network connectivity and retry"
        elif isinstance(exception, asyncio.TimeoutError):
            category = ErrorCategory.TIMEOUT_ERROR
            severity = ErrorSeverity.MEDIUM
            retryable = True
            fallback_available = True
            recovery_suggestion = "Increase timeout or retry with exponential backoff"
        elif "429" in message or "rate limit" in message.lower():
            category = ErrorCategory.RATE_LIMIT_ERROR
            severity = ErrorSeverity.MEDIUM
            retryable = True
            fallback_available = True
            recovery_suggestion = "Wait and retry with increased delay"
        elif "401" in message or "403" in message:
            category = ErrorCategory.AUTHENTICATION_ERROR
            severity = ErrorSeverity.HIGH
            retryable = False
            fallback_available = True
            recovery_suggestion = "Check API credentials and configuration"
        elif "404" in message:
            category = ErrorCategory.API_ERROR
            severity = ErrorSeverity.MEDIUM
            retryable = False
            fallback_available = True
            recovery_suggestion = "Check coordinates and API endpoint"
        elif "500" in message or "502" in message or "503" in message:
            category = ErrorCategory.API_ERROR
            severity = ErrorSeverity.HIGH
            retryable = True
            fallback_available = True
            recovery_suggestion = "Server error, retry with exponential backoff"
        elif isinstance(exception, (ValueError, TypeError)):
            category = ErrorCategory.VALIDATION_ERROR
            severity = ErrorSeverity.LOW
            retryable = False
            fallback_available = False
            recovery_suggestion = "Check input parameters and data format"
        else:
            category = ErrorCategory.UNKNOWN_ERROR
            severity = ErrorSeverity.MEDIUM
            retryable = True
            fallback_available = True
            recovery_suggestion = "Retry or use fallback mechanism"
            
        error_info = ErrorInfo(
            error_type=error_type,
            message=message,
            severity=severity,
            category=category,
            context=context,
            original_exception=exception,
            retryable=retryable,
            fallback_available=fallback_available,
            recovery_suggestion=recovery_suggestion
        )
        
        # Update statistics
        self.error_stats[error_type] = self.error_stats.get(error_type, 0) + 1
        self.error_history.append(error_info)
        
        # Keep only last 100 errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
            
        return error_info
        
    async def handle_error(self, 
                          error: Exception, 
                          context: ErrorContext,
                          retry_func: Optional[Callable] = None,
                          fallback_func: Optional[Callable] = None) -> Any:
        """
        Handle an error with retry logic and fallback.
        
        Args:
            error: The exception that occurred
            context: Error context information
            retry_func: Function to retry (if retryable)
            fallback_func: Function to use as fallback
            
        Returns:
            Result from retry or fallback function
            
        Raises:
            APIError: If all retries and fallback fail
        """
        error_info = self.classify_error(error, context)
        
        # Log the error
        self._log_error(error_info)
        
        # Try retry if retryable and retry function provided
        if error_info.retryable and retry_func and context.retry_count < self.max_retries:
            context.retry_count += 1
            delay = self._calculate_delay(context.retry_count)
            
            _LOGGER.warning(f"Retrying {context.operation} in {delay:.2f}s (attempt {context.retry_count}/{self.max_retries})")
            await asyncio.sleep(delay)
            
            try:
                return await retry_func()
            except Exception as retry_error:
                return await self.handle_error(retry_error, context, retry_func, fallback_func)
                
        # Try fallback if available and fallback function provided
        if error_info.fallback_available and fallback_func:
            _LOGGER.warning(f"Using fallback for {context.operation}")
            try:
                return await fallback_func()
            except Exception as fallback_error:
                _LOGGER.error(f"Fallback also failed: {fallback_error}")
                
        # All options exhausted, raise error
        raise APIError(
            f"Operation {context.operation} failed after {context.retry_count} retries: {error_info.message}",
            error_info
        )
        
    def _calculate_delay(self, retry_count: int) -> float:
        """Calculate delay for retry with exponential backoff and jitter."""
        delay = min(self.base_delay * (self.backoff_factor ** (retry_count - 1)), self.max_delay)
        
        if self.jitter:
            # Add random jitter (±25%)
            import random
            jitter_factor = random.uniform(0.75, 1.25)
            delay *= jitter_factor
            
        return delay
        
    def _log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level based on severity."""
        context = error_info.context
        log_message = (
            f"Error in {context.operation}: {error_info.message} "
            f"(Category: {error_info.category.value}, Severity: {error_info.severity.value})"
        )
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            _LOGGER.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            _LOGGER.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            _LOGGER.warning(log_message)
        else:
            _LOGGER.info(log_message)
            
        if error_info.recovery_suggestion:
            _LOGGER.info(f"Recovery suggestion: {error_info.recovery_suggestion}")
            
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        total_errors = sum(self.error_stats.values())
        recent_errors = len([e for e in self.error_history if e.context.timestamp > datetime.now() - timedelta(hours=1)])
        
        return {
            'total_errors': total_errors,
            'recent_errors': recent_errors,
            'error_types': self.error_stats.copy(),
            'error_categories': self._get_category_stats(),
            'error_severities': self._get_severity_stats()
        }
        
    def _get_category_stats(self) -> Dict[str, int]:
        """Get error statistics by category."""
        categories = {}
        for error in self.error_history:
            category = error.category.value
            categories[category] = categories.get(category, 0) + 1
        return categories
        
    def _get_severity_stats(self) -> Dict[str, int]:
        """Get error statistics by severity."""
        severities = {}
        for error in self.error_history:
            severity = error.severity.value
            severities[severity] = severities.get(severity, 0) + 1
        return severities
        
    def get_recent_errors(self, hours: int = 24) -> List[ErrorInfo]:
        """Get recent errors within specified hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [e for e in self.error_history if e.context.timestamp > cutoff]
        
    def clear_error_history(self):
        """Clear error history and statistics."""
        self.error_stats.clear()
        self.error_history.clear()
        _LOGGER.info("Error history cleared")


class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures."""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
            expected_exception: Exception type to count as failures
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            APIError: If circuit is open
        """
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise APIError("Circuit breaker is OPEN")
                
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
            
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
        
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "CLOSED"
        
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            _LOGGER.warning(f"Circuit breaker opened after {self.failure_count} failures")
            
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state."""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time,
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout
        }


# Global error handler instance
error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler."""
    return error_handler


def create_error_context(operation: str, 
                        coordinates: Optional[tuple] = None,
                        endpoint: Optional[str] = None,
                        user_agent: Optional[str] = None) -> ErrorContext:
    """Create error context for an operation."""
    return ErrorContext(
        operation=operation,
        coordinates=coordinates,
        endpoint=endpoint,
        user_agent=user_agent
    )