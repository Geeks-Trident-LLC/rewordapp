

import yaml
import re
import string

from rewordapp import utils
from rewordapp.rewrite import mapping
import rewordapp.exceptions as exceptions


def load_rules(rules_str: str) -> dict:
    """Load YAML rules and ensure the result is a dictionary."""
    result = yaml.safe_load(rules_str)

    if not isinstance(result, dict):
        raise exceptions.InvalidRulesFormat(
            f"Rules must be a dictionary, but received {type(result).__name__}."
        )

    return result


class RewriteRules(dict):
    """Dictionary-like container for rewrite rules loaded from YAML."""

    token_to_rule = {
        "FilePermissionToken": "rewrite_file_permission",
        "IPv4Token": "rewrite_ipv4",
        "IPv6Token": "rewrite_ipv6",
        "MACToken": "rewrite_mac",
        "URLToken": "rewrite_url",
        "NumberToken": "rewrite_number",
        "WordToken": "rewrite_word",
    }

    # rule_to_token = dict(zip(token_to_rule.values(), token_to_rule.keys()))

    def __init__(self, rules_text: str=""):
        # Load provided YAML or fall back to default rule
        if rules_text:
            parsed = load_rules(rules_text)
            super().__init__(**parsed)
        else:
            super().__init__(rewrite_on_each_generate=True)

    def __repr__(self):
        return repr(self.text)

    def __str__(self):
        return self.text

    @property
    def text(self):
        return yaml.dump(
            dict(self),
            allow_unicode=True,
            indent=2,
            default_flow_style=False,
            sort_keys=False,
        ).rstrip("\r\n")

    def to_string(self) -> str:
        """Return the rules as a YAML-formatted string."""
        return self.text

    def has_rule_for(self, token) -> bool:
        """Return True if a rewrite rule exists for the given token."""
        rule_name = self.token_to_rule.get(token.class_name)
        return rule_name in self

    def get_rule_for(self, token):
        """Return the rewrite rule for the given token, or 'n/a' if missing."""
        rule_name = self.token_to_rule.get(token.class_name)
        return self.get(rule_name, "n/a")

    def has_boolean_rule(self, token) -> bool:
        """Return True if the rule for the given token is a boolean."""
        rule = self.get_rule_for(token)
        return isinstance(rule, bool)

    def update_rule_for(self, token) -> None:
        """Enable the rewrite rule associated with the given token type."""
        rule_name = self.token_to_rule.get(token.class_name)
        if rule_name:
            self[rule_name] = True

    def refresh(self):
        """Refresh rewritten output if auto-rewrite is enabled."""
        if self.get("rewrite_on_each_generate", False):
           mapping.refresh()

    def get_datetime_token_rule(self):
        """Return a DateTimeTokenRule if rewrite_datetime is defined."""
        value = self.get("rewrite_datetime") or ""
        return DateTimeTokenRule(value) if value else None

    def get_unchanged_lines_rule(self):
        """Return an UnchangedLinesRule if unchanged_lines is defined."""
        value = self.get("unchanged_lines")
        return UnchangedLinesRule(value) if value else None


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
        return bool(self._is_parsed)

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
            msg = "rewrite_datetime must be [true|false|yes|no, index, width]"
            raise exceptions.DateTimeRuleError(msg)

        # Normalize values
        items = [str(item).strip().lower() for item in self.raw]

        # Default width when omitted
        if len(items) == 2:
            items.append("1")

        flag, index_str, width_str = items

        # Validate flag
        if not re.fullmatch(r"(?i)(true|false|yes|no)", flag):
            msg = "first element must be one of: true, false, yes, no"
            raise exceptions.DateTimeRuleError(msg)

        # Validate index
        if not re.fullmatch(r"(?i)[+-]?\d+", index_str):
            msg = "second element must be a signed integer index"
            raise exceptions.DateTimeRuleError(msg)

        # Validate width
        if not re.fullmatch(r"(?i)(\d+|eol|none)", width_str):
            msg = "third element must be a width value or 'eol' or 'none'"
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
                   "where flag is one of: yes, no, true, false")
            raise exceptions.DateTimeRuleError(msg)

        pattern = r"""(?ix)
            (?P<flag>yes|no|true|false)\s*,\s*
            (?P<start>-?\d+)
            (?:\s*,\s*(?P<width>\d+|eol|null|none)?)?
        """

        match = re.fullmatch(pattern, self._rule_value.strip())
        if not match:
            msg = ("rewrite_datetime must be 'flag, index, width' "
                   "where flag is one of: yes, no, true, false")
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


