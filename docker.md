# docker 入门

https://yeasy.gitbooks.io/docker_practice/content/image/build.html

1. docker镜像层数查看
docker history --no-trunc=true ubuntu:14.04

2. docker创建镜像
docker build -t ubuntu:v1 .
 Dockerfile
 ```docker
 FROM ubuntu:14.04
RUN apt-get update \
    && apt-get install -y g++ libc6-dev make vim subversion git tmux
 ```

3. docker挂载主机文件夹
```bash
docker run -i -t -P \
    --restart=always \
    --name web \
    --mount type=bind,source=$HOME/workspaces/test_docker,target=/data \
    ubuntu:v1 \
    /bin/bash

# -v /src/webapp:/opt/webapp
```

4. docker清空所有容器
docker container  prune

5. docker导出导入镜像
docker image save 91549c39f359 > samba_ad_dc.tar
docker image load -i samba_ad_dc.tar
docker tag 91549c39f359 samba-ad-dc:latest

6. docker连接容器
docker exec -it ubuntu_sphinx bash

7. Dockerfile模板
```
FROM ubuntu:18.04

MAINTAINER  Adam Xiao "http://github.com/adamxiao"

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
    && apt-get install -y \
    git 

#CMD ["/bin/bash"]
```

8. docker多阶段构建
https://docs.docker.com/v17.09/engine/userguide/eng-image/multistage-build/#before-multi-stage-builds

9. 基于centos构建自定义基础镜像方法
```
yum install supermin5 supermin 

# 制作镜像
# 配置yum源
vim /etc/yum.repos.d/Kylin-Base.repo
# 安装基础软件
supermin5 -v --prepare bash vim-minimal yum passwd dbus iputils yum-utils bind-license rootfiles net-tools -o kylin.d --packager-config /etc/yum.repos.d/
# 编译生成根文件系统
supermin5 -v --build --format chroot kylin.d -o appliance.d
# 打包基础镜像文件系统
tar --numeric-owner -cpf kylin.tar -C appliance.d .
# 导入基础镜像
cat kylin.tar |docker import - kylinos
```

centos_sphinx Docerfile
docker run -it --privileged --restart=always --name centos_sphinx -v $HOME/tmp:/data centos:7.4.1708 bash
```
yum makecache
#yum install -y python-sphinx

yum install -y python3-pip
pip3 install sphinx sphinx-autobuild sphinx_rtd_theme
pip3 install nbsphinx 
```


## 问题
1. docker里面的tlinux镜像不能strace, gdb, 没有权限？
  解决: run --privileged 参数
2. docker的系统编译代码比较慢? 扫描文件都很慢！！！
  可能是mac版本是samba共享文件夹导致的
