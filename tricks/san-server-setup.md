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

首先修改客户端的iqn, 跟上面的iqn一致
```bash
sed -i -e 's/:\w\+$/:sanclient1/' /etc/iscsi/initiatorname.iscsi
cat /etc/iscsi/initiatorname.iscsi 
```

然后关联使用
```bash
iscsiadm -m discovery -t st -p 10.90.3.28
iscsiadm -m node -L all
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
