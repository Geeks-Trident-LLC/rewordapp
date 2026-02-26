
import string
import re
from datetime import datetime, timedelta
from random import randint

from rewordapp import utils


def random_day(base: int) -> int:
    """Return a randomized day value different from the base."""
    return randint(1, 9) if base < 10 else randint(10, 28)


def random_month(base: int) -> int:
    """Return a randomized month value different from the base."""
    return randint(1, 9) if base < 10 else randint(10, 12)


def random_hour(base: int) -> int:
    """Return a randomized hour value different from the base."""
    if base < 10:
        return randint(0, 9)
    return randint(10, 12) if base < 13 else randint(10, 23)


def random_minute_or_second(base: int) -> int:
    """Return a randomized minute/second value different from the base."""
    return randint(1, 9) if base < 10 else randint(1, 59)


class BaseParser:
    def __init__(self, text):
        raw_text = "".join(text) if isinstance(text, (list, tuple)) else str(text)

        self._raw_text = raw_text

        self._prefix = ""
        self._suffix = ""
        self._data = ""

        self._is_parsed = False
        self._node = None
        self._output_format = ""

        self._parse()

    def __len__(self) -> int:
        """Return 1 if datetime was parsed, else 0."""
        return int(self._is_parsed)

    def __bool__(self) -> bool:
        """Return True if datetime was parsed."""
        return bool(self._is_parsed)

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
    def output_format(self) -> str:
        return self._output_format

    @property
    def rewritten(self):
        if not self:
            return self._raw_text
        return f"{self._prefix}{self._node.rewritten}{self._suffix}"

    def _build(self, func):
        """Extract prefix, core datetime text, and suffix,
        then delegate to a datetime parser."""
        punct_pattern = f"[{re.escape(string.punctuation)}]"
        pattern = rf"""(?ix)
            (?P<prefix>{punct_pattern}*)
            (?P<datetime>[a-z0-9].+[a-z0-9])
            (?P<suffix>{punct_pattern}*)
            """

        match = re.fullmatch(pattern, self._raw_text)
        if not match:
            return

        dt_text = match.group("datetime")
        node = func(dt_text)
        if node:
            self._is_parsed = True
            self._prefix = match.group("prefix")
            self._suffix = match.group("suffix")
            self._node = node
            self._output_format = f"{self._prefix}{node.output_format}{self._suffix}"

    def _parse(self):
        NotImplementedError("Subclasses must implement _parse()")

    def generate_new(self):
        if not self:
            return self.__class__(self.raw)
        rewritten = self.rewritten
        return self.__class__(rewritten)


class DateTimeParser(BaseParser):
    """Parse a datetime string using the full parser registry."""

    @property
    def datetime(self) -> str:
        return self._data

    def _parse(self) -> None:
        """Delegate parsing to the registered datetime parser."""
        self._build(build_datetime_parser)


class DateParser(BaseParser):
    """Parse a date string using the full parser registry."""

    @property
    def date(self) -> str:
        return self._data

    def _parse(self) -> None:
        """Delegate parsing to the registered date parser."""
        self._build(build_date_parser)


class TimeParser(BaseParser):
    """Parse a time string using the full parser registry."""

    @property
    def time(self) -> str:
        return self._data

    def _parse(self) -> None:
        """Delegate parsing to the registered time parser."""
        self._build(build_time_parser)


