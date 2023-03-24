# cinder独立部署安装

问题:
- cinder-volume多个访问同一个存储，需要etcd
  意味着etcd必须部署吧，否则不能高可用了吧?
- cinder-schedule和cinder-api都是无状态的服务吧?
- cinder-api启动，有两个--config-file?
  实际上只用了后面那个吧?
- rabbitmq的队列用法
  cinder创建和用了那些队列?
  => 叫做cinder-scheduler, cinder-volume等(使用rabbitmq管理页面轻松看到)
- 使用project admin，noauth认证?
  => 写死project id?

## centos7安装配置cinder组件

基于centos7.9 cloud image

注意: 需要剥离nova，keystone等依赖(通过配置文件剥离, 特殊需求的话要改代码适配)

#### 概述

安装配置如下服务

- cinder-api
- cinder-schedule
- cinder-volume
- rabbitmq
- mariadb
- cli工具测试创建卷挂载卷等

#### 部署mariadb数据库服务

```
yum install mariadb mariadb-server python2-PyMySQL -y
systemctl enable --now mariadb
```

运行mysql_secure_installation建mariadb的root密码。

依官网建mariadb的cinder数据库, 如下所示(注意: 替换CINDER_DBPASS为合适的密码):
https://docs.openstack.org/cinder/wallaby/install/cinder-controller-install-rdo.html
```
CREATE DATABASE cinder;
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' IDENTIFIED BY 'CINDER_DBPASS';
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' IDENTIFIED BY 'CINDER_DBPASS';
```

注意: 后续使用cinder-manage工具初始化数据库

#### 部署rabbitmq-server服务

安装启动
```
yum install -y rabbitmq-server
systemctl enable --now rabbitmq-server
```

开启web管理界面
```
rabbitmq-plugins enable rabbitmq_management
```

配置文件为: /etc/rabbitmq/rabbitmq.config

因为默认用户为guest，要添加其他的管理账户
访问管理页面: http://10.90.2.190:15672/
```
rabbitmqctl add_user kylin-ksvd passwordxx
rabbitmqctl set_user_tags kylin-ksvd administrator
rabbitmqctl set_permissions -p / kylin-ksvd ".*" ".*" ".*"
# 最后重启rabbitmq
systemctl restart rabbitmq-server
```

#### 安装部署cinder-api服务

安装
```
yum install openstack-cinder
```

创建cinder配置: /usr/share/cinder/cinder-dist.conf
```
[DEFAULT]
#logdir = /var/log/cinder
use_stderr = False
state_path = /var/lib/cinder
lock_path = /var/lib/cinder/tmp
volumes_dir = /etc/cinder/volumes
iscsi_helper = lioadm
rootwrap_config = /etc/cinder/rootwrap.conf
#auth_strategy = keystone
auth_strategy = noauth
debug = true
transport_url = rabbit://kylin-ksvd:passwordxx@10.90.2.190:5672/
default_volume_type = lvmdriver-1
enabled_backends = lvmdriver-1
my_ip = 10.90.2.190

[database]
connection = mysql+pymysql://cinder:CINDER_DBPASS@10.90.2.190/cinder

[lvmdriver-1]
image_volume_cache_enabled = True
volume_clear = zero
lvm_type = auto
target_helper = lioadm
target_protocol = iscsi
iscsi_ip_address = 10.90.2.190
volume_group = ksvd-volumes-lvmdriver-1
volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
volume_backend_name = lvmdriver-1

[coordination]
#backend_url = etcd3+http://192.168.0.171:2379
```

初始化数据库(工具会在db中建表)
```
cinder-manage --config-file /usr/share/cinder/cinder-dist.conf --config-file /etc/cinder/cinder.conf db sync
```

启动cinder-api, cinder-scheduler服务
```
/usr/bin/cinder-api --config-file /usr/share/cinder/cinder-dist.conf --config-file /etc/cinder/cinder.conf
/usr/bin/cinder-scheduler --config-file /usr/share/cinder/cinder-dist.conf --config-file /etc/cinder/cinder.conf
```
(最终部署时应使用默认的systemctl来启动服务，systemctl启动cinder-api的过程比较复杂且不便于调试，我们在原型中直接使用命令行来运行服务。)

#### 准备cinder-volume卷类型

使用lvm提供本地lvm卷测试使用

安装相关软件包
```
yum install -y openstack-cinder targetcli \
    lvm2 device-mapper-persistent-data
```

