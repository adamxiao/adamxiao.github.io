# cinder存储后端部署

## 一.部署华为ipsan存储卷

参考文档: https://docs.openstack.org/cinder/latest/configuration/block-storage/drivers/huawei-storage-driver.html
https://docs.openstack.org/kilo/config-reference/content/huawei-storage-driver.html

注意事项:
- 需要授权才能配置创建瘦卷
- 用户名和密码在配置后会变为密文

#### 1.配置华为san存储xml配置文件

/etc/cinder/cinder_huawei_conf.xml
注意点:需要给这个文件正确的权限,cinder会把用户名和密码修改一下
```
<?xml version='1.0' encoding='UTF-8'?>
<config>

<Storage>
<Product>V3</Product>
<Protocol>iSCSI</Protocol>
<RestURL>https://10.0.0.250:8088/deviceManager/rest/</RestURL>
<UserName>username</UserName>
<UserPassword>password</UserPassword>
</Storage>

<LUN>
<LUNType>Thick</LUNType>
<WriteType>1</WriteType>
<LUNcopyWaitInterval>5</LUNcopyWaitInterval>
<Timeout>432000</Timeout>
<StoragePool>StoragePool003</StoragePool>
</LUN>

<iSCSI>
<DefaultTargetIP>192.168.120.234</DefaultTargetIP>
</iSCSI>

</config>
```

参数配置说明:
- LUNType: lun类型，瘦卷或胖卷
  Thick, 或Thin

#### 2.配置cinder配置文件

/etc/cinder/cinder.conf
或者可能是 /usr/share/cinder/cinder-dist.conf
```
[huawei]
volume_driver = cinder.volume.drivers.huawei.huawei_driver.HuaweiFCDriver
cinder_huawei_conf_file = /etc/cinder/cinder_huawei_conf.xml
volume_backend_name = huawei
```

## 二.部署nfs存储卷

```
[nfs]
volume_driver = cinder.volume.drivers.nfs.NfsDriver
nfs_shares_config = /etc/cinder/nfs_shares
# 192.168.120.5:/pool-1/nasvolume/openstack
nfs_mount_point_base = /var/lib/nova/mnt
volume_backend_name = nfs
```

底层nfs存储实现
TODO:

## 三.部署lvm卷存储

参考: https://docs.openstack.org/cinder/victoria/install/cinder-storage-install-rdo.html
```
pvcreate /dev/vdb
vgcreate lvm-vol /dev/vdb
```

cinder配置示例
```
[lvm]
volume_backend_name=lvm
volume_driver=cinder.volume.drivers.lvm.LVMVolumeDriver
iscsi_ip_address=192.168.140.4
iscsi_helper=lioadm
volume_group=cinder-volumes
volumes_dir=/var/lib/cinder/volumes
```

上面有问题，用这个...
```
[lvm_1]
image_volume_cache_enabled = True
volume_clear = zero
lvm_type = auto
target_helper = lioadm
target_protocol = iscsi
iscsi_ip_address = 10.90.4.237
volume_group = lvm_1
volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
volume_backend_name = lvm_1
```

ubuntu系列用如下lvm配置
```
[lvm-vol]
image_volume_cache_enabled = True
volume_clear = zero
lvm_type = auto
target_helper = tgtadm
volume_group = lvm-vol
volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
volume_backend_name = lvm-vol
```