class BaseDTParser:
    """Base class for parsing datetime components from text."""

    def __init__(self, text: str):
        self._raw_text = text
        self._is_parsed = False

        self._output_format = ""
        self._dt = datetime.now()
        self._parse()

    def __bool__(self) -> bool:
        return self._is_parsed

    def __len__(self) -> int:
        return int(self._is_parsed)

    @property
    def raw(self) -> str:
        return self._raw_text

    @property
    def output_format(self) -> str:
        return self._output_format

    @property
    def rewritten(self) -> str:
        """Return rewritten datetime text, preserving original segment widths."""
        if not self:
            return self._raw_text

        randomized = self._generate_random_datetime()
        formatted = randomized.strftime(self._output_format)

        step1 = self._match_prefixed_number_widths(formatted)
        step2 = self._match_datetime_component_widths(step1)

        return step2

    def _match_prefixed_number_widths(self, formatted_text: str) -> str:
        """Match widths of letter‑prefixed numeric segments against the raw text."""
        raw = self._raw_text
        pattern = r"[bcdeghilnprtuvy]\s+\d+(?:\s+\d{4})?"

        raw_parts = utils.split_by_matches(raw, pattern)
        fmt_parts = utils.split_by_matches(formatted_text, pattern)

        if len(raw_parts) != len(fmt_parts):
            return formatted_text

        for idx, raw_seg in enumerate(raw_parts):
            fmt_seg = fmt_parts[idx]

            if re.match(pattern, raw_seg) and re.match(pattern, fmt_seg):
                raw_items = utils.split_by_matches(raw_seg)
                fmt_items = utils.split_by_matches(fmt_seg)

                for i, raw_item in enumerate(raw_items):
                    fmt_item = fmt_items[i]

                    if raw_item.isdigit() and fmt_item.isdigit():
                        width = len(raw_item)
                        fmt_items[i] = f"{int(fmt_item):>{width}}"
                    else:
                        fmt_items[
                            i] = fmt_item if fmt_item.strip() else raw_item

                fmt_parts[idx] = "".join(fmt_items)

        return "".join(fmt_parts)

    def _match_datetime_component_widths(self, formatted_text: str) -> str:
        """Match widths of date/time components to those in the raw text."""
        raw = self._raw_text

        pattern = (
            r"((\d{1,2}[/.-]){2}\d{2,4})|"  # 12/05/2024 or 12-05-24
            r"(\d{2,4}([/.-]\d{1,2}){2})|"  # 2024/05/12
            r"(\d{1,2}:\d{1,2}(:\d{1,2})?)"  # 12:30 or 12:30:45
        )

        raw_parts = utils.split_by_matches(raw)
        fmt_parts = utils.split_by_matches(formatted_text)

        if len(raw_parts) != len(fmt_parts):
            return formatted_text

        for idx, raw_seg in enumerate(raw_parts):
            fmt_seg = fmt_parts[idx]

            if re.match(pattern, raw_seg) and re.match(pattern, fmt_seg):
                raw_groups = utils.split_by_matches(raw_seg, pattern=r"[/.:-]")
                fmt_groups = utils.split_by_matches(fmt_seg, pattern=r"[/.:-]")

                for g_idx, raw_item in enumerate(raw_groups):
                    fmt_item = fmt_groups[g_idx]

                    if raw_item.isdigit() and fmt_item.isdigit():
                        if len(raw_item) < len(fmt_item):
                            trimmed = str(int(fmt_item))  # remove leading zeros
                            fmt_groups[g_idx] = (
                                trimmed if len(trimmed) == len(raw_item)
                                else trimmed[:len(raw_item)]
                            )

                new_fmt_seg = "".join(fmt_groups)

                if len(new_fmt_seg) == len(raw_seg):
                    fmt_parts[idx] = new_fmt_seg
                    if idx > 0:
                        fmt_parts[idx - 1] = raw_parts[idx - 1]

        return "".join(fmt_parts)

    def _generate_random_datetime(self) -> datetime:
        """Return a randomized datetime that never exceeds the original."""
        base = self._dt.replace(tzinfo=None)

        # Initial randomized candidate
        candidate = datetime(
            year=base.year,
            month=random_month(base.month),
            day=random_day(base.day),
            hour=random_hour(base.hour),
            minute=random_minute_or_second(base.minute),
            second=random_minute_or_second(base.second),
            microsecond=randint(0, 999999),
        )

        # If already earlier, return immediately
        if candidate < base:
            return candidate

        # Ensure month/day alignment before searching backward
        candidate = candidate.replace(
            month=base.month,
            day=base.day,
            hour=random_hour(base.hour),
            minute=random_minute_or_second(base.minute),
            second=random_minute_or_second(base.second)
        ) - timedelta(days=randint(1, 20))

        # Walk backward until month/day digit-width matches the base
        for _ in range(360):
            candidate -= timedelta(days=1)
            if (
                len(str(candidate.month)) == len(str(base.month))
                and len(str(candidate.day)) == len(str(base.day))
            ):
                return candidate

        return candidate

    def _parse(self):
        """Subclasses must implement parsing logic."""
        raise NotImplementedError("Subclasses must implement _parse()")

    def try_parse_with(self, fmt: str) -> bool:
        """Try parsing raw text using the given strptime fmt."""
        try:
            dt = datetime.strptime(self._raw_text, fmt)
        except ValueError:
            return False

        if re.search("(?i) GMT$", fmt):
            # 1. Literal GMT at end (RFC 1123)
            output_format = fmt
        elif fmt.count(".") == 1 or fmt.count(".") >= 3:
            # 2. Fractional seconds: preserve raw fractional precision
            fmt_prefix, _ = fmt.rsplit(".", 1)
            _, raw_fraction = self._raw_text.rsplit(".", 1)
            output_format = f"{fmt_prefix}.{raw_fraction}"
        elif re.search("(?i) %Z$", fmt):
            # 3. Named timezone (%Z) with space before it
            fmt_parts = utils.split_by_matches(fmt)[:-2]
            raw_parts = utils.split_by_matches(self._raw_text)[-2:]
            output_format = "".join(fmt_parts + raw_parts)
        elif re.search("(?i)[^ ]%Z$", fmt):
            # 4. Named timezone (%Z) with no preceding space
            prefix = fmt[:-2]
            consumed = dt.strftime(prefix)
            remainder = self._raw_text[len(consumed):]
            output_format = f"{prefix}{remainder}"
        else:
            # 5. Default: pattern is already the correct output format
            output_format = fmt

        # --- ISO date-length consistency check ---
        if "T" in self._raw_text and "T" in output_format:
            fmt_date, _ = output_format.split("T", 1)
            raw_date, _ = self._raw_text.split("T", 1)

            # If the formatted date doesn't match the raw date length, reject
            if len(dt.strftime(fmt_date)) != len(raw_date):
                return False

        # --- Store parsed components ---

        self._output_format = output_format
        self._dt = dt
        self._is_parsed = True

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


