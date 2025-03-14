from __future__ import annotations
import os
from abc import (
    ABC,
    ABCMeta,
    abstractmethod
)
from typing import (
    TextIO,
    Optional

)
from collections.abc import Iterable

from file42._utils.__init__ import raise_if


class _FileABCMeta(ABCMeta):
    def __new__(
            cls, name: str, bases: tuple, namespace: dict,
            file_like: bool = True, custom_extension: Optional[str] = False
    ) -> _FileABCMeta:
        if file_like:
            raise_if(
                NameError('A class that inherits FileABC must end with File and start with the extension.'),
                not (name.endswith('File'))
            )
            extension: str = f'.{name[:-4].lower()}'
        elif custom_extension:
            extension = f'.{custom_extension if not custom_extension.startswith('.') else custom_extension[:-1]}'
        else:
            extension = ''
        namespace['extension'] = extension
        return super().__new__(cls, name, bases, namespace)


class FileABC(
    ABC,
    metaclass=_FileABCMeta,
    file_like=False
):

    def __init__(self, file: str) -> None:

        if not file.endswith(self.extension):  # NOQA
            self._file = file + f'{self.extension}'
        else:
            self._file = file

        if not os.path.isfile(self.file):
            with open(self._file, 'w'):
                pass

        self.__is_open: bool = False
        self.__file_state: Optional[TextIO] = None

    def open(self, mode: str = 'r') -> TextIO:
        self.__file_state = open(self.file, mode)
        self.__is_open = True
        return self.__file_state

    def close(self) -> None:
        self.__file_state.close()
        self.__file_state = None
        self.__is_open = False

    @property
    def is_open(self) -> bool:
        return self.__is_open

    @property
    def file(self):
        return self._file

    @property
    @abstractmethod
    def _content(self):  # used for iternal processes
        pass

    @abstractmethod
    def rewrite(self, content) -> None:
        pass

    @classmethod
    def set_up(cls, file_name: str, content) -> FileABC:
        file = cls(file_name)
        file.rewrite(content)
        return file

    def clear(self) -> None:
        with open(self.file, 'w'):
            pass

    def __str__(self) -> str:
        return str(self._content)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.file}'

    def __bool__(self) -> bool:
        return True if self._content else False

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            if self.__class__ == other.file:
                return True
        return False

    def __ne__(self, other) -> bool:
        return not (self == other)

    def __gt__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self._content > other._content
        return False

    def __lt__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self._content < other._content
        return False

    def __ge__(self, other) -> bool:
        return not (self < other)

    def __le__(self, other) -> bool:
        return not (self > other)

    def __len__(self) -> int:
        return len(self._content)

    def __iter__(self) -> Iterable:
        return iter(self._content)

    def __hash__(self) -> int:
        return hash((self.__class__, self.file))

    def delete(self) -> None:
        os.remove(self.file)
        del self

    def duplicate(self, new_file_name: str = None) -> FileABC:
        filtered_new_file_name: str = new_file_name
        if new_file_name is not None:
            version: int = 0
            while True:
                if not os.path.isfile(filtered_new_file_name := f'{self.file.split('.')[0]}({version}){self.extension}'):
                    break
                version += 1

        (new_file := self.__class__(filtered_new_file_name)).rewrite(self._content)
        return new_file

    def copy_to(self, file_to_copy_to: FileABC | str) -> None:
        if isinstance(file_to_copy_to, str):
            self.duplicate(file_to_copy_to)
        elif isinstance(file_to_copy_to, self.__class__):
            self.duplicate(file_to_copy_to.file)
