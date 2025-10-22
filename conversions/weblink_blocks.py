import re


def convert_weblink_blocks(text: str) -> str:
    lines = text.splitlines()
    converted_lines = []
    # Two or more hashes, optional space, then [weblink, target=..., icon=...]
    # Saving the target only
    open_pattern = re.compile(r'^##+\s*\[weblink,\s*target=\"([^"]+)\",\s*icon=[^\]]*\]$')
    close_pattern = re.compile(r'^##+\s*\[/weblink\]$')

    for line in lines:
        open_match = open_pattern.match(line)
        if open_match:
            target = open_match.group(1).strip()
            converted_lines.append(":::{.Weblink}")
            converted_lines.append(f"<{target}>")
            converted_lines.append("")
            continue

        close_match = close_pattern.match(line)
        if close_match:
            converted_lines.append(":::")
            converted_lines.append("<!-- end Weblink -->")
            converted_lines.append("")
            continue

        converted_lines.append(line)

    return "\n".join(converted_lines)
