
import re
import string
from datetime import datetime
import random

from rewordapp import utils


def random_day_or_month(base: int) -> int:
    """Return a randomized day/month value based on the given base."""
    if base == 1:
        return 1
    if base < 10:
        return random.randint(1, base)
    if base < 29:
        return random.randint(10, base)
    return random.randint(10, 29)


def random_time_component(base: int) -> int:
    """Return a randomized hour/minute/second based on the given base."""
    if base < 10:
        return random.randint(0, base)
    return random.randint(10, base)


class DateTimeParser:
    def __init__(self, text):
        raw_text = "".join(text) if isinstance(text, (list, tuple)) else str(text)

        self._raw_text = raw_text

        self._prefix = ""
        self._suffix = ""
        self._datetime = ""

        self._year = datetime.now().year
        self._month = datetime.now().month
        self._day = datetime.now().day
        self._hour = random.randint(0, 12)
        self._minute = random.randint(0, 59)
        self._second = random.randint(0, 59)

        self._parse()

    def __len__(self) -> int:
        """Return 1 if datetime was parsed, else 0."""
        return 1 if self._datetime else 0

    def __bool__(self) -> bool:
        """Return True if datetime was parsed."""
        return bool(self._datetime)

    # ------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------

    @property
    def raw(self) -> str:
        return self._raw_text

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def datetime(self):
        return self._datetime

    @property
    def rewritten(self):
        return f"{self._prefix}{self._datetime}{self._suffix}"


    def _parse_compact(self):
        # punct_pattern = f"[{re.escape(string.punctuation)}]"
        # pattern = rf"""(?ix)
        #     (?P<prefix>{punct_pattern}*)
        #     (?P<dt_txt>[a-z0-9].+[a-z0-9])
        #     (?P<suffix>{punct_pattern}*)
        #     """
        # match = re.fullmatch(pattern, self._raw_text)
        # if not match:
        #     return

        pass


    def _parse(self):
        # if not re.search(r"\s", self._raw_text):
        #     self._parse_compact()
        #     return
        #
        # punct_pattern = f"[{re.escape(string.punctuation)}]"
        # pattern = rf"""(?ix)
        #     (?P<prefix>{punct_pattern}*)
        #     (?P<datetime>[a-z0-9].+[a-z0-9])
        #     (?P<suffix>{punct_pattern}*)
        #     """
        #
        # match = re.fullmatch(pattern, self._raw_text)

        pass


class BaseDTParser:
    """Base class for parsing datetime components from text."""

    def __init__(self, text: str):
        self._raw_text = text
        self._is_parsed = False

        self._output_format = ""

        now = datetime.now()
        self._year = now.year
        self._month = now.month
        self._day = now.day
        self._hour = 0
        self._minute = 0
        self._second = 0

        self._parse()

    def __bool__(self) -> bool:
        return self._is_parsed

    def __len__(self) -> int:
        return int(self._is_parsed)

    @property
    def raw(self) -> str:
        return self._raw_text

    @property
    def rewritten(self) -> str:
        """Return rewritten datetime string or raw text if not parsed."""
        if not self:
            return self._raw_text

        month = random_day_or_month(self._month)
        day = random_day_or_month(self._day)
        hour = random_time_component(self._hour)
        minute = random_time_component(self._minute)
        second = random_time_component(self._second)

        dt = datetime(
            year=self._year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=random.randint(0, 999999),
        )
        return dt.strftime(self._output_format)

    def _parse(self):
        """Subclasses must implement parsing logic."""
        raise NotImplementedError("Subclasses must implement _parse()")

    def try_parse_with(self, fmt: str) -> bool:
        """Try parsing raw text using the given strptime fmt."""
        try:
            dt = datetime.strptime(self._raw_text, fmt)
        except ValueError:
            return False

        self._year = dt.year
        self._month = dt.month
        self._day = dt.day
        self._hour = dt.hour
        self._minute = dt.minute
        self._second = dt.second
        self._is_parsed = True

        if re.search("(?i) GMT$", fmt):
            # 1. Literal GMT at end (RFC 1123)
            self._output_format = fmt
        elif "." in fmt:
            # 2. Fractional seconds: preserve raw fractional precision
            fmt_prefix, _ = fmt.rsplit(".", 1)
            _, raw_fraction = self._raw_text.rsplit(".", 1)
            self._output_format = f"{fmt_prefix}.{raw_fraction}"
        elif re.search("(?i) %Z$", fmt):
            # 3. Named timezone (%Z) with space before it
            fmt_parts = utils.split_by_matches(fmt)[:-2]
            raw_parts = utils.split_by_matches(self._raw_text)[-2:]
            self._output_format = "".join(fmt_parts + raw_parts)
        elif re.search("(?i)[^ ]%Z$", fmt):
            # 4. Named timezone (%Z) with no preceding space
            prefix = fmt[:-2]
            consumed = dt.strftime(prefix)
            remainder = self._raw_text[len(consumed):]
            self._output_format = f"{prefix}{remainder}"
        else:
            # 5. Default: pattern is already the correct output format
            self._output_format = fmt

        return True

    def parse_with_any(self, *fmts):
        """Try parsing raw text using each pattern until one succeeds."""
        for fmt in fmts:
            if self.try_parse_with(fmt):
                return


