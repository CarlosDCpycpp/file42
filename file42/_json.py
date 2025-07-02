from __future__ import annotations

from ._file_abc import DictLikeFileABC

import json
from typing import Any


class JsonFile(DictLikeFileABC):

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

    def rewrite(self, content: Any) -> None:
        with open(self.file, 'w') as file:
            json.dump(content, file, indent=4)
