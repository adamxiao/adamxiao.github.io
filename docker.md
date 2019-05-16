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


## 问题
1. docker里面的tlinux镜像不能strace, gdb, 没有权限？
  解决: run --privileged 参数
2. docker的系统编译代码比较慢? 扫描文件都很慢！！！
  可能是mac版本是samba共享文件夹导致的
