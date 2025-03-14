from __future__ import annotations

from ._file_abc import FileABC


class TxtFile(FileABC):

    @property
    def text(self) -> str:
        with open(self.file, 'r') as f:
            text = f.read()
        return text

    @text.setter
    def text(self, value) -> None:
        self.rewrite(value)

    @property
    def _content(self) -> str:
        return self.text

    @property
    def lines(self) -> tuple[str, ...]:
        return tuple(self.text.split('\n'))

    @property
    def n_lines(self) -> int:
        return len(self.lines)

    @property
    def words(self) -> tuple[str, ...]:
        return tuple(self.text.split(' '))

    @property
    def n_words(self) -> int:
        return len(self.words)

    def get_line(self, index) -> str:
        return self.lines[index]

    def get_word(self, index) -> str:
        return self.words[index]

    def __getitem__(self, item: tuple[str, int] | int) -> str:
        if isinstance(item, int):
            return self['line', item]

        raw_type = item[0].lower().strip()
        match (get_type := raw_type if not raw_type.endswith('s') else raw_type[:-1]):
            case 'line' | 'l':
                return self.get_line(item[1])
            case 'word' | 'w':
                return self.get_word(item[1])
            case _:
                raise ValueError(f'Invalid type for the TxtFile.__getitem__ method: {get_type}; TxtFile({self.file})[{item}]')

    def __setitem__(self, key: int, value) -> None:
        new_text = ''
        for index, line in enumerate(self.lines):
            if index == key:
                new_text += f'{value}\n'
                continue
            new_text += self.lines[index]
        self.text = new_text

    def __contains__(self, item: str) -> bool:
        return item in self.text

    def write(self, *content, sep='\n', end=None) -> None:
        to_write = ''
        for part in content:
            to_write += f'{part!s}{sep!s}'
        # to_write = to_write[:-len(str(sep))]

        with open(self.file, 'a') as file:
            file.write(f'{to_write}{str(end) if end is not None else ''}')

    def rewrite(self, *content, sep='\n', end=None) -> None:
        self.clear()
        self.write(*content, sep=sep, end=end)

    def set_line(self, index, new_line_content):
        self[index] = new_line_content

    def replace(self, old: str, new: str, count: int = -1) -> None:
        self.text = self.text.replace(old, new, count)
