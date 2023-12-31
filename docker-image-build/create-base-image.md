# 基础镜像制作

使用 febootstrap 制作自定义基础镜像
https://cloud.tencent.com/developer/article/1454524

https://xiazemin.github.io/MyBlog/docker/2020/10/31/image.html

[创建自己的Docker基础镜像(rhel、centos)](https://blog.csdn.net/bjywxc/article/details/103976310)

## 使用mkimage-yum.sh制作基础镜像

参考http://ask.loongnix.org/?/article/81

使用 mkimage-yum.sh
https://raw.githubusercontent.com/docker/docker/master/contrib/mkimage-yum.sh

```
./mkimage-yum.sh -y /etc/yum.conf centos-base
```

例如制作345基础镜像
```
./mkimage-yum.sh -y /etc/yum.conf -p yum -g base -t 345 hub.iefcu.cn/xiaoyun/kylinos
chkconfig findutils pkgconf yum => 某次用这几个包做了基础镜像, 后来验证发现其实就是安装了yum包, core组有问题 `-p yum -g core`
chkconfig findutils gdb-gdbserver pkgconf procps-ng rootfiles tar vim-minimal yum => 而os那边用这几个
```

## 使用supermin制作基础镜像

```
supermin5 -v --prepare bash vim-minimal yum passwd dbus iputils yum-utils bind-license rootfiles net-tools -o kylin.d --packager-config /etc/yum.repos.d/
```

## 镜像大小精简

思路:
- libcurl 使用精简版的
- dnf 使用精简版的
- 运行镜像不包含yum工具? 
- 参考其他基础镜像, 不包含某些功能

## UBI基础镜像

关键字《UBI容器镜像制作》

https://blog.csdn.net/aarenw/article/details/124857917
Red Hat免费发布通用基础镜像（UBI）

https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/8/html/building_running_and_managing_containers/con_understanding-the-ubi-init-images_assembly_types-of-container-images

- 不包含 ps 和进程相关的命令（procps-ng 软件包）
- 最小映像包含常规的 RHEL 软件 RPM 软件包，但删除了一些功能。最小镜像不包括初始化和服务管理系统，如 systemd 或 System V init、Python 运行时环境和一些 shell 工具。
- 支持 microdnf 的模块
- ubi-micro 可能是最小的 UBI 镜像，通过去掉软件包管理器及通常包含在容器镜像中的所有依赖项而得到。

[(好)初探 openEuler 容器镜像剪裁](https://ost.51cto.com/posts/15309)

版本                     软件包数量  基础镜像大小
- openeuler-20.03-lts      352         469MB
- openeuler-20.03-lts-sp1  358         512MB
- openeuler-20.09          346         531MB
- ubi                      186         205MB
- ubi-init                 187         220MB
- ubi-minimal              105         103MB
- centos8                  172         209MB
- fedora                   145         175MB
- ubuntu                   92          72.9MB

可以发现，虽然 openEuler 比 CentOS 基础镜像多 43 个软件包，但是/usr/lib64 库文件目录大小却几乎相同。经过繁琐但并不枯燥的软件包查询，能够逐渐发现 openEuler 基础镜像"大"的原因，主要表现为以下三点：
- 软件包的不必要依赖较多
- 软件包库文件的多版本共存
- 没有考虑软件包的精简版本实现

以下举例说明以上问题：
- openEuler libcurl、libssh 依赖 e2fsprogs 提供的 libcom_err.so，但实际上并不需要除 libcom_err.so 之外其他 e2fsprogs 软件包提供的文件。
- openEuler 存在多个版本的 libncurses 相关的动态链接库文件。
- CentOS8 基础镜像包含 libcurl-minimal、coreutils-single 软件包以实现提供相应软件包基础能力的精简版本，openEuler 尚未实现。

[使用 mkosi 构建 RHEL 和 RHEL UBI 镜像 | Linux 中国](https://redian.news/wxnews/689449)
