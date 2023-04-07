# openstack 快照

- 实例快照
- 卷快照

问题:

- 做实例快照时，虚拟机是否暂停了?
  => 理论应该暂停了?
  => 使用virsh list查看, 没有暂停
  => **源码分析,以及实际打开libvirt调试日志查看, 没有暂停!!!** 但是可能会冻结文件系统!

http://people.csail.mit.edu/jon/openstack-ops/content/snapshots.html
However, an instance snapshot is an image.

## 实例快照

- 生成一个镜像
- 实例每一个卷都生成一个快照

关键字《openstack instance snapshot》

关键字《openstack instance snapshot vs volume snapshot》

[Use snapshots to migrate instances](https://docs.openstack.org/nova/rocky/admin/migrate-instance-with-snapshot.html)
https://docs.openstack.org/nova/yoga/admin/migrate-instance-with-snapshot.html

就是用这个命令创建快照, 查一下原理
```
openstack server image create --name snap-inst1 cirros
```


这就是一个多卷实例快照
```
openstack image  list
openstack image show xxx
| properties       | base_image_ref='', bdm_v2='True', block_device_mapping='[{"guest_format": null, "tag": null, "volume_type": null, "boot_index": 0, "snapshot_id": "f0e9906d-b598-4468-8922-a65ef71d2452", "disk_bus": "virtio", "delete_on_termination": false, "no_device": null, "device_type": "disk", "source_type": "snapshot", "volume_id": null, "image_id": null, "destination_type": "volume", "device_name": "/dev/vda", "volume_size": 1}, {"guest_format": null, "tag": null, "volume_type": null, "boot_index": null, "snapshot_id": "f88a72d0-b133-4c12-ba10-1bcdf4c87104", "disk_bus": null, "delete_on_termination": false, "no_device": null, "device_type": null, "source_type": "snapshot", "volume_id": null, "image_id": null, "destination_type": "volume", "device_name": "/dev/vdb", "volume_size": 2}]', boot_roles='reader,heat_stack_owner,member,admin', hw_cdrom_bus='ide', hw_disk_bus='virtio', hw_input_bus='usb', hw_machine_type='pc', hw_pointer_model='usbtablet', hw_video_model='virtio', hw_vif_model='virtio', os_hash_algo='sha512', os_hash_value='cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e', os_hidden='False', os_type='linux', owner_project_name='admin', owner_specified.openstack.md5='', owner_specified.openstack.object='images/cirros', owner_specified.openstack.sha256='', owner_user_name='admin', root_device_name='/dev/vda', signature_verified='False', stores='file' |
```

[(好)Create and use OpenStack snapshots](https://blog.ovhcloud.com/create-and-use-openstack-snapshots/)

简单来说, 快照就是有如下属性的镜像:
- image_type: snapshot
- instance_uuid: <uuid of instance that was used for the snapshot>
- base_image_ref: <uuid of original image of instance that was used for snapshot>
- image_location: snapshot

可以使用命令行，或者web页面来创建快照

在线快照，以及数据一致性:

在线快照是只有磁盘数据的, 可能会出现数据不一致性(guest系统没有感知到快照时)
```
This phenomenon occurs when a hypervisor freezes the instance to allow the creation of a “delta” file before resuming the execution of the instance. This is done to prevent the instance writing directly to its disk while it is copied. When the copy is done, the instance is frozen again to allow the “delta” to be merged with the instance’s disk, and the execution is then resumed with the disk fully merged.

Inconsistencies can appear on the first freeze if the instance is not aware that the hypervisor is taking a snapshot, because the applications and the kernel running on the instance are not told to flush their buffers.
```

确保数据一致性, 配置通知qga进行冻结文件系统:
```
openstack image set --property hw_qemu_guest_agent=yes <image name or uuid>
```

#### 创建快照

同时创建多个卷的快照?
```
2023-03-29 05:55:13.519 24 INFO cinder.volume.manager [req-21ec55dd-5562-468f-a045-4cd6ca8e3c76 a541aaefa5844596a7288c30d8a10367 4ec1a6d159c340c4bb3ba7a7f0f8255c - - -] Create snapshot completed successfully
2023-03-29 05:55:13.648 24 INFO cinder.volume.manager [req-7dbd18b6-5fb1-4728-a342-edd5488f0dfd a541aaefa5844596a7288c30d8a10367 4ec1a6d159c340c4bb3ba7a7f0f8255c - - -] Create snapshot completed successfully
2023-03-29 05:55:13.745 24 INFO cinder.volume.manager [req-8a3c83c7-5d24-41a2-bd30-b74ee8279bd9 a541aaefa5844596a7288c30d8a10367 4ec1a6d159c340c4bb3ba7a7f0f8255c - - -] Create snapshot completed successf
ully
```

#### 自动定时快照

关键字《openstack automatic snapshot》

https://stackoverflow.com/questions/70188055/how-to-schedule-snapshot-of-openstack-instance
Furthermore, Freezer has a mechanism for scheduling periodic backups. See the [Freezer: Agent User Guide](https://docs.openstack.org/freezer/latest/user/freezer-agent.html).

- Nova不支持定期备份
- Horizon面板也不支持定期任务
- If you set up Freezer, you should be able to use it to create a backup job to do a periodic instance snapshot.
- You can do other sorts of backup as will ... which might be more appropriate than instance snapshots.
- There is a Horizon plugin for Freezer.

可以使用cron或者python脚本做定期任务
https://opendev.org/openstack/ => 有官方的freezer?
OpenStack Swift incremental backup and restore automation tool for file system, MongoDB, MySQL. LVM snapshot and encryption support.


[(好)OpenStack Data Protection As Service("Raksha")](https://wiki.openstack.org/wiki/Raksha)
本质就是数据保护, 而且这个是openstack官方文档?


https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.1/html-single/block_storage_backup_guide/index

You can use Red Hat Ceph and NFS as alternative back ends for backups.


https://github.com/houtknots/Openstack-Automatic-Snapshot
写个脚本定时做实例快照和卷快照..


[你真的会 Snapshot 吗？ – 每天5分钟玩转 OpenStack（163）](https://www.xjimmy.com/openstack-5min-163.html)
https://developer.aliyun.com/article/463333
如果在生产系统中执行 snapshot 操作，必须确保此操作快速且安全。
- 1.快速
    为保证数据的一致性，snapshot 时需要 pause instance，操作完后再 resume。
    在这个过程中 instance 是无法对外服务的，为了减少对业务的影响，我们希望 snapshot 越快越好。

- 2.安全
    即数据一致性，snapshot 出来的 image 不能有没落盘的数据，能够正常启动。
    所以通常在执行 snapshot 前要 pause instance，暂停所有的 IO 操作。

  真正的解决方案  
默认 snapshot 的问题在于 qemu-img convert 耗时太长，而耗时太长的原因是 instance 的系统盘是文件，拷贝文件本身就是一个耗时的操作。真正的解决方案是：

让 instance 从 cinder volume 启动，利用 storage provider 自己的 snapshot 技术实现快速复制。

#### nova live snapshot源码分析

根据snapshot关键字，搜索到nova yoga的源码位置，大概是 nova/virt/hyperv/snapshotops.py
可能是这个: nova/virt/libvirt/driver.py: snapshot
  发现在线实例快照是可能pause实例的: _suspend_guest_for_snapshot

关键字《nova实例快照源码》

https://blog.csdn.net/qq_33909098/article/details/103892361
=> 确实是调用相关代码进行实例快照的

可能是让其他进程处理的???。。。
=> 但是打开libvirt调试日志，没有发现suspend日志???
=> live_snapshot=True, 则不需要暂停vm
```
        self._suspend_guest_for_snapshot(
            context, live_snapshot, original_power_state, instance)

        root_disk = self.image_backend.by_libvirt_path(
            instance, disk_path, image_type=source_type)

        if live_snapshot:
            LOG.info("Beginning live snapshot process", instance=instance)
        else:
            LOG.info("Beginning cold snapshot process", instance=instance)

        update_task_state(task_state=task_states.IMAGE_PENDING_UPLOAD)

        update_task_state(task_state=task_states.IMAGE_UPLOADING,
                          expected_state=task_states.IMAGE_PENDING_UPLOAD)
```


https://www.cnblogs.com/qianyeliange/p/9713022.html
可以发现在做live_snapshot的时候，会调用“abort_job()”来停止系统盘上的所有任务，即就是调用“_guest._domain.blockJobAbort(self._disk, flags=flags)”。
在线快照源码就分析到这里，与离线快照最大的区别就是：在线快照不会挂起实例；相同点是：都需要先在本地生成临时快照文件，再上传到glance。

检查一下做快照前，有没有冻结文件系统? => 有相关日志，但是没有配置qga支持，没有做
```
    def quiesce(self, context, instance, image_meta):
        """Freeze the guest filesystems to prepare for snapshot.

        The qemu-guest-agent must be setup to execute fsfreeze.
        """
        self._set_quiesced(context, instance, image_meta, True)
```

发现有quiesce日志
```
Apr 03 07:04:39 ubuntu devstack@n-api.service[319269]: INFO nova.compute.api [None req-3343156f-d036-47a9-b235-91af613fcd01 admin admin] [instance: 73335d60-6d7c-4e92-b35f-045195a3a88b] Attempting to quiesce instance before volume snapshot.

=> 但是系统不支持的话，那也不会处理
2023-04-03 06:41:00.701 20 INFO nova.compute.api [req-14be6717-8669-4af0-9b65-4fc175658b53 - - - - -] [instance: 148ee060-366a-4923-9ac9-bdfe65c1f0e1] Skipping quiescing instance: QEMU guest agent is not enabled.
```


[OpenStack Nova源码结构解析](https://www.aboutyun.com/thread-10105-1-1.html)
列举了源码中的文件作用..
问题导读
- 1.处理虚拟机磁盘镜像由哪个文件来完成？
- 2.调度器中的主机权重在哪个文件中？
- 3./nova/scheduler/host_manager.py文件的作用是什么？


[(好)Openstack liberty 创建实例快照源码分析1](https://blog.csdn.net/lzw06061139/article/details/51720653)
Openstack支持对处于运行或者停止状态的云主机执行快照，另外Openstack既可以从镜像启动云主机，也可以从启动磁盘启动云主机，根据条件组合，可以执行下面4中快照：

还有这么多种情况?
- 镜像启动云主机的离线快照
- 镜像启动云主机的在线快照
- 磁盘启动云主机的离线快照
- 磁盘启动云主机的在线快照

镜像启动云主机的快照, 分析:

nova-api部分:
- nova/api/openstack/compute/servers.py: ServersController: _action_create_image
  根据nova-api启动时设置的路由，我们可以很容易的知道快照函数入口
- nova/compute/api.py: API: snapshot
  接上文(非卷存储才走这个分支)
- nova/compute/api.py: API: snapshot_volume_backed
  **卷存储走这个分支!!!**
- nova/compute/api.py: API: snapshot_instance
  snapshot_volume_backed接口中定义了，然后再调用的

nova-compute部分:
- nova/compute/manager.py: ComputeManager: snapshot_instance
  收到nova-api发来的’snapshot_instance’快照请求后，nova-compute调用
  => kolla我改了源码，加了调试日志，居然没有输出 => 原来是根本没有走这条分支, 从servers.py就走其他分支了!!!
  => 使用devstack验证也没有???
- _snapshot_instance
  接上文
- nova/virt/libvirt/driver.py: LibvirtDriver: snapshot
  接上文

在线快照源码就分析到这里，与离线快照最大的区别就是：在线快照不会挂起实例；相同点是：都需要先在本地生成临时快照文件，再上传到glance。

http://pythontime.iswbm.com/en/latest/c08/c08_05.html#id3
基本同上, 看没有额外资料

询问chatgpt:
openstack实例快照源码分析, 对应具体的源码路径呢？

- Nova API代码路径：nova/compute/api.py
- Nova Compute Manager代码路径：nova/compute/manager.py
- Hypervisor代码路径：nova/virt/
- Glance镜像服务代码路径：glance/
- Cinder块存储服务代码路径：cinder/

关键字: 《snapshot_volume_backed源码分析》
[(好)Openstack liberty 创建实例快照源码分析2](https://blog.csdn.net/lzw06061139/article/details/51754024)

#### nova开启调试日志

[OpenStack 调试](https://gtcsq.readthedocs.io/en/latest/openstack/openstack_debug.html)
加上--debug参数

https://www.cnblogs.com/potato-chip/p/10196503.html
修改nova.conf
debug = True
=> 明显这个更合理

#### openstack 内存快照

问题:
- 内存存到哪里?
  之前qcow2磁盘, 内存存储到系统盘中?
  是可以指定存储到某个地方的!

- 内存快照时，必定暂停虚拟机
  使用virsh list查看虚拟机状态为: paused
  057422a8-c688-3aa3-2a96-d72b72618bca paused
 
系统盘大小和额外盘大小
```
57671694 -rw-r--r-- 1 kylin-ksvd kylin-ksvd 34G Apr  6 11:06 /home/kylin-data/ssd113/ksvd-orgs/org-0/users/0local/mcadmin1/057422a8-c688-3aa3-2a96-d72b72618bca/GUEST.IMG
57671698 -rw-r--r-- 1 kylin-ksvd kylin-ksvd 41M Apr  6 11:05 /home/kylin-data/ssd113/ksvd-orgs/org-0/users/0local/mcadmin1/057422a8-c688-3aa3-2a96-d72b72618bca/DISK11303.IMG
```

https://www.prnasia.com/story/372594-1.shtml
OpenStack高级虚拟化特性之内存快照技术解析

最后，实现云硬盘快照与内存快照数据一致的"真"云主机快照。浪潮云海OS团队通过深度优化相关虚拟化组件，解决了云主机内存和存储后端磁盘数据在不同维度上的数据一致性问题，降低内存快照创建过程对业务的影响，保证云主机在快照之后业务不停机，优化后的内存快照创建效率较原Libvirt内存快照流程提升40%以上。同时解决原生快照恢复过程中由于设备信息部分丢失导致光盘无法挂载的问题。

[Openstack云主机实现快照分析](https://veinfu.github.io/%E6%8A%80%E6%9C%AF%E5%8D%9A%E5%AE%A2/2019/04/15/Openstack%E4%BA%91%E4%B8%BB%E6%9C%BA%E5%BF%AB%E7%85%A7%E5%AE%9E%E7%8E%B0%E5%88%86%E6%9E%90/)

```
# 创建内存快照，会保存至一个文件
virsh save fuel-9.0-vienfu_slave-07 slave07-mem.sanpshot
```

https://www.cnblogs.com/luohaixian/p/9344803.html
可以使用 “--memspec” 和 “--diskspec” 参数来给内存和磁盘外部快照。这时候，在获取内存状态之前需要 Pause 虚机，就会产生服务的 downtime。

openstack 快照分析
https://www.vinchin.com/blog/vinchin-technique-share-details.html?id=8111

1.  snapshot overview
对openstack而言，虚拟机的快照即是镜像，快照做完后以镜像形式存于glance。虽然openstack的快照是基于libvirt(qemu-kvm)，但是二者在实现上有很大区别：
libvirt 主流快照实现： 采用virDomainSnapshotCreateXML()函数(CLI为virsh snapshot-create)。 新建的快照与虚拟机有关联：若为内置快照，快照信息和虚拟机存在同一个qcow2镜像中；若为外置快照，新建一个qcow2文件，原虚拟机的disk将变为一个read only的模板镜像，新qcow2镜像仅记录与2.模板镜像的差异数据。这种快照包含快照链信息，可保留disk和ram信息，可回滚至快照点。

openstack快照实现：openstack并未采用virDomainSnapshotCreateXML()来实现快照，而是单纯的对虚拟机镜像做转换和拷贝，生成一个与虚拟机无关联的镜像，最后上传至glance中。这种快照不包含快照链信息，只保留disk信息，无法回滚至快照点，只能采用该快照镜像创建一个新的虚拟机。


2. cold snapshot and live snapshot
- cold snapshot:  创建snapshot时，需暂停虚拟机。
- live snapshot:   创建snapshot时，无需暂停虚拟机。

虚拟化 快照功能总结（libvirt，openstack）
1.内部快照不支持raw格式
（raw 启动的虚拟机会比QCOW2 启动的虚拟机I/O 效率更高一些(25%)
qcow2是一种当下比较主流的虚拟化磁盘格式，具有占用空间小，支持加密，支持压缩，支持快照的特点）

#### 其他资料

https://github.com/bohai/openstack-note/blob/master/QF_vm_snapshot.md
磁盘快照:
对磁盘数据进行快照。主要用于虚拟机备份等场合。

按快照信息保存为可以可以分为：
- 内置快照
  快照数据和base磁盘数据放在一个qcow2文件中。
- 外置快照
  快照数据单独的qcow2文件存放。

按虚拟机状态可以分为:
- 关机态快照
  数据可以保证一致性。
- 运行态快照
  数据无法保证一致性，类似与系统crash后的磁盘数据。使用时可能需要fsck等操作。

按磁盘数量可以分为
- 单盘
  单盘快照不涉及原子性。
- 多盘
  涉及原子性。主要分两个方面：1.是所有盘快照点相同 2.所有盘要么都快照成功，要么都快照失败。
  主要依赖于qemu的transaction实现。

- 运行态
可以利用qemu的snapshot_blkdev命令。（为了数据一致性，可以使用guest-fsfreeze-freeze和guest-fsfreeze-thaw进行文件系统的冻结解冻结操作）
多盘可以利用qemu的transaction实现atomic。

[openstack导出实例，制作镜像](https://juejin.cn/post/7097029220320641032)
就是创建实例快照，然后导出?


[OpenStack虚拟机快照功能分析](https://liujiong63.github.io/2018/07/03/OpenStack%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%BF%AB%E7%85%A7%E5%8A%9F%E8%83%BD%E5%88%86%E6%9E%90/)
目前，OpenStack虚拟机启动源支持镜像和卷，这两种方式创建出的虚拟机，快照过程
也不同。

由镜像启动的虚拟机做快照时，只对系统盘进行快照，不对数据盘进行快照，快照过程
中要挂起虚拟机，因此虚拟机中运行的业务可能会中断。快照完成后，将快照上传到
glance服务中，保存为snapshot类型的镜像，并恢复虚拟机状态。

附上一张卷后端虚拟机做快照的流程图
不同的卷后端，行为不一样? => 看代码没区别.

