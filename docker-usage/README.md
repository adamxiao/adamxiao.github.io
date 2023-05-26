# docker镜像使用总结

未分类零散知识点

设置容器的自动重启策略
```
docker container update --restart=always ksvd-MStorage
docker container update --restart=no ksvd-MStorage
```

将一些镜像方法记录下来

java mvn项目编译方法 ![](../asserts/mvn-settings.xml)
```bash
docker run -it --rm \
   --env http_proxy=http://proxy.iefcu.cn:20172 \
   --env https_proxy=http://proxy.iefcu.cn:20127 \
   -v /home/adam/workspaces/settings.xml:/usr/share/maven/conf/settings.xml \
   -v $PWD:/app  -w /app \
   hub.iefcu.cn/public/maven:3.8-jdk-8 \
   mvn clean install -Dmaven.test.skip=true
```

[Authenticate Docker to Harbor Image Registry with a Robot Account](https://veducate.co.uk/authenticate-docker-harbor-robot/)

```bash
username=$(cat file.json | jq -r .name)
password=$(cat file.json | jq -r .token) <<< See below update
echo "$password" | docker login https://URL --username "$username" --password-stdin

Example
username=$(cat "robot\$veducate.json" | jq -r .name)
password=$(cat robot\$veducate.json | jq -r .token)
echo "$password" | docker login https://harbor-repo.veducate.com --username "$username" --password-stdin

Update October 2021
Since Harbor 2.2 minor release, and I found that within the JSON the key name has changed to secret, so this is the updated example

username=$(cat robot-veducate.json | jq -r .name)
password=$(cat robot-veducate.json | jq -r .secret)
echo "$password" | docker login https://harbor-repo.veducate.com --username "$username" --password-stdin
```

## 容器中文乱码问题

就是语言字符环境没有配置utf8, 默认为POSIX
(TODO: 尝试配置LANG=C.UTF-8, 也能显示中文, 有什么区别呢?)

```bash
locale  # 查看当前系统字符集
locale  -a # 查看系统支持的字符集

root@9fb0e2335090:/data# locale
LANG=
LANGUAGE=
LC_CTYPE="POSIX"
LC_NUMERIC="POSIX"
LC_TIME="POSIX"
LC_COLLATE="POSIX"
LC_MONETARY="POSIX"
LC_MESSAGES="POSIX"
LC_PAPER="POSIX"
LC_NAME="POSIX"
LC_ADDRESS="POSIX"
LC_TELEPHONE="POSIX"
LC_MEASUREMENT="POSIX"
LC_IDENTIFICATION="POSIX"
LC_ALL=

root@33c7ce6ff69c:/data# locale -a
C
C.UTF-8
POSIX
```

#### ubuntu容器

参考: [【问题】解决docker 容器中文乱码](https://blog.csdn.net/bbj12345678/article/details/115263565)

先安装语言工具locale, 然后生成中文utf8字符集?
```bash
apt install -y locales
locale-gen zh_CN.UTF-8
locale-gen en_US.UTF-8
```

最后配置shell终端环境使用utf8
```bash
ENV LANG en_US.UTF-8
# 这个不知道有啥用, 不管之前配置了现在继续用
ENV LESSCHARSET utf-8
```

#### debian容器

这里单独拎debian容器来说，是因为ubuntu上的方法，居然在debian上不好使!
发现`locale-gen zh_CN.UTF-8`处理之后, 使用`locale -a`没找到新的字符集!

查资料发现, 使用另外一个命令生成有效:
```bash
localedef -c -f UTF-8 -i zh_CN zh_CN.utf8
```

#### centos系列备忘

(暂未验证)

跟debian类似, 参考: [创建容器内中文乱码问题解决](https://www.cxybb.com/article/weixin_39153210/83617792)
```dockerfile
FROM centos
MAINTAINER maochengli
#设置系统编码
RUN yum install kde-l10n-Chinese -y
RUN yum install glibc-common -y
RUN localedef -c -f UTF-8 -i zh_CN zh_CN.utf8
#RUN export LANG=zh_CN.UTF-8
#RUN echo "export LANG=zh_CN.UTF-8" >> /etc/locale.conf
#ENV LANG zh_CN.UTF-8
ENV LC_ALL zh_CN.UTF-8
```

https://stackoverflow.com/questions/58304278/how-to-fix-character-map-file-utf-8-not-found
```bash
yum -y install glibc-locale-source glibc-langpack-en
```

## 容器工作环境

#### ubuntu tmux 终端工作环境

编写脚本run-adam-ubuntu.sh
```bash
docker run -it --privileged --name adam --restart=always \
  -v $HOME/Downloads:/home/adam/Downloads \
  -v $HOME/Documents:/home/adam/Documents \
  -v $HOME/workspaces:/home/adam/workspaces \
  -v $HOME/bin:/home/adam/bin \
  -v $HOME/.gitconfig:/home/adam/.gitconfig \
  -v $HOME/.ssh:/home/adam/.ssh \
  -w /home/adam/ hub.iefcu.cn/public/adam-ubuntu

alias adam='docker exec -it adam zsh'
```

最后每次进入容器环境, 就可以使用`adam`命令进入

#### vim工作环境

安装了我的常用vim基本插件, 方便我在哪里使用vim效果都一样

* 源码: vim-env仓库 (分支base)

```bash
alias vi='docker run -ti -e TERM=xterm-256color -e COLUMNS=$(tput cols) -e LINES=$(tput lines) --rm -v $(pwd):/data hub.iefcu.cn/public/vim-env:base'
```

顺便给go.exp的脚本也配置了登录执行命令
```bash
ssh_ip=`env | awk '/^SSH_CONNECTION=/ {print $3}'`; export PS1="\[\e[31m\][ssh_"$ssh_ip"]\[\e[0m\] \u@\h: \W\$"
PROMPT_COMMAND="printf '\e]0;ssh_$ssh_ip\7\n'"
export PATH=/usr/lib/ksvd/bin/:$PATH
if [[ -f /usr/bin/vim ]]; then alias vi=vim; fi
if [[ -f /usr/bin/docker ]]; then alias vi='docker run -ti -e TERM=xterm-256color -e COLUMNS=$(tput cols) -e LINES=$(tput lines) --rm -v $(pwd):/data hub.iefcu.cn/public/vim-env:base'; fi
```

## FAQ

#### Build --privileged

podman build --cap-add待验证ok
https://man7.org/linux/man-pages/man7/capabilities.7.html
```bash
podman build --cap-add CAP_SYS_ADMIN \
        --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
        --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
        -f containers/wetty/Dockerfile \
        -t hub.iefcu.cn/xiaoyun/wetty:arm64 .
```

使用docker buildx: https://docs.docker.com/engine/reference/commandline/buildx_build/
[docker build should support privileged operations #1916](https://github.com/moby/moby/issues/1916)
[Build with docker and --privileged](https://stackoverflow.com/questions/48098671/build-with-docker-and-privileged)

```
docker buildx create --use --name insecure-builder --buildkitd-flags '--allow-insecure-entitlement security.insecure'
docker buildx build --allow security.insecure .

docker buildx build --allow security.insecure \
        --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
        --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
        --platform=linux/arm64,linux/amd64 \
        -f containers/wetty/Dockerfile \
        -t hub.iefcu.cn/xiaoyun/wetty . --push
```

#### 清理空间

[Is it safe to clean docker/overlay2/](https://stackoverflow.com/questions/46672001/is-it-safe-to-clean-docker-overlay2)

Docker uses /var/lib/docker to store your images, containers, and local named volumes. Deleting this can result in data loss and possibly stop the engine from running. The overlay2 subdirectory specifically contains the various filesystem layers for images and containers.

To cleanup unused containers and images, see docker system prune. There are also options to remove volumes and even tagged images, but they aren't enabled by default due to the possibility of data loss:

```
$ docker system prune --help

Usage:  docker system prune [OPTIONS]

Remove unused data

Options:
  -a, --all             Remove all unused images not just dangling ones
      --filter filter   Provide filter values (e.g. 'label=<key>=<value>')
  -f, --force           Do not prompt for confirmation
      --volumes         Prune volumes
```

What a prune will never delete includes:

* running containers (list them with docker ps)
* logs on those containers (see this post for details on limiting the size of logs)
* filesystem changes made by those containers (visible with docker diff)

To completely refresh docker to a clean state, you can delete the entire directory, not just sub-directories like overlay2:
```
# danger, read the entire text around this code before running
# you will lose data
sudo -s
systemctl stop docker
rm -rf /var/lib/docker
systemctl start docker
exit
```

The engine will restart in a completely empty state, which means you will lose all:

* images
* containers
* named volumes
* user created networks
* swarm state
