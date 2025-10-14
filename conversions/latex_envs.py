import re

# Mapping of LaTeX environments to new names
LATEX_ENV_MAP = {
    "align": "aligned",
    "align*": "aligned",
    "multline": "multlined",
    "multline*": "multlined"
}

LATEX_ENVS = list(LATEX_ENV_MAP.keys())


def convert_latex_envs(text: str) -> str:
    env_pattern = '|'.join(re.escape(env) for env in LATEX_ENVS)
    begin_pattern = re.compile(rf'\\begin\{{({env_pattern})\}}')
    end_pattern = re.compile(rf'\\end\{{({env_pattern})\}}')

    lines = text.splitlines()
    converted_lines = []

    for line in lines:
        # Replace \begin{env} with $$ + new env name
        def replace_begin(match):
            env = match.group(1)
            new_env = LATEX_ENV_MAP.get(env, env)
            return f"$$\n\\begin{{{new_env}}}"

        line = begin_pattern.sub(replace_begin, line)

        # Replace \end{env} with \end{new_env} + $$
        def replace_end(match):
            env = match.group(1)
            new_env = LATEX_ENV_MAP.get(env, env)
            return f"\\end{{{new_env}}}\n$$\n"

        line = end_pattern.sub(replace_end, line)
        converted_lines.append(line)

    return "\n".join(converted_lines)


def convert_bracket_math(text: str) -> str:
    """
    Convert LaTeX-style [ ... ] math to block $$ ... $$, 
    putting $$ on separate lines for readability.
    """
    # Replace [ ... ] spans with $$ ... $$, only for entire-line matches
    def replacer(match):
        content = match.group(1).strip()
        return f"$$\n{content}\n$$"

    # Use non-greedy match between \[ and \]
    pattern = re.compile(r'\\\[(.*?)\\\]', re.DOTALL)
    return pattern.sub(replacer, text)
