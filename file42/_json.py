from __future__ import annotations

from ._file_abc import FileABC
from ._utils import pformat_return, applied

import json
from typing import Any, Callable, Iterable
from functools import wraps


class JsonFile(FileABC):

    @property
    def data(self) -> dict[str, Any]:
        try:
            with open(self.file, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    @property
    def _content(self) -> dict[str, Any]:
        return self.data

    @pformat_return
    def __str__(self) -> str:
        return self.data  # NOQA

    @property
    @applied(dict.keys)
    def keys(self):
        return self.data

    @property
    @applied(dict.values)
    def values(self):
        return self.data

    @property
    @applied(dict.items)
    def items(self):
        return self.data

    def rewrite(self, content: Any) -> None:
        with open(self.file, 'w') as file:
            json.dump(content, file, indent=4)

    def remove(self, key: str) -> None:
        content = self._content
        if key in content:
            del content[key]
            self.rewrite(content)

    def __getitem__(self, item: str) -> Any:
        return self.data[item]

    @applied(dict.get, unpack=True)
    def get(self, item, subs_value):
        return self.data, item, subs_value

    def __setitem__(self, key: str, value: Any) -> None:
        (temp_data := self.data)[key] = value
        self.rewrite(temp_data)

    def __iter__(self):
        return iter(self.data)

    @staticmethod
    def _semi_applied(applied_func: Callable):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(self: JsonFile, *args, **kwargs):

                temp_data = self.data
                value = applied_func(temp_data, *args, **kwargs)
                self.rewrite(temp_data)
                return value

            return wrapper
        return decorator

    @_semi_applied(dict.update)
    def update(self, updates: dict[str, Any]) -> None:
        pass

    @_semi_applied(dict.pop)
    def pop(self, key: str, default: Any = None):
        pass

    @_semi_applied(dict.fromkeys)
    def fromkeys(self, iterable: Iterable, value: Any = None):
        pass

    @_semi_applied(dict.popitem)
    def popitem(self):
        pass

    @_semi_applied(dict.setdefault)
    def setdefault(self, key: str, default: Any = None):
        pass
