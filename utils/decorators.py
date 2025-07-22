import functools
from fastapi import HTTPException

def api_exception_handler(logger=None, default_status=500, default_detail="Internal Server Error"):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                if logger:
                    logger.error(f"{func.__name__} error: {e}")
                raise HTTPException(status_code=default_status, detail=f"{default_detail}: {str(e)}")
        return wrapper
    return decorator 