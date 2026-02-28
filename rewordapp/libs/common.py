
def decorate_list_of_line(items: list[str]) -> str:
    """Return a framed text block with each line padded to the longest width."""
    max_len = max(len(item) for item in items)
    border = f"+-{'-' * max_len}-+"
    rows = [f"| {item.ljust(max_len)} |" for item in items]
    return "\n".join([border] + rows + [border])