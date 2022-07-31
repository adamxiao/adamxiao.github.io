# using sphinx write doc

## 概述

Sphinx是一个基于Python的文档生成项目，最早只是用来生成 Python 官方文档，随着工具的完善， 越来越多的知名的项目也用他来生成文档，甚至完全可以用他来写书采用了reStructuredText作为文档写作语言, 不过也可以通过模块支持其他格式，待会我会介绍怎样支持MarkDown格式。

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

## docker镜像的sphinx环境

编写dockerfile如下:
```dockerfile
FROM centos:7.4.1708
LABEL maintainer="iefcuxy@gmail.com"

ENV DEBIAN_FRONTEND noninteractive

RUN yum makecache \
    && yum install -y python3-pip \
    && pip3 install sphinx sphinx-autobuild sphinx_rtd_theme

RUN pip3 install recommonmark \
    && yum install -y graphviz

ENTRYPOINT ["/bin/bash"]
```

一键构建镜像
```
docker build -t centos_sphinx .
```
