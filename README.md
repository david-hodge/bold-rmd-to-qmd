Script to convert BOLDtools .Rmd files into working Quarto files, designed to be used with my booktemplate or weektemplate (key point is I have custom enviornments defined called .Example, .Task etc..)

\textbf seem to have been used exclusively to highlight key terms, these are converted to [...]{.term} and then use quarto-ext/latex-environment extensions to function in both HTML and PDF.

Other features of this conversion will be documented later.

## Main syntax for single file

For now the syntax to use is it:

```
python convert.py inputfilename.Rmd outputfilename.qmd
```

## New multifile syntax

There are some BOLDtools examples where a folder contains many Rmd files (e.g. BOLDpython) which are compiled together and turned into a single chapter. The specification of which files and what order is normally found in a yaml file, like `week4.yaml`.

This `build.py` script, will

+ find all .Rmd files in a folder
+ for each one withh convert to qmd with the standard `convert.py` script -- all resulting qmds gain a starting UNDERSCORE in their filename
+ in addition it will read the `week4.yaml` file and extract the files mentioned and put them into a new file called `index.qmd` via shortcode `{{< include <filename> >}}` commands.

You then copy all the `_filename.qmd` files and `index.qmd` along with resources like .svgs etc... into your new project.

The syntax to call `build.py` is:

```
python build.py <path/to/convert.py> <path/to/week4.yaml>
```
