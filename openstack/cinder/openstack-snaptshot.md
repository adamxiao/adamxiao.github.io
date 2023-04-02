# openstack 快照

- 实例快照
- 卷快照

问题:

- 做实例快照时，虚拟机是否暂停了?
  => 理论应该暂停了?
  => 使用virsh list查看, 没有暂停

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
