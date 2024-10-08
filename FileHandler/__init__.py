from __future__ import annotations
import csv
import typing as _t
import os as _os


_matrix = _t.Optional[list[list[_t.Optional[_t.Any]]]]


class TxtFile:
    def __init__(self, file: str, new: bool = False):
        self.file = file + ".txt"

        if new:
            self.txt = ''
            with open(self.file, 'w'):
                pass
        else:
            with open(self.file, "r") as file_:
                self.txt = file_.read()

            self.words = list(self.txt.split())
            self.n_words = len(self.words)

            with open(self.file, 'r') as file_:
                self.lines: list = file_.readlines()
                self.n_lines: int = len(self.lines)

    def _update(self):
        with open(self.file, "r") as file_:
            self.txt = file_.read()
        self.words = list(self.txt.split())
        self.n_words = len(self.words)

        with open(self.file, 'r') as file_:
            self.lines: list = file_.readlines()
            self.n_lines: int = len(self.lines)

    def __str__(self):
        return self.txt

    def __repr__(self):
        return str(self)

    def __bool__(self):
        if self.txt == '':
            return False
        return True

    def __add__(self, other):
        if isinstance(other, TxtFile):
            if self.txt == '':
                z = ''
            else:
                z = '\n'
            return self.txt + z + other.txt

        elif isinstance(other, str):
            return self.txt + '\n' + other

        else:
            return self.txt + "\n" + str(other)

    def __iadd__(self, other):
        if self.txt == '':
            self.re_write(self.txt + str(other))
        else:
            self.re_write(self.txt + '\n' + str(other))
        self._update()
        return self

    def __eq__(self, other):
        if isinstance(other, TxtFile):
            if self.txt == other.txt:
                return True
            return False
        elif isinstance(other, str):
            if self.txt == other:
                return True
            return False
        return False

    def __ne__(self, other):
        if self == other:
            return False
        return True

    def __iter__(self):
        for line in self.lines:
            yield line.strip()

    def __getitem__(self, index: int|tuple) -> str:
        if isinstance(index, int):
            return self.lines[index-1]
        elif isinstance(index, (tuple, list)):
            if len(index) != 2:
                raise ValueError("Index tuple/list must have exactly two elements: (index, type).")

            ind, type_ = index

            if not isinstance(ind, int):
                raise TypeError("First item in index must be an int.")
            if not isinstance(type_, str):
                raise TypeError("Second item in index must be a string.")

            if type_.lower() in ['w', "word"]:
                if 1 <= ind <= self.n_words:
                    return self.words[ind - 1]
                else:
                    raise IndexError("Word index out of range.")
            elif type_.lower() in ['l', "line"]:
                if 1 <= ind <= self.n_lines:
                    return self.lines[ind - 1]
                else:
                    raise IndexError("Index out of range.")
            else:
                raise ValueError("Type must be either 'word' or 'line'.")
        else:
            raise TypeError("Index must be either an integer, tuple or list.")

    def __contains__(self, item: str):
        obj: list = item.split()
        if len(obj) == 1:
            if item in self.words:
                return True
            return False
        else:
            if item in self.lines:
                return True
            return False

    def __hash__(self):
        return hash(self.words)

    def write(self, content: str, new_line: bool = True):
        if new_line:
            with open(self.file, "a") as file_:
                file_.write('\n')
        with open(self.file, "a") as file_:
            file_.write(content)
        self._update()

    def re_write(self, content: str):
        with open(self.file, "w") as file_:
            file_.write(content)
        self._update()

    def clear(self):
        with open(self.file, 'w'):
            pass
        self._update()

    def write_lines(self, content: list):
        with open(self.file, 'w') as file:
            file.writelines(content)

    def re_write_line(self, index: int, content: str):
        if 1 <= index <= self.n_lines:
            with open(self.file, 'r') as file_:
                lines = file_.readlines()
            lines[index - 1] = content + '\n'
            with open(self.file, 'w') as file_:
                file_.writelines(lines)
            self._update()
        else:
            raise IndexError("Index out of range.")

    def clear_line(self, index: int):
        if 0 <= index < self.n_lines:
            with open(self.file, 'r') as file_:
                lines = file_.readlines()

            # Remove the specific line
            lines.pop(index-1)

            # Write the remaining lines back to the file
            with open(self.file, 'w') as file_:
                file_.writelines(lines)
            self._update()
        else:
            raise IndexError("Index out of range.")

    def get_line(self, line: int) -> str|None:
        with open(self.file, 'r') as file:
            lines = file.readlines()
            if line <= len(lines):
                return lines[line - 1].strip()

    def find_word(self, word: str, bool_: bool = False) -> int|bool:
        n = 0
        word = word.strip()
        b = False
        for i in self.words:
            if i.lower() == word.lower():
                if bool_:
                    b = True
                n += 1
        return b if bool_ else n

    def lower(self):
        self.re_write(self.txt.lower())

    def upper(self):
        self.re_write(self.txt.upper())

    def replace(self, old: str, new: str = ""):
        self.re_write(self.txt.replace(old, new))

    def trim(self):
        self.re_write(self.txt.strip())