class RFC822DTParser(BaseDTParser):
    """Parse RFC 822–style datetime strings using multiple fmts."""

    def _parse(self):
        self.parse_with_any(
            "%d %b %y %H:%M:%S %Z",
            "%a, %d %b %y %H:%M:%S %Z",
            "%d %b %y %H:%M %Z",
            "%a, %d %b %y %H:%M %Z",
        )


class RFC850DTParser(BaseDTParser):
    """Parse RFC 850–style datetime strings."""

    def _parse(self):
        self.parse_with_any(
            "%A, %d-%b-%y %H:%M:%S %Z",
        )


class RFC1036DTParser(BaseDTParser):
    """Parse RFC 1036–style datetime strings."""

    def _parse(self):
        self.parse_with_any(
            "%a, %d %b %Y %H:%M:%S %Z",
            "%d %b %Y %H:%M:%S %Z",
        )


class RFC1123DTParser(BaseDTParser):
    """Parse RFC 1123–style datetime strings."""

    def _parse(self):
        self.parse_with_any(
            "%a, %d %b %Y %H:%M:%S GMT",
        )


class RFC2822DTParser(BaseDTParser):
    """Parse RFC 2822–style datetime strings."""

    def _parse(self):
        self.parse_with_any(
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M %z",
            "%d %b %Y %H:%M:%S %z",
            "%d %b %Y %H:%M %z",
        )


class RFC3339DTParser(BaseDTParser):
    """Parse RFC 3339–style datetime strings."""

    def _parse(self):
        self.parse_with_any(
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z"
        )


class RFC7231DTParser(BaseDTParser):
    """Parse RFC 7231–style datetime strings."""

    @property
    def rewritten(self) -> str:
        """Return rewritten datetime string with RFC 1123 asctime() spacing fix."""
        result = super().rewritten

        # Fix asctime() day spacing: "Feb 07" → "Feb  7"
        if self._output_format == "%a %b %d %H:%M:%S %Y":
            # If the day is zero‑padded, replace " 0" with "  "
            # Example: "Sat Feb 07 12:57:36 2026" → "Sat Feb  7 12:57:36 2026"
            if len(result) > 8 and result[8] == "0":
                return result[:8] + " " + result[9:]

        return result

    def _parse(self):
        self.parse_with_any(
            "%a, %d %b %Y %H:%M:%S %Z",
            "%A, %d-%b-%y %H:%M:%S %Z",
            "%a %b %d %H:%M:%S %Y"
        )


class RFC5322DTParser(BaseDTParser):
    """Parse RFC 5322–style datetime strings."""

    def _parse(self):
        self.parse_with_any(
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M %z",
            "%d %b %Y %H:%M:%S %z",
            "%d %b %Y %H:%M %z",
        )
