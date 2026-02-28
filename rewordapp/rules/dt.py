import re

from rewordapp import exceptions as exceptions


class DateTimeTokenRule:
    def __init__(self, rule_value):
        self._rule_value = rule_value
        self._is_rewrite = False
        self._is_parsed = False
        self._start_pos = ""
        self._width = ""

        self._parse()

    def __bool__(self):
        return self._is_parsed

    def __len__(self):
        return 1 if self._is_parsed else 0

    @property
    def raw(self):
        return self._rule_value

    @property
    def is_rewrite(self):
        return self._is_rewrite

    def _parse_list_type(self) -> None:
        """Parse rewrite_datetime list: [flag, index, width]."""
        if not isinstance(self.raw, list):
            return

        if len(self.raw) not in (2, 3):
            msg = (
                "rewrite_datetime must be [true|false|yes|no, index, width]"
                f"\nReceived: {self.raw!r}"
            )
            raise exceptions.DateTimeRuleError(msg)

        # Normalize values
        items = [str(item).strip().lower() for item in self.raw]

        # Default width when omitted
        if len(items) == 2:
            items.append("1")

        flag, index_str, width_str = items

        # Validate flag
        if not re.fullmatch(r"(?i)(true|false|yes|no)", flag):
            msg = (
                "first element must be one of: true, false, yes, no"
                f"\nReceived: {self.raw!r}"
            )
            raise exceptions.DateTimeRuleError(msg)

        # Validate index
        if not re.fullmatch(r"(?i)[+-]?\d+", index_str):
            msg = (
                "second element must be a signed integer index"
                f"\nReceived: {self.raw!r}"
            )
            raise exceptions.DateTimeRuleError(msg)

        # Validate width
        if not re.fullmatch(r"(?i)(\d+|eol|none|null)", width_str):
            msg = (
                "third element must be a width value or 'eol' or 'none'"
                f"\nReceived: {self.raw!r}"
            )
            raise exceptions.DateTimeRuleError(msg)

        # Apply parsed values
        self._is_parsed = True
        self._is_rewrite = flag in ("true", "yes")
        self._start_pos = int(index_str)
        self._width = int(width_str) if width_str.isdigit() else "eol"

    def _parse_string_type(self) -> None:
        """Parse rewrite_datetime string: 'flag, index, width'."""
        if self:  # already parsed
            return

        if not isinstance(self._rule_value, str):
            msg = ("rewrite_datetime must be 'flag, index, width' "
                   "where flag is one of: yes, no, true, false"
                   f"\nReceived: {self.raw!r}")
            raise exceptions.DateTimeRuleError(msg)

        pattern = r"""(?ix)
            (?P<flag>yes|no|true|false)\s*,\s*
            (?P<start>-?\d+)
            (?:\s*,\s*(?P<width>\d+|eol|null|none)?)?
        """

        match = re.fullmatch(pattern, self._rule_value.strip())
        if not match:
            msg = ("rewrite_datetime must be 'flag, index, width' "
                   "where flag is one of: yes, no, true, false"
                   f"\nReceived: {self.raw!r}")
            raise exceptions.DateTimeRuleError(msg)

        flag = match.group("flag").lower()
        start = match.group("start")
        width = match.group("width")

        self._is_parsed = True
        self._is_rewrite = flag in ("yes", "true")
        self._start_pos = int(start)

        if width is None:
            self._width = 1
        elif width.isdigit():
            self._width = int(width)
        else:
            self._width = "eol"

    def _parse(self):
        self._parse_list_type()
        self._parse_string_type()

    def extract_segments(self, items):
        """Return the slice of items defined by start and width settings."""
        total = len(items)
        start_pos = int(self._start_pos) or 1

        # If start is beyond the list, return everything unchanged
        if start_pos > 0 and start_pos > total:
            return items

        # Convert 1‑based positive index → 0‑based; keep negative indexes as-is
        start_index = start_pos - 1 if start_pos >= 0 else start_pos

        # No width specified → return everything from start_index onward
        if self._width == "" or str(self._width).lower() == "eol":
            return items[start_index:]

        # Width: default to 1, otherwise absolute integer
        width = 1 if self._width is None else abs(int(self._width))

        return items[start_index:start_index + width]
