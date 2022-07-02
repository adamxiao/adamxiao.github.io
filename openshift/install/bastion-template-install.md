# 使用堡垒机虚拟机模板安装kcp

* bastion
* template

TODO:
* 1.修改release
* 2.修改openshift-install的缓存
* 3.增加master安装脚本(增加修改说明)

## 准备一个堡垒机环境，基于x86的，gitlab代码如下:

http://192.168.120.13/xiaoyun/bastion-allinone/-/tree/x86-install

## 制作x86堡垒机模板

#### 1. 准备一个centos7的qcow2云镜像部署虚拟机

* 配置用户名密码为root/xxx
* 禁用防火墙, selinux
* 配置ip地址，dns等;
* 磁盘分区扩容; (默认分区大小只有8g，不够存放容器镜像)

#### 2. 安装基础软件(docker, docker-compose, oc等)

* 安装docker;
* 安装docker-compose;
* 安装oc;
* 安装git;（方便拉取堡垒机程序）

#### 3. 配置dns，haproxy，生成点火文件

(周明自动话脚本弄进来就更简单了)

#### 4. 启动所有服务

启动服务

```
bash run.sh up -d
```

停止所有服务
```
bash run.sh down
```

**至此，堡垒机虚拟机就部署好了，可以导出为一个虚拟机模板了。
额外的容器镜像没有放到虚拟机模板中来，因为镜像很大，而且易变，作为额外附件保存更合适**

#### 5. 同步容器镜像

我会将镜像数据打包成一个tar包，只需要解压到/root/bastion-allinone/registry/data目录即可

## 使用这个堡垒机的方法，默认堡垒机的配置，就是安装一个单节点的x86的容器云平台

#### 1. 堡垒机配置

修改时间并写入到硬件
```
hwclock -w
```

然后生成点火文件（注意24小时内过期）
```
bash ./adam-create-ign.sh
```

#### 2. 安装节点配置

使用rhcos-4.9.0-x86_64-live.x86_64.iso刻录到u盘中启动系统
修改系统时间，并写入到硬件hwclock -w

**由于我的堡垒机中的点火配置，和dns，haproxy的配置，都已经配置好容器云集群的ip地址，集群名称了，所以安装基本上不用修改配置。**

bootstrap节点安装:
(注意修改网卡名称，其他均不用修改)

```
sudo coreos-installer install /dev/vdb \
    --append-karg ip=192.168.100.10::192.168.100.1:255.255.255.0:bootstrap.kcp4.iefcu.cn:enp3s0:none \
    --append-karg nameserver=192.168.100.200 \
    --append-karg selinux=0 \
    --insecure-ignition \
    --ignition-url http://192.168.100.200:9090/kcp4.iefcu.cn/bootstrap.ign
```

master节点安装:
(注意修改网卡名称，其他均不用修改)

```
sudo coreos-installer install /dev/vdb \
    --append-karg ip=192.168.100.11::192.168.100.1:255.255.255.0:master1.kcp4.iefcu.cn:enp3s0:none \
    --append-karg nameserver=192.168.100.200 \
    --insecure-ignition \
    --ignition-url http://192.168.100.200:9090/kcp4.iefcu.cn/master.ign
```

## 附件说明

上述说明提到的堡垒机，iso，容器镜像等，都放到这个目录中了。
ftp://10.0.0.5/02-研发二部/01-仅部门内可见/xiaoyun/北京容器云平台安装堡垒机/x86平台/
 

* bastion-img.7z => 堡垒机guest.img镜像，压缩后只有467M

* rhcos-4.9.0-x86_64-live.x86_64.iso => x86平台的iso，987M

* docker => 容器镜像文件, 9.7G

## 安装完后续操作

* 注意修改时间, 堡垒机时间, xxx时间 => done
* 注意现在的release, master安装不能加selinux=0, 这里后续需要更新release
  提取openshift-install也比较慢, 需要适配做一个新的release!
* kylin-logo => done
* 增加修改ip, dns => done, 只有master节点需要, done
* 禁止清理镜像 => master done
* 搭建内置dns,registry => done
* 限定haproxy内置调度 => done
* 添加额外worker节点 => done
=> 优化堡垒机程序以及文档