class UnchangedLinesRule:
    def __init__(self, rule_value):
        self._rule_value = rule_value
        self._is_parsed = False
        self._indices = []
        self._pairs = []

        self._parse()

    def __bool__(self):
        return self._is_parsed

    def __len__(self):
        return bool(self._is_parsed)

    @property
    def raw(self):
        return self._rule_value

    @property
    def indices(self):
        return self._indices

    @property
    def pairs(self):
        return self._pairs

    def _to_index_or_pattern(self, value):  # noqa
        """Convert a value into an index (int) or a regex-like pattern."""
        if value is None:
            return "eof"

        text = str(value).strip()

        # Case 1: signed integer index
        if re.fullmatch(r"(?i)[+-]?\d+", text):
            return int(text)

        # Case 2: build a tokenized pattern
        tokens = []
        punct = f"[{re.escape(string.punctuation)}]+"
        token_pattern = rf"(?i)\s+|[a-z]+|{punct}|[0-9]+"

        for token in utils.split_by_matches(text, pattern=token_pattern):
            if re.fullmatch(punct, token):
                tokens.append(re.escape(token))
            elif re.fullmatch(r"\d+", token):
                tokens.append(r"[0-9]+")
            elif re.fullmatch(r"\s+", token):
                tokens.append(r"\s+")
            else:
                tokens.append(token)

        return "".join(tokens)


    def _validate_ranges(self) -> None:
        """Validate unchanged_lines as [[start, stop], ...] pairs."""
        msg = (
            "unchanged_lines must be in the format [[start, stop], ...] where "
            "start is an integer or string, and stop is an integer, string, or null"
        )

        raw = self.raw

        # Case 1: list of pairs
        if isinstance(raw, list) and all(
                isinstance(pair, list) and len(pair) == 2 for pair in raw):
            for start, stop in raw:
                if not isinstance(start, (int, str)):
                    raise exceptions.UnchangedLinesError(msg)
                if not (isinstance(stop, (int, str)) or stop is None):
                    raise exceptions.UnchangedLinesError(msg)
            return

        # Case 2: single pair [start, stop]
        if isinstance(raw, list) and len(raw) == 2:
            start, stop = raw
            if isinstance(start, (int, str)) and (
                    isinstance(stop, (int, str)) or stop is None):
                return
            raise exceptions.UnchangedLinesError(msg)

        # Anything else is invalid
        raise exceptions.UnchangedLinesError(msg)

    def _parse_list_ranges(self) -> None:
        """Parse unchanged_lines list into normalized [start, stop] pairs."""
        if not self.raw:
            return

        if isinstance(self.raw, (str, int)):
            return
        self._validate_ranges()
        self._pairs.clear()

        # Normalize: either a list of pairs or a single pair
        pairs = self.raw if isinstance(self.raw[0], list) else [self.raw]

        for start, stop in pairs:
            start_val = self._to_index_or_pattern(start)

            # Convert positive indices to zero‑based
            if isinstance(start_val, int) and start_val > 0:
                start_val -= 1

            normalized = [
                start_val,
                self._to_index_or_pattern(stop),
            ]
            self._pairs.append(normalized)

        if self._pairs:
            self._is_parsed = True

    def _parse_string_ranges(self) -> None:
        """Parse unchanged_lines string into a list of zero-based indices."""
        raw = self.raw

        # Only process primitive string/int forms; lists handled elsewhere
        if isinstance(raw, list):
            return

        if not isinstance(raw, (str, int)):
            msg = (
                "unchanged_lines must be in the format: "
                "idx-k, idx-m, idx-k:idx-j, ..."
            )
            raise exceptions.UnchangedLinesError(msg)

        text = str(raw).strip()

        # Capture comma-separated index/range expressions
        pattern = r"(?ix)\s*(?P<indices>[+-]?\d+(?:[\s0-9,:+-]*))\s*,?\s*"
        match = re.fullmatch(pattern, text)
        if not match:
            msg = (
                "unchanged_lines must be in the format: "
                "idx-k, idx-m, idx-k:idx-j, ..."
            )
            raise exceptions.UnchangedLinesError(msg)

        self._indices.clear()
        indices_text = match.group("indices")

        for token in indices_text.split(","):
            token = token.strip()
            if not token:
                continue

            # Case 1: single index
            if re.fullmatch(r"[+-]?\d+", token):
                idx = int(token)
                idx = idx if idx <= 0 else idx - 1  # convert to zero-based
                if idx not in self._indices:
                    self._indices.append(idx)
                continue

            # Case 2: range a:b
            if token.count(":") == 1:
                start_str, stop_str = (part.strip() for part in
                                       token.split(":"))
                if re.fullmatch(r"[+-]?\d+", start_str) and re.fullmatch(
                        r"[+-]?\d+", stop_str):
                    start = int(start_str)
                    stop = int(stop_str)

                    # convert to zero-based
                    start = start if start <= 0 else start - 1

                    if start < stop:
                        for idx in range(start, stop):
                            if idx not in self._indices:
                                self._indices.append(idx)

        if self._indices:
            self._is_parsed = True

    def _parse(self) -> None:
        """Parse unchanged_lines using list-based or string-based rules."""
        self._parse_list_ranges()
        self._parse_string_ranges()

    def apply_unchanged_lines(self, lines):
        """Mark lines as unchanged based on index rules or start/stop pairs."""

        def matches(index, idx_or_pat, text, total_):
            """Return True if the current line matches an index or pattern rule."""
            if isinstance(idx_or_pat, str):
                return bool(re.search(idx_or_pat, text))
            if idx_or_pat is None:
                return index == total_ - 1  # EOF
            # numeric index (supports negative indexing)
            idx_ = idx_or_pat if idx_or_pat >= 0 else total_ + idx_or_pat
            idx_ = idx_ if idx_ >= 0 else 0
            return idx_ == index

        total = len(lines)
        if total == 0:
            return

        # Case 1: explicit index list
        if self._indices:
            resolved = [(i if i >= 0 else total + i) for i in self._indices]
            for idx, line in enumerate(lines):
                if idx in resolved:
                    line.unchanged = True
            return

        # Case 2: start/stop pattern pairs
        if self._pairs:
            for start_rule, stop_rule in self._pairs:
                in_range = False
                for idx, line in enumerate(lines):
                    if in_range:
                        line.unchanged = True
                        if matches(idx, stop_rule, line.raw, total):
                            break
                    if matches(idx, start_rule, line.raw, total):
                        line.unchanged = True
                        in_range = True
