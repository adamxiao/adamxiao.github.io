# using sphinx write doc

## 概述

Sphinx是一个基于Python的文档生成项目，最早只是用来生成 Python 官方文档，随着工具的完善， 越来越多的知名的项目也用他来生成文档，甚至完全可以用他来写书采用了reStructuredText作为文档写作语言, 不过也可以通过模块支持其他格式，待会我会介绍怎样支持MarkDown格式。

https://juejin.cn/post/6844903721617326088
* gitbook: 基于 nodejs,支持导出成 pdf/epub 等格式，使用 markdown 书写
* mkdocs: 基于Python，使用 markdown 书写
* sphinx: 基于 Python，可以用 rst/markdown 书写，很多知名 py 项目的选择。可以基于 docstring 生成文档，支持生成 pdf/epub 等，功能相比 gitbook/mkdocs 更加强大

[几款制作帮助文档的工具汇总](https://blog.csdn.net/zz153417230/article/details/109494390)
其它类似工具对比
* docusaurus: teedoc 的 UI 布局几乎和它类似，不过它使用 vue 写的， teedoc 是原生 js, 如果你用的是 vue 可以考虑用这个
* gitbook: 曾经很好用的工具，但是官方不维护了，转向商业了，不建议再使用
* docsify: 只需要一个页面，markdown 在浏览器渲染，而不是预先渲染成 HTML， 好处就是轻量，但是 SEO 不太友好，可以用它的 SSR 功能， nodejs 编写
* readthedocs(Sphinx): 其实是用了用 Sphinx 做为生成工具，Python 官网文档就是这个工具生成的， 很多开源项目使用的工具，readthedocs 只是一个公开文档的网站，你不用自己搭建网站，注册登录就可以开始写文档，对 RST 格式支持友好
* mkdoc: 也是一个 python 写的工具，简单易上手，插件也多，如果你的文档是单一语言的文档，可以使用这个工具

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

## docker镜像的mkdocs环境

编写dockerfile如下:
```dockerfile
FROM ubuntu:20.04

LABEL maintainer="iefcuxy@gmail.com"

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y \
    && apt-get install -y python3-pip \
    && pip3 config --user set global.index-url http://mirrors.aliyun.com/pypi/simple \
    && pip config --user set global.trusted-host mirrors.aliyun.com \
    && pip3 install mkdocs mkdocs-material

#ENTRYPOINT ["/bin/bash"]
```

一键构建镜像
```
docker build -t ubuntu_mkdocs .
```

## 参考资料

* [搭建在线电子书：Sphinx + Github + ReadTheDocs](https://blog.51cto.com/u_15441270/4724717)
* [基于mkdocs-material搭建个人静态博客(含支持的markdown语法)](https://cyent.github.io/markdown-with-mkdocs-material/install/local/)
* [几款制作帮助文档的工具汇总](https://blog.csdn.net/zz153417230/article/details/109494390)
* [笔记文档一把梭——MkDocs 快速上手指南](https://sspai.com/prime/story/mkdocs-primer)
