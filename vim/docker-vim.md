# 容器vim环境安装使用

## 使用方法

####  alias vi='docker run -it --rm vim-env'

参考: https://github.com/JAremko/alpine-vim

```bash
alias avi='docker run -ti -e TERM=xterm-256color --rm -v $(pwd):/data vim-env:base'

# 由于docker容器tty size的问题，传入tty size进去
alis vi='docker run -ti -e TERM=xterm-256color -e COLUMNS=$(tput cols) -e LINES=$(tput lines) --rm -v $(pwd):/data vim-env:base'
```

```bash
alias myedit='docker run -ti --rm -v $(pwd):/home/developer/workspace jare/vim-bundle'
edit some.file
alias edit_update="docker pull jare/vim-bundle:latest"

# disable some plugin
docker run ... -e DISABLE="'vim-airline', 'nerdtree'" ... jare/vim-bundle
```

#### 启动docker容器，进去docker容器中使用

这个比较简单, 不做详细描述...

## 构建vim镜像

#### 基于ubuntu构建一个比较好用的vim环境

```dockerfile
from ubuntu:20.04

RUN apt-get update -y \
    && apt-get install -y vim
```

#### 基于alpine构建一个精简vim环境

```dockerfile
from alpine

RUN apk add --no-cache vim
```

## 容器vim安装扩展插件

重点插件:
* nerdtree
* fzf
* ag

开发插件:

#### xxx

## 容器中使用vim注意事项

#### 中文编码

#### 不能使用链接文件

## FAQ

* 1.docker vim tty size不正确的问题

偶现问题

> 验证发现jare/vim-bundle没有问题, 且跟vim配置有关？ 使用podman没问题
关键字《shell 终端大小bug》

应该是docker里面的vim获取tty size失败导致的!
[Docker 的 tty size 问题](https://diabloneo.github.io/2018/09/22/docker-tty-size-problem/)


## 参考资料

* [thinca/vim](https://hub.docker.com/r/thinca/vim/)

开箱即用docker版本vim
vim-plus => 一般
https://github.com/chxuan/vimplus

docker vim env - Google 搜索 
JAremko/alpine-vim: "dockerized" Vim 
dekelund/vim-env: Dockerfile to setup vim and tmux as development environment 
Docker as an Integrated Development Environment - Ashley Broadley - Medium 
Env variable cannot be passed to container - General Discussions - Docker Forums 
Dev Environments Within Docker Containers ⋆ Mark McDonnell 
