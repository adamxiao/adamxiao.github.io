# centos8作为c应用镜像

指纹识别，人脸识别，需要的一些依赖包，记录下来

#### 构建Dockerfile文件

```dockerfile
#from hub.iefcu.cn/library/kylinos:KY3.4-4A AS builder
#from hub.iefcu.cn/public/centos:8
from docker.io/library/centos:8

# refer https://stackoverflow.com/questions/70963985/error-failed-to-download-metadata-for-repo-appstream-cannot-prepare-internal
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

RUN yum makecache && yum install -y epel-release \
	&& yum makecache && yum install -y \
	openssl-libs openssl openldap libuuid uuid unixODBC \
	gcc gcc-c++ autoconf automake glibc-devel libxcrypt-devel libstdc++-devel \
	make hidapi-devel libtool systemd-devel usbredir-devel \
	curl cmake mysql-devel \
	java-1.8.0-openjdk curl-devel libticonv \
	&& yum clean all

#RUN yum install -y java-1.8.0-openjdk strace \
	#&& yum clean all

#COPY ./libDeviceCom.so /usr/lib
#COPY ./authmanager-face-service.jar /root
#COPY ./data.txt /root

#CMD ["java", "-jar", "/root/authmanager-face-service.jar"]

# hidapi-devel , 也可以自己编译，自己编译就依赖其他devel包
# 编译依赖  => libtool
# udev => systemd-devel
# libusb-1.0 => usbredir-devel
```

#### 在x86机器下使用buildx构建

```bash
docker buildx build \
  -t hub.iefcu.cn/public/centos8:1.5 \
  --platform linux/arm64 --load .
```

#### 版本变更记录

* 1.5 添加jdk, curl-devel libticonv
* 1.4 添加curl cmake mysql-devel, 修正yum install mirror list问题
