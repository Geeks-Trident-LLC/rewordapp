

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
        dt_rule_txt = self.get("rewrite_datetime", "") or ""
        if dt_rule_txt:
            return DateTimeTokenRule(text=dt_rule_txt)
        return None


class DateTimeTokenRule:
    def __init__(self, text: str=""):
        self._text = text
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
        return self._text

    @property
    def is_rewrite(self):
        return self._is_rewrite

    def _parse(self):
        pattern = r"""(?ix)
            (?P<rewrite>yes|no|true|false)\s*,\s*
            (?P<start_pos>-?\d+)
            (\s*,\s*(?P<width>\d*))?
        """

        match = re.fullmatch(pattern, self._text.strip())
        if match:
            self._is_parsed = True
            self._is_rewrite = match.group("rewrite").lower() in ["yes", "true"]
            self._start_pos = match.group("start_pos")
            self._width = match.group("width")

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
        if self._width == "":
            return items[start_index:]

        # Width: default to 1, otherwise absolute integer
        width = 1 if self._width is None else abs(int(self._width))

        return items[start_index:start_index + width]