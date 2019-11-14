# using sphinx write doc

## install sphinx

refer https://kinshines.github.io/archivers/read-the-doc-sphinx

```
pip install sphinx sphinx-autobuild sphinx_rtd_theme
```

## sphinx quick start

```bash
sphinx-quickstart

# change the option
> Root path for the documentation [.]: adam_doc
> Separate source and build directories (y/n) [n]: y
> Project name: adam_doc
> Author name(s): Adam Xiao
> Project language [en]: zh_CN

```

build and view html
```bash
make html
# then open build/html/index.html
```

## other change

1. update html theme

update `source/conf.py`
```python
import sphinx_rtd_theme
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
```

2. write doc with markdown

install markdown package
```bash
pip install recommonmark
```

update `source/conf.py`
```python
from recommonmark.parser import CommonMarkParser
source_parsers = {
    '.md': CommonMarkParser,
}
source_suffix = ['.rst', '.md']
```
