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