class ISO8601DTParser(BaseDTParser):
    """Parse ISO 8601 datetime strings."""

    def _parse(self):
        self.parse_with_any(
            # Ordinal date + time
            "%Y-%jT%H:%M:%S",
            "%Y-%jT%H:%M:%S%z",
            "%Y-%jT%H:%M:%S.%f",
            "%Y-%jT%H:%M:%S.%f%z",

            "%Y%jT%H%M%S",
            "%Y%jT%H%M%S%z",
            "%Y%jT%H%M%S.%f",
            "%Y%jT%H%M%S.%f%z",

            # Week date + time
            "%G-W%V-%uT%H:%M:%S",
            "%G-W%V-%uT%H:%M:%S%z",
            "%GW%V%uT%H%M%S",
            "%GW%V%uT%H%M%S%z",

            "%G-W%V-%uT%H:%M:%S.%f",
            "%G-W%V-%uT%H:%M:%S.%f%z",
            "%GW%V%uT%H%M%S.%f",
            "%GW%V%uT%H%M%S.%f%z",

            # Calendar date + time
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M%z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",

            "%Y%m%dT%H%M",
            "%Y%m%dT%H%M%S",
            "%Y%m%dT%H%M%S.%f",
            "%Y%m%dT%H%M%z",
            "%Y%m%dT%H%M%S%z",
            "%Y%m%dT%H%M%S.%f%z",

        )


class ISO8601DateParser(BaseDTParser):
    """Parse ISO 8601 date strings."""

    def _parse(self):
        self.parse_with_any(
            # Ordinal Date
            "%Y-%j",
            "%Y%j",

            # Week date
            "%G-W%V-%u",
            "%G-W%V",
            "%GW%V%u",
            "%GW%V",

            # Calendar date
            "%Y-%m-%d",
            "%Y%m%d",

        )


class ISO8601TimeParser(BaseDTParser):
    """Parse ISO 8601 datetime strings."""

    def _parse(self):
        self.parse_with_any(
            # time
            "%H:%M:%S.%f",
            "%H:%M:%S",
            "%H:%M",

            "%H:%M:%S.%f%z",
            "%H:%M:%S%z",
            "%H:%M%z",

            "%H%M%S.%f",
            "%H%M%S",
            "%H%M",

            "%H%M%S.%f%z",
            "%H%M%S%z",
            "%H%M%z",

        )


