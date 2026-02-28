import sys
import textwrap

from rewordapp.libs import ECODE


def dedent_and_strip(txt):
    """Normalize text by decoding bytes, converting non-strings, and removing indentation."""
    value = (
        txt.decode("utf-8")
        if isinstance(txt, bytes)
        else txt if isinstance(txt, str)
        else repr(txt)
    )
    return textwrap.dedent(value).strip()


def decorate_list_of_line(items: list[str]) -> str:
    """Return a framed text block with each line padded to the longest width."""
    max_len = max(len(item) for item in items)
    border = f"+-{'-' * max_len}-+"
    rows = [f"| {item.ljust(max_len)} |" for item in items]
    return "\n".join([border] + rows + [border])


def sys_exit(success: bool = True, msg: str = "") -> None:
    """Terminate the process with a standardized exit code and optional message."""
    exit_code = ECODE.SUCCESS if success else ECODE.BAD

    if msg:
        stream = sys.stderr if exit_code == ECODE.BAD else sys.stdout
        print(msg, file=stream)

    sys.exit(exit_code)