import time
from functools import wraps


def sleep_after(time_sleep):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            time.sleep(time_sleep)
            return result
        return wrapper
    return decorator
