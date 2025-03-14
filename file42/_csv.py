from __future__ import annotations
from typing import Any
from functools import cache

from ._utils import Matrix

import csv
from ._file_abc import FileABC


class CsvFile(FileABC):

    @property
    def data(self) -> Matrix:
        # data is process in a different func
        # because the processing can be extensive
        # so to make it faster I used a cache decorated func
        with open(self.file, 'r') as file:  # when read csv data is all in strings
            raw_data: list[list[str]] = list(csv.reader(file))
        hashable_data: tuple[tuple[str, ...], ...] = tuple(tuple(row) for row in raw_data)  # cached funcs strictly use hashable args
        return CsvFile.__process_data(hashable_data)  # said func

    @staticmethod
    @cache  # avoid time waste processing already precessed data
    # func used in property data only
    def __process_data(raw_data: tuple[tuple[str, ...], ...]) -> Matrix:

        filtered_data = []
        header_flag: bool = False
        # filter
        for row in raw_data:

            if not header_flag:  # avoid changing the header
                header_flag = True
                filtered_data.append([value for value in row])
                continue

            filtered_row = []  # filtered values will be appended here
            for value in row:

                if (lowered_value := value.strip().lower()) in ['', 'none']:
                    filtered_row.append(None)
                    continue

                conversion_done_flag: bool = False
                for conversion_type in {int, float}:  # numerical types
                    try:
                        filtered_row.append(conversion_type(value))
                        conversion_done_flag = True
                        break
                    except ValueError:
                        continue
                if conversion_done_flag:
                    continue

                if lowered_value in {"true", "false"}:  # bool
                    filtered_row.append(lowered_value == "true")
                    continue

                filtered_row.append(value)  # is nothing works make it a string

            filtered_data.append(filtered_row)  # add to the return matrix the filtered row

        return filtered_data

    @property
    def _content(self) -> Matrix:  # used internally for abc meths
        return self.data

    @property
    def header(self) -> list:
        return self.data[0]

    @property
    def columns(self) -> list:
        if not self.data:
            return []

        max_length = max(len(row) for row in self.data)
        result = [
            [row[index] for row in self.data if index < len(row)]
            for index in range(max_length)
        ]
        return result

    @property
    def ratio(self) -> tuple[int, int]:
        return len(self.data), len(self.columns)

    def rewrite(self, content: Matrix):
        with open(self.file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(content)

    def __str__(self) -> str:
        col_widths = [max(len(str(item)) for item in col) for col in zip(*self.data)]
        result = ''
        for row in self.data:
            row_str = ''
            for idx, element in enumerate(row):
                row_str += str(element).ljust(col_widths[idx] + 2)
            result += row_str.rstrip() + '\n'
        return result[:-1]

    def __format__(self, format_spec: str) -> str:
        filtered_format_spec: str = format_spec if not format_spec.endswith('s') else format_spec[:-1]

        format_keys: dict[tuple[str, ...], str] = {
            ('file', 'f'): self.file,
            ('ratio', 'r'): self.ratio,
            ('column', 'c'): self.columns,
            ('matrix', 'm'): f'[\n\t{'\n\t'.join([str(row) for row in self.data])}\n]'
        }

        for key, value in format_keys.items():
            if filtered_format_spec in key:
                return value
        raise ValueError(f'Invalid specifier "{format_spec}" for CsvFile.__format__.')

    def __getitem__(self, item: str | int | tuple[int, int]) -> Any:
        if isinstance(item, int):
            return self.data[item]
        elif isinstance(item, str):
            for index, title in enumerate(self.header):
                if title == item:
                    return self.columns[index]
        elif isinstance(item, tuple):
            return self.data[item[0]][item[1]]
        raise IndexError(f'Invalid index "{item}" for the CsvFile object ({self!r}).')

    def __setitem__(self, key: str | int | tuple[int, int], value: list | Any) -> None:
        temp_data: Matrix = self.data

        if isinstance(key, int):  # row
            if not (0 <= key < len(temp_data)):
                raise IndexError(f"Row index {key} out of range.")
            if not isinstance(value, list):
                raise ValueError("Value must be a list when replacing a row.")
            if len(value) != len(temp_data[0]):
                raise ValueError(f"Row length mismatch: expected {len(temp_data[0])}, got {len(value)}.")
            temp_data[key] = value

        elif isinstance(key, str):  # column
            try:
                col_index = self.header.index(key)
            except ValueError:
                raise KeyError(f"Column with header '{key}' not found.")
            if not isinstance(value, list):
                raise ValueError("Value must be a list when replacing a column.")
            if len(value) != len(temp_data):
                raise ValueError(f"Column length mismatch: expected {len(temp_data)}, got {len(value)}.")
            for row_idx, val in enumerate(value):
                temp_data[row_idx][col_index] = val

        elif isinstance(key, tuple):  # value
            row_idx, col_idx = key
            if not (0 <= row_idx < len(temp_data)):
                raise IndexError(f"Row index {row_idx} out of range.")
            if not (0 <= col_idx < len(temp_data[row_idx])):
                raise IndexError(f"Column index {col_idx} out of range.")
            temp_data[row_idx][col_idx] = value

        else:
            raise TypeError(f"Key of type {type(key).__name__} is not supported for __setitem__.")

        self.rewrite(temp_data)

    def __contains__(self, item) -> bool:
        return True if item in [*self.data, *self.columns] else item in [value for row in self.data for value in row]

    def add_row(self, new_row: list, index: int = None) -> None:
        new_data: Matrix = self.data

        if len(new_row) != self.ratio[1]:
            raise ValueError('The length of the new row must be the same as the one of the other rows.')

        if index is None:
            new_data.append(new_row)
        else:
            new_data.insert(index, new_row)

        self.rewrite(new_data)

    def remove_row(self, index) -> None:
        self.rewrite(self.data.pop(index))

    def add_column(self, new_column: list, index: int = None) -> None:
        new_columns = self.columns

        if len(new_column) != self.ratio[0]:
            raise ValueError('The length of the new column must be the same as the one of the other columns.')

        if index is None:
            new_columns.append(new_column)
        else:
            new_columns.insert(index, new_column)

        new_data = [list(row) for row in zip(*new_columns)]
        self.rewrite(new_data)

    def remove_column(self, index) -> None:
        new_columns = self.columns.pop(index)
        new_data = [list(row) for row in zip(*new_columns)]
        self.rewrite(new_data)

    def replace(
            self,
            old: Any, new: Any,
            row_index: int = None,
            column_index: int = None
            ) -> None:

        if row_index == 0:
            raise IndexError('CsvFile.replace cannot take 0 as the row index since row 0 is the header.')

        new_data = self.data
        rows, cols = self.ratio

        if row_index is None and column_index is None:  # all values
            for row_idx in range(1, rows):  # don't change header
                new_data[row_idx] = [
                    new if value == old else value for value in new_data[row_idx]
                ]

        elif column_index is None:  # row
            if not (1 <= row_index < rows):
                raise IndexError(f"Row index out of range. Must be between 1 and {rows - 1}.")
            new_data[row_index] = [
                new if value == old else value for value in new_data[row_index]
            ]

        elif row_index is None:  # column
            if not (0 <= column_index < cols):
                raise IndexError(f"Column index out of range. Must be between 0 and {cols - 1}.")
            for row_idx in range(1, rows):  # don't change header
                if new_data[row_idx][column_index] == old:
                    new_data[row_idx][column_index] = new

        else:  # specific value
            if not (1 <= row_index < rows) or not (0 <= column_index < cols):
                raise IndexError(f"Row or column index out of range.")
            if new_data[row_index][column_index] == old:
                new_data[row_index][column_index] = new

        self.rewrite(new_data)

    def search(self, value_to_search) -> int:
        counter: int = 0

        for row in self.data:
            for value in row:
                if value == value_to_search:
                    counter += 1

        return counter

    @property
    def pandas(self):
        try:
            import pandas
            return pandas.read_csv(self.file)
        except ModuleNotFoundError:
            raise ImportError("Pandas is not installed, therefore the CsvFile.pandas function failed.")
        finally:
            del pandas
