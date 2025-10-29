import re

# Quarto is a bit weird, requires $$ for display math but then...
# the PDF will be upset by $$\begin{align} as align starts a mathmode
# So we replace \begin{align} with $$\begin{aligned}
# Similarly multline has a non-math-mode invoking version called multlined

# Mapping of LaTeX environments to new names
LATEX_ENV_MAP = {
    "align": "aligned",
    "align*": "aligned",
    "multline": "multlined",
    "multline*": "multlined"
}

LATEX_ENVS = list(LATEX_ENV_MAP.keys())


import re

LATEX_ENV_MAP = {
    "align": "aligned",
    "align*": "aligned",
    "multline": "multlined",
    "multline*": "multlined",
}

LATEX_ENVS = list(LATEX_ENV_MAP.keys())


import re

LATEX_ENV_MAP = {
    "align": "aligned",
    "align*": "aligned",
    "multline": "multlined",
    "multline*": "multlined",
}

LATEX_ENVS = list(LATEX_ENV_MAP.keys())


def convert_latex_envs(text: str) -> str:
    """
    Convert LaTeX math environments into MathJax-friendly display math blocks.

    This function:
      • Finds LaTeX environments such as `align`, `align*`, `multline`, and `multline*`.
      • Converts them into their inline equivalents (`aligned`, `multlined`) wrapped in
        display math delimiters (`$$ ... $$`).
      • Ensures `$$` delimiters appear on their own lines, even if the environment
        begins or ends mid-line (with text before or after).
      • Adds newlines after LaTeX line breaks (`\\`) **only inside** math environments,
        to make each equation line easier to read.
      • Preserves surrounding text and layout for Markdown / MathJax rendering.

    Args:
        text (str): A string containing LaTeX code.

    Returns:
        str: The modified LaTeX text with properly formatted math environments.

    Example:
        Input:
            "Before \\begin{align} a &= b + c \\\\ d &= e + f \\end{align} after"

        Output:
            "Before\n$$\n\\begin{aligned} a &= b + c \\\\\n d &= e + f \\end{aligned}\n$$\nafter"
    """
    env_pattern = '|'.join(re.escape(env) for env in LATEX_ENVS)
    begin_pattern = re.compile(rf'(.*?)\\begin\{{({env_pattern})\}}')
    end_pattern = re.compile(rf'\\end\{{({env_pattern})\}}(.*)')

    lines = text.splitlines()
    converted_lines = []
    in_env = False  # Track whether we’re inside an environment

    for line in lines:
        # Check for environment starts
        if begin_pattern.search(line):
            in_env = True

        # Apply \\ → \\\n only if inside an environment
        if in_env:
            line = re.sub(r'\\\\(?!\s*\n)', r'\\\\\n', line)

        # Handle \begin{...}
        def replace_begin(match):
            before = match.group(1)
            env = match.group(2)
            new_env = LATEX_ENV_MAP.get(env, env)
            if before.strip():
                return f"{before.rstrip()}\n$$\n\\begin{{{new_env}}}"
            else:
                return f"$$\n\\begin{{{new_env}}}"

        line = begin_pattern.sub(replace_begin, line)

        # Handle \end{...}
        def replace_end(match):
            nonlocal in_env
            env = match.group(1)
            after = match.group(2)
            new_env = LATEX_ENV_MAP.get(env, env)
            in_env = False  # We're leaving the environment now
            if after.strip():
                return f"\\end{{{new_env}}}\n$$\n{after.lstrip()}"
            else:
                return f"\\end{{{new_env}}}\n$$"

        line = end_pattern.sub(replace_end, line)
        converted_lines.append(line)

    return "\n".join(converted_lines)




def convert_bracket_math(text: str) -> str:
    """
    Convert LaTeX-style \\[ ... \\] math to block $$ ... $$, 
    putting $$ on separate lines for readability.
    """
    # Replace \\[ ... \\] spans with $$ ... $$, only for entire-line matches
    def replacer(match):
        content = match.group(1).strip()
        return f"$$\n{content}\n$$"

    # Use non-greedy match between \\[ and \\]
    pattern = re.compile(r'\\\[(.*?)\\\]', re.DOTALL)
    return pattern.sub(replacer, text)