参考官网准备卷类型后端：
https://docs.openstack.org/cinder/victoria/install/cinder-storage-install-rdo.html
```
pvcreate /dev/vdb
vgcreate ksvd-volumes-lvmdriver-1 /dev/vdb # 注意: 卷类型名称跟配置文件的名称一致
```

我们这里卷类型取名为ksvd-volumes-lvmdriver-1，后端取名为lvmdriver-1。将创建的cinder volume type为vol-type-ksvd（故意不使用缺省名）。
```
default_volume_type = lvmdriver-1
enabled_backends = lvmdriver-1

[lvmdriver-1]
image_volume_cache_enabled = True
volume_clear = zero
lvm_type = auto
target_helper = lioadm
target_protocol = iscsi
iscsi_ip_address = 10.90.2.190
volume_group = ksvd-volumes-lvmdriver-1
volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
volume_backend_name = lvmdriver-1
```

手动启动volume服务:
```
/usr/bin/cinder-volume --config-file /usr/share/cinder/cinder-dist.conf --config-file /etc/cinder/cinder.conf
```

#### 准备客户端环境验证

安装qemu环境
```
yum install -y libvirt qemu-kvm
```

模拟云平台的计算节点，连接块存储设备需要使用os-brick包：
```
#pip install os-brick
yum install -y python2-os-brick
```

创建配置文件 uniqb-cinder.conf:
(注意: disk1相关数据是创建卷之后获取到的)
```
[local]
my_ip = 10.90.2.191
initiator = iqn.1994-05.com.redhat:node123

[cinder]
cinder_url = http://10.90.2.190:8776/v3
default_volume_type = vol-type-ksvd

[disk1]
volume_type = lvmdriver-1
volume_id = f14ae42a-98da-4e75-88bf-79966fc598ad
driver_volume_type = iscsi
auth_username = fQCR9WAhTDCh3tgkphKF
auth_password = pJ7W6pJCuEdwLJCA
target_iqn = iqn.2010-10.org.openstack:volume-f14ae42a-98da-4e75-88bf-79966fc598ad
target_portal = 192.168.0.191:3260
target_lun = 0
connection_info = {"connection_info": {"driver_volume_type": "iscsi", "data": {"auth_password": "pJ7W6pJCuEdwLJCA", "target_discovered": false, "encrypted": false, "qos_specs": null, "target_iqn": "iqn.2010-10.org.openstack:volume-f14ae42a-98da-4e75-88bf-79966fc598ad", "target_portal": "192.168.0.191:3260", "volume_id": "f14ae42a-98da-4e75-88bf-79966fc598ad", "target_lun": 0, "access_mode": "rw", "auth_username": "fQCR9WAhTDCh3tgkphKF", "auth_method": "CHAP"}}}
device_info = {"path": "/dev/sdc", "scsi_wwn": "36001405d6282f6275d642bea4d253ccf", "type": "block"}
```

创建测试脚本 uniqb-cinder-cli.py 进行测试:
=> 其实基本就是组REST api访问cinder-api
用法示例:
```
./uniqb-cinder-cli.py get-all
./uniqb-cinder-cli.py create -s 10 -n vol1
```

可以使用测试工具按照cinder服务正常的使用次序进行调用：创建卷类型、批量创建卷、初始化连接、连接（此时指定卷将挂载至本地）、断开连接、终止连接、删除卷。

例如使用curl工具直接调用
```
curl -v -H "Content-Type: application/json" -H "X-Auth-Token: admin:db135c4b5391422da5a55c81dfbf803d" -X POST -d '{"volume": {"backup_id": null, "description": null, "availability_zone": null, "source_volid": null, "consistencygroup_id": null, "snapshot_id": null, "size": 10, "name": "vol1", "imageRef": null, "multiattach": null, "volume_type": "vol-type-ksvd", "metadata": {}}}'  http://10.90.2.190:8776/v3/db135c4b5391422da5a55c81dfbf803d/volumes
```

cinder官方api文档: https://docs.openstack.org/api-ref/block-storage/v3/index.html

获取所有卷类型
```
export project=db135c4b5391422da5a55c81dfbf803d
curl -H "X-Auth-Token: admin:${project}" -X GET \
  http://10.90.2.190:8776/v3/${project}/types
```

