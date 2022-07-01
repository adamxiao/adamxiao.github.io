# 搭建ipsan存储服务的方法

* ipsan
* targetcli

## centos安装san存储服务

#### 安装命令

安装`yum install -y targetcli`
   机器上有targetcli命令，表示安装成功

#### 修改本机器的iqn

修改iqn为iqn.1994-05.com.redhat:sanserver1
```
[root@localhost ~]#cat /etc/iscsi/initiatorname.iscsi 
InitiatorName=iqn.1994-05.com.redhat:sanserver1
```

#### 启动target服务
```
systemctl enable target.service
systemctl start target.service
```

#### 关闭防火墙

```
systemctl disable firewalld.service
systemctl stop firewalld.service
```

#### 创建一个块lun，然后将客户端的iqn关联到这个lun

命令如下：  
```
targetcli
cd backstores/block
create block1 /dev/sdc
cd /iscsi/iqn.1994-05.com.redhat:sanserver1/tpg1/luns/
create /backstores/block/block1
cd /iscsi
create iqn.1994-05.com.redhat:sanserver1
cd /iscsi/iqn.1994-05.com.redhat:sanserver1/tpg1/acls/
create iqn.1994-05.com.redhat:node126
exit 
```
