from __future__ import annotations

from functools import cache
import re
import subprocess
from typing import Any

from ._file_abc import FileABC

from ._utils import Null


class PyFile(FileABC):

    @property
    def code(self) -> str:
        with open(self.file, 'r') as file:
            code = file.read()
        return code

    @property
    def _content(self):
        return self.code

    def rewrite(self, content) -> None:
        with open(self.file, 'w') as file:
            file.write(content)

    @property
    def functions(self) -> list[str]:
        return PyFile._find_funcs(self.code)

    @staticmethod
    @cache
    def _find_funcs(code: str) -> list[str]:
        return re.findall(r'^def (\w+)\(', code, re.MULTILINE)

    @property
    def variables(self) -> list[str]:
        return PyFile._find_variables(self.code)

    @staticmethod
    @cache
    def _find_variables(code: str) -> list[str]:
        return re.findall(r'^(\w+)\s*=', code, re.MULTILINE)

    @property
    def classes(self) -> list[str]:
        return PyFile._find_classes(self.code)

    @staticmethod
    @cache
    def _find_classes(code: str) -> list[str]:
        return re.findall(r'^class (\w+)\(', code, re.MULTILINE)

    @property
    def imports(self) -> list[str]:
        return PyFile._find_imports(self.code)

    @staticmethod
    @cache
    def _find_imports(code: str) -> list[str]:
        return re.findall(r'^\s*(?:import|from\s+\S+\s+import)\s+[\w.,* ]+', code, re.MULTILINE)

    def run(self) -> None:
        try:
            result = subprocess.run(['python', self.file], check=True, text=True, capture_output=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error running the file: {e}")

    def write(self, line) -> None:
        with open(self.file, 'a') as file:
            file.write(f'\n{line}\n')

    def add_base(self) -> None:
        self.write(
                'from __future__ import annotations\n\n'
                'from typing import (\n\n)\n\n\n'
                'def main() -> None:\n'
                '    pass\n\n\n'
                'if __name__ == \'__main__\':\n'
                '    main()\n'
            )

    def add_func(self, func_name: str, *args, return_type: type = Null, **kwargs) -> None:

        positional_args = ', '.join([str(arg) for arg in args])
        keyword_args = ', '.join([f"{key}={value!r}" for key, value in kwargs.items()])
        all_args = ', '.join(filter(None, [positional_args, keyword_args]))
        return_string = f" -> {return_type.__name__ if return_type else 'None'}" if return_type is not Null else ''

        self.write(
                f"def {func_name}({all_args})"
                f"{return_string}:\n"
                f"    pass\n"
            )

    def add_var(self, var_name: str, var_value: Any = Null, var_type: type = Null) -> None:

        type_annotation = f": {var_type.__name__}" if var_type is not Null else ""
        value_assignment = f" = {repr(var_value)}" if var_value is not Null else ""

        self.write(f"{var_name}{type_annotation}{value_assignment}\n")

    def add_class(self, cls_name: str, *bases, metaclass: type | str = Null, **kwargs) -> None:

        bases_str = f"({', '.join(bases)})" if bases else ""

        kwargs_str = ""

        if metaclass is not Null:
            kwargs_str += f"metaclass={metaclass.__name__ if isinstance(metaclass, type) else repr(metaclass)}"
        kwargs_str += ", ".join(f"{key}={repr(value)}" for key, value in kwargs.items())

        if kwargs_str:
            kwargs_str = f", {kwargs_str}" if bases else f"({kwargs_str})"

        self.write(
                f"\nclass {cls_name}{bases_str}{kwargs_str}:\n"
                f"    pass\n"
            )

    def add_import(self, module: str, *args, **kwargs) -> None:

        if not args and not kwargs:
            self.rewrite(f'import {module}\n{self.code}')
            return

        if args and not kwargs:
            items = ', '.join(args)
            self.rewrite(f'from {module} import {items}\n{self.code}')
            return

        if kwargs:
            items = ', '.join(f'{key} as {value}' for key, value in kwargs.items())
            self.rewrite(f'from {module} import {items}\n{self.code}')
