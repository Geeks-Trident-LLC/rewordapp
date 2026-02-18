

import yaml
import re

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
        "MACAddressToken": "rewrite_mac",
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
        rule_value = self.get("rewrite_datetime", "") or ""
        if rule_value:
            return DateTimeTokenRule(rule_value)
        return None


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
            msg = "rewrite_datetime must be 'true|false, index, width'"
            raise exceptions.DateTimeRuleError(msg)

        pattern = r"""(?ix)
            (?P<flag>yes|no|true|false)\s*,\s*
            (?P<start>-?\d+)
            (?:\s*,\s*(?P<width>\d+|eol|null|none)?)?
        """

        match = re.fullmatch(pattern, self._rule_value.strip())
        if not match:
            msg = "rewrite_datetime must be 'flag, index, width'"
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