删除卷类型
```
export project=db135c4b5391422da5a55c81dfbf803d
export volume_type=53a325f7-727d-4a47-b4ef-3ab7e394603a
curl -H "X-Auth-Token: admin:${project}" -X DELETE \
  http://10.90.2.190:8776/v3/${project}/types/${volume_type}
```

获取卷详情
```
export project=db135c4b5391422da5a55c81dfbf803d
export volume_id=aa00b686-b23c-4751-86de-f6991be36995
curl -H "X-Auth-Token: admin:$project" -X GET \
  http://10.90.2.190:8776/v3/$project/volumes/$volume_id
```

删除卷
```
export volume_id=aa00b686-b23c-4751-86de-f6991be36995
./uniqb-cinder-cli.py delete -i $volume_id
./uniqb-cinder-cli.py delete -i $volume_id -n vol2
curl -H "X-Auth-Token: admin:$project" -X DELETE \
  http://10.90.2.190:8776/v3/${project_id}/volumes/${volume_id}
```

获取cinder服务
```
export project=db135c4b5391422da5a55c81dfbf803d
curl -H "X-Auth-Token: admin:$project" -X GET \
  http://10.90.2.190:8776/v3/{project}/os-services
```

## ubuntu20.04 server独立部署

#### 准备cinder-volume卷类型

使用lvm提供本地lvm卷测试使用

安装相关软件包
```
apt install -y cinder-volume
# cinder-api cinder-scheduler cinder-volume
```

参考官网准备卷类型后端：
https://docs.openstack.org/cinder/victoria/install/cinder-storage-install-rdo.html
```
pvcreate /dev/vdb
vgcreate ksvd-volumes-lvmdriver-1 /dev/vdb # 注意: 卷类型名称跟配置文件的名称一致
```

我们这里卷类型取名为ksvd-volumes-lvmdriver-1，后端取名为lvmdriver-1。将创建的cinder volume type为vol-type-ksvd（故意不使用缺省名）。
```
default_volume_type = lvmdriver-1
enabled_backends = lvmdriver-1

[lvmdriver-1]
image_volume_cache_enabled = True
volume_clear = zero
lvm_type = auto
target_helper = lioadm
target_protocol = iscsi
iscsi_ip_address = 10.90.2.190
volume_group = ksvd-volumes-lvmdriver-1
volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
volume_backend_name = lvmdriver-1
```

手动启动volume服务:
```
/usr/bin/cinder-volume --config-file /etc/cinder/cinder.conf
```

## cinder volume配置示例

nfs后端
=> 为啥cinder块存储还能使用nfs?
```
[nfs]
volume_driver = cinder.volume.drivers.nfs.NfsDriver
nfs_shares_config = /etc/cinder/nfs_shares
nfs_mount_point_base = /var/lib/nova/mnt
volume_backend_name = nfs
```

华为存储
```
[V3_FC]
volume_driver = cinder.volume.drivers.huawei.huawei_driver.HuaweiFCDriver
cinder_huawei_conf_file = /etc/cinder/cinder_huawei_conf.xml
volume_backend_name = V3_FC
```

配置: /etc/cinder/cinder_huawei_conf.xml
```
<?xml version='1.0' encoding='UTF-8'?>
<config>

<Storage>
<Product>V3</Product>
<Protocol>iSCSI</Protocol>
<RestURL>https://10.100.3.168:8088/deviceManager/rest/</RestURL>
<UserName>!$$$aHdjbG91ZA==</UserName>
<UserPassword>!$$$SHVhd2VpQDIwMjA=</UserPassword>
</Storage>

<LUN>
<LUNType>Thick</LUNType>
<WriteType>1</WriteType>
<LUNcopyWaitInterval>5</LUNcopyWaitInterval>
<Timeout>432000</Timeout>
<StoragePool>yf2pool</StoragePool>
</LUN>

<iSCSI>
<DefaultTargetIP>10.100.3.202</DefaultTargetIP>
</iSCSI>

</config>
```

## FAQ

#### cinder service-list没有后端

配置已经配置了cinder mmj后端
原来是没有安装驱动

```
cinder-volume[108725]: ERROR cinder.cmd.volume [None req-9ea1980e-5ed9-4a87-b337-2fd5ce11610f None None] Volume service kolla2@mmj2 failed to start.: AttributeError: module 'cinder.utils' has no attribute 'trace'
```

#### 删除卷类型: 500错误: default volume type lvmdriver-1 cannot be found

