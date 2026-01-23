"""Rate limiting configuration (optional, disabled by default)."""

import os
from typing import Callable, Any
from functools import wraps

# Check if rate limiting is enabled via environment variable
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true"

if ENABLE_RATE_LIMITING:
    try:
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        
        limiter = Limiter(key_func=get_remote_address)
        RateLimitExceededException = RateLimitExceeded
    except ImportError:
        # If slowapi is not installed, disable rate limiting
        ENABLE_RATE_LIMITING = False
        limiter = None
        RateLimitExceededException = Exception
else:
    limiter = None
    RateLimitExceededException = Exception


def rate_limit(limit: str = "10/minute") -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for rate limiting endpoints.
    
    This decorator only applies rate limiting if ENABLE_RATE_LIMITING
    environment variable is set to "true". Otherwise, it's a no-op.
    
    Args:
        limit: Rate limit string (e.g., "10/minute", "100/hour")
    
    Example:
        @router.post("/login")
        @rate_limit("5/minute")
        async def login(...):
            ...
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if ENABLE_RATE_LIMITING and limiter is not None:
            # Apply actual rate limiting
            return limiter.limit(limit)(func)  # type: ignore[no-any-return]
        else:
            # No rate limiting, just return the function as-is
            return func
    return decorator


__all__ = ["rate_limit", "limiter", "ENABLE_RATE_LIMITING", "RateLimitExceededException"]

