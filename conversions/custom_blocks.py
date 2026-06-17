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


def make_patterns():
    block_names = "|".join(BLOCK_TYPES.keys())

    opening_pattern = re.compile(
        r'^(#{2,6})\s*\[\s*('
        + block_names
        + r')(?:\s*,\s*label\s*=\s*["\']?([\w\-]+)["\']?)?\s*\]\s*(.*)?\s*$'
    )

    closing_pattern = re.compile(
        r'^(#{2,6})\s*\[\s*/(' + block_names + r')\s*\]\s*$'
    )

    # Case-insensitive only for the "ref" part.
    # The label itself is captured as written.
    reference_pattern = re.compile(
        r'\bref://([\w\-]+)',
        flags=re.IGNORECASE
    )

    return opening_pattern, closing_pattern, reference_pattern


def collect_label_map(text: str) -> dict:
    """
    First pass over the document.

    Builds a dictionary mapping original labels to converted labels.

    For example:
        svc1     -> rex-svc1
        whisky1  -> rtask-whisky1
    """
    opening_pattern, _, _ = make_patterns()

    label_map = {}

    for line in text.splitlines():
        open_match = opening_pattern.match(line)

        if open_match:
            hashes, tag, label, heading_text = open_match.groups()

            if label:
                label = label.strip()
                _, prefix = BLOCK_TYPES[tag]
                converted_label = f"{prefix}-{label}"

                if label in label_map and label_map[label] != converted_label:
                    raise ValueError(
                        f"Duplicate label '{label}' maps to both "
                        f"'{label_map[label]}' and '{converted_label}'."
                    )

                label_map[label] = converted_label

    return label_map


def replace_refs(text: str, label_map: dict) -> str:
    """
    Replace ref://label references using the label_map.

    For example:
        ref://svc1 -> \\longref{rex-svc1}

    If a reference is not found in label_map, it is left unchanged.
    """
    _, _, reference_pattern = make_patterns()

    def replacement(match):
        original_label = match.group(1)

        if original_label in label_map:
            return f"\\longref{{{label_map[original_label]}}}"

        # Leave unresolved references unchanged.
        return match.group(0)

    return reference_pattern.sub(replacement, text)


def convert_custom_blocks(text: str) -> str:
    lines = text.splitlines()
    converted_lines = []

    opening_pattern, closing_pattern, _ = make_patterns()

    # First pass: collect all labelled block conversions.
    label_map = collect_label_map(text)

    # State tracking
    open_task = False
    open_task_hashes = None
    task_closed_early = False

    for line in lines:
        open_match = opening_pattern.match(line)

        if open_match:
            hashes, tag, label, heading_text = open_match.groups()
            num_hashes = max(3, len(hashes))
            type_name, prefix = BLOCK_TYPES[tag]

            # If we’re opening an Answer and nesting is off,
            # close the currently open Task first.
            if not NEST_TASK_ANSWERS and tag == "answer" and open_task:
                converted_lines.append(f"{':' * open_task_hashes}")
                converted_lines.append("<!-- end of Task -->")
                converted_lines.append("")
                open_task = False
                task_closed_early = True

            # Build the opening block line.
            block_header = f"{':' * num_hashes} {{.{type_name}"

            if label:
                label = label.strip()
                block_header += f" #{prefix}-{label}"

            block_header += "}"

            converted_lines.append("")
            converted_lines.append(block_header)
            converted_lines.append("")

            if heading_text:
                heading_text = heading_text.strip()

                if heading_text:
                    heading_text = replace_refs(heading_text, label_map)
                    converted_lines.append(f"## {heading_text}")
                    converted_lines.append("")

            # Record state if it's a task.
            if tag == "task":
                open_task = True
                open_task_hashes = num_hashes
                task_closed_early = False

            continue

        close_match = closing_pattern.match(line)

        if close_match:
            hashes, tag = close_match.groups()
            num_hashes = max(3, len(hashes))

            # Ignore a Task close if we already closed it early.
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

        # Normal content line:
        # convert ref://label syntax using the collected label map.
        line = replace_refs(line, label_map)
        converted_lines.append(line)

    return "\n".join(converted_lines)