```
DEBUG cinder.api.openstack.wsgi [req-1dce2697-79e1-45ba-a1d3-a1dc31f404f6 admin db135c4b5391422da5a55c81dfbf803d - - -] Calling method '_delete' _process_stack /usr/lib/python2.7/site-packages/cinder/api/openstack/wsgi.py:879
ERROR cinder.volume.volume_types [req-1dce2697-79e1-45ba-a1d3-a1dc31f404f6 admin db135c4b5391422da5a55c81dfbf803d - - -] Default volume type is not found. Please check default_volume_type config:: VolumeTypeNotFoundByName: Volume type with name lvmdriver-1 could not be found.
ERROR cinder.volume.volume_types Traceback (most recent call last):
ERROR cinder.volume.volume_types   File "/usr/lib/python2.7/site-packages/cinder/volume/volume_types.py", line 199, in get_default_volume_type
ERROR cinder.volume.volume_types     vol_type = get_volume_type_by_name(ctxt, name)
ERROR cinder.volume.volume_types   File "/usr/lib/python2.7/site-packages/cinder/volume/volume_types.py", line 186, in get_volume_type_by_name
ERROR cinder.volume.volume_types     return db.volume_type_get_by_name(context, name)
ERROR cinder.volume.volume_types   File "/usr/lib/python2.7/site-packages/cinder/db/api.py", line 656, in volume_type_get_by_name
ERROR cinder.volume.volume_types     return IMPL.volume_type_get_by_name(context, name)
ERROR cinder.volume.volume_types   File "/usr/lib/python2.7/site-packages/cinder/db/sqlalchemy/api.py", line 189, in wrapper
ERROR cinder.volume.volume_types     return f(*args, **kwargs)
ERROR cinder.volume.volume_types   File "/usr/lib/python2.7/site-packages/cinder/db/sqlalchemy/api.py", line 3990, in volume_type_get_by_name
ERROR cinder.volume.volume_types     return _volume_type_get_by_name(context, name)
ERROR cinder.volume.volume_types   File "/usr/lib/python2.7/site-packages/cinder/db/sqlalchemy/api.py", line 189, in wrapper
ERROR cinder.volume.volume_types     return f(*args, **kwargs)
ERROR cinder.volume.volume_types   File "/usr/lib/python2.7/site-packages/cinder/db/sqlalchemy/api.py", line 3968, in _volume_type_get_by_name
ERROR cinder.volume.volume_types     raise exception.VolumeTypeNotFoundByName(volume_type_name=name)
ERROR cinder.volume.volume_types VolumeTypeNotFoundByName: Volume type with name lvmdriver-1 could not be found.
ERROR cinder.volume.volume_types
INFO cinder.api.openstack.wsgi [req-1dce2697-79e1-45ba-a1d3-a1dc31f404f6 admin db135c4b5391422da5a55c81dfbf803d - - -] HTTP exception thrown: The request cannot be fulfilled as the default volume type lvmdriver-1 cannot be found.
```

#### FreeNASApiError: FREENAS api failed. Reason - TrueNAS not found:unknown

就是不支持python2.7, 代码问题没有体现在日志中

```
ERROR cinder.volume.drivers.ixsystems.common [req-9f31c3db-3a03-4dac-acdb-1716304dfc76 - - - - -] TrueNAS not found
ERROR oslo_service.service [req-9f31c3db-3a03-4dac-acdb-1716304dfc76 - - - - -] Error starting thread.: FreeNASApiError: FREENAS api failed. Reason - TrueNAS not found:unknown
ERROR oslo_service.service Traceback (most recent call last):
ERROR oslo_service.service   File "/usr/lib/python2.7/site-packages/oslo_service/service.py", line 810, in run_service
ERROR oslo_service.service     service.start()
ERROR oslo_service.service   File "/usr/lib/python2.7/site-packages/cinder/service.py", line 229, in start
ERROR oslo_service.service     service_id=Service.service_id)
ERROR oslo_service.service   File "/usr/lib/python2.7/site-packages/cinder/volume/manager.py", line 444, in init_host
ERROR oslo_service.service     self._init_host(added_to_cluster, **kwargs)
ERROR oslo_service.service   File "/usr/lib/python2.7/site-packages/cinder/volume/manager.py", line 478, in _init_host
ERROR oslo_service.service     self.driver.init_capabilities()
ERROR oslo_service.service   File "/usr/lib/python2.7/site-packages/cinder/volume/driver.py", line 760, in init_capabilities
ERROR oslo_service.service     stats = self.get_volume_stats(True)
ERROR oslo_service.service   File "/usr/lib/python2.7/site-packages/cinder/volume/drivers/ixsystems/iscsi.py", line 277, in get_volume_stats
ERROR oslo_service.service     self.stats = self.common._update_volume_stats()
ERROR oslo_service.service   File "/usr/lib/python2.7/site-packages/cinder/volume/drivers/ixsystems/common.py", line 474, in _update_volume_stats
ERROR oslo_service.service     raise FreeNASApiError('TrueNAS not found')
ERROR oslo_service.service FreeNASApiError: FREENAS api failed. Reason - TrueNAS not found:unknown
ERROR oslo_service.service
```