class CsvFile:
    def __init__(self, file: str, new: bool = False):
        self.file = file + ".csv"

        self.data: list[list] = []
        if new:
            with open(self.file, 'w', newline='') as file_:
                writer = csv.writer(file_)
                if self.data:
                    writer.writerows(self.data)
                self.ratio: list[int] = [0, 0]

            self.rows = []
            self.columns = []
            self.header = None
        else:
            self._update_properties()
            # with open(self.file, 'r', newline='') as file_:
            #     reader = csv.reader(file_)
            #     self.data: list[list] = list(reader)
            #
            #     self.rows: list = []
            #     for i in range(len(self.data)):
            #         self.rows.append(self.get(row=i+1))
            #
            #     self.columns: list = []
            #     for i in range(len(self.data[0])):
            #         self.columns.append(self.get(column = i+1))
            #
            #     self.header = self.rows[0]
            #
            #     self.ratio: list[int] = [len(self.rows), len(self.columns)]

    def _update_properties(self) -> None:
        with open(self.file, 'r', newline='') as file_:
            reader = csv.reader(file_)
            self.data: list[list] = list(reader)

            self.rows: list = []
            for i in range(len(self.data)):
                self.rows.append(self.get(row=i + 1))

            self.columns: list = []
            for i in range(len(self.data[0])):
                self.columns.append(self.get(column=i + 1))

            self.header = self.rows[0]

            self.ratio: list[int] = [len(self.rows), len(self.columns)]

    def update_file(self) -> None:
        self.re_write(self.get())

    @staticmethod
    def set_up(name: str, data: _matrix) -> CsvFile:
        f"""This method is supposed to be used if a file is empty 
        or if you want to rewrite an existing file and assign it to a variable.\n
        The parameter \"name\" is the name of the file (don\'t include the extension, i.e. \".csv\").\n
        The parameter \"data\" is the data that you want to assign to the file."""
        file = CsvFile(name)
        file.re_write(data)
        return file

    @staticmethod
    def set_up_new(name: str, data: _matrix) -> CsvFile:
        file = CsvFile(name, new=True)
        file.re_write(data)
        return file

    def __enter__(self, specs: str):
        possible_specs: list[str] = ['r', 'w']
        if not specs in possible_specs:
            ps: str = ''
            for i in possible_specs:
                ps += ' ' + i + ','
            ps = ps[::-1]
            raise ValueError(f"Unknown specifier {specs}. Possible specifiers are {ps}")
        self._opened = open(self.file)
        return self._opened

    def __exit__(self):
        self._opened.close()

    def __str__(self):
        col_widths = [max(len(str(item)) for item in col) for col in zip(*self.data)]
        result = ''
        for row in self.data:
            row_str = ''
            for idx, element in enumerate(row):
                row_str += str(element).ljust(col_widths[idx] + 2)
            result += row_str.rstrip() + '\n'
        return result[:-1]

    def __repr__(self):
        return str(self)

    def __format__(self, format_spec: str) -> str:
        result = ''
        match format_spec.lower().strip():
            case 'file':
                return self.file
            case 'header':
                return str(self.header)
            case 'ratio':
                return str(self.ratio)
            case 'no_lines':
                return str(self.data)
            case 'no_lines_unpacked':
                result = []
                for i in self.data:
                    temp = ''
                    for j in i:
                        temp += f'{j} '
                    result.append(temp)
                return str(result)
            case 'matrix':
                result += '\n'
                for i in self.data:
                    result += str(i) + '\n'
                return result.rstrip()
            case 'base':
                for i in self.data:
                    result += '\n'
                    for j in i:
                        result += f'{j} '
                return result
            case '':
                return str(self)
            case _:
                raise ValueError(f"Unknown specifier: {format_spec}.")

    def formatted(self, format_specs: str) -> str:
        return self.__format__(format_specs)

    def __bool__(self):
        if self.data:
            return True
        return False

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index: int|tuple[int, int]|str) -> list|None:
        if index == 0:
            raise ValueError("Index cannot be 0, this is due to the 1 based indexing used in the CsvFile class.")

        if isinstance(index, str):
            for index_, _ in enumerate(self.data):
                if self.header[index_] == index:
                    return self.columns[index_]
            else:
                return None
        elif isinstance(index, int):
            return self.get(row=index-1)
        elif isinstance(index, tuple):
            return self.get(row=index[0]-1, column=index[1]-1)

    def __iter__(self):
        for i in self.get():
            for j in i:
                yield j

    def __contains__(self, item):
        if isinstance(item, list):
            for i in self.rows:
                if i == item:
                    return True
            for i in self.columns:
                if i == item:
                    return True
            return False
        else:
            for i in self:
                for j in i:
                    if j == item:
                        return True
            return False

    def __delitem__(self, key: int):
        del self.data[key]
        self.update_file()

    def __hash__(self):
        return hash(self.data)

    def __sizeof__(self):
        x = 0
        for i in self.data:
            for j in i:
                try:
                    x += j.__sizeof__()
                except AttributeError:
                    return None
        return x

    def __eq__(self, other: CsvFile|_matrix):
        if isinstance(other, CsvFile):
            if self.data == other.data:
                return True
            return False
        elif isinstance(other, _matrix):
            if self.data == other:
                return True
            return False

    def __ne__(self, other: CsvFile|_matrix):
        if self == other:
            return False
        return True

    def __gt__(self, other):
        z = 0
        for i in self.data:
            z += len(i)
        x = 0
        if isinstance(other, _matrix|CsvFile):
            for i in other.data:
                x += len(i)
        elif isinstance(other, list):
            x += len(other)

        if z > x:
            return True
        return False

    def __ge__(self, other: CsvFile|list|_matrix):
        z = 0
        for i in self.data:
            z += len(i)
        x = 0
        if isinstance(other, _matrix|CsvFile):
            for i in other.data:
                x += len(i)
        elif isinstance(other, list):
            x += len(other)

        if z >= x:
            return True
        return False

    def __lt__(self, other: CsvFile|list|_matrix):
        z = 0
        for i in self.data:
            z += len(i)
        x = 0
        if isinstance(other, _matrix|CsvFile):
            for i in other.data:
                x += len(i)
        elif isinstance(other, list):
            x += len(other)

        if z < x:
            return True
        return False

    def __le__(self, other: CsvFile|list|_matrix):
        z = 0
        for i in self.data:
            z += len(i)
        x = 0
        if isinstance(other, _matrix|CsvFile):
            for i in other.data:
                x += len(i)
        elif isinstance(other, list):
            x += len(other)

        if z <= x:
            return True
        return False

    def __add__(self, other: list):
        new_data = self.data[:]
        new_data.append(other)
        new_csv = CsvFile(self.file, new=True)
        new_csv.data = new_data
        new_csv._update_properties()
        return new_csv

    def __radd__(self, other):
        return other - self.get()

    def __iadd__(self, other: list) -> _t.Self:
        self.insert_row(other)
        return self

    def __sub__(self, other: list):
        if len(other) not in self.ratio:
            raise ValueError("The length isn't equal to number of rows or columns.")

        temp_data = self.data
        for i in temp_data:
            if i == other:
                temp_data.remove(other)
                break
        else:
            for i in range(len(self.columns)):
                if self.columns[i] == other:
                    for index, _ in enumerate(temp_data):
                        del temp_data[index][i]
                    break
            else:
                raise ValueError(f"\"{other}\" is neither a row nor a column.")

        return temp_data

    def __isub__(self, other: list) -> _t.Self:
        self.data = self - other
        self.update_file()
        return self

    def __rsub__(self, other):
        return other - self.data

    def __call__(self):
        return self.data

    def get(self, row: int|None = None, column: int|None = None):
        if isinstance(row, int) and isinstance(column, int):
            return self.data[row - 1][column - 1]
        elif isinstance(row, int):
            return self.data[row - 1]
        elif isinstance(column, int):
            z = []
            for i in self.data:
                z.append(i[column - 1])
            return z
        else:
            return self.data

    def set(self, value: list|_t.Any, row_index: int|None = None, column_index: int|None = None):
        if (row_index is None and
                column_index is None):
            raise IndexError("At least one of the \"set\" method's parameters must be given.")
        elif (row_index is not None and
                column_index is not None):
            self.data[row_index][column_index-1] = value
        else:
            if not isinstance(value, list):
                raise TypeError("The value parameter must be a list when on of the other parameters are None.")
            if row_index is not None:
                if len(value) != self.ratio[1]:
                    raise ValueError(f"Row length must match the number of columns: {self.ratio[1]}.")
                if not (1 <= row_index <= self.ratio[0]):
                    raise IndexError("Row index out of range.")
                self.data[row_index] = value
            elif column_index is not None:
                if len(value) != self.ratio[0]:
                    raise ValueError(f"Column length must match the number of rows: {self.ratio[0]}.")
                if not (1 <= column_index <= self.ratio[1]):
                    raise IndexError("Column index out of range.")
                for i in range(self.ratio[0]):
                    self.data[i][column_index - 1] = value[i]

        self.update_file()

    @property
    def iter_rows(self):
        return iter(self.rows)

    @property
    def iter_column(self):
        return iter(self.columns)

    def insert_row(self, row: list, index: int | None = None):
        if len(row) != self.ratio[1]:
            raise ValueError("Row length must match the number of rows.")
        elif index == 0:
            raise ValueError("Row cannot be positioned as the header.")

        if index is None:
            self.data.append(row)
        else:
            self.data.insert(index, row)

        self.update_file()

    def insert_column(self, column: list, index: int | None = None):
        if len(column) != self.ratio[0]:
            raise ValueError("Column length must match the number of rows.")

        if index is None:
            for row_idx, row in enumerate(self.data):
                row.append(column[row_idx])
        else:
            if not (1 <= index <= self.ratio[1] + 1):
                raise ValueError(f"Index must be between 1 and {self.ratio[1] + 1}.")
            for row_idx, row in enumerate(self.data):
                row.insert(index - 1, column[row_idx])

        self.update_file()

    def clear_all(self):
        with open(self.file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([[None]])
        self._update_properties()

    def clear_row(self, index: int):
        if index < 1:
            raise IndexError("Index must be above 0.")
        elif index > self.ratio[0]:
            raise IndexError(f"Index must be lower than {self.ratio[0]}.")

        for i in range(len(self.rows[index-1])):
            self.data[index-1][i] = None
        self.update_file()

    def clear_column(self, index: int):
        if index < 1:
            raise IndexError("Index must be above 0.")
        elif index > self.ratio[1]:
            raise IndexError(f"Index must be lower than {self.ratio[1]}.")

        for i in range(len(self.data)):
            self.data[i][index - 1] = None
        self.update_file()

    def clear_item(self, row_index: int, column_index: int):
        if row_index < 1 or column_index < 1:
            raise IndexError("Indexes must be above 0.")
        elif row_index > self.ratio[0]:
            raise IndexError(f"Row index must be lower than {self.ratio[0]}.")
        elif column_index > self.ratio[1]:
            raise IndexError(f"Column index must be lower than {self.ratio[0]}.")

        self.data[row_index][column_index] = None
        self.update_file()

    def re_write(self, content: _matrix):
        with open(self.file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(content)
        self._update_properties()

    def elim_row(self, index: int):
        if index is None or not (1 <= index <= self.ratio[0]):
            raise ValueError("Invalid row index.")
        del self.data[index - 1]
        if self.header:
            self.header = self.data[0]
            self.data.pop(0)
        self.re_write(self.data)

    def elim_column(self, index: int):
        if index is None or not (1 <= index <= self.ratio[1]):
            raise ValueError("Invalid column index.")
        for row in self.data:
            del row[index - 1]
        if self.header:
            del self.header[index - 1]
        self.re_write(self.data)

    def search(self, item) -> list[list[int]]|list[int]|None:
        indexes = []
        for index, j in enumerate(self.data):
            for index_, i in enumerate(j):
                if i == item:
                    indexes.append([index, index_])
        if not indexes:
            return None
        elif len(indexes) == 1:
            return indexes[0]
        else:
            return indexes

    def replace(self, old, new, row_index: int|None = None, column_index: int|None = None):
        indexes = [row_index, column_index]
        if indexes == [None, None]:
            for i in range(len(self.data)):
                for j in range(len(self.data[i])):
                    if self.data[i][j] == old:
                        self.data[i][j] = new
        elif row_index is None:
            if column_index is not None and 1 <= column_index <= self.ratio[1]:
                for i in range(len(self.data)):
                    if self.data[i][column_index - 1] == old:
                        self.data[i][column_index - 1] = new
        elif column_index is None:
            if row_index is not None and 1 <= row_index <= self.ratio[0]:
                for j in range(len(self.data[row_index - 1])):
                    if self.data[row_index - 1][j] == old:
                        self.data[row_index - 1][j] = new
        else:
            if 1 <= row_index <= self.ratio[0] and 1 <= column_index <= self.ratio[1]:
                if self.data[row_index - 1][column_index - 1] == old:
                    self.data[row_index - 1][column_index - 1] = new

        self.update_file()

    def pop(self, row: int|str):
        if isinstance(row, int):
            self.data.pop(row)
            self.update_file()
            return self
        elif isinstance(row, str):
            for index, i in enumerate(self.header):
                if i == row:
                    for j, _ in enumerate(self.data):
                        del self.data[j][index]
            else:
                raise ValueError("No match found.")

    def remove(self, list_: list):
        if len(list_) not in self.ratio:
            raise ValueError("the \"list_\" argument took has more items than the number of rows or columns.")

        for index, i in enumerate(self.data):
            if i == list_:
                self.data.pop(index)
                break
        else:
            for index, i in enumerate(self.columns):
                if i == list_:
                    for j, _ in enumerate(self.data):
                        del self.data[j][index]
                break
            else:
                raise ValueError("No match found.")

        self.update_file()
        return self

    def index(self, index_) -> tuple[int|None, int|None]:
        for index__, i in enumerate(self.data):
            if i == index_:
                return index__, None
        for index__, i in enumerate(self.columns):
            if i == index_:
                return None, index__
        for index__, _ in enumerate(self.data):
            for index_x, j in enumerate(self.columns):
                if j == index_:
                    return index__, index_x
        return None, None

    def unique_vals(self, row_index: int|None = None, column_index: int|None = None) -> list|None|bool:
        unique_vals = set()
        if (column_index is None and
                row_index is None):
            for i in self:
                unique_vals.add(i)
        elif (column_index is not None and
              row_index is not None):
            row_vals = self.get(row=row_index)
            column_vals = self.get(column=column_index)
            specific_value = self.get(row_index, column_index)
            return specific_value in row_vals and specific_value in column_vals
        else:
            if row_index is None:
                x = self.get(column=column_index)
            else:  # column_index is None
                x = self.get(row=row_index)
            for i in x:
                unique_vals.add(i)

        if unique_vals == set():
            return None
        return list(unique_vals)

    def duplicate_vals(self, row_index: int|None = None, column_index: int|None = None) -> list|None|bool:
        seen = set()
        duplicates = set()
        if (row_index is None and
                column_index is None):
            for i in self:
                if i in seen:
                    duplicates.add(i)
                else:
                    seen.add(i)
        elif (column_index is not None and
              row_index is not None):
            return not bool(self.unique_vals())
        else:
            if row_index is None:
                vals = self.get(column=column_index)
            else:  # column_index is None
                vals = self.get(row=row_index)

            for value in vals:
                if value in seen:
                    duplicates.add(value)
                else:
                    seen.add(value)

        if duplicates == set():
            return None
        return list(duplicates)

    def delete_duplicate_rows(self):
        seen = set()
        for i in self.rows:
            seen.add(i)
        self.data = list(seen)
        self.update_file()
        return self

    def delete(self):
        x = self.file
        _os.remove(self.file)
        del self
        return f'\"{x}\" was deleted.'

    # file creator

    def save_to(self, other: CsvFile):
        other.re_write(self.get())
        return other.get()

    def duplicate(self, file_name: str|None = None) -> CsvFile:
        if file_name is None:
            file_name = self.file + '_'
        new = CsvFile(file_name, new=True)
        new.re_write(self.get())
        return new

    # convert

    def pandas(self):
        try:  # imports pandas if its installed
            import pandas as _pd
            _pd.read_csv(self.file)
        except ModuleNotFoundError:
            raise ImportError("Pandas is not installed, therefore the CsvFile.pandas function returned None.")
