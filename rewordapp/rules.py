

import yaml
import re

import textwrap

from rewordapp import utils
from rewordapp.rewrite import mapping
import rewordapp.exceptions as exceptions


def load_rules(rule_text: str = "", rule_file: str = "") -> dict:
    """Load rewrite rules from YAML text or a YAML file and return a dictionary."""
    data = {}

    if rule_text:
        data = yaml.safe_load(rule_text)

    if rule_file:
        with open(rule_file, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)

    if not isinstance(data, dict):
        raise exceptions.InvalidRulesFormat(
            f"Rules must be a dictionary, but received {type(data).__name__}."
        )

    return data


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

    def __init__(self, rule_text: str="", rule_file: str=""):
        # Load provided YAML or fall back to default rule
        if rule_text or rule_file:
            parsed = load_rules(rule_text=rule_text, rule_file=rule_file)
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

    @property
    def text_with_rule_docs(self) -> str:
        """Return the text prefixed with a banner and links to rewrite‑rule documentation."""
        header = "# See the full list of rewrite rules in the wiki:"
        link = "# https://github.com/Geeks-Trident-LLC/rewordapp/wiki/Rewrite-Rule-Editor"

        border = "#" * max(len(header), len(link))
        docs_block = f"{border}\n{header}\n{link}\n{border}"

        return f"{docs_block}\n{self.text}"

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
        return UnchangedLinesRule(value) if isinstance(value, (str, int, list, tuple)) else None


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


