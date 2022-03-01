# centos8作为c应用镜像

指纹识别，人脸识别，需要的一些依赖包，记录下来

```dockerfile
#from hub.iefcu.cn/library/kylinos:KY3.4-4A AS builder
#from hub.iefcu.cn/public/centos:8
from docker.io/library/centos:8

RUN yum makecache && yum install -y epel-release \
	&& yum makecache && yum install -y \
	openssl-libs openssl openldap libuuid uuid unixODBC \
	gcc gcc-c++ autoconf automake glibc-devel libxcrypt-devel libstdc++-devel \
	make hidapi-devel libtool systemd-devel usbredir-devel \
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
