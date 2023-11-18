# openstack cinder组件

openstack cinder组件，提供块存储管理

[cinder volume启动流程解析](https://blog.csdn.net/hedongho/article/details/80937746)

## 命令行使用

https://docs.openstack.org/cinder/rocky/cli/cli-manage-volumes.html

[redhat openstack 10文档](https://access.redhat.com/documentation/zh-tw/red_hat_openstack_platform/10/html/command-line_interface_reference_guide/openstackclient_commands)

卷后端状态
```
cinder service-list # 高版本不支持了
ERROR: Version 3.70 is not supported by the API. Minimum is 3.0 and maximum is 3.68. (HTTP 406) (Request-ID: req-79d6d663-699a-4c43-b64d-19a54cd3d254)
openstack volume service list
```

列举卷
```
openstack volume list
```

创建卷
```
openstack volume create --size 1 vol1
openstack volume create --size 1 --type mmj2 vol1
openstack volume create --image c0a27c4d-151f-484a-937c-dd35d4d3cefa \
  --type mmj2 --size 1 vol4
openstack volume create --image c0a27c4d-151f-484a-937c-dd35d4d3cefa \
  --type huawei --size 1 vol5
openstack volume create --image c0a27c4d-151f-484a-937c-dd35d4d3cefa \
  --size 8 --availability-zone nova my-new-volume
```

基于卷克隆卷
```
openstack volume create --source xxx vol-clone
```

基于卷快照克隆卷
```
openstack volume create --snapshot xxx vol-clone
```

删除卷
```
openstack volume delete my-new-volume
```

查看卷详情, 可以根据卷名
(如果多个卷名相同怎么办=>报错!)
```
openstack volume show vol4
```

列举卷类型
```
openstack volume type list
```

创建卷类型, 并指定backend
```
openstack volume type create --property volume_backend_name=huawei huawei
```

获取镜像列表
openstack image list

#### remove service

关键字《cinder remove service》

https://platform9.com/kb/openstack/deleting-a-cinder-service-from-host
```
docker exec cinder_api \
  cinder-manage service remove cinder-backup node1

cinder-manage service remove cinder-volume <UUID>@netapp_std1
openstack volume service list --service cinder-volume

docker exec cinder_api   cinder-manage service remove cinder-volume node1@mmj
```

#### 列举服务

```
[ssh_10.90.3.21] root@node1: ~$cinder service-list --binary cinder-volume --host node1
+---------------+------------+------+---------+-------+----------------------------+---------+-----------------+
| Binary        | Host       | Zone | Status  | State | Updated_at                 | Cluster | Disabled Reason |
+---------------+------------+------+---------+-------+----------------------------+---------+-----------------+
| cinder-volume | node1@mmj  | nova | enabled | up    | 2023-07-04T14:01:31.000000 | -       | -               |
| cinder-volume | node1@mmj2 | nova | enabled | up    | 2023-07-04T14:01:30.000000 | -       | -               |
+---------------+------------+------+---------+-------+----------------------------+---------+-----------------+
```

cinder list backend

#### cinder local-attach

安装cinder额外组件，扩展cinder命令
https://github.com/openstack/python-brick-cinderclient-ext.git

```
cinder local-attach {vol-id}
```

## cinder rest api

cinder官方api文档: https://docs.openstack.org/api-ref/block-storage/v3/index.html

环境如下:
```
export cinder_api_host=10.90.2.190
export project=db135c4b5391422da5a55c81dfbf803d
export token=admin:${project}
```

创建卷
```
curl -v -H "Content-Type: application/json" -H "X-Auth-Token: ${token}" \
  -X POST -d '{"volume": {"backup_id": null, "description": null, "availability_zone": null, "source_volid": null, "consistencygroup_id": null, "snapshot_id": null, "size": 10, "name": "vol1", "imageRef": null, "multiattach": null, "volume_type": "vol-type-ksvd", "metadata": {}}}' \
  http://${cinder_api_host}:8776/v3/${project}/volumes
```

列举卷类型
```
curl -H "X-Auth-Token: ${token}" -X GET \
  http://${cinder_api_host}:8776/v3/${project}/types
```

删除卷类型
```
export volume_type=53a325f7-727d-4a47-b4ef-3ab7e394603a
curl -H "X-Auth-Token: ${token}" -X DELETE \
  http://${cinder_api_host}:8776/v3/${project}/types/${volume_type}
```

获取卷详情
```
export volume_id=1117637e-d57e-40c3-a3b1-7f843ec9cd30
curl -H "X-Auth-Token: ${token}" -X GET \
  http://${cinder_api_host}:8776/v3/$project/volumes/$volume_id
```

删除卷
```
export volume_id=aa00b686-b23c-4751-86de-f6991be36995
./uniqb-cinder-cli.py delete -i $volume_id
./uniqb-cinder-cli.py delete -i $volume_id -n vol2
curl -H "X-Auth-Token: ${token}" -X DELETE \
  http://${cinder_api_host}:8776/v3/${project}/volumes/${volume_id}
```

获取cinder服务
```
curl -H "X-Auth-Token: ${token}" -X GET \
  http://${cinder_api_host}:8776/v3/${project}/os-services
```

## 卷挂载流程

```
./uniqb-cinder-cli.py init-connect
initialized faild
```

初始化连接失败?
```
[ssh_10.90.2.191] root@localhost: ~$./uniqb-cinder-cli.py init-connect -n vol1
Traceback (most recent call last):
  File "./uniqb-cinder-cli.py", line 596, in <module>
    main(arguments)
  File "./uniqb-cinder-cli.py", line 578, in main
    switch.get(args.action, default)(args)
  File "./uniqb-cinder-cli.py", line 346, in volume_init_connect
    CONF.set(volume_name, 'driver_volume_type', driver_volume_type)
  File "/usr/lib64/python2.7/ConfigParser.py", line 396, in set
    raise NoSectionError(section)
ConfigParser.NoSectionError: No section: 'vol'
```

对应rest接口是
```
/v3/{project}/volumes/{volume_id}/action
Initialize volume attachment

curl -v -H "Content-Type: application/json" -H "X-Auth-Token: ${token}" \
  -X POST -d '{"os-initialize_connection": {"connector": {"ip": "10.90.2.191", "host": "10.90.2.191", "multipath": false, "initiator": "iqn.1994-05.com.redhat:cb90d8e6e0a6"}}}' \
  http://${cinder_api_host}:8776/v3/${project}/volumes/${volume_id}/action
```

返回示例, 例如卷id不存在
```
HTTP/1.1 404 Not Found

{"itemNotFound": {"message": "Volume vol could not be found.", "code": 404}}
```

连接卷
```
./uniqb-cinder-cli.py connect -n vol1
```

断开连接
```
./uniqb-cinder-cli.py disconnect -n vol1
```

终止链接
```
./uniqb-cinder-cli.py term-connect -n vol1
```


## openstack cinder-volume 高可用

[OpenStack cinder-volume 的高可用（HA）](https://blog.51cto.com/u_15127625/2758231)

对cinder-volume做HA，第一个想到的就是负载均衡+keepalived来实现。经过验证这样的配置方式是可行的。不过我在测试过程中发现了一个有趣的问题：如果按照了cinder-volume的主机名一致那么，服务列表就只会显示一个cinder-volume服务。

但是AA HA模式目前还在开发中：

https://specs.openstack.org/openstack/cinder-specs/specs/mitaka/cinder-volume-active-active-support.html

[⑧ OpenStack高可用集群部署方案(train版)—Cinder](https://www.jianshu.com/p/62f0e1b066e4)
=> 不同的节点名，但是都配置ceph后端

openstack-nova-volume以active/passive模式运行
在采用ceph或其他商业/非商业后端存储时，建议将cinder-volume服务部署在控制节点，通过pacemaker将服务运行在active/passive模式。

[Cinder-Volume实现AA高可用:分布式锁及在Openstack上的应用](https://searchcloudcomputing.techtarget.com.cn/5-11364/)

我们知道OpenStack的大多数无状态服务都可以通过在不同的主机同时运行多个实例来保证高可用，即使其中一个服务挂了，只要还存在运行的实例就能保证整个服务是可用的，比如nova-api、nova-scheduler、nova-conductor等都是采用这种方式实现高可用，该方式还能实现服务的负载均衡，增加服务的并发请求能力。而极为不幸的是，由于Cinder使用的是本地锁，导致cinder-volume服务长期以来只能支持Active/Passive(主备)HA模式，而不支持Active/Active（AA，主主)多活，即对于同一个backend，只能同时起一个cinder-volume实例，不能跨主机运行多个实例，这显然存在严重的单点故障问题，该问题一直以来成为实现Cinder服务高可用的痛点。

总而言之，cinder-volume不支持Active/Active HA模式是Cinder的一个重大缺陷。

显然volume数据卷资源也需要处理并发访问的冲突问题，比如防止删除一个volume时，另一个线程正在基于该volume创建快照，或者同时有两个线程同时执行挂载操作等。cinder-volume也是使用锁机制实现资源的并发访问，volume的删除、挂载、卸载等操作都会对volume加锁。

cinder/volume/manager.py: delete_volume
```
    @clean_volume_locks
    @coordination.synchronized('{volume.id}-delete_volume')
    @objects.Volume.set_workers
    def delete_volume(self,
                      context: context.RequestContext,
                      volume: objects.volume.Volume,
                      unmanage_only=False,
                      cascade=False) -> Optional[bool]:
        """Deletes and unexports volume.

        1. Delete a volume(normal case)
           Delete a volume and update quotas.

        2. Delete a migration volume
           If deleting the volume in a migration, we want to skip
           quotas but we need database updates for the volume.

        3. Delete a temp volume for backup
           If deleting the temp volume for backup, we want to skip
           quotas but we need database updates for the volume.
      """
```

cinder/coordination.py
=> 这里有分布式锁的wrapper代码
其实只调用了tzoo的几个api
- coordinator.get_lock(lock_name)
- coordinator.remove_lock(glob_name)
- 还有start和stop

[(好)Tooz锁(Lock)](https://xiaomu-li.cn/2021/08/05/Openstack-Tooz/#%E9%94%81lock)

文件驱动则是
```
fasteners.InterProcessLock(path)
            gotten = self._lock.acquire(
                blocking=blocking,
                # Since the barrier waiting may have
                # taken a long time, we have to use
                # the leftover (and not the original).
                timeout=watch.leftover(return_none=True))
=> 看源码是使用fcntl.lockf
class _FcntlLock(_InterProcessLock):
    """Interprocess lock implementation that works on posix systems."""

    def trylock(self):
        fcntl.lockf(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def unlock(self):
        fcntl.lockf(self.lockfile, fcntl.LOCK_UN)
```

[tooz lock openstack官方文档](https://docs.openstack.org/tooz/latest/user/tutorial/lock.html)

https://docs.openstack.org/tooz/latest/reference/index.html#file
文件锁配置方法:
```
file://DIRECTORY[?timeout=TIMEOUT]
```

异常场景:
- 加锁前，共享存储异常
  没有问题，大不了加锁失败
- 加锁后, 共享存储异常
  也没有问题，其他程序无法获取锁
  => 就是最后自己无法解锁了
- 解锁中，共享存储异常
  => 无法解锁

唯一的缺点就是创建文件不能保证是原子操作!
=> 提前创建好文件，使用大锁? 至少是需要基于卷的锁...
=> 但是我们的上层其实也有锁，关系不是很大， 例如调用者也锁定了卷

[OpenStack 高可用和灾备解决方案完整操作手册](https://toutiao.io/posts/clheol/preview)


[3月技术周 | CINDER 架构分析、高可用部署与核心功能解析](https://www.99cloud.net/10758.html%EF%BC%8F)

CINDER 的高可用部署架构
- cinder-api + cinder-scheduler 都部署在 Controller，3 个 Controller 同时共享同一个 VIP 实现多活
- 一个存储设备可以对应多个 cinder-volume，结合 cinder-volume 分布式锁实现多活，分布式锁可以避免不同的 cinder-scheduler 同时调用到同一个 cinder-volume，从而避免多活部署的 cinder-volume 同时操作后端存储设备，简而言之就是避免并发操作带来（cinder-volume 与后端存储设备之间的）数据不一致性。锁是为了通过互斥访问来保证共享资源在并发环境中的数据一致性。分布式锁主要解决的是分布式资源访问冲突的问题，保证数据的一致性（Etcd、Zookeeper）。

## 参考资料

[Cinder 架构分析、高可用部署与核心功能解析](https://blog.51cto.com/u_15301988/3080852)