#### 创建卷: volume:create: No valid backend was found

更新truesnas driver代码，它支持的是python3
根据Python 2.x urlparse模块文档，
urlparse模块在Python 3中重命名为urllib.parse
所以模块在Python 2.7下你应该使用urlparse, `from urlparse import urlparse`
Python 2.7 imports parse like this:
`from urlparse import urlparse`
While Python 3 uses:
`from urllib.parse import urlparse`

cinder-scheduler日志
```
volume:create: No valid backend was found. No weighed backends available: NoValidBackend: No valid backend was found. No weighed backends available
```

查看cinder-volume的日志，发现有报错
=> 没有吧对应的volume backend 引入进来
```
2023-03-16 06:06:04.233 23728 INFO cinder.volume.manager [req-dd225df7-1a00-4674-8044-f4dfcd8a3cfc - - - - -] Service not found for updating active_backend_id, assuming default for driver init.
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume [req-dd225df7-1a00-4674-8044-f4dfcd8a3cfc - - - - -] Volume service localhost.localdomain@ixsystems-iscsi failed to start.: ImportError: No module named parse
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume Traceback (most recent call last):
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume   File "/usr/lib/python2.7/site-packages/cinder/cmd/volume.py", line 104, in _launch_service
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume     cluster=cluster)
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume   File "/usr/lib/python2.7/site-packages/cinder/service.py", line 400, in create
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume     cluster=cluster, **kwargs)
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume   File "/usr/lib/python2.7/site-packages/cinder/service.py", line 155, in __init__
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume     *args, **kwargs)
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume   File "/usr/lib/python2.7/site-packages/cinder/volume/manager.py", line 268, in __init__
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume     active_backend_id=curr_active_backend_id)
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume   File "/usr/lib/python2.7/site-packages/oslo_utils/importutils.py", line 44, in import_object
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume     return import_class(import_str)(*args, **kwargs)
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume   File "/usr/lib/python2.7/site-packages/oslo_utils/importutils.py", line 30, in import_class
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume     __import__(mod_str)
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume   File "/usr/lib/python2.7/site-packages/cinder/volume/drivers/ixsystems/iscsi.py", line 24, in <module>
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume     from cinder.volume.drivers.ixsystems import common
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume   File "/usr/lib/python2.7/site-packages/cinder/volume/drivers/ixsystems/common.py", line 18, in <module>
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume     import urllib.parse
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume ImportError: No module named parse
2023-03-16 06:06:04.236 23728 ERROR cinder.cmd.volume
```

其他python库问题
- ImportError: No module named error
  => 去除import, 没有用到
- ImportError: No module named request
  使用urllib2替换


#### 创建卷失败

最后发现没有卷类型，使用__DEFAULT__, 暂时测试一下
=> 原来是需要手动创建卷类型
```
./uniqb-cinder-cli.py create-volume-type
volume type vol-type-ksvd created.
```

发现是指定了不存在的卷类型? 
```
{"itemNotFound": {"message": "Volume type with name vol-type-ksvd could not be found.", "code": 404}}
```

使用curl获取所有卷类型
```
curl -v -H "X-Auth-Token: admin:db135c4b5391422da5a55c81dfbf803d" http://10.90.2.190:8776/v3/db135c4b5391422da5a55c81dfbf803d/types
对应openstack, cinder命令如下:
cinder volume type list?
```

## 旧的资料

#### 任务 #38444

[KSVD 预研项目2021][存储][预研实施]云产品和cinder对接的原型设计

一、去配keystone的依赖
因为auth_strategy在config.py中缺省值为keystone，需要在cinder.conf中添加：
[DEFAULT]
auth_strategy = noauth

