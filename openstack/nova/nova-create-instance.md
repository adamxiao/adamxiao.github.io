# nova创建实例

关键字《nova创建虚拟机源码分析》

#### 创建虚拟机流程

[openstack nova源码分析--compute创建虚拟机（1）](https://blog.csdn.net/ksj367043706/article/details/89287020)

在OpenStack nova创建虚拟机过程中，nova-api收到虚拟机创建请求，然后nova-scheduler完成选择合适计算节点的任务，nova-conductor则开始调用build_instance()来创建虚机。

在conductor.manager.ComputeTaskManager.build_instance()中，通过rpc调用：self.compute_rpcapi.build_and_run_instance()，来调用compute节点上的build_and_run_instance()方法。而build_and_run_instance()方法就完成VM在计算节点上的创建和启动任务。

nova/compute/manager.py: build_and_run_instance

nova/compute/manager.py: ComputeManager: _build_resources
创建块设备映射的代码在这里吧?
```
            block_device_info = self._prep_block_device(context, instance,
                    block_device_mapping)
            resources['block_device_info'] = block_device_info
```

[(好)云硬盘启动与镜像启动源码分析及差异](https://www.aboutyun.com/thread-20390-1-1.html)
先使用cinder创建云硬盘，然后在nova中创建示例的时候，会先在_prep_block_device中挂载cinder中创建的卷，然后创建虚拟机
镜像启动: nova还有一种启动方式：“从镜像启动（创建一个新卷）”
这个流程中，nova会在_prep_block_device中的attach_block_device去调用cinder的create创建一个卷
然后会在_prep_block_device中的attach_block_device去调用cinder的attach挂载这个卷
然后才去spawn，孵化虚拟机，在spawn中会调用_create_image来创建镜像，这里创建镜像不是创建卷，卷是在_prep_block_device创建好的，除非是“从镜像启动”才会在

这个代码里面在等待卷存储创建，看是否成功, 有超时时间, 默认sleep 120*3s!
```
_await_block_device_map_created
        start = time.time()
        retries = CONF.block_device_allocate_retries
        # (1) if the configured value is 0, one attempt should be made
        # (2) if the configured value is > 0, then the total number attempts
        #      is (retries + 1)
        attempts = 1
        if retries >= 1:
            attempts = retries + 1
        for attempt in range(1, attempts + 1):
            volume = self.volume_api.get(context, vol_id)
            volume_status = volume['status']
            if volume_status not in ['creating', 'downloading']:
                if volume_status == 'available':
                    return attempt
                LOG.warning("Volume id: %(vol_id)s finished being "
                            "created but its status is %(vol_status)s.",
                            {'vol_id': vol_id,
                             'vol_status': volume_status})
                break
            greenthread.sleep(CONF.block_device_allocate_retries_interval)
```

#### 开启虚拟机流程

xxx

[openstack创建虚拟机源码阅读](https://segmentfault.com/a/1190000015371691)
nova模块结构: xxx
创建虚拟机流程: xxx

[零基础学习openstack【完整中级篇】及openstack资源汇总](https://www.vinchin.com/blog/vinchin-technique-share-details.html?id=21903)
=> 后续学习

[OpenStack建立实例完整过程源码详细分析（10）](https://blog.csdn.net/gaoxingnengjisuan/article/details/10907313)

[openstack创建虚拟机源码分析三（Glance下载镜像）](https://blog.csdn.net/qq_33909098/article/details/104414587)
3.后端存储（支持很多种，用那种用户自己选），用来真正存放镜像本体的backend。因为glance 自己并不存储镜像。

下面这些是glance 支持的许多种后端存储的一些，比如：
- A directory on a local file system：这是默认配置，在本地的文件系统里进行保存镜像。
- GridFS：使用MongoDB存储镜像。
- Ceph RBD：使用Ceph的RBD接口存储到Ceph集群中。
- Amazon S3：亚马逊的S3。
- Sheepdog：专为QEMU/KVM提供的一个分布式存储系统。
- OpenStack Block Storage (Cinder)
- OpenStack Object Storage (Swift)
- HTTP：可以使用英特网上的http服务获取镜像。这种方式只能只读。
- VMware ESX/ESXi or vCenter。