class UserDTParser(BaseDTParser):
    """Parse Common User datetime strings."""

    def _parse_12h_style(self):
        """Attempt parsing 12‑hour (AM/PM) datetime formats."""
        if self:
            return

        if re.search(r"(?i)[ap]m", self._raw_text):
            if "-" in self._raw_text:
                self.parse_with_any(
                    '%m-%d-%Y %I%p',
                     '%m-%d-%Y %I %p',
                     '%m-%d-%Y %I:%M%p',
                     '%m-%d-%Y %I:%M %p',
                     '%m-%d-%Y %I:%M:%S %p',
                     '%m-%d-%Y %I:%M:%S.%f %p',
                     '%m-%d-%Y %I:%M:%S.%f %p %z',
                     '%m-%d-%Y %I:%M:%S.%f %p %Z'
                )
                return
            elif "/" in self._raw_text:
                self.parse_with_any(
                    "%m/%d/%Y %I%p",
                    "%m/%d/%Y %I %p",
                    "%m/%d/%Y %I:%M%p",
                    "%m/%d/%Y %I:%M %p",
                    "%m/%d/%Y %I:%M:%S %p",
                    "%m/%d/%Y %I:%M:%S.%f %p",
                    "%m/%d/%Y %I:%M:%S.%f %p %z",
                    "%m/%d/%Y %I:%M:%S.%f %p %Z",
                )
                return

            elif self._raw_text.count(",") == 2:
                self.parse_with_any(
                    "%a, %b %d, %Y %I%p",
                    "%A, %B %d, %Y %I%p",
                    "%a, %b %d, %Y %I %p",
                    "%A, %B %d, %Y %I %p",
                    "%a, %b %d, %Y %I:%M %p",
                    "%A, %B %d, %Y %I:%M %p",
                    "%a, %b %d, %Y %I:%M:%S %p",
                    "%A, %B %d, %Y %I:%M:%S %p",
                    "%a, %b %d, %Y %I:%M:%S.%f %p",
                    "%A, %B %d, %Y %I:%M:%S.%f %p",

                    "%a, %b %d, %Y %I%p%Z",
                    "%A, %B %d, %Y %I%p%Z",
                    "%a, %b %d, %Y %I%p %Z",
                    "%A, %B %d, %Y %I%p %Z",
                    "%a, %b %d, %Y %I %p %Z",
                    "%A, %B %d, %Y %I %p %Z",
                    "%a, %b %d, %Y %I:%M %p %Z",
                    "%A, %B %d, %Y %I:%M %p %Z",
                    "%a, %b %d, %Y %I:%M:%S %p %Z",
                    "%A, %B %d, %Y %I:%M:%S %p %Z",
                    "%a, %b %d, %Y %I:%M:%S.%f %p %Z",
                    "%A, %B %d, %Y %I:%M:%S.%f %p %Z",

                    "%a, %b %d, %Y %I%p%z",
                    "%A, %B %d, %Y %I%p%z",
                    "%a, %b %d, %Y %I%p %z",
                    "%A, %B %d, %Y %I%p %z",
                    "%a, %b %d, %Y %I %p %z",
                    "%A, %B %d, %Y %I %p %z",
                    "%a, %b %d, %Y %I:%M %p %z",
                    "%A, %B %d, %Y %I:%M %p %z",
                    "%a, %b %d, %Y %I:%M:%S %p %z",
                    "%A, %B %d, %Y %I:%M:%S %p %z",
                    "%a, %b %d, %Y %I:%M:%S.%f %p %z",
                    "%A, %B %d, %Y %I:%M:%S.%f %p %z",
                )
                return
            elif self._raw_text.count(",") == 1:
                self.parse_with_any(
                    "%b %d, %Y %I%p",
                    "%B %d, %Y %I%p",
                    "%b %d, %Y %I %p",
                    "%B %d, %Y %I %p",
                    "%b %d, %Y %I:%M %p",
                    "%B %d, %Y %I:%M %p",
                    "%b %d, %Y %I:%M:%S %p",
                    "%B %d, %Y %I:%M:%S %p",
                    "%b %d, %Y %I:%M:%S.%f %p",
                    "%B %d, %Y %I:%M:%S.%f %p",

                    "%b %d, %Y %I%p %Z",
                    "%B %d, %Y %I%p %Z",
                    "%b %d, %Y %I %p %Z",
                    "%B %d, %Y %I %p %Z",
                    "%b %d, %Y %I:%M %p %Z",
                    "%B %d, %Y %I:%M %p %Z",
                    "%b %d, %Y %I:%M:%S %p %Z",
                    "%B %d, %Y %I:%M:%S %p %Z",
                    "%b %d, %Y %I:%M:%S.%f %p %Z",
                    "%B %d, %Y %I:%M:%S.%f %p %Z",

                    "%b %d, %Y %I%p %z",
                    "%B %d, %Y %I%p %z",
                    "%b %d, %Y %I %p %z",
                    "%B %d, %Y %I %p %z",
                    "%b %d, %Y %I:%M %p %z",
                    "%B %d, %Y %I:%M %p %z",
                    "%b %d, %Y %I:%M:%S %p %z",
                    "%B %d, %Y %I:%M:%S %p %z",
                    "%b %d, %Y %I:%M:%S.%f %p %z",
                    "%B %d, %Y %I:%M:%S.%f %p %z",
                )
                return
            else:
                self.parse_with_any(
                    "%A %I %p",
                    "%a %I %p",
                    "%A %I%p",
                    "%a %I%p",
                )
                return

    def _parse_other_style(self):
        """Parse datetime strings using month/weekday names in various layouts."""

        if self:
            return

        # Weekday-month-day
        if re.match(r"(?i)[a-z]+, +[a-z]+ +\d{1,2}, +\d{4} ", self._raw_text):
            self.parse_with_any(
                "%A, %B %d, %Y %H:%M",
                "%A, %B %d, %Y %H:%M:%S",
                "%A, %B %d, %Y %H:%M:%S.%f",

                "%a, %b %d, %Y %H:%M",
                "%a, %b %d, %Y %H:%M:%S",
                "%a, %b %d, %Y %H:%M:%S.%f",

                "%A, %B %d, %Y %H:%M %z",
                "%A, %B %d, %Y %H:%M:%S %z",
                "%A, %B %d, %Y %H:%M:%S.%f %z",

                "%A, %B %d, %Y %H:%M %Z",
                "%A, %B %d, %Y %H:%M:%S %Z",
                "%A, %B %d, %Y %H:%M:%S.%f %Z",

                "%a, %b %d, %Y %H:%M %z",
                "%a, %b %d, %Y %H:%M:%S %z",
                "%a, %b %d, %Y %H:%M:%S.%f %z",

                "%a, %b %d, %Y %H:%M %Z",
                "%a, %b %d, %Y %H:%M:%S %Z",
                "%a, %b %d, %Y %H:%M:%S.%f %Z",
            )
            return

        # month-day
        if re.match(r"(?i)[a-z]+ +\d{1,2}, +\d{4} ", self._raw_text):
            self.parse_with_any(
                "%B %d, %Y %H:%M",
                "%B %d, %Y %H:%M:%S",
                "%B %d, %Y %H:%M:%S.%f",

                "%b %d, %Y %H:%M",
                "%b %d, %Y %H:%M:%S",
                "%b %d, %Y %H:%M:%S.%f",

                "%B %d, %Y %H:%M %z",
                "%B %d, %Y %H:%M:%S %z",
                "%B %d, %Y %H:%M:%S.%f %z",

                "%B %d, %Y %H:%M %Z",
                "%B %d, %Y %H:%M:%S %Z",
                "%B %d, %Y %H:%M:%S.%f %Z",

                "%b %d, %Y %H:%M %z",
                "%b %d, %Y %H:%M:%S %z",
                "%b %d, %Y %H:%M:%S.%f %z",

                "%b %d, %Y %H:%M %Z",
                "%b %d, %Y %H:%M:%S %Z",
                "%b %d, %Y %H:%M:%S.%f %Z",
            )
            return

        # day-month
        if re.match(r"(?i)\d{1,2} +[a-z]+ +\d{4} ", self._raw_text):
            if self._raw_text.count("."):
                self.parse_with_any(
                    "%d %B %Y %H:%M:%S.%f",
                    "%d %b %Y %H:%M:%S.%f",

                    "%d %B %Y %H:%M:%S.%f %z",
                    "%d %B %Y %H:%M:%S.%f %Z",

                    "%d %b %Y %H:%M:%S.%f %z",
                    "%d %b %Y %H:%M:%S.%f %Z",

                )
                return

            if self._raw_text.count(":") == 2:
                self.parse_with_any(
                    "%d %B %Y %H:%M:%S",
                    "%d %b %Y %H:%M:%S",

                    "%d %B %Y %H:%M:%S %z",
                    "%d %B %Y %H:%M:%S %Z",

                    "%d %b %Y %H:%M:%S %z",
                    "%d %b %Y %H:%M:%S %Z",
                )
                return

            self.parse_with_any(
                "%d %B %Y %H:%M",
                "%d %b %Y %H:%M",

                "%d %B %Y %H:%M %z",
                "%d %B %Y %H:%M %Z",

                "%d %b %Y %H:%M %z",
                "%d %b %Y %H:%M %Z",
            )
            return


    def _parse_compact_numeric_style(self) -> None:
        """Parse compact numeric datetime strings (YYYYMMDDHHMM...)."""
        text = self._raw_text

        # Already parsed or clearly not compact (contains separators)
        if self or re.match(r"\d{2,4}[/.-]", text) or not re.match(r"\d{8}", text):
            return

        spaced_formats = [
            "%Y%m%d %H:%M",
            "%Y%m%d %H:%M:%S",
            "%Y%m%d %H:%M:%S.%f",

            "%Y%m%d %H:%M %Z",
            "%Y%m%d %H:%M:%S %Z",
            "%Y%m%d %H:%M:%S.%f %Z",

            "%Y%m%d %H:%M %z",
            "%Y%m%d %H:%M:%S %z",
            "%Y%m%d %H:%M:%S.%f %z",
        ]

        compact_formats = [
            "%Y%m%d%H%M",
            "%Y%m%d%H%M%S",
            "%Y%m%d%H%M%S.%f",

            "%Y%m%d%H%M%Z",
            "%Y%m%d%H%M%S%Z",
            "%Y%m%d%H%M%S.%f%Z",

            "%Y%m%d%H%M%z",
            "%Y%m%d%H%M%S%z",
            "%Y%m%d%H%M%S.%f%z",
        ]

        if " " in text:
            self.parse_with_any(*spaced_formats)
        else:
            self.parse_with_any(*compact_formats)

    def _parse_us_style(self) -> None:
        """Parse US‑style numeric dates (MM/DD/YYYY or MM‑DD‑YYYY)."""
        if self:
            return

        text = self._raw_text

        # Match: MM/DD/YYYY␣ or MM-DD-YYYY␣
        if not re.match(r"(\d{1,2}[/-]){2}\d{4} ", text):
            return

        # Reject impossible month (e.g., 15/02/2026)
        month = int(re.split(r"[/-]+", text)[0])
        if month > 12:
            return

        dash_formats = [
            "%m-%d-%Y %H:%M",
            "%m-%d-%Y %H:%M:%S",
            "%m-%d-%Y %H:%M:%S.%f",

            "%m-%d-%Y %H:%M %Z",
            "%m-%d-%Y %H:%M:%S %Z",
            "%m-%d-%Y %H:%M:%S.%f %Z",

            "%m-%d-%Y %H:%M %z",
            "%m-%d-%Y %H:%M:%S %z",
            "%m-%d-%Y %H:%M:%S.%f %z",
        ]

        slash_formats = [
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S.%f",

            "%m/%d/%Y %H:%M %Z",
            "%m/%d/%Y %H:%M:%S %Z",
            "%m/%d/%Y %H:%M:%S.%f %Z",

            "%m/%d/%Y %H:%M %z",
            "%m/%d/%Y %H:%M:%S %z",
            "%m/%d/%Y %H:%M:%S.%f %z",
        ]

        if "-" in text:
            self.parse_with_any(*dash_formats)
        else:
            self.parse_with_any(*slash_formats)

    def _parse_european_style(self) -> None:
        """Parse European-style numeric dates (DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY)."""
        if self:
            return

        text = self._raw_text

        # Match: DD/MM/YYYY␣ or DD-MM-YYYY␣ or DD.MM.YYYY␣
        if not re.match(r"(\d{1,2}[./-]){2}\d{4} ", text):
            return

        # Reject impossible month (e.g., 15/02/2026 is fine, but 15/20/2026 is not)
        # Month is the *second* numeric component in European formats.
        month = int(re.split(r"[./-]+", text)[1])
        if month > 12:
            return

        dash_formats = [
            "%d-%m-%Y %H:%M",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y %H:%M:%S.%f",

            "%d-%m-%Y %H:%M %Z",
            "%d-%m-%Y %H:%M:%S %Z",
            "%d-%m-%Y %H:%M:%S.%f %Z",

            "%d-%m-%Y %H:%M %z",
            "%d-%m-%Y %H:%M:%S %z",
            "%d-%m-%Y %H:%M:%S.%f %z",
        ]

        slash_formats = [
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S.%f",

            "%d/%m/%Y %H:%M %Z",
            "%d/%m/%Y %H:%M:%S %Z",
            "%d/%m/%Y %H:%M:%S.%f %Z",

            "%d/%m/%Y %H:%M %z",
            "%d/%m/%Y %H:%M:%S %z",
            "%d/%m/%Y %H:%M:%S.%f %z",
        ]

        dot_formats = [
            "%d.%m.%Y %H:%M",
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y %H:%M:%S.%f",

            "%d.%m.%Y %H:%M %Z",
            "%d.%m.%Y %H:%M:%S %Z",
            "%d.%m.%Y %H:%M:%S.%f %Z",

            "%d.%m.%Y %H:%M %z",
            "%d.%m.%Y %H:%M:%S %z",
            "%d.%m.%Y %H:%M:%S.%f %z",
        ]

        if "-" in text:
            self.parse_with_any(*dash_formats)
        elif "/" in text:
            self.parse_with_any(*slash_formats)
        else:
            self.parse_with_any(*dot_formats)

    def _parse_iso_style(self) -> None:
        """Parse ISO-like numeric dates (YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD)."""
        if self:
            return

        text = self._raw_text

        # Match: YYYY-MM-DD␣ or YYYY/MM/DD␣ or YYYY.MM.DD␣
        if not re.match(r"\d{4}[./-]", text):
            return

        hyphen_formats = [
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",

            "%Y-%m-%d %H:%M:%S.%f %Z",
            "%Y-%m-%d %H:%M:%S.%f %z",
            "%Y-%m-%d %H:%M:%S.%f%Z",
            "%Y-%m-%d %H:%M:%S.%f%z",

            "%Y-%m-%d %H:%M:%S %Z",
            "%Y-%m-%d %H:%M:%S %z",
            "%Y-%m-%d %H:%M:%S%Z",
            "%Y-%m-%d %H:%M:%S%z",

            "%Y-%m-%d %H:%M %Z",
            "%Y-%m-%d %H:%M %z",
            "%Y-%m-%d %H:%M%Z",
            "%Y-%m-%d %H:%M%z",
        ]

        slash_formats = [
            "%Y/%m/%d %H:%M:%S.%f",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",

            "%Y/%m/%d %H:%M:%S.%f %Z",
            "%Y/%m/%d %H:%M:%S.%f %z",
            "%Y/%m/%d %H:%M:%S.%f%Z",
            "%Y/%m/%d %H:%M:%S.%f%z",

            "%Y/%m/%d %H:%M:%S %Z",
            "%Y/%m/%d %H:%M:%S %z",
            "%Y/%m/%d %H:%M:%S%Z",
            "%Y/%m/%d %H:%M:%S%z",

            "%Y/%m/%d %H:%M %Z",
            "%Y/%m/%d %H:%M %z",
            "%Y/%m/%d %H:%M%Z",
            "%Y/%m/%d %H:%M%z",
        ]

        dot_formats = [
            "%Y.%m.%d %H:%M:%S.%f",
            "%Y.%m.%d %H:%M:%S",
            "%Y.%m.%d %H:%M",

            "%Y.%m.%d %H:%M:%S.%f %Z",
            "%Y.%m.%d %H:%M:%S.%f %z",
            "%Y.%m.%d %H:%M:%S.%f%Z",
            "%Y.%m.%d %H:%M:%S.%f%z",

            "%Y.%m.%d %H:%M:%S %Z",
            "%Y.%m.%d %H:%M:%S %z",
            "%Y.%m.%d %H:%M:%S%Z",
            "%Y.%m.%d %H:%M:%S%z",

            "%Y.%m.%d %H:%M %Z",
            "%Y.%m.%d %H:%M %z",
            "%Y.%m.%d %H:%M%Z",
            "%Y.%m.%d %H:%M%z",
        ]

        if "-" in text:
            self.parse_with_any(*hyphen_formats)
        elif "/" in text:
            self.parse_with_any(*slash_formats)
        else:
            self.parse_with_any(*dot_formats)

    def _parse_iso_week_style(self) -> None:
        """Parse ISO week dates (YYYY‑Www‑d)."""
        if self:
            return

        text = self._raw_text

        # --- ISO week date: YYYY‑Www‑d or YYYYWwwd ------------------------------
        if re.match(r"\d{4}-?W\d{2}-?\d ", text):
            hyphen_formats = [
                "%G-W%V-%u %H:%M",
                "%G-W%V-%u %H:%M:%S",
                "%G-W%V-%u %H:%M:%S.%f",

                "%G-W%V-%u %H:%M %Z",
                "%G-W%V-%u %H:%M:%S %Z",
                "%G-W%V-%u %H:%M:%S.%f %Z",

                "%G-W%V-%u %H:%M %z",
                "%G-W%V-%u %H:%M:%S %z",
                "%G-W%V-%u %H:%M:%S.%f %z",
            ]

            compact_formats = [
                "%GW%V%u %H%M",
                "%GW%V%u %H%M%S",
                "%GW%V%u %H%M%S.%f",

                "%GW%V%u %H%M %Z",
                "%GW%V%u %H%M%S %Z",
                "%GW%V%u %H%M%S.%f %Z",

                "%GW%V%u %H%M %z",
                "%GW%V%u %H%M%S %z",
                "%GW%V%u %H%M%S.%f %z",
            ]

            if "-" in text:
                self.parse_with_any(*hyphen_formats)
            else:
                self.parse_with_any(*compact_formats)
            return

    def _parse_iso_ordinal_style(self) -> None:
        """Parse ISO ordinal dates (YYYY‑DDD)"""
        if self:
            return

        text = self._raw_text

        # --- Ordinal date: YYYY‑DDD or YYYYDDD ---------------------------------
        if re.match(r"\d{4}-?\d{3} ", text):
            hyphen_formats = [
                "%Y-%j %H:%M",
                "%Y-%j %H:%M:%S",
                "%Y-%j %H:%M:%S.%f",

                "%Y-%j %H:%M %Z",
                "%Y-%j %H:%M:%S %Z",
                "%Y-%j %H:%M:%S.%f %Z",

                "%Y-%j %H:%M %z",
                "%Y-%j %H:%M:%S %z",
                "%Y-%j %H:%M:%S.%f %z",
            ]

            compact_formats = [
                "%Y%j %H%M",
                "%Y%j %H%M%S",
                "%Y%j %H%M%S.%f",

                "%Y%j %H%M %Z",
                "%Y%j %H%M%S %Z",
                "%Y%j %H%M%S.%f %Z",

                "%Y%j %H%M %z",
                "%Y%j %H%M%S %z",
                "%Y%j %H%M%S.%f %z",
            ]

            if "-" in text:
                self.parse_with_any(*hyphen_formats)
            else:
                self.parse_with_any(*compact_formats)
            return

    def _parse_custom_case(self):
        """Parse month–day formats using 12‑hour or 24‑hour patterns."""
        if self:
            return

        text = self._raw_text

        # 12‑hour formats with AM/PM
        if re.search(r"(?i)[ap]m", text):
            self.parse_with_any(
                "%b %d %I %p",
                "%b %d %I:%M %p",
                "%b %d %I:%M:%S %p %z",
            )
            return

        # 24‑hour formats
        self.parse_with_any(
            "%b %d %H",
            "%b %d %H:%M",
            "%b %d %H:%M:%S",
        )

    def _parse(self):
        self._parse_12h_style()
        self._parse_other_style()
        self._parse_compact_numeric_style()
        self._parse_us_style()
        self._parse_european_style()
        self._parse_iso_style()
        self._parse_iso_week_style()
        self._parse_iso_ordinal_style()
        self._parse_custom_case()


