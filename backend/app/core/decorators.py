"""Decorators for error handling and cross-cutting concerns.

These decorators provide consistent error handling across services and repositories,
reducing code duplication and improving maintainability.
"""

import functools
import time
from typing import Callable, Any
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.exceptions import ValidationError, NotFoundError, ConflictError
from app.core.logging import logger


def handle_service_errors(func: Callable) -> Callable:
    """Decorator to handle common service-layer errors.
    
    Catches and converts exceptions from repositories and business logic
    into appropriate HTTP exceptions.
    
    Usage:
        @handle_service_errors
        async def create_user(self, user_data: UserCreate) -> User:
            # ... service logic
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            # Business logic validation errors
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            raise ValidationError(str(e))
        except LookupError as e:
            # Not found errors (e.g., KeyError, IndexError)
            logger.warning(f"Resource not found in {func.__name__}: {str(e)}")
            raise NotFoundError("Resource", "unknown")
        except Exception as e:
            # Unexpected errors
            logger.error(
                f"Unexpected error in {func.__name__}: {str(e)}", 
                exc_info=True
            )
            raise ValidationError(f"An unexpected error occurred: {str(e)}")
    
    return wrapper


def handle_repository_errors(func: Callable) -> Callable:
    """Decorator to handle database-related errors in repositories.
    
    Catches SQLAlchemy exceptions and converts them into application exceptions.
    
    Usage:
        @handle_repository_errors
        async def create(self, data: CreateSchema) -> Model:
            # ... repository logic
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            # Database constraint violations (unique, foreign key, etc.)
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            logger.warning(f"Integrity error in {func.__name__}: {error_msg}")
            
            # Try to extract meaningful message
            if "unique constraint" in error_msg.lower() or "duplicate" in error_msg.lower():
                raise ConflictError("Resource already exists")
            elif "foreign key constraint" in error_msg.lower():
                raise ValidationError("Referenced resource does not exist")
            else:
                raise ConflictError(f"Database constraint violation: {error_msg}")
                
        except SQLAlchemyError as e:
            # Other database errors
            logger.error(
                f"Database error in {func.__name__}: {str(e)}", 
                exc_info=True
            )
            raise ValidationError(f"Database error: {str(e)}")
        except Exception as e:
            # Unexpected errors
            logger.error(
                f"Unexpected error in {func.__name__}: {str(e)}", 
                exc_info=True
            )
            raise
    
    return wrapper


def log_execution_time(func: Callable) -> Callable:
    """Decorator to log execution time of functions.
    
    Useful for identifying performance bottlenecks in services and repositories.
    
    Usage:
        @log_execution_time
        async def get_complex_report(self, ...):
            # ... complex logic
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 1.0:  # Log if slower than 1 second
                logger.warning(
                    f"Slow operation: {func.__name__} took {execution_time:.2f}s"
                )
            else:
                logger.debug(
                    f"{func.__name__} executed in {execution_time:.3f}s"
                )
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.3f}s: {str(e)}"
            )
            raise
    
    return wrapper


def retry_on_db_lock(max_retries: int = 3, delay: float = 0.1):
    """Decorator to retry operations on database lock errors.
    
    Useful for handling transient database lock issues in high-concurrency scenarios.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Usage:
        @retry_on_db_lock(max_retries=3, delay=0.1)
        async def update_with_lock(self, ...):
            # ... update logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import asyncio
            
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except SQLAlchemyError as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Check if it's a lock-related error
                    if "lock" in error_msg or "deadlock" in error_msg:
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Database lock detected in {func.__name__}, "
                                f"retry {attempt + 1}/{max_retries}"
                            )
                            await asyncio.sleep(delay * (attempt + 1))  # Exponential backoff
                            continue
                        # If it's the last attempt and still a lock error, exit loop to raise
                        break
                    # If not a lock error, don't retry - raise immediately
                    raise
            
            # All retries exhausted (lines 171-172)
            logger.error(f"Max retries exceeded in {func.__name__}")
            if last_exception is not None:
                raise last_exception
            # Fallback: raise a generic exception if last_exception is None (shouldn't happen)
            raise RuntimeError(f"Max retries exceeded in {func.__name__}") from None
        
        return wrapper
    return decorator


def validate_not_none(*param_names: str):
    """Decorator to validate that specified parameters are not None.
    
    Args:
        *param_names: Names of parameters to validate
        
    Usage:
        @validate_not_none('user_id', 'email')
        async def update_user(self, user_id: int, email: str):
            # ... update logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Get function signature to map args to param names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Check each parameter
            for param_name in param_names:
                if param_name in bound_args.arguments:
                    if bound_args.arguments[param_name] is None:
                        raise ValueError(f"Parameter '{param_name}' cannot be None")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def cache_result(ttl_seconds: int = 300):
    """Decorator to cache function results for a specified time.
    
    Note: This is a simple in-memory cache. For production, use Redis or similar.
    
    Args:
        ttl_seconds: Time to live for cached results in seconds
        
    Usage:
        @cache_result(ttl_seconds=60)
        async def get_expensive_data(self):
            # ... expensive operation
    """
    cache: dict[str, tuple[Any, float]] = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import hashlib
            import json
            
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hashlib.md5(json.dumps(str(args) + str(kwargs), sort_keys=True).encode()).hexdigest()}"
            
            # Check if cached result exists and is still valid
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            # Simple cache cleanup (remove expired entries)
            if len(cache) > 1000:  # Prevent unbounded growth
                current_time = time.time()
                expired_keys = [
                    k for k, (_, ts) in cache.items() 
                    if current_time - ts >= ttl_seconds
                ]
                for k in expired_keys:
                    del cache[k]
            
            return result
        
        return wrapper
    return decorator


__all__ = [
    "handle_service_errors",
    "handle_repository_errors",
    "log_execution_time",
    "retry_on_db_lock",
    "validate_not_none",
    "cache_result",
]
