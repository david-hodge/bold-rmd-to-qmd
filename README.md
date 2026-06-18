## BOLDtools Rmd to Quarto conversion tools

These scripts convert BOLDtools `.Rmd` source files into Quarto-ready `.qmd` files. They are designed for use with the `booktemplate` or `weektemplate`, where custom Quarto/Pandoc environments such as `.Example`, `.Task`, `.Answer`, `.Definition`, and related blocks are defined.

The main converter is `convert.py`. For weekly/multi-file material, the recommended workflow is now split into two scripts:

- `convert_all_weeks.py` — converts `.Rmd` files inside `week1/`, `week2/`, etc. into underscored `.qmd` partials. Here, “partial” means a `.qmd` file whose filename starts with `_`, so Quarto treats it as an included fragment rather than a standalone page.
- `build_week_index_files.py` — builds the week-level index/master files that include those partials in the order specified by the `weekN.yaml` file present in the source.

The older `build.py` script is retained for reference only and is documented at the bottom of this README.

---

### Single-file conversion with `convert.py`

Use `convert.py` when you want to convert one `.Rmd` file into one `.qmd` file.

```bash
python convert.py inputfilename.Rmd outputfilename.qmd
```

For example:

```bash
python convert.py intro.Rmd intro.qmd
```

The converter applies the custom transformations defined in the conversion modules. These include custom block conversion, LaTeX environment conversion, video and weblink blocks, label/reference handling, equation tidying, and other miscellaneous fixes.

One important convention is that `\textbf{...}` has generally been used in the old BOLDtools material to highlight key terms. The converter treats these as key terms and converts them into the appropriate Quarto-compatible form used by the template/extensions. You may need to ensure your Quarto template styles the converted key-term syntax appropriately.

---

### Recommended workflow to convert multiple weeks

For weekly material organised like this:

```text
parent-folder/
├── convert_all_weeks.py
├── build_week_index_files.py
├── week1/
│   ├── week1.yaml
│   ├── intro.Rmd
│   └── examples.Rmd
├── week2/
│   ├── week2.yaml
│   ├── intro.Rmd
│   └── tasks.Rmd
└── ...
```

run the two scripts from the `parent-folder`.

The converter itself is expected to live elsewhere, for example in a cloned repository such as:

```text
bold-rmd-to-qmd/
├── convert.py
└── conversions/
    ├── custom_blocks.py
    ├── latex_envs.py
    └── ...
```

The usual safe workflow is:

```bash
python convert_all_weeks.py <converter-dir> --dry-run
python build_week_index_files.py --dry-run
```

where `<converter-dir>` is the path to the cloned BOLDtools conversion folder containing `convert.py` and the `conversions/` package.

If the dry runs look correct, run:

```bash
python convert_all_weeks.py <converter-dir>
python build_week_index_files.py
```

For example, if `convert.py` lives up two levels in a folder called `bold-rmd-to-qmd`, you would preview the conversion with:

```bash
python convert_all_weeks.py ../../bold-rmd-to-qmd/ --dry-run
python build_week_index_files.py --dry-run
```

and then run the actual conversion/build with:

```bash
python convert_all_weeks.py ../../bold-rmd-to-qmd/
python build_week_index_files.py
```

---

### Script 1: `convert_all_weeks.py`

`convert_all_weeks.py` converts all `.Rmd` files inside the week folders into underscored `.qmd` partial files.

For example:

```text
week1/intro.Rmd    -> week1/_intro.qmd
week1/examples.Rmd -> week1/_examples.qmd
week2/tasks.Rmd    -> week2/_tasks.qmd
```

#### Usage

```bash
python convert_all_weeks.py convert_dir [--dry-run] [--archive-rmds]
```

where:

- `convert_dir` is required and must point to the folder containing `convert.py` and the `conversions/` package.
- `--dry-run` prints the conversions that would be performed without creating or moving files.
- `--archive-rmds` moves successfully converted `.Rmd` files into `old-rmds/weekN/`.