class UserDateParser(BaseDTParser):
    """Parse Common User date strings."""

    def _parse_user_date_style(self):
        """Parse date‑only strings using common user‑typed formats."""
        if self:
            return

        text = self._raw_text

        # Weekday, Month Day, Year
        if re.match(r"(?i)[a-z]+,\s+[a-z]+\s+\d{1,2},\s+\d{4}", text):
            self.parse_with_any(
                "%A, %B %d, %Y",
                "%a, %b %d, %Y",
            )
            return

        # Month Day, Year
        if re.match(r"(?i)[a-z]+\s+\d{1,2},\s+\d{4}", text):
            self.parse_with_any(
                "%B %d, %Y",
                "%b %d, %Y",
            )
            return

        # Day Month Year
        if re.match(r"(?i)\d{1,2}\s+[a-z]+\s+\d{4}", text):
            self.parse_with_any(
                "%d %B %Y",
                "%d %b %Y",
            )
            return

        # Month day Year
        if re.match(r"(?i)[a-z]+\s+\d{1,2}\s+\d{4}", text):
            self.parse_with_any(
                "%B %d %Y",
                "%b %d %Y",
            )
            return

        if re.fullmatch(r"\d\d?[/-]\d\d?[/-]\d{2}", text):
            month = int(re.split(r"[/-]", text)[0])
            if month > 12:
                return
            self.parse_with_any(
                "%m/%d/%y",
                "%m-%d-%y",
            )
            return

    def _parse_compact_date_style(self):
        """Parse compact date-only strings in YYYYMMDD format."""
        if self:
            return

        text = self._raw_text

        # Must be exactly 8 digits: YYYYMMDD
        if len(text) == 8 and text.isdigit():
            month = int(text[4:6])
            day = int(text[6:8])

            # Basic sanity check
            if month > 12 or day > 31:
                return

            self.parse_with_any("%Y%m%d")

    def _parse_us_or_eu_date_style(self):
        if self:
            return

        text = self._raw_text

        if not re.match(r"(\d{1,2}[./-]){2}\d{4}", text):
            return

        # Match: us or european date style
        if "." in text:
            self.parse_with_any("%d.%m.%Y")
            return
        else:
            month = int(re.split("[/-]+", text)[0])
            if month <= 12:
                self.parse_with_any(
                    "%m-%d-%Y",
                    "%m/%d/%Y",
                )
                return

            self.parse_with_any(
                "%d-%m-%Y",
                "%d/%m/%Y",
            )

    def _parse_iso_date_style(self) -> None:
        """Parse ISO-style date-only strings: week dates (YYYY-Www-d),
        ordinal dates (YYYY-DDD), or calendar dates (YYYY-MM-DD)."""
        if self:
            return

        text = self._raw_text

        # --- ISO week date: YYYY-Www-d or YYYYWwwd --------------------------------
        if re.match(r"\d{4}-?W\d{2}-?\d", text):
            self.parse_with_any(
                "%G-W%V-%u",  # hyphenated
                "%GW%V%u",  # compact
            )
            return

        # --- ISO ordinal date: YYYY-DDD or YYYYDDD --------------------------------
        if re.match(r"\d{4}-?\d{3}", text):
            self.parse_with_any(
                "%Y-%j",  # hyphenated
                "%Y%j",  # compact
            )
            return

        # --- ISO calendar date: YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD ----------------
        if not re.match(r"\d{4}[./-]", text):
            return

        self.parse_with_any(
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y.%m.%d",
        )

    def _parse(self):
        self._parse_user_date_style()
        self._parse_compact_date_style()
        self._parse_us_or_eu_date_style()
        self._parse_iso_date_style()


