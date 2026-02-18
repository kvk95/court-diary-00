# app\database\repositories\base\repo_context.py
from functools import wraps
from inspect import iscoroutinefunction


# Import the ContextVar directly to restore safely


def repo_context(name: str):
    """Decorator for individual async repo methods."""

    def decorator(func):
        if not iscoroutinefunction(func):
            raise TypeError("repo_context can only be applied to async functions")

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            return await func(self, *args, **kwargs)

        return wrapper

    return decorator



def apply_repo_context(repo_class):
    """
    Class decorator that:
    - wraps ONLY async methods defined on the repo itself
    - skips inherited methods from BaseRepository
    - names repo context as RepoClassName.method_name
    """
    from app.database.repositories.base.base_repository import BaseRepository

    for attr_name, attr_value in repo_class.__dict__.items():
        # Skip "private" items
        if attr_name.startswith("_"):
            continue

        # Skip anything not callable or not async
        if not callable(attr_value) or not iscoroutinefunction(attr_value):
            continue

        # Skip inherited methods from BaseRepository
        if hasattr(BaseRepository, attr_name):
            continue

        # Decorate the repo's own async method
        decorated = repo_context(f"{repo_class.__name__}.{attr_name}")(attr_value)
        setattr(repo_class, attr_name, decorated)

    return repo_class