class UnchangedLinesRule:
    def __init__(self, rule_value):
        self._rule_value = rule_value
        self._is_parsed = False

        self._indices = []
        self._slice_indices = []
        self._text_matcher = utils.TextMatcher()

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

        if text.lower() in ("none", "null", "eof"):
            return text if text.lower() == "eof" else 0

        if re.fullmatch(r"(?i)w\d+", text):
            return text.lower()

        return utils.text_to_pattern(text)

    def _validate_ranges(self) -> None:
        """Validate unchanged_lines as [[start, stop], ...] pairs."""
        msg = textwrap.dedent(
            f"""
            Invalid value for `unchanged_lines`.

            Expected one of the following pair formats:
            ======================================
            unchanged_lines: [<idx-i>, <idx-k>]
            unchanged_lines: [<idx-i>, <width>]
            unchanged_lines: [<start>, <stop>]
            unchanged_lines: [<start>, <idx-k>]
            unchanged_lines: [<start>, <width>]
            unchanged_lines: [<idx-i>, <stop>]
            ======================================
            
            Multiple pairs may be combined:
            ======================================
            unchanged_lines: [
              [<idx-i>, <idx-k>],
              [<idx-i>, <width>],
              ...,
              [<start>, <stop>]
            ]
            ======================================
            
            Received: {self.raw!r}
            """
        ).strip()

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

        # Lists are handled by the list parser
        if isinstance(raw, list):
            return

        # Only primitive string/int forms are valid here
        if not isinstance(raw, (str, int)):
            msg = textwrap.dedent(
                f"""
                Invalid value for `unchanged_lines`.

                Expected one of the following formats:
                ================================================================
                unchanged_lines: <idx-k>
                unchanged_lines: <idx-i>, <idx-j>, ..., <idx-n>
                unchanged_lines: <idx-i>, <matching-text-i>, ..., <matching-text-k>, <idx-n>
                unchanged_lines: <idx-i>, <idx-j>:<idx-k>, ..., <idx-n>
                unchanged_lines: <idx-i>, <idx-j>:<width>, ..., <idx-n>
                ================================================================
                
                Received: {self.raw!r}
                """
            ).strip()
            raise exceptions.UnchangedLinesError(msg)

        self._indices.clear()
        self._slice_indices.clear()
        self._text_matcher.clear()

        # Single integer form
        if isinstance(raw, int):
            value = raw if raw <= 0 else raw - 1
            self._indices.append(value)
            self._is_parsed = True
            return

        text = self.raw

        # String form: comma-separated items
        for item in re.split(r"\s*,\s*", text):

            # Simple index
            if re.fullmatch(r"-?\d+", item.strip()):
                value = int(item.strip())
                self._indices.append(value if value <=0 else value - 1)
                continue

            if item.strip().lower() == "eof":
                self._indices.append(-1)
                continue

            # Slice form: a:b
            if re.fullmatch(r"(?i)(null|none|-?\d+):(eof|[w-]?\d+)", item.strip()):
                a, b = item.lower().split(":")
                a = 0 if a in ("null", "none") else int(a)
                start = a if a <= 0 else a - 1
                if b == "eof":
                    self._slice_indices.append(slice(start, None))
                elif b.startswith("w"):
                    width = int(b[1:])
                    if width == 0:
                        continue
                    stop = start + width
                    if start < 0 <= stop:
                        self._slice_indices.append(slice(start, None))
                    else:
                        if stop > start:
                            self._slice_indices.append(slice(start, stop))
                else:
                    stop = int(b)
                    stop = stop if stop >= 0 else stop + 1
                    if start < 0 and stop == 0:
                        self._slice_indices.append(slice(start, None))
                    else:
                        if stop > start:
                            self._slice_indices.append(slice(start, stop))
                continue

            # Fallback: treat as matching text
            self._text_matcher.add_pattern(item)

        if self._indices or self._slice_indices or self._text_matcher:
            self._is_parsed = True

    def _parse(self) -> None:
        """Parse unchanged_lines using list-based or string-based rules."""
        self._parse_list_ranges()
        self._parse_string_ranges()

    def _apply_index_rules(self, lines):
        """Mark lines as unchanged based on slice ranges, explicit indices, and text patterns."""
        total = len(lines)

        # Slice-based ranges
        for slc in self._slice_indices:
            for line in lines[slc]:
                line.unchanged = True

        # Explicit indices and text-matching rules
        if self._indices or self._text_matcher:
            matcher = self._text_matcher
            resolved_indices = [(i if i >= 0 else total + i) for i in
                                self._indices]

            for idx, line in enumerate(lines):
                if line.unchanged:
                    continue
                if idx in resolved_indices:
                    line.unchanged = True
                elif matcher.matches(line.raw):
                    line.unchanged = True

    def _apply_pair_rules(self, lines):
        """Mark lines as unchanged based on start/stop index or pattern pairs."""
        total = len(lines)

        def match_rule(idx_: int, rule, text: str) -> bool:
            """Return True if the index or text satisfies the given rule."""
            if isinstance(rule, str):
                return bool(re.search(rule, text))
            if rule is None:
                return idx_ == total - 1  # EOF
            resolved = rule if rule >= 0 else total + rule
            return max(resolved, 0) == idx_

        for start_rule, stop_rule in self._pairs:
            # Normalize numeric start/stop pairs
            if isinstance(start_rule, int) and isinstance(stop_rule, int):
                if stop_rule < start_rule:
                    continue
                start_rule = start_rule - 1 if start_rule > 0 else start_rule
                stop_rule = stop_rule - 1 if stop_rule > 0 else stop_rule

            in_range = False

            for idx, line in enumerate(lines):
                if in_range:
                    line.unchanged = True
                    if match_rule(idx, stop_rule, line.raw):
                        break

                if match_rule(idx, start_rule, line.raw):
                    line.unchanged = True
                    in_range = True

                    # Case: start == stop (single-line range)
                    if isinstance(start_rule, int) and start_rule == stop_rule:
                        break

                    # Width form: wN
                    if isinstance(stop_rule, str) and re.fullmatch(r"(?i)w\d+",
                                                                   stop_rule):
                        width = int(stop_rule[1:])
                        if width in (0, 1):
                            line.unchanged = bool(width)
                            break
                        stop_rule = idx + width - 1

    def apply_unchanged_lines(self, lines):
        """Mark lines as unchanged using index rules, slice ranges, text patterns, or start/stop pairs."""
        total = len(lines)
        if total == 0:
            return

        # Index-based rules: slices, explicit indices, text patterns
        if self._indices or self._slice_indices or self._text_matcher:
            self._apply_index_rules(lines)
            return

        # Start/stop pair rules
        if self._pairs:
            self._apply_pair_rules(lines)
