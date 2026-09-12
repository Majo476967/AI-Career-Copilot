"""Small shared boundary: expose readable storage errors, with no retry side effects."""
import sqlite3
from functools import wraps
from core.errors import BusinessError


def storage_errors(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except sqlite3.Error:
            raise BusinessError("storage_error", "数据库操作失败，已取消本次写入，请稍后重试。") from None
    return wrapped
