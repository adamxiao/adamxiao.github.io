# sshd容器镜像构建

## 旧的资料

构建ssh,http,ftp镜像

ngxin, 8.7MB 在alpine上构建的Dockerfile(官方镜像) (docker hub下载量10M+,star 10K+)
docker pull nginx
https://github.com/nginxinc/docker-nginx/blob/master/stable/alpine/Dockerfile

lighthttpd 
docker pull rlecomte/lighthttpd-docker
https://github.com/rlecomte/lighthttpd-docker/blob/master/Dockerfile


sshd镜像，16.96MB (基于alpine apk安装openssh, docker hub下载量 1M+)
docker pull panubo/sshd
https://github.com/panubo/docker-sshd/blob/master/Dockerfile

vsftpd镜像, 基于centos7，135.49 MB 下载量1M+
docker pull fauria/vsftpd
https://github.com/fauria/docker-vsftpd/blob/master/Dockerfile
compose配置运行可以指定映射端口
https://github.com/fauria/docker-vsftpd/blob/master/docker-compose.yml

## 参考资料

* [如何缩减镜像大小](https://www.infoq.cn/article/3-simple-tricks-for-smaller-docker-images)
  主要是使用小的基础镜像，以及去除容器服务运行不依赖的文件
