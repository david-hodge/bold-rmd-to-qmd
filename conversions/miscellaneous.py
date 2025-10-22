import re


def convert_definition_misc(text: str) -> str:
    """
    Convert :::definition[...] {label=...} blocks into Quarto-style blocks
    and append <!-- end definition --> after the next ::: block following it.
    """
    lines = text.splitlines()
    converted_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Match :::definition[Title]{label=...}
        match = re.match(
            r'^:::(definition)\[([^\]]+)\]\{label=([^\}]+)\}$', line)
        if match:
            block_type, title, label = match.groups()
            # Output the converted opening block
            converted_lines.append(
                f":::{{.{block_type.capitalize()} #r{label}}}")
            converted_lines.append(f"## {title.strip()}")
            i += 1
            # Now copy all content lines until we hit the next ::: (closing any block)
            while i < len(lines):
                converted_lines.append(lines[i])
                if lines[i].startswith(":::"):
                    # After this line, insert the end comment
                    converted_lines.append("<!-- end definition -->")
                    i += 1
                    break
                i += 1
            continue

        # Otherwise, just copy the line
        converted_lines.append(line)
        i += 1

    return "\n".join(converted_lines)


def convert_labels_and_refs(text: str) -> str:
    """
    Replace LaTeX \label{...} with right-aligned \text{[label: ...]} and
    \ref{...} with \emph{ref{...}} for safe LaTeX display inside aligned.
    """
    # Currently Quarto/Mathjax doesn't support numbering and reffig inside
    # a multiline equation. So this will need to be manually fixed later.
    
    # Replace \label{CONTENT} → right-aligned text version to easily spot
    # Using a unique marker [label: CONTENT] so it's easy to find later
    text = re.sub(r'\\label\{([^\}]+)\}', r'\\hfill \\text{[label: \1]}', text)

    # Replace \ref{CONTENT} → \emph{ref{CONTENT}}
    # References turned into italic to be fixed later too.
    text = re.sub(r'\\ref\{([^\}]+)\}', r'*{ref{\1}*', text)

    return text


def convert_textbf_to_term(text: str) -> str:
    """
    Replace all instances of \textbf{...} with \term{...}.
    """
    return re.sub(r'\\textbf\{([^\}]+)\}', r'\\term{\1}', text)
