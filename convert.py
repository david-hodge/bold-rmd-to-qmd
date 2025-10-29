import argparse
from conversions.custom_blocks import convert_custom_blocks
from conversions.latex_envs import convert_latex_envs, convert_bracket_math
from conversions.video_blocks import convert_video_blocks
from conversions.weblink_blocks import convert_weblink_blocks
from conversions.miscellaneous import (
    convert_definition_misc,
    convert_labels_and_refs,
    convert_textbf_to_term,
    split_labelled_equations,
    tidy_equations,
    update_refs,
)


CONVERSION_FUNCTIONS = [
    convert_custom_blocks,
    convert_latex_envs,
    convert_video_blocks,
    convert_weblink_blocks,
    convert_definition_misc,
    convert_bracket_math,
    convert_textbf_to_term,
    split_labelled_equations,
    tidy_equations,
    update_refs,
]


def main():
    parser = argparse.ArgumentParser(
        description="Convert Rmd to Qmd with custom transformations.")
    parser.add_argument("input_file", help="Path to input .Rmd file")
    parser.add_argument("output_file", help="Path to output .qmd file")
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as f:
        text = f.read()

    for func in CONVERSION_FUNCTIONS:
        text = func(text)

    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Converted {args.input_file} → {args.output_file}")


if __name__ == "__main__":
    main()
