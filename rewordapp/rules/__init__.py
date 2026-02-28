import yaml

from rewordapp import exceptions as exceptions
from rewordapp.rewrite import mapping
from rewordapp.rules.unchanged import UnchangedLinesRule
from rewordapp.rules.dt import DateTimeTokenRule


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
        link = "# https://github.com/Geeks-Trident-LLC/rewordapp/wiki/Rewrite-Rules"

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
