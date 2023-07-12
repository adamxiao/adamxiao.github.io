# 搭建ipsan存储服务的方法

* ipsan
* targetcli

## centos安装san存储服务

#### 安装命令

机器上有targetcli命令，表示安装成功
```bash
yum install -y targetcli
```

安装更多包, 例如: /etc/iscsi/initiatorname.iscsi
```bash
yum install iscsi*

iscsi-initiator-utils
iscsi-initiator-utils-devel
iscsi-initiator-utils-iscsiuio
```

#### 修改本机器的iqn

修改iqn为iqn.1994-05.com.redhat:sanserver1
```bash
sed -i -e 's/:\w\+$/:sanserver1/' /etc/iscsi/initiatorname.iscsi

cat /etc/iscsi/initiatorname.iscsi 
InitiatorName=iqn.1994-05.com.redhat:sanserver1
```

#### 启动target服务

```bash
systemctl enable --now target.service
```

#### 关闭防火墙

```
systemctl disable firewalld.service
systemctl stop firewalld.service
```

#### 创建一个块lun，然后将客户端的iqn关联到这个lun

命令如下:
```
targetcli
cd backstores/block
create block1 /dev/vdb
cd /iscsi
create iqn.1994-05.com.redhat:sanserver1
cd /iscsi/iqn.1994-05.com.redhat:sanserver1/tpg1/luns/
create /backstores/block/block1
cd /iscsi/iqn.1994-05.com.redhat:sanserver1/tpg1/acls/
create iqn.1994-05.com.redhat:sanclient1
exit 
```

#### (或者)创建一个文件Lun，然后将客户端的iqn关联到这个lun

命令如下：  
```
targetcli
cd backstores/fileio
create ipsan_h3c /data/ipsan_h3c 1G
cd /iscsi
create iqn.1994-05.com.redhat:sanserver1
cd /iscsi/iqn.1994-05.com.redhat:sanserver1/tpg1/luns/
create /backstores/fileio/ipsan_h3c
cd /iscsi/iqn.1994-05.com.redhat:sanserver1/tpg1/acls/
create iqn.1994-05.com.redhat:sanclient1
exit 
```

#### 客户端关联使用

安装软件包
```
$rpm -qf /usr/sbin/iscsiadm
iscsi-initiator-utils
```

首先修改客户端的iqn, 跟上面的iqn一致
```bash
sed -i -e 's/:\w\+$/:sanclient1/' /etc/iscsi/initiatorname.iscsi
cat /etc/iscsi/initiatorname.iscsi 
```

然后关联使用
```bash
iscsiadm -m discovery -t st -p 10.90.3.28
10.90.3.28:3260,1 iqn.2005-10.org.freenas.ctl:ubuntu1
iscsiadm -m node -L all
Logging in to [iface: default, target: iqn.2005-10.org.freenas.ctl:ubuntu1, portal: 10.90.3.28,3260] (multiple)
Login to [iface: default, target: iqn.2005-10.org.freenas.ctl:ubuntu1, portal: 10.90.3.28,3260] successful.
```

客户端需要重启iscsid, 让修改initiatorname.iscsi生效
```
systemctl restart iscsid.service
```

否则看server端日志, 会发现认证失败
```
[19505.799312] iSCSI Initiator Node: iqn.1994-05.com.redhat:4de8cdfb7866 is not authorized to access iSCSI target portal group: 1.
[19505.802665] iSCSI Login negotiation failed.
```

san存储服务器添加ｓａｎ存储设备，客户端需要刷新, 然后才能看到更多设备
```
# 注销所有sanserver的登录
iscsiadm -m node -U all

# 然后再重新登录
iscsiadm -m node -L all
```


iscsiadm -m discovery -t st -p 10.90.3.183
iscsiadm  -m node  -d  1 T iqn.1994-05.com.redhat:sanserver1 -p  10.90.3.183 -l

```
tgtadm -L iscsi -o show -m target # 查看 target 创建的信息
```