2，curl调用中增加http头字段X-Auth-Token: admin:admin_project_id。

然后可使用cinder restful api做用户admin在project内的卷操作。

相关分析：
cinder api-paste.ini可以看到：

[composite:openstack_volume_api_v3]
use = call:cinder.api.middleware.auth:pipeline_factory
noauth = cors http_proxy_to_wsgi request_id faultwrap sizelimit osprofiler noauth apiv3
keystone = cors http_proxy_to_wsgi request_id faultwrap sizelimit osprofiler authtoken keystonecontext apiv3

pipeline_factory查看CONF.auth_strategy来选择不同的pipeline，noauth pipeline使用noauth filter，不走authtoken和keystonecontext。

NoAuthMiddleware.__call__()：

token = req.headers['X-Auth-Token']
user_id, _sep, project_id = token.partition(':')

说明:如果使用noauth，http头中X-Auth-Token字段仍然需要，且内容不再是从keystone获取的token，而是user_id:project_id的格式，
注意这里的user_id指如admin，而project_id是指如db135c4b5391422da5a55c81dfbf803d，而不是project的名字如admin（指admin用户的admin项目）。

参考：
官网https://docs.openstack.org/python-cinderclient/latest/user/no_auth.html给了client调用方式下的参数。
搜索帖子如“H版Openstack使用noauth方法”可以印证对处理逻辑的理解，但修改代码的方法是不必要的（也可能是老版本的原因）。
Quote Edit Delete #3
Updated by 卢刚 almost 2 years ago

    % Done changed from 20 to 60

二、mariadb更换为sqlite db

1, /etc/cinder/cinder.conf将[database]节内容更改为：
[database]
connection = sqlite:////opt/stack/data/cinder/cinder.sqlite

2，初始化数据库
cinder-manage --config-file /etc/cinder/cinder.conf db sync
之后会看到/opt/stack/data/cinder/目录下生成了cinder.sqlite数据库文件
sqlite3 /opt/stack/data/cinder/cinder.sqlite后，可以查看volume_types, volumes等表的内容

3，重新启动cinder服务，通过restful api访问cinder api，创建volume type为原devstack的volume type，然后进行创建volume、初始化连接等操作
查看sqlite db表相应内容，查看LVM卷建立和删除情况，查看targetcli输出。
Quote Edit Delete #4
Updated by 卢刚 almost 2 years ago

三、nova api去配

1，相关代码
功能代码：cinder/compute: __init__py, nova.py
              nova.py中通过生成nova client实例，对nova进行查询和通知
调用位置：cinder/volume/manager.py
涉及volume调用：migrate_volume(有attachments字段时）, extend_volume（当volume状态为in-use时）
                nova_api = compute.API()
                # This is an async call to Nova, which will call the completion
                # when it's done
                for attachment in attachments:
                    instance_uuid = attachment['instance_uuid']
                    nova_api.update_server_volume(ctxt, instance_uuid,

        if orig_volume_status == 'in-use':
            nova_api = compute.API()

2，场景分析
从源码实现来看，不调用migrate（或无attachments)和不设置volume状态为in-use时，可以不进行代码的修改。
为了重用volume的status字段，当使用in-use时，需要注意查清nova的调用逻辑，如果需要通知计算组件，需要重写通知代码。
为了重用attachments的通知，需要重写通知代码。
Quote Edit Delete #5
Updated by 卢刚 almost 2 years ago

四、glance api (image api)去配

1，相关代码
功能代码：cinder/image: accelerator.py (+gzip.py, qat.py), cache.py, glance.py, image_utils.py
              
调用位置主要在：
    1.1 以指定image初始化卷
    1.2 将卷复制为image

2，场景分析
    块存储对镜像服务的依赖主要涉及基于镜像的存储初始化。
Quote Edit Delete #6
Updated by 卢刚 almost 2 years ago

五、原型环境测试

1，安装两台干净系统VM1（node171)、VM2(node172)（干净是指未安装安装openstack环境），安装glusterfs双机环境，建两副本复制卷在两VM间共享，挂载至/home/kylin-ksvd。

2，安装cinder组件及其依赖，安装rabbitmq-server

3, vm2提供volume服务，建卷类型，修改cinder配置文件

4，使用cinder-manager创建共享sqlite db文件： /home/kylin-ksvd/cinder/cinder.sqlite

