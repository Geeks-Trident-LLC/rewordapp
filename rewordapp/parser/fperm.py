"""
rewordapp.parser.fperm
======================

File permission parsing and rewriting utilities.
"""

import re
from rewordapp import rewritten

class FilePermissionParser:

    def __init__(self, text: str):
        self._text = text
        self._prefix = ""
        self._suffix = ""
        self._file_permission = ""

        self._parse()

    # ------------------------------------------------------------
    # Magic methods
    # ------------------------------------------------------------

    def __len__(self) -> int:
        """Return 1 if word was parsed, else 0."""
        return 1 if self._file_permission else 0

    def __bool__(self) -> bool:
        """Return True if word was parsed."""
        return bool(self._file_permission)

    # ------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------

    @property
    def raw(self) -> str:
        return self._text

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def file_permission(self):
        return self._file_permission

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------

    def _parse(self) -> None:
        """Parse word from raw text."""

        pattern = r"""(?ix)
            (?P<file_permission>
                (
                    [dlcbpsw-]              # filetype
                    [rts-][wts-][xts-]      # owner
                    [rts-][wts-][xts-]      # group
                    [rts-][wts-][xts-]      # other
                    [+@.-]{0,2}             # extended attributes
                )|
                (
                    [d-]                    # filetype
                    [rhsail-]{5}            #
                )
            )
        """

        match = re.fullmatch(pattern, self._text)
        if not match:
            return

        self._file_permission = match.groupdict().get("file_permission") or ""

    def generate_new(self):
        if not self:
            return self.__class__(self.raw)

        new_file_permission = rewritten.new_file_permission(self.file_permission)
        return self.__class__(new_file_permission)