lsscsi -sti
iqn为ipsan
fc为fcsan
```
[ssh_10.90.6.76] root@node1: ~$lsscsi -sti
[3:0:0:0]    disk    sata:                           /dev/sda   -  2.00TB
[5:0:0:0]    disk    sata:                           /dev/sdb   -  2.00TB
[7:0:0:0]    cd/dvd  sata:                           /dev/sr0   -       -
[8:0:0:0]    disk    fc:0x210000d02308d7c40x010b00   /dev/sdc   3600d02310008d7c43c8d1ef64f92ab08   322GB
[8:0:0:6]    disk    fc:0x210000d02308d7c40x010b00   /dev/sdd   3600d02310008d7c477694b970bc32cd5   214GB
[8:0:0:8]    disk    fc:0x210000d02308d7c40x010b00   /dev/sde   3600d02310008d7c477694b970bc32cd5   214GB
[8:0:0:9]    enclosu fc:0x210000d02308d7c40x010b00   -          -       -
[8:0:1:0]    disk    fc:0x210000d02318d7c40x010f00   /dev/sdf   3600d02310008d7c43c8d1ef64f92ab08   322GB
[8:0:1:6]    disk    fc:0x210000d02318d7c40x010f00   /dev/sdg   3600d02310008d7c477694b970bc32cd5   214GB
[8:0:1:8]    disk    fc:0x210000d02318d7c40x010f00   /dev/sdh   3600d02310008d7c477694b970bc32cd5   214GB
[8:0:1:9]    enclosu fc:0x210000d02318d7c40x010f00   -          -       -
[9:0:0:0]    disk    iqn.2002-10.com.infortrend:raid.uid579524.201,t,0x1  /dev/sdi   3600d02310008d7c462bd594015b44935   214GB
[9:0:0:1]    disk    iqn.2002-10.com.infortrend:raid.uid579524.201,t,0x1  /dev/sdj   3600d02310008d7c45e58417a7554715c   214GB
[9:0:0:7]    enclosu iqn.2002-10.com.infortrend:raid.uid579524.201,t,0x1  -          -       -
```

## ubuntu安装san存储服务

关键字《ubuntu setup san server》