在vm1上启动cinder-api, cinder-scheduler, vm2上启动cinder-volume，此后cinder-volume, cinder-scheduler都有报错，都是涉及对db文件的IO错误， ERROR cinder.service DBNonExistentDatabase: (sqlite3.OperationalError) unable to open database file [SQL: u'UPDATE services SET updated_at=?, report_count=? WHERE services.deleted = 0 AND services.id = ?'] [parameters: ('2021-06-03 11:23:30.655343', 13666, 2)] (Background on this error at: http://sqlalche.me/e/e3q8)
查看 http://sqlalche.me/e/e3q8，alchemy表示这是sqlite驱动的错：This error is a DBAPI Error and originates from the database driver (DBAPI), not SQLAlchemy itself.

在两台机器上配置etcd服务后，仍有报错。在继续在vm2上安装memcached后，长时间运行，未见报错。

问题在于：memcached与sqlite db文件并发访问冲突报错之间的关系，需查清该使用sqlite db取代mariadb在多节点并发访问场景下的可行性。                 
Quote Edit Delete #7
Updated by 卢刚 almost 2 years ago

    % Done changed from 60 to 90

近日继续跟踪调试cinder-scheduler，仍未找到memcached对sqlite db共享访问的影响。

目前查到的情况如下：
1，异常发生在cinder-scheduler, cinder-volume报告服务状态，因其都要更新数据库表中服务状态，而sqlite db对并发写有限制，同一时刻仅允许一个写，当写操作同时发生时，“可能”发生异常；
2，考虑到并发写操作的持续时间很短，cinder的数据库更新操作中，使用了retry=5的装饰器来缓解写冲突操作，装饰器中判如果是db更新操作异常则重试；
3，测试环境中sqlite db文件在glusterfs，从日志上看是在写操作时cinder.sqlite-journal文件的stale file handle，该文件是对sqlite db文件的更新和事务日志文件；
4，文件io错误引发的异常不在retry装饰器的异常监控范围，所以引发该异常的操作没有被重试，会导致该写操作丢失。
5，单就service的状态报告而言，偶尔的丢失关系不大，但是如果是卷相关的数据更新，则问题严重。

拟继续：
1，glusterfs stale file handle的原因（初判与缓存一致性、open-behind、write-behind等特征相关）
2，将该异常加入retry装饰器的重试异常列表
3，继续查为什么打开memcached后sqlite db并发访问异常就没有发生了。
Quote Edit Delete #8
Updated by 卢刚 almost 2 years ago

    % Done changed from 90 to 100

近期工作：

1，加大服务更新频率，对sqlite db文件放在glusterfs存储情况，在glusterfs侧，进行配置逐项修改与测试，仍有并发访问问题；
     a: 将服务状态更新则10s->1s，加入sqlite db的访问压力     

     /usr/lib/python2.7/site-packages/cinder/service.py：
     61 service_opts = [
     62     cfg.IntOpt('report_interval',
     63                default=10,
     64                # default=1,
     65                help='Interval, in seconds, between nodes reporting state '
     66                     'to datastore'),

     b:逐项修改glusterfs的xlator性能开发和挂载开关后测试：

性能开关：open-behind=off, write-behind=off、open-behind=off, write-behind=on

挂载参数：  mount -o entry-timeout=0,attribute-timeout=0

2，cinder相关代码中将sqlite3 stale file handle引发的异常加入retry列表，能解决服务状态更新的并发访问问题；

/usr/lib/python2.7/site-packages/oslo_db/sqlalchemy/exc_filters.py
    297 @filters("mysql", sqla_exc.InternalError,
    298          r".*1049,.*Unknown database '(?P<database>.+)'\"")
    299 @filters("mysql", sqla_exc.OperationalError,
    300          r".*1049,.*Unknown database '(?P<database>.+)'\"")
    301 @filters("postgresql", sqla_exc.OperationalError,
    302          r".*database \"(?P<database>.+)\" does not exist")
    303 @filters("sqlite", sqla_exc.OperationalError,
    304          ".*unable to open database file.*")
    305 @filters("sqlite", sqla_exc.OperationalError,
    306          ".*disk I/O error.*")
    307 def _check_database_non_existing(
    308         error, match, engine_name, is_disconnect):
    309     try:
    310         database = match.group("database")
    311     except IndexError:
    312         database = None
    313
    314     raise exception.DBNonExistentDatabase(database, error)

/usr/lib/python2.7/site-packages/oslo_db/api.py
    182     def _is_exception_expected(self, exc):
    183         if isinstance(exc, self.db_error):
    184             # RetryRequest is application-initated exception
    185             # and not an error condition in case retries are
    186             # not exceeded
    187             if not isinstance(exc, exception.RetryRequest):
    188                 LOG.debug('DB error: %s', exc)
    189             return True
    190         if isinstance(exc, exception.DBNonExistentDatabase):
    191             LOG.debug('KSVD-cinder capture the error: %s', exc)
    192             return True

3，批量测试lvm后端的卷创建与删除，测试结果和代码跟踪表明引发sqlite db文件并发访问问题的访问点过多，修改不太可行；

4，将cinder-api, scheduler, volume服务放回同一个vm，测试sqlite db在gluterfs存储，并发访问问题仍然存在；

5，将cinder-api, scheduler, volume服务放回同一个vm，测试sqlite db也移回本地存储，并发访问仍然低概率发生，可在测试代码的应用层做重试解决；

6，将sqlite-db改为在另一台vm上运行的mariadb服务，批量测试和状态更新的压力测试下没有发现问题。

7，在加大服务更新频率（加大sqlite db并发访问压力）下，重测memcached是否能解决并发访问问题。
     测试结果是也有并发访问问题。
     之前测试怀疑memcached与sqlite  db文件并发访问报错之间有关联，现基本排除关联，原因在于：
     a,从目前的代码排查和调试跟踪未看到与memcached的关联，也未能搜索到直接的资料说明；
     b，当时的初步测试没有加大sqlitedb的访问压力，默认情况下cinder-scheduler, cinder-volume的服务状态更新都是10s每次，可能正好是memcached运行后scheduler、volume所在的两台vm的服务状态更新进入了一个比较同步的状态，导致两次整晚的测试都没有发生并发访问。

8，基于修改、测试和代码分析，开始编写原型设计文档


#### 评审 #40401

评审的主要点：

1、说明并演示下原型，熟悉下目前的预研状态下，支持的功能点。
2、讨论产品化的方向，并且根据产品化方向的要求，是否还存在需要继续预研的技术点
3、讨论是否进入产品化方案设计，由产品化实施负责人主导产品化方案设计，UI原型，前后端人员等

- 1. 与我们的产品结合的话，各vm中的组件应该都是运行在我们的host节点吧？各个组件在各个host节点上的分布应该是怎样的？

分两种情况：1，由某个存储节点提供本地存储，则要求该节点上要启动1个volume服务，各组件的分布没有要求，只要网络可达。
            2，由单独的盘阵设备提供存储，则只要求存储与各服务之间网络可达。
目前可考虑把cinder-api/scheduler/volume运行在MC上，重用已有的rabbitmq和mariadb，如果有多个volume访问同一个存储，还需要加入etcd。

- 2. 是否需要考虑高可用方面的设计？

服务的高可用可与KSVD自身的高可用一起考虑。用户业务数据的高可用由盘阵自身保障。

- 3. 该设计当前是否还不考虑多虚拟机访问同一块卷设计的情况？还是说cinder已经对此做好了处理？

没有测试过这个特性。据资料查找cinder支持该特性，也可能会与具体盘阵提供的驱动程序有依赖关系。

- 4. 从设计文档上来看，大多为配置过程，只有一个uniqb-clinder-cli为需要研发，其它cinder可不用代码修改，可否这么理解？

就基本的volume创建、分配、使用、删除而言，只需要配置。uniqb-clinder-cli只是如何使用和验证的原型程序。
但是，如果涉及到img与卷之间的互拷贝、正在in-use状态卷的扩容、卷的backup等功能（没有做详尽测试），需要单独设计和修改cinder中相关代码。

- 5. 深信服有引入cinder么？使用的是什么技术方案？

之前好像是听到有同事说有引入，但是我曾经登入部门sxf对比环境搜索，没有找到相关内容或证据。

 
- 看了下针对产品化的工作还要出一个详细的产品设计，需要和业务逻辑关联起来，明确下目标和功能需求，这个讨论的时候可以考虑下。

是的，MC上除了必要操作添加cinder服务、添加存储设备（也可以只在配置文件中手工配好）外，每个具体业务的需求都要与cinder-api相应接口对上，然后看是不是可以直接用或者需要修改。

- 评审结论为工作表明了cinder服务单独重用的技术路线可行性。下一步以业务需求侧为主（调用cinder的业务逻辑与界面），cinder侧做配合修改和适配。