class UserTimeParser(BaseDTParser):
    """Parse Common User time strings."""

    def _parse_user_12h_style(self) -> None:
        """Parse common 12‑hour user-typed times containing AM/PM."""
        if self:
            return

        text = self._raw_text

        # Must contain AM/PM (case‑insensitive)
        if not re.search(r"(?i)[ap]m", text):
            return

        # Fractional seconds (e.g., 8:30:15.123 PM or 083015.123PM)
        if "." in text:
            self.parse_with_any(
                "%I:%M:%S.%f %p",
                "%I:%M:%S.%f %p %z",
                "%I:%M:%S.%f %p %Z",

                "%I%M%S.%f%p",
                "%I%M%S.%f%p%z",
                "%I%M%S.%f%p%Z",
            )
            return

        # HH:MM:SS AM/PM
        if re.match(r"(\d{1,2}:){2}\d{1,2}\s", text):
            self.parse_with_any(
                "%I:%M:%S %p",
                "%I:%M:%S %p %z",
                "%I:%M:%S %p %Z",
            )
            return

        # HH:MM AM/PM
        if re.match(r"\d{1,2}:\d{1,2}\s", text):
            self.parse_with_any(
                "%I:%M %p",
                "%I:%M %p %z",
                "%I:%M %p %Z",
            )
            return

        # Compact or minimal forms (H PM, HPM, HHMMSSPM, etc.)
        self.parse_with_any(
            "%I %p",
            "%I%p",
            "%I%M%p",
            "%I%M%S%p",

            "%I %p %z",
            "%I%p%z",
            "%I%M%p%z",
            "%I%M%S%p%z",

            "%I %p %Z",
            "%I%p%Z",
            "%I%M%p%Z",
            "%I%M%S%p%Z",
        )

    def _parse_user_24h_style(self) -> None:
        """Parse common user-typed 24‑hour time strings."""
        if self:
            return

        text = self._raw_text

        # Fractional seconds (e.g., 12:34:56.789 or 123456.789)
        if "." in text:
            self.parse_with_any(
                "%H:%M:%S.%f",
                "%H:%M:%S.%f %z",
                "%H:%M:%S.%f %Z",

                "%H%M%S.%f",
                "%H%M%S.%f%z",
                "%H%M%S.%f%Z",
            )
            return

        # HH:MM:SS
        if re.match(r"(\d{1,2}:){2}\d{1,2}", text):
            self.parse_with_any(
                "%H:%M:%S",
                "%H:%M:%S %z",
                "%H:%M:%S %Z",
            )
            return

        # HH:MM
        if re.match(r"\d{1,2}:\d{1,2}", text):
            self.parse_with_any(
                "%H:%M",
                "%H:%M %z",
                "%H:%M %Z",
            )
            return

        # Compact forms: H, HHMM, HHMMSS, with optional timezone
        self.parse_with_any(
            "%H",
            "%H%M",
            "%H%M%S",

            "%H%z",
            "%H%M%z",
            "%H%M%S%z",

            "%H%Z",
            "%H%M%Z",
            "%H%M%S%Z",
        )

    def _parse(self):
        if self:
            return

        self._parse_user_12h_style()
        self._parse_user_24h_style()


def build_datetime_parser(text):
    """Return the first parser that successfully interprets the given datetime string."""
    parser_classes = [
        UserDTParser,
        ISO8601DTParser,
        RFC5322DTParser,
        RFC7231DTParser,
        RFC3339DTParser,
        RFC2822DTParser,
        RFC1123DTParser,
        RFC1036DTParser,
        RFC850DTParser,
        RFC822DTParser,
    ]
    for parser_cls in parser_classes:
        parser = parser_cls(text)
        if parser:
            return parser

    # Fallback
    return UserDTParser(text)


def build_date_parser(text):
    """Return the first parser that successfully interprets a date-only string."""
    parser_classes = [
        UserDateParser,
        ISO8601DateParser,
    ]

    for parser_cls in parser_classes:
        parser = parser_cls(text)
        if parser:
            return parser

    # Fallback: user-friendly date parser
    return UserDateParser(text)


def build_time_parser(text):
    """Return the first parser that successfully interprets a time-only string."""
    parser_classes = [
        UserTimeParser,
        ISO8601TimeParser,
    ]

    for parser_cls in parser_classes:
        parser = parser_cls(text)
        if parser:
            return parser

    # Fallback: user-friendly time parser
    return UserTimeParser(text)