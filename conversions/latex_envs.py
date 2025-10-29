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

def convert_latex_envs(text: str) -> str:
    """
    Convert LaTeX math environments into MathJax-friendly display math blocks.

    - Converts environments like `align`, `align*`, `multline`, `multline*` into
      inline equivalents wrapped in $$.
    - Ensures $$ delimiters are on their own lines.
    - Adds a newline after each \\ inside math environments only if not already there.
    - Handles multi-line environments (begin/end can be on different lines).
    """
    env_pattern = '|'.join(re.escape(env) for env in LATEX_ENVS)
    # Matches \begin{env} ... \end{env}, including multi-line content
    pattern = re.compile(rf'(\\begin\{{({env_pattern})\}})(.*?)(\\end\{{({env_pattern})\}})', re.DOTALL)

    def replacer(match):
        begin = match.group(1)
        env = match.group(2)
        content = match.group(3)
        end = match.group(4)

        new_env = LATEX_ENV_MAP.get(env, env)

        # Strip blank line (will add back later)
        content = content.strip()
        # Normalize \\ to add newline only if not already there
        content = re.sub(r'\\\\(?![ \t]*\n)', r'\\\\\n', content)

        return f"\n$$\n\\begin{{{new_env}}}\n{content}\n\\end{{{new_env}}}\n$$\n"

    # Replace all matched environments
    return pattern.sub(replacer, text)




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
