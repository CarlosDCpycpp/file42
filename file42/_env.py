from __future__ import annotations

from functools import cache
from typing import Any

from ._file_abc import DictLikeFileABC
from ._utils import base_value

# try:
#     import dotenv  # NOQA
#     _dotenv_usable: bool = True
# except ModuleNotFoundError as _usable_error:
#     _dotenv_usable: bool = False


class EnvFile(DictLikeFileABC):

    def __init__(self, file: str = '') -> None:
        super().__init__(file)

    @property
    def variables(self) -> dict[str, Any]:
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

    def rewrite(self, **variables) -> None:
        data = '\n'.join([f'{var!s}={value!s}' for var, value in variables.items()])
        with open(self.file, 'w') as file:
            file.write(data)
