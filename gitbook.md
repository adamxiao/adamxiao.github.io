# 使用gitbook编写文档

## gitbook安装

使用docker镜像安装的方式,
参考fellah/gitbook
```bash
#docker run -v /srv/gitbook -v /srv/html docker.io/fellah/gitbook gitbook build . /srv/html
docker run -v $PWD:/srv/gitbook -v $PWD/html:/srv/html hub.iefcu.cn/public/gitbook gitbook build . /srv/html

docker run -it --rm -v $PWD:/srv/gitbook hub.iefcu.cn/public/gitbook bash
```

自己构建gitbook镜像, 创建Dockerfile内容如下：
```dockerfile
#FROM node:6-slim
FROM hub.iefcu.cn/public/node:6-slim

MAINTAINER Adam Xiao <iefcuxy@gmail.com>

ARG VERSION=3.2.1
ARG NPM_MIRROR=http://docker.iefcu.cn:5565/repository/npm-group/

LABEL version=$VERSION

RUN npm config set registry "${NPM_MIRROR}" &&\
        npm install --global gitbook-cli &&\
        gitbook fetch ${VERSION} &&\
        npm cache clear &&\
        rm -rf /tmp/*

WORKDIR /srv/gitbook

EXPOSE 4000

CMD /usr/local/bin/gitbook serve
```

然后一键构建gitbook镜像
```bash
docker build -t hub.iefcu.cn/xiaoyun/gitbook .

# 或者使用buildx一键构建多架构镜像
#docker buildx build \
        #--build-arg http_proxy=http://proxy.iefcu.cn:20172 --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
        #--build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \
        #--platform=linux/arm64,linux/amd64 \
        #-t hub.iefcu.cn/xiaoyun/gitbook . --push
```

或者一键构建多架构gitbook镜像
(目前这个buildx构建arm64镜像有点问题，很奇怪)
```bash
docker buildx build \
    --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
    --build-arg no_proxy=yumrepo.unikylin.com.cn,192.0.0.0/8 \                                                                                                                                                         --platform=linux/arm64,linux/amd64 \
    -t hub.iefcu.cn/xiaoyun/gitbook . --push
```

## gitbook导出pdf

参考文章: [新版gitbook导出pdf](https://cloud.tencent.com/developer/article/1657839)

目前还是使用vscode的markdown preview enhanced弄吧。


## xxx

TODO:
https://zhaoda.net/2015/11/09/gitbook-plugins/

[1.5.1.1. 个人觉得必须实用的插件](https://zq99299.gitbooks.io/gitbook-guide/content/chapter/plugin.html)

latex-codecogs
使用数学方程式。

mermaid
使用流程图。

tbfed-pagefooter
自定义页脚，显示版权和最后修订时间。

prism
基于 Prism 的代码高亮。

include-codeblock
通过引用文件插入代码。

TOC插件
intopic-toc

summary插件
summary

TODO:
其他好插件


Recommend 12 practical gitbook plug-ins
https://developpaper.com/recommend-12-practical-gitbook-plug-ins/


* popup Big picture pop-up
* splitter Side Bar Width Adjustable
* code Copy code
* chapter-fold Navigation Directory Folding
* back-to-top-button Back to the top



Gitbook plugin to auto-generate SUMMARY.md
https://github.com/julianxhokaxhiu/gitbook-plugin-summary


TODO: 找一个更合适markdown viewer?
Gitbook Markdown Viewer
This Vue.js webapp is a simple reader for Markdown files generated using Gitbook.
https://github.com/taigers/gitbook-markdown-viewer


与Github的融合
Gitbook的博客上说Github提供了对Gitbook的特殊支持，但我没有测试。只是依然把源文件保存在Github上，然后用Gitbook去编译。期待Gitbook做的更好。


GitBook默认使用Markdown语法。

下面这些可以作为一个快速参考和展示。更多完整的信息，请参考 John Gruber’s original spec 和 Github-flavored Markdown info page。
https://www.bookstack.cn/read/gitbook-documentation/format-markdown.md


3 Markdown 扩展语法 GFM
GitHub Flavored Markdown（简称 GFM）是目前最流行的 Markdown 扩展语法，它提供了包括表格、任务列表、删除线、围栏代码、Emoji 等在内的标记语法。
https://zhuanlan.zhihu.com/p/261016461

https://skyao.gitbooks.io/learning-gitbook/content/plugin/
* Tbfed-pagefooter: 为页面添加页脚,可以增加版权信息和文件的最后修订时间
https://zhousiwei.gitee.io/ibooks/notes/gitbook_config.html


https://zhousiwei.gitee.io/ibooks/notes/gitbook_config.html
* 4、GitBook插件列表: 
* prism 基于 Prism 的代码高亮 ➡️ https://github.com/gaearon/gitbook-plugin-prism

