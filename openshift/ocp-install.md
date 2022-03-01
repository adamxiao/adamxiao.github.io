# 离线安装部署kcp文档

v1.6 20220215

v1.6计划：
使用nmcli配置修改网络，主机名
selinux=0在安装阶段处理一下。
dns配置文档更新。

## 准备工作
需要准备硬件，软件，ip等

#### 硬件准备
单节点环境部署，至少需要三台机器：
一台x86机器，另外两台arm机器
x86机器作为负载均衡和dns等，cpu和内存需要4u8g
arm机器作为master等，cpu和内存至少需要8u16g
bootstrap的arm机器可以4u4g

#### 软件数据准备
kylin coreos系统iso
haproxy负载均衡
dns 服务
quay镜像仓库
kcp-install和oc 
（以上软件数据全部在容器云ftp服务器上）

#### ip准备
至少准备三个ip（其中有1个临时ip，可以释放）
bootstrap => x.x.x.0 (临时)
master1 => x.x.x.1
haproxy => x.x.x.99

#### 域名准备
准备*.ocp4.iefcu.cn，可自定义，例如
bootstrap.ocp4.iefcu.cn
master1.ocp4.iefcu.cn
etcd1.ocp4.iefcu.cn

## 安装步骤

### 1. 初始化配置bastion堡垒机

x86机器，可以是虚拟机。
安装系统，例如unikylin3.3-6A，最小安装即可，创建管理员adam/ksvd2020，配置网络
安装docker，然后把我准备好的软件放上去，有如下文件
quay.tgz => 私有镜像仓库
kcp-extra.tgz => 其他配置
docker-images.tar => 基础服务docker镜像
然后创建一个目录，例如/data/kcp-install，解压上述文件

```bash
mkdir -p /data/kcp-install && cd /data/kcp-install
# XXX: 把上述文件放到这里 ...
# 解压私有镜像仓库
sudo tar --numeric-owner -xpzf quay.tgz
# 解压其他配置
tar -xzf kcp-extra.tgz
# 导入docker镜像
docker image load -i docker-images.tar

# XXX: 最后，禁用selinxu和防火墙
```

### 2. 部署配置镜像仓库

我已经在使用docker部署配置好了，启动即可。

```bash
cd /data/kcp-install/quay && docker-compose up -d
```


### 3. 配置dnsmasq服务

使用dnsmasq提供pxe安装系统服务，以及dns服务
```bash
cd /data/kcp-install/pxe-dnsmasq && docker-compose up -d
```

dns配置内容示例如下

```conf
# 泛域名解析apps
address=/apps.kcp4.iefcu.cn/172.16.135.98
address=/api.kcp4.iefcu.cn/172.16.135.98
address=/api-int.kcp4.iefcu.cn/172.16.135.98

# 这里默认etcd是部署在master节点上
address=/etcd-0.kcp4.iefcu.cn/172.16.135.11
address=/etcd-1.kcp4.iefcu.cn/172.16.135.12
address=/etcd-2.kcp4.iefcu.cn/172.16.135.13

# 加密的etcd域名SRV记录
srv-host=_etcd-server-ssl._tcp.kcp4.iefcu.cn,etcd-0.kcp4.iefcu.cn,2380,10
srv-host=_etcd-server-ssl._tcp.kcp4.iefcu.cn,etcd-1.kcp4.iefcu.cn,2380,10
srv-host=_etcd-server-ssl._tcp.kcp4.iefcu.cn,etcd-2.kcp4.iefcu.cn,2380,10

# 除此之外再添加各节点主机名记录
address=/bootstrap.kcp4.iefcu.cn/172.16.135.10
address=/master1.kcp4.iefcu.cn/172.16.135.11
address=/master2.kcp4.iefcu.cn/172.16.135.12
address=/master3.kcp4.iefcu.cn/172.16.135.13

# 临时使用
address=/quay.iefcu.cn/172.16.135.99
```


### 4. 配置运行haproxy

cd /data/kcp-install/haproxy && docker-compose up -d

修改haproxy配置
TODO:

### 5. 生成点火文件

配置install-config.yaml.bak，生成点火文件
```
cd /data/kcp-install/ocp-install.arm && bash adam.sh
```

### 安装kylin coreos


按F7（也可能是F11）选择cdrom启动，**在livecd的grub配置中增加内核参数selinux=0**
livecd网络准备工作
准备工作，配置可以ssh到服务器上去执行命令

```bash
# 使用nmcli配置ip地址, 注意enp3s0这个名称需要适配修改
sudo nmcli c add con-name enp3s0 type ethernet ifname enp3s0
sudo nmcli c mod enp3s0 ipv4.addresses 10.90.3.84/24 ipv4.gateway 10.90.3.1 ipv4.method manual
sudo nmcli c mod enp3s0 ipv4.dns 10.90.3.38
sudo nmcli c mod enp3s0 ipv6.method disabled
sudo nmcli c mod enp3s0 ipv4.dhcp-hostname bootstrap.kcp4-arm.iefcu.cn
# confirm /etc/NetworkManager/system-connections/enp3s0.nmconnection
sudo nmcli c up enp3s0

# 可选，这些ssh配置以及密码配置是为了能够ssh登录复制粘贴命令的。
# 修改core用户的密码为password
echo password | sudo passwd --stdin core
```

准备工作，校准服务器硬件时间
```bash
# 这里livecd一般是utc时区，我们设置时间要减去8个小时
date -s '2022-01-22 10:00:00'
# 将系统时间写入硬件
hwclock -w
```

**TODO:（有额外的dhcp服务器，需要处理，可能会遇到安装失败的问题）**


#### 手动安装bootstrap

注意修改如下参数, 部分参数可以在livecd中使用相关命令查看:
	a. 系统安装到哪个磁盘上，例如 /dev/vda
	b. 配置系统的网卡网络信息，例如 enp3s0
	c. 静态ip地址，例如 ip=10.90.3.82::10.90.3.1:255.255.255.0
	d. 主机名，例如 bootstrap.kcp3-arm.iefcu.cn
	e. dns信息, 例如 nameserver=10.90.3.38
	f. 点火文件地址, 例如 http://10.90.3.38:9090/bootstrap.ign

```bash
sudo coreos-installer install /dev/vda \
    --append-karg ip=10.90.3.82::10.90.3.1:255.255.255.0:bootstrap.kcp3-arm.iefcu.cn:enp3s0:none \
    --append-karg nameserver=10.90.3.38 \
    --append-karg selinux=0 \
    --insecure-ignition \
    --ignition-url http://10.90.3.38:9090/bootstrap.ign


sudo coreos-installer install /dev/vda -n \
    --append-karg selinux=0 \
    --insecure-ignition \
    --ignition-url http://10.90.3.38:9090/bootstrap.ign
```