Script to convert BOLDtools .Rmd files into working Quarto files, designed to be used with my booktemplate or weektemplate (key point is I have custom enviornments defined called .Example, .Task etc..)

\textbf seem to have been used exclusively to highlight key terms, these are converted to [...]{.term} and then use quarto-ext/latex-environment extensions to function in both HTML and PDF.

Other features of this conversion will be documented later.

For now the syntax to use is it:

```
python convert.py inputfilename.Rmd outputfilename.qmd
```
