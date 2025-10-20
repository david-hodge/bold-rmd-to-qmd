import re

BLOCK_TYPES = {
    "example": "Example",
    "task": "Task",
    "answer": "Answer",
    "definition": "Definition",
    "theorem": "Theorem",
    "supplement": "Supplement",
}


def convert_custom_blocks(text: str) -> str:
    lines = text.splitlines()
    converted_lines = []

    # Match 3–6 #, optional spaces, then [blocktype], optional heading text
    opening_pattern = re.compile(
        r'^(#{2,6})\s*\[\s*(' +
        '|'.join(BLOCK_TYPES.keys()) +
        r')\s*\]\s*(.*)?\s*$'
    )

    # Closing: same number of #, [/blocktype]
    closing_pattern = re.compile(
        r'^(#{2,6})\s*\[\s*/(' + '|'.join(BLOCK_TYPES.keys()) + r')\s*\]\s*$'
    )

    for line in lines:
        open_match = opening_pattern.match(line)
        if open_match:
            hashes, tag, heading_text = open_match.groups()
            num_hashes = max(3, len(hashes))
            type_name = BLOCK_TYPES[tag]

            converted_lines.append("")
            converted_lines.append(f"{':' * num_hashes}{{.{type_name}}}")

            if heading_text:
                heading_text = heading_text.strip()
                converted_lines.append("")
                converted_lines.append(f"## {heading_text}")
                converted_lines.append("")
            continue

        close_match = closing_pattern.match(line)
        if close_match:
            hashes, tag = close_match.groups()
            num_hashes = max(3, len(hashes))
            converted_lines.append(f"{':' * num_hashes}")
            converted_lines.append(f"<!-- end of {BLOCK_TYPES[tag]} -->")
            continue

        converted_lines.append(line)

    return "\n".join(converted_lines)