#### Examples

Preview what would happen:

```bash
python convert_all_weeks.py <converter-dir> --dry-run
```

Actually convert all weekly `.Rmd` files:

```bash
python convert_all_weeks.py <converter-dir>
```

Preview conversion and archiving:

```bash
python convert_all_weeks.py <converter-dir> --dry-run --archive-rmds
```

Convert and then archive the original `.Rmd` files:

```bash
python convert_all_weeks.py <converter-dir> --archive-rmds
```

If `convert.py` lives up two levels and in the `bold-rmd-to-qmd` folder, then you would write:

```bash
python convert_all_weeks.py ../../bold-rmd-to-qmd/ --dry-run
```

---

### Script 2: `build_week_index_files.py`

`build_week_index_files.py` builds the week-level index/master files after the `.Rmd` files have been converted to `.qmd` partials.

It reads each `weekN.yaml` file and creates the corresponding generated week file, such as:

```text
week1/unit1.qmd
week2/unit2.qmd
week3/unit3.qmd
```

Each generated file contains a level-1 heading from the YAML title and a sequence of Quarto include shortcodes.

For example, if `week1.yaml` contains:

```yaml
title: Getting started
content:
  - type: text
    src: intro.Rmd
  - type: text
    src: examples.Rmd
```

then the generated `week1/unit1.qmd` will contain something like:

```markdown
# Getting started

{{< include _intro.qmd >}}

{{< include _examples.qmd >}}
```

#### Usage

```bash
python build_week_index_files.py [base_dir] [--dry-run]
```

where:

- `base_dir` is optional and defaults to the current directory.
- `--dry-run` prints what would be renamed or written without changing files.

#### Examples

Preview the index-file build:

```bash
python build_week_index_files.py --dry-run
```

Build the week index files:

```bash
python build_week_index_files.py
```

If running from somewhere else, provide the parent directory containing the week folders:

```bash
python build_week_index_files.py path/to/parent-folder --dry-run
```

#### What it does

For each week folder, the script:

- checks for `.qmd` files that do not start with `_`;
- renames ordinary `.qmd` files as underscored partials, for example:

  ```text
  week1/intro.qmd -> week1/_intro.qmd
  ```

- leaves generated files such as `unit1.qmd` alone;
- reads `weekN.yaml`;
- writes the corresponding generated week index/master file, such as `unitN.qmd`.

---

### Complete weekly example

Starting point:

```text
week1/
├── week1.yaml
├── intro.Rmd
└── examples.Rmd
```

Run:

```bash
python convert_all_weeks.py <converter-dir>
python build_week_index_files.py
```

Result:

```text
week1/
├── week1.yaml
├── intro.Rmd
├── examples.Rmd
├── _intro.qmd
├── _examples.qmd
└── unit1.qmd
```

If you use `--archive-rmds`, the original `.Rmd` files are moved to:

```text
old-rmds/week1/intro.Rmd
old-rmds/week1/examples.Rmd
```

---

### Legacy script: `build.py`

`build.py` is the older single-folder multi-file builder. It has effectively been replaced by the two-script weekly workflow:

```bash
python convert_all_weeks.py <converter-dir>
python build_week_index_files.py
```

The older `build.py` script was designed for cases where a single folder contains several `.Rmd` files that are compiled together into one chapter. It would:

- find all `.Rmd` files in a folder;
- convert each one to `.qmd` using `convert.py`;
- add an initial underscore to each generated `.qmd` filename;
- read a YAML file such as `week4.yaml`;
- create an `index.qmd` file containing Quarto include shortcodes such as:

  ```markdown
  {{< include _filename.qmd >}}
  ```

The old syntax was:

```bash
python build.py path/to/convert.py path/to/week4.yaml
```

This is retained for reference, but for week-based folders use `convert_all_weeks.py` followed by `build_week_index_files.py` instead.
