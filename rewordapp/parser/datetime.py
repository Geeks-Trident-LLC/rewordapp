
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

    def try_parse_with(self, pattern: str) -> bool:
        """Try parsing raw text using the given strptime pattern."""
        try:
            dt = datetime.strptime(self._raw_text, pattern)
        except ValueError:
            return False

        self._year = dt.year
        self._month = dt.month
        self._day = dt.day
        self._hour = dt.hour
        self._minute = dt.minute
        self._second = dt.second
        self._is_parsed = True
        return True


class RFC822DTParser(BaseDTParser):
    """Parse RFC 822–style datetime strings using multiple patterns."""

    def _parse(self):
        patterns = [
            "%d %b %y %H:%M:%S %Z",
            "%a, %d %b %y %H:%M:%S %Z",
            "%d %b %y %H:%M %Z",
            "%a, %d %b %y %H:%M %Z",
        ]

        for pattern in patterns:
            if self.try_parse_with(pattern):
                # Reconstruct output format by merging tokens from pattern + raw text
                fmt_parts = utils.split_by_matches(pattern)[:-2]
                raw_parts = utils.split_by_matches(self._raw_text)[-2:]
                self._output_format = "".join(fmt_parts + raw_parts)
                return


class RFC850DTParser(BaseDTParser):
    """Parse RFC 850–style datetime strings."""

    def _parse(self):
        patterns = [
            "%A, %d-%b-%y %H:%M:%S %Z",
        ]

        for pattern in patterns:
            if self.try_parse_with(pattern):
                # Reconstruct output format by merging tokens from pattern + raw text
                fmt_parts = utils.split_by_matches(pattern)[:-2]
                raw_parts = utils.split_by_matches(self._raw_text)[-2:]
                self._output_format = "".join(fmt_parts + raw_parts)
                return


class RFC1036DTParser(BaseDTParser):
    """Parse RFC 1036–style datetime strings."""

    def _parse(self):
        patterns = [
            "%a, %d %b %Y %H:%M:%S %Z",
            "%d %b %Y %H:%M:%S %Z",
        ]

        for pattern in patterns:
            if self.try_parse_with(pattern):
                # Reconstruct output format by merging tokens from pattern + raw text
                fmt_parts = utils.split_by_matches(pattern)[:-2]
                raw_parts = utils.split_by_matches(self._raw_text)[-2:]
                self._output_format = "".join(fmt_parts + raw_parts)
                return


class RFC1123DTParser(BaseDTParser):
    """Parse RFC 1123–style datetime strings."""

    def _parse(self):
        patterns = [
            "%a, %d %b %Y %H:%M:%S GMT",
        ]

        for pattern in patterns:
            if self.try_parse_with(pattern):
                # Reconstruct output format by merging tokens from pattern + raw text
                fmt_parts = utils.split_by_matches(pattern)[:-2]
                raw_parts = utils.split_by_matches(self._raw_text)[-2:]
                self._output_format = "".join(fmt_parts + raw_parts)
                return
