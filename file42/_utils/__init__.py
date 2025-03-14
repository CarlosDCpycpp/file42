from pprint import pformat
from functools import wraps
from typing import (
    NoReturn,
    Callable,
    Optional,
    Any
)

from .null import Null  # access


Matrix = Optional[list[list[Optional[Any]]]]


def raise_if(
        error: type[Exception] | Exception,
        *conditions,
        spec: str = 'and'
) -> None | NoReturn:

    raise_flag: bool = {
        'and': all,
        'or': any,
        'xor': lambda *args: sum(args) == 1
    }[spec.lower().strip()](conditions)

    if raise_flag:
        raise error


def not_implemented(func: Callable) -> Callable:
    print(f'\033[31mFunction "{func.__name__}" is not implemented.\033[0m')

    @wraps(func)
    def wrapper(*args, **kwargs) -> NoReturn:  # NOQA
        raise NotImplementedError(f'Not implemented function "{func.__name__}" run.')
    return wrapper


def return_list(func: Callable) -> Callable[[...], list]:
    def wrapper(*args, **kwargs) -> list:
        return list(func(*args, **kwargs))
    return wrapper


def pformat_return(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> str:
        return pformat(func(*args, **kwargs))
    return wrapper


def applied(
        applied_func: Callable,
        unpack: bool = False,
        unpack_dict: bool = False
) -> Callable[[Callable], Callable]:

    def decorator(func: Callable) -> Callable:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            if unpack:
                return applied_func(*func(*args, **kwargs))

            elif unpack_dict:
                return applied_func(**func(*args, **kwargs))

            return applied_func(func(*args, **kwargs))

        return wrapper

    return decorator


def base_value(value: str) -> Any:

    for typ in int, float:
        try:
            return typ(value)
        except ValueError:
            pass

    bool_none_map: dict[str, bool | None] = {
        'true': True,
        'false': False,
        'none': None,
        '': None
    }

    bool_none_value = bool_none_map.get(value.lower().strip(), Null)

    return bool_none_value if bool_none_value is not Null else value
