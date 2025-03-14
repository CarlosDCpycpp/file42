# for access

from ._txt import TxtFile
from ._csv import CsvFile
from ._py import PyFile
from ._json import JsonFile
from ._env import EnvFile

from ._file_abc import FileABC


def file(file_name: str) -> FileABC:
    extension = file_name.split('.')[-1]

    keys: dict[str, type[FileABC]] = {
        'txt': TxtFile,
        'csv': CsvFile,
        'py': PyFile,
        'json': JsonFile,
        'env': EnvFile
    }

    return keys[extension](file_name)