- https://www.howtoforge.com/tutorial/how-to-setup-iscsi-storage-server-on-ubuntu-2004-lts/
- https://linuxhint.com/iscsi_storage_server_ubuntu/
- [(好)iSCSI : Configure iSCSI Target (tgt)](https://www.server-world.info/en/note?os=Ubuntu_20.04&p=iscsi&f=2)

安装服务端
```
apt install tgt -y
systemctl status tgt
```

创建文件镜像
```
# create a disk image
mkdir /var/lib/iscsi_disks
dd if=/dev/zero of=disk01.img count=0 bs=1 seek=10G
```

创建iscsi target
编辑文件: /etc/tgt/conf.d/ubuntu1.conf
```
# create new
# if you set some devices, add <target>-</target> and set the same way with follows
# naming rule : [ iqn.(year)-(month).(reverse of domain name):(any name you like) ]
<target iqn.2020-05.world.srv:dlp.ubuntu1>
    # provided devicce as a iSCSI target
    backing-store /var/lib/iscsi_disks/disk01.img
    # iSCSI Initiator's IQN you allow to connect
    initiator-name iqn.2020-05.world.srv:node01.initiator01
    # authentication info ( set anyone you like for "username", "password" )
    incominguser username password
</target> 
```

重启生效, 查看状态
```
sudo systemctl restart tgt
sudo tgtadm --mode target --op show
```

## ubuntu使用ipsan存储服务

#### ubuntu客户端使用

安装工具包
```
sudo apt install open-iscsi
```

然后关联使用
```bash
iscsiadm -m discovery -t st -p 10.90.3.25
iscsiadm -m node -L all
```

注销所有sanserver的登录
```
iscsiadm -m node -U all
iscsiadm -m discoverydb -t sendtargets -p <IP>:<port> -o delete
```

删除session
关键字《iscsiadm remove session》
https://helpdesk.kaseya.com/hc/en-gb/articles/4407512021521-Remove-ISCSI-sessions-using-the-Linux-command-line
```
iscsiadm -m node -T <iqn> -p <ip address>:<port number> -u
iscsiadm -m node -o delete -T <iqn>
iscsiadm -m discoverydb -t sendtargets -p <IP>:<port> -o delete
```


## 相关资料

https://blog.51cto.com/wgmml/1597982

iSCSI术语

- IQN（iSCSI Qualified Name）用来识别iSCSI通信的服务端和客户端，格式是
  iqn.yyyy-mm.com.reverse.domain:optional-extra-name
  如主机名为instructor.example.com。第一个分享的LV空间可以是iqn.2013-10.com.example.instructor:lv1-my-first-lv
  可选部分（含前面的冒号）加上可以用于区分多个分享的设备，如有多个lv要分享的时候

- target :iSCSI服务端叫target,target 分享LUN，logical unit ,一台服务器可以分享一个或者多个LUN 

- initiator:iSCSI客户端叫initiator,可以由软硬件实现，通常软件实现的较多（省钱）

- node: iSCSI服务端,iSCSI客户端都叫node

- Portal :在iSCSI中,Portal是一个target或者initiator的IP，用于建立连接

- iSNS:  internet storage name service ,一个命名服务，用来让initiator发现target，较少使用


#### iscsiadm使用

常用模式：discovery|node|session|iface

- discovery：发现某服务器是否有target输入，以及输出哪些target；
- node：管理跟某target的关联关系，建立关联、断开关联。。。
- session：会话管理
- iface：端口管理

```
iscsiadm -m session # 获取连接会话
tcp: [1] 192.168.99.112:3260,1 iqn.1994-05.com.redhat:sanserver2 (non-flash)
tcp: [2] 10.60.5.112:3260,1 iqn.1994-05.com.redhat:sanserver1 (non-flash)
tcp: [3] 10.90.3.118:3260,1 iqn.2005-10.org.freenas.ctl:iscsi (non-flash)
```

```
iscsiadm -m discovery -t st -p 10.90.3.21 # 发现target?
# 查看10.90.3.21主机共享的target及端口，发现完后会在/var/lib/iscsi/send_targets/下显示记录，不想使用是需要删除。

iscsiadm -m discovery -t st -p 10.90.3.21 -o delete # 删除target

iscsiadm -m discovery -t st -p 10.90.3.21 # 设置了密码也能发现?
10.90.3.21:3260,1 iqn.2005-10.org.freenas.ctl:adam1
10.90.3.21:3260,1 iqn.2005-10.org.freenas.ctl:adam80

iscsiadm -m discovery -t st -p 10.90.3.25
10.90.3.25:3260,1 iqn.2005-10.org.freenas.ctl:adam-ipsan0214
10.90.3.25:3260,1 iqn.2005-10.org.freenas.ctl:adam-iscsi1
```

```
iscsiadm -m discovery # 列举发现列表?
10.90.3.21:3260 via sendtargets
10.90.3.25:3260 via sendtargets
```

挂载登录
```
iscsiadm -m node -T iqn.2005-10.org.freenas.ctl:adam1 -p 10.90.3.21 -l
挂载登录 10.90.3.21, target服务器 iqn.2005-10.org.freenas.ctl:adam1 磁盘

CHAP认证，登录失败

Logging in to [iface: default, target: iqn.2005-10.org.freenas.ctl:adam1, portal: 10.90.3.21,3260] (multiple)
iscsiadm: Could not login to [iface: default, target: iqn.2005-10.org.freenas.ctl:adam1, portal: 10.90.3.21,3260].
iscsiadm: initiator reported error (24 - iSCSI login failed due to authorization failure)
iscsiadm: Could not log into all portals
```

配置chap认证登录
```
iscsiadm -m node -p 10.90.3.21:3260 -o update --name node.session.auth.authmethod --value CHAP
iscsiadm -m node -p 10.90.3.21:3260 -o update --name node.session.auth.username --value adam
iscsiadm -m node -p 10.90.3.21:3260 -o update --name node.session.auth.password --value xxx

iscsiadm -m node -p 10.90.3.21:3260 --login # 会尝试登录发现的所有target, 如果某些target的chap认证信息不对, 则登录失败
# 在fusion compute表现会关联主机失败
```

两个target配置的chap用户名密码不一样，则登录一个成功, 一个失败
```
[ssh_192.168.99.31] root@node1: ~$iscsiadm -m node -p 10.90.3.21:3260 --login
Logging in to [iface: default, target: iqn.2005-10.org.freenas.ctl:adam1, portal: 10.90.3.21,3260] (multiple)
Logging in to [iface: default, target: iqn.2005-10.org.freenas.ctl:adam80, portal: 10.90.3.21,3260] (multiple)
iscsiadm: Could not login to [iface: default, target: iqn.2005-10.org.freenas.ctl:adam1, portal: 10.90.3.21,3260].
iscsiadm: initiator reported error (24 - iSCSI login failed due to authorization failure)
Login to [iface: default, target: iqn.2005-10.org.freenas.ctl:adam80, portal: 10.90.3.21,3260] successful.
iscsiadm: Could not log into all portals
```

#### 参考资料

https://www.linuxteck.com/how-to-configure-iscsi-target-initiator-on-rhel-centos-7-6/
