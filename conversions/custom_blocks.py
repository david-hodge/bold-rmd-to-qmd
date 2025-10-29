import re

# Each block type maps to (DisplayName, LabelPrefix)
BLOCK_TYPES = {
    "example": ("Example", "rex"),
    "task": ("Task", "rtask"),
    "answer": ("Answer", "rans"),
    "definition": ("Definition", "rdef"),
    "theorem": ("Theorem", "rthm"),
    "supplement": ("Supplement", "rsupp"),
}

# Toggle: if True, keep Answer nested inside Task.
# If False, close Task before opening Answer.
NEST_TASK_ANSWERS = False


def convert_custom_blocks(text: str) -> str:
    lines = text.splitlines()
    converted_lines = []

    # State tracking
    open_task = False
    open_task_hashes = None
    task_closed_early = False

    opening_pattern = re.compile(
        r'^(#{2,6})\s*\[\s*('
        + '|'.join(BLOCK_TYPES.keys())
        + r')(?:\s*,\s*label\s*=\s*["\']?([\w\-]+)["\']?)?\s*\]\s*(.*)?\s*$'
    )

    closing_pattern = re.compile(
        r'^(#{2,6})\s*\[\s*/(' + '|'.join(BLOCK_TYPES.keys()) + r')\s*\]\s*$'
    )

    for line in lines:
        open_match = opening_pattern.match(line)
        if open_match:
            hashes, tag, label, heading_text = open_match.groups()
            num_hashes = max(3, len(hashes))
            type_name, prefix = BLOCK_TYPES[tag]

            # If we’re opening an Answer and nesting is off
            if not NEST_TASK_ANSWERS and tag == "answer" and open_task:
                # Close the open Task first
                converted_lines.append(f"{':' * open_task_hashes}")
                converted_lines.append("<!-- end of Task -->")
                converted_lines.append("")
                open_task = False
                task_closed_early = True

            # Build the opening block line
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

            # Record state if it's a task
            if tag == "task":
                open_task = True
                open_task_hashes = num_hashes
                task_closed_early = False

            continue

        close_match = closing_pattern.match(line)
        if close_match:
            hashes, tag = close_match.groups()
            num_hashes = max(3, len(hashes))

            # Ignore a Task close if we already closed it early
            if tag == "task" and task_closed_early:
                task_closed_early = False
                continue

            converted_lines.append(f"{':' * num_hashes}")
            converted_lines.append(f"<!-- end of {BLOCK_TYPES[tag][0]} -->")
            converted_lines.append("")

            if tag == "task":
                open_task = False
                open_task_hashes = None

            continue

        converted_lines.append(line)

    return "\n".join(converted_lines)
