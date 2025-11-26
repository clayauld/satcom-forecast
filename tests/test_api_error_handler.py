"""Test the API Error Handler."""

import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.satcom_forecast.api_error_handler import (
    APIError,
    CircuitBreaker,
    ErrorCategory,
    ErrorContext,
    ErrorHandler,
    ErrorInfo,
    ErrorSeverity,
    create_error_context,
)


@pytest.fixture
def error_handler():
    """Create an ErrorHandler instance."""
    return ErrorHandler(max_retries=2, base_delay=0.01, jitter=False)


def test_classify_error(error_handler):
    """Test error classification."""
    context = create_error_context("test_op")

    # Network error
    error = ConnectionError("Connection refused")
    info = error_handler.classify_error(error, context)
    assert info.category == ErrorCategory.NETWORK_ERROR
    assert info.severity == ErrorSeverity.MEDIUM
    assert info.retryable is True

    # Timeout error
    error = asyncio.TimeoutError()
    info = error_handler.classify_error(error, context)
    assert info.category == ErrorCategory.TIMEOUT_ERROR
    assert info.retryable is True

    # Rate limit error
    error = Exception("429 Too Many Requests")
    info = error_handler.classify_error(error, context)
    assert info.category == ErrorCategory.RATE_LIMIT_ERROR
    assert info.retryable is True

    # Auth error
    error = Exception("401 Unauthorized")
    info = error_handler.classify_error(error, context)
    assert info.category == ErrorCategory.AUTHENTICATION_ERROR
    assert info.retryable is False

    # Validation error
    error = ValueError("Invalid input")
    info = error_handler.classify_error(error, context)
    assert info.category == ErrorCategory.VALIDATION_ERROR
    assert info.retryable is False

    # Unknown error
    error = Exception("Unknown error")
    info = error_handler.classify_error(error, context)
    assert info.category == ErrorCategory.UNKNOWN_ERROR


async def test_handle_error_retry(error_handler):
    """Test handle_error with retry."""
    context = create_error_context("test_op")
    retry_func = AsyncMock()
    retry_func.side_effect = [ConnectionError("Fail 1"), "Success"]

    result = await error_handler.handle_error(
        ConnectionError("Initial fail"), context, retry_func=retry_func
    )

    assert result == "Success"
    assert retry_func.call_count == 2  # Initial fail + 1 retry success? No.
    # handle_error is called with an exception. It calls retry_func.
    # retry_func raises ConnectionError("Fail 1").
    # handle_error catches it and calls itself recursively.
    # Second call calls retry_func again. It returns "Success".

    # Wait, retry_func is called inside handle_error.
    # First call to handle_error: context.retry_count=0. Increments to 1. Calls retry_func.
    # retry_func raises. handle_error catches and recurses.
    # Second call to handle_error: context.retry_count=1. Increments to 2. Calls retry_func.
    # retry_func returns "Success".

    # So retry_func called twice.
    assert retry_func.call_count == 2


async def test_handle_error_max_retries_exceeded(error_handler):
    """Test handle_error when max retries exceeded."""
    context = create_error_context("test_op")
    retry_func = AsyncMock(side_effect=ConnectionError("Fail"))

    with pytest.raises(APIError) as excinfo:
        await error_handler.handle_error(
            ConnectionError("Initial fail"), context, retry_func=retry_func
        )

    assert "failed after 2 retries" in str(excinfo.value)


async def test_handle_error_fallback(error_handler):
    """Test handle_error with fallback."""
    context = create_error_context("test_op")
    retry_func = AsyncMock(side_effect=Exception("Non-retryable"))
    fallback_func = AsyncMock(return_value="Fallback success")

    result = await error_handler.handle_error(
        Exception("401 Unauthorized"),
        context,
        retry_func=retry_func,
        fallback_func=fallback_func,
    )

    assert result == "Fallback success"
    # Retry func should NOT be called for non-retryable error
    retry_func.assert_not_called()
    fallback_func.assert_called_once()


def test_get_error_stats(error_handler):
    """Test get_error_stats."""
    context = create_error_context("test_op")
    error_handler.classify_error(ConnectionError("Fail"), context)
    error_handler.classify_error(ValueError("Invalid"), context)

    stats = error_handler.get_error_stats()
    assert stats["total_errors"] == 2
    assert stats["error_types"]["ConnectionError"] == 1
    assert stats["error_types"]["ValueError"] == 1


async def test_circuit_breaker():
    """Test CircuitBreaker."""
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
    func = AsyncMock()

    # Success case
    func.return_value = "Success"
    assert await cb.call(func) == "Success"
    assert cb.state == "CLOSED"
    assert cb.failure_count == 0

    # Failure case
    func.side_effect = Exception("Fail")
    with pytest.raises(Exception):
        await cb.call(func)
    assert cb.failure_count == 1
    assert cb.state == "CLOSED"

    with pytest.raises(Exception):
        await cb.call(func)
    assert cb.failure_count == 2
    assert cb.state == "OPEN"

    # Circuit open
    with pytest.raises(APIError, match="Circuit breaker is OPEN"):
        await cb.call(func)

    # Wait for recovery
    await asyncio.sleep(0.15)

    # Half-open
    func.side_effect = None
    func.return_value = "Recovered"
    assert await cb.call(func) == "Recovered"
    assert cb.state == "CLOSED"
    assert cb.failure_count == 0
