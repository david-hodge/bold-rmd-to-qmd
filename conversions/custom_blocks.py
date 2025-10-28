import re

# Each block type maps to (DisplayName, LabelPrefix)
BLOCK_TYPES = {
    "example": ("Example", "rexa"),
    "task": ("Task", "rtsk"),
    "answer": ("Answer", "rans"),
    "definition": ("Definition", "rdef"),
    "theorem": ("Theorem", "rthm"),
    "supplement": ("Supplement", "rsup"),
}


def convert_custom_blocks(text: str) -> str:
    lines = text.splitlines()
    converted_lines = []

    # Opening tag pattern
    # Examples it should match:
    #   ### [task]
    #   ### [task, label="anovatask"]
    #   ### [task, label='anovatask']
    #   ### [task, label=anovatask]
    #   ### [task] Optional heading
    opening_pattern = re.compile(
        r'^(#{2,6})\s*\[\s*('
        + '|'.join(BLOCK_TYPES.keys())
        + r')(?:\s*,\s*label\s*=\s*["\']?([\w\-]+)["\']?)?\s*\]\s*(.*)?\s*$'
    )

    # Closing pattern
    closing_pattern = re.compile(
        r'^(#{2,6})\s*\[\s*/(' + '|'.join(BLOCK_TYPES.keys()) + r')\s*\]\s*$'
    )

    for line in lines:
        open_match = opening_pattern.match(line)
        if open_match:
            hashes, tag, label, heading_text = open_match.groups()
            num_hashes = max(3, len(hashes))
            type_name, prefix = BLOCK_TYPES[tag]

            # Build the start of the enclosure
            block_header = f"{':' * num_hashes}{{.{type_name}"
            if label:
                block_header += f" #{prefix}-{label.strip()}"
            block_header += "}"

            converted_lines.append("")
            converted_lines.append(block_header)
            converted_lines.append("")

            if heading_text:
                heading_text = heading_text.strip()
                if heading_text:
                    converted_lines.append(f"## {heading_text}")
                    converted_lines.append("")

            continue

        close_match = closing_pattern.match(line)
        if close_match:
            hashes, tag = close_match.groups()
            num_hashes = max(3, len(hashes))
            converted_lines.append(f"{':' * num_hashes}")
            converted_lines.append(f"<!-- end of {BLOCK_TYPES[tag][0]} -->")
            continue

        converted_lines.append(line)

    return "\n".join(converted_lines)
