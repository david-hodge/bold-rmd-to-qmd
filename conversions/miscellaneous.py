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
    Replace LaTeX \\label{...} with right-aligned \\text{[label: ...]} and
    \\ref{...} with \\emph{ref{...}} for safe LaTeX display inside aligned.
    """
    # Currently Quarto/Mathjax doesn't support numbering and reffig inside
    # a multiline equation. So this will need to be manually fixed later.
    
    # Replace \\label{CONTENT} → right-aligned text version to easily spot
    # Using a unique marker [label: CONTENT] so it's easy to find later
    text = re.sub(r'\\label\{([^\}]+)\}', r'\\hfill \\text{[label: \1]}', text)

    # Replace \\ref{CONTENT} → \emph{ref{CONTENT}}
    # References turned into italic to be fixed later too.
    text = re.sub(r'\\ref\{([^\}]+)\}', r'*{ref{\1}*', text)

    return text

import re

def split_labelled_equations(text: str) -> str:
    """
    Split lines containing \\label{...} inside math environments into
    standalone Quarto-style equation blocks:

        $$ 
        equation
        $$ {#eq-LABEL}

    while preserving the rest of the environment structure.
    """
    label_pattern = re.compile(r'\\label\{([^\}]+)\}')
    begin_pattern = re.compile(r'\\begin\{([a-zA-Z*]+)\}')
    end_pattern = re.compile(r'\\end\{([a-zA-Z*]+)\}')

    lines = text.splitlines()
    output = []
    in_env = None

    for line in lines:
        begin_match = begin_pattern.search(line)
        end_match = end_pattern.search(line)
        label_match = label_pattern.search(line)

        # Detect entering an environment
        if begin_match:
            in_env = begin_match.group(1)
            output.append(line)
            continue

        # Handle line with a label
        if in_env and label_match:
            label_name = label_match.group(1)
            label_name = re.sub(r'^eqn:', 'eq-', label_name)

            # Remove the label markup
            clean_line = label_pattern.sub('', line).strip()

            # Remove leading/trailing alignment characters and trailing \\\\ 
            clean_line = re.sub(r'^[&\s]+', '', clean_line)   # leading &
            clean_line = re.sub(r'[&\s]+$', '', clean_line)   # trailing & and spaces
            clean_line = re.sub(r'\\\\$', '', clean_line)     # trailing \\

            # Close current environment and $$ block
            output.append(f"\\end{{{in_env}}}")
            output.append("$$")

            # Emit labeled line as its own standalone block
            output.append(f"$$\n{clean_line}\n$$ {{#{label_name}}}")

            # Reopen environment for remaining lines
            output.append("$$")
            output.append(f"\\begin{{{in_env}}}")
            continue

        # Detect leaving an environment
        if end_match:
            in_env = None
            output.append(line)
            continue

        # Default: copy the line as-is
        output.append(line)

    return "\n".join(output)


def tidy_equations(text: str) -> str:
    """
    Remove empty math environments of the form:
    
        $$
        \\begin{env}
        \\end{env}
        $$
    
    where 'env' can be any LaTeX math environment name.
    """
    # Regex matches:
    # $$, optional whitespace/newlines, \begin{env}, optional whitespace/newlines, \end{env}, optional whitespace/newlines, $$
    empty_env_pattern = re.compile(
        r'\$\$\s*\\begin\{([a-zA-Z*]+)\}\s*\\end\{\1\}\s*\$\$',
        flags=re.DOTALL,
    )

    cleaned = re.sub(empty_env_pattern, '', text)
    return cleaned.strip()

def update_refs(text: str) -> str:
    """
    Replace LaTeX \\ref{prefix:name} with Quarto-style references:
      - eqn:cat → @eq-cat
      - other three-letter prefixes → @prefix-...
      - like fig:car --> fig-car
    """
    def repl(match):
        prefix = match.group(1)
        name = match.group(2)
        if prefix == 'eqn':
            new_prefix = 'eq'
        else:
            new_prefix = prefix[:3]  # keep first 3 letters
        return f"@{new_prefix}-{name}"

    return re.sub(r'\\ref\{([a-zA-Z]+):([^\}]+)\}', repl, text)



def convert_textbf_to_term_md(text: str) -> str:
    """
    Replace all \\textbf{...} with [...]{.term}.
    """
    return re.sub(r'\\textbf\{([^\}]+)\}', r'[\1]{.term}', text)
