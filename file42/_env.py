from __future__ import annotations

from functools import cache
from pprint import pformat
from typing import Any

from ._file_abc import FileABC
from ._utils import base_value, applied

try:
    import dotenv
    _dotenv_usable: bool = True
except ModuleNotFoundError as _usable_error:
    _dotenv_usable: bool = False


class EnvFile(FileABC):
    def __init__(self, file: str = '') -> None:
        super().__init__(file)

    @property
    def variables(self):
        with open(self.file, 'r') as file:
            return EnvFile._find_variables(file.read())

    @staticmethod
    @cache
    def _find_variables(data: str):

        variables: dict[str, str] = dict()

        for line in data.split('\n'):
            if line:
                var, value = line.split('=')
                variables[var] = base_value(value)

        return variables

    def _content(self):
        return self.variables

    def __str__(self):
        return pformat(self.variables)

    def rewrite(self, **variables) -> None:
        data = '\n'.join([f'{var!s}={value!s}' for var, value in variables.items()])
        with open(self.file, 'w') as file:
            file.write(data)

    def __getitem__(self, item):
        return self.variables[item]

    def __setitem__(self, key, value):
        temp_vars = self.variables
        temp_vars[key] = value
        self.rewrite(**temp_vars)

    @property
    @applied(dict.items)
    def items(self):
        return self.variables

    @property
    @applied(dict.values)
    def values(self):
        return self.variables

    @property
    @applied(dict.keys)
    def keys(self):
        return self.variables

    @applied(dict.get, unpack=True)
    def get(self, key, default: Any = None) -> Any:
        return self.variables, key, default

    # @applied()
