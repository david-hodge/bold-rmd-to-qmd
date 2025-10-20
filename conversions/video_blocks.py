import re


def convert_video_blocks(text: str) -> str:
    lines = text.splitlines()
    converted_lines = []
    open_pattern = re.compile(
        r'^#{2,}s*\[video,\s*videoid=\"([^"]+)\",\s*duration=\"([^"]+)\"\]\s*(.*)$')

    for line in lines:
        open_match = open_pattern.match(line)
        if open_match:
            videoid, duration, title = open_match.groups()
            title = title.strip()
            if duration:
                title = f"{title} ({duration})"
            converted_lines.append(f":::{{#vid-vid{videoid}}}")
            converted_lines.append("")
            converted_lines.append(f"{{{{< video https://youtu.be/{videoid}")
            converted_lines.append(f'title = "{title}"')
            converted_lines.append(">}}")
            converted_lines.append("")              # blank line
            converted_lines.append(title)           # title on its own line
            converted_lines.append("")              # blank line before closing
            converted_lines.append(":::")
            converted_lines.append("<!-- end of vid -->")
            continue
        converted_lines.append(line)

    return "\n".join(converted_lines)
