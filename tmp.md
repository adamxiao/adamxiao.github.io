# 临时计划

#### lsof 使用

https://blog.csdn.net/carefree2005/article/details/113450562
https://www.cnblogs.com/my-show-time/p/15625662.html

恢复删除的文件
cat /proc/101595/fd/1 > /var/log/mysqld.log
查看文件是由哪些进程打开

深度好文｜TCP连接的状态详解以及故障排查 转载
https://blog.51cto.com/mingongge/5182870

#### tcpdump使用

https://www.cnblogs.com/ggjucheng/archive/2012/01/14/2322659.html
tcpdump -r /tmp/adam.pcap -n arp net 10.90.3.67

#### xfs相关

https://github.com/ianka/xfs_undelete
改造为xfs_erase_deleted

https://unix.stackexchange.com/questions/54973/what-filesystems-preferentially-reuse-blocks-from-deleted-files
xfs is stable and well established and has the characteristics I'm looking for — it reuses the 'just freed' blocks very quickly:

用zero填充少量空间，然后再使用qemu-img convert，确实可以所有磁盘空间

#### linux查看分区文件系统

https://cloud.tencent.com/developer/article/1721881
* df -T
* parted -l
* blkid
* lsblk -f 

#### 使用Next Terminal在浏览器中管理你的服务器

使用Next Terminal在浏览器中管理你的服务器
https://www.xiaoz.me/archives/15752

服务器不允许上网并且需要跳板机才能访问？学会使用这个工具，轻松让服务器使用yum。
https://typesafe.cn/posts/4dnat/

普通用户还是使用了guacc, 连接不上ssh
http://10.20.1.99:8088/#/access?assetId=325213cd-8e13-4435-9baf-9155fbc116da&assetName=arm-docker&protocol=ssh
http://10.20.1.99:8088/#/term?assetId=325213cd-8e13-4435-9baf-9155fbc116da&assetName=arm-docker

https://github.com/dushixiang/next-terminal

配置nginx反向代理报错
```
$ docker logs -f next-terminal_next-terminal_1
2022-10-23 16:37:14 ERROR [log.Errorf:114]升级为WebSocket协议失败：websocket: the client is not using the websocket protocol: 'upgrade' token not found in 'Connection' header
echo: http: superfluous response.WriteHeader call from github.com/labstack/echo/v4.(*Response).WriteHeader (response.go:63)
```

按照官方文档配置nginx反向代理, 参考官方文档： https://next-terminal.typesafe.cn/install/reverse-proxy.html
```
location / {
    proxy_pass http://127.0.0.1:8088/;
    proxy_set_header Host      $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $http_connection;
}
```

#### gitbook再优化

其实我想要的就是自己维护的web系统, 可以分享给其他人

[绝妙的个人生产力（Awesome Productivity 中文版）](https://github.com/eastlakeside/awesome-productivity-cn)

[计划使用hexo建立个人博客](https://zhouyifan.net/2021/09/21/20210916-git-note/)

[git教程](https://www.cnblogs.com/javahr/p/15488087.html)

[使用Github+Markdown搭键自己的笔记本](https://blog.csdn.net/ZM_Yang/article/details/105617607)

梳理出需求
* 免费（哈哈）；
* 能放到服务器：自己的电脑是靠不住的，只有本地有的孤本吃枣药丸；
* 支持Markdown：Markdown是一个可以用普通文本写出结构化文档的标记语言，目前有多种支持Markdown的编辑器，这就使得笔记的显示效果跨平台、跨应用。同样一份文档，不管拿到那里都基本能得到统一的显示效果。永远也不会忘记当初写论文在自己电脑上排版特别精美，一去打印一团乱麻的噩梦，所以统一的显示效果特别重要。
* 支持足够深的层级结构：方便归类，所有东西都放到一个文件夹里面的结果和什么都没有差不多；
* 有网页版，不需要下载客户端：自己家里电脑装的Ubuntu，公司Windows+Ubuntu,目前很多桌面软件对Linux支持不好；
* 支持笔记下载和上传：自己的笔记只能存在于某个平台上这是不能忍的；
* 支持保存非markdown内容：平时可能偶尔在网上找到一些认为比较好的PDF之类的资料，直接当参考资料，当然自己备份，网上的东西谁知道下一秒它的服务器还在不在；
* 支持批量上传下载（可选）：方便5、6点的批量操作，万一哪天哪个平台倒了，如果只能一个个操作不得累死。杞人忧天？也许吧；
* 支持VIM（可选）：解放鼠标的利器啊。

[使用 GitBook 在 Github 搭建个人网站](https://exp-blog.com/website/gitbook-da-jian-ge-ren-wang-zhan/)

个人网站建站, 非常繁琐的搭建过程和日常维护，来看一下你需要做什么：
* 申请域名、网站备案： 最快需要 1 个月
* 租用云服务器： 低配怕访问慢、高配怕财务困难
* 搭建 HTTP 服务： nginx、 apache
* 搭建数据库： MySQL、 MariaDB
* 搭建网站平台： wordpress、 Discuz!
* 网站平台模板/插件不好用： css、 js 各种魔改
* 安全加固： 后台被爆破、 前台被钓鱼
* 服务容灾： 进程挂起、 定期备份
* 访问加速： Redis缓存、 CDN
* 搜索引擎不收录： SEO、 提交链接

openshift-sdn日志
```
I0826 06:46:01.640187    2484 node.go:151] Initializing SDN node "worker1.kcp2-arm.iefcu.cn" (192.168.100.34) of type "redhat/openshift-ovs-networkpolicy"
I0826 06:46:01.711950    2484 cmd.go:159] Starting node networking (4.9.0-202201101708.p0.gecd60f9.assembly.stream-ecd60f9)
I0826 06:46:01.712282    2484 node.go:352] Starting openshift-sdn network plugin
```

启动参数待ip地址
root        7827    7794  0 Aug26 ?        00:46:03 /usr/bin/openshift-sdn-node --node-name master1.kcp2-arm.iefcu.cn --node-ip 192.168.100.31 --proxy-config /config/kube-proxy-config.yaml --v 2

            - name: K8S_NODE_NAME
              valueFrom:
                fieldRef:
                  apiVersion: v1
                  fieldPath: spec.nodeName
            - name: K8S_NODE_IP
              valueFrom:
                fieldRef:
                  apiVersion: v1
                  fieldPath: status.hostIP


[轻量级 Kubernetes 集群发行版 K3s 完全进阶指南](https://www.hi-linux.com/posts/907.html)
默认使用sqlite3数据(同时支持etcd，mysql等)

TODO:
* xxx

pvc应用部署特别慢
有时候还挂载不上(nextcloud容器里面没有pvc目录内容?)
=> 感觉都是glusterfs问题?

思路:
* 可能没法远程查看日志!
* 尝试复现问题?
  => delete pod,让有pvc的pod不停的启动挂载
* 理清启动pvc容器的流程,到时候就有精确的日志可以分析?
* 可能是mount挂载失败,但是返回成功,导致的?
  又或者挂载成功,glusterfs啥的又退出重启导致的?
  分析glusterfsd的日志,对着哪个时间点分析

=> 看journel日志好像都挂载成功了(127.log)?是否挂载成功又断开导致的?(有奇怪日志如下)
```
Jul 25 16:12:02 worker2.kcp5.iefcu.cn hyperkube[2997]: I0725 16:12:02.873423    2997 reconciler.go:196] "operationExecutor.UnmountVolume started for volume \"nextcloud-data\" (UniqueName: \"kubernetes.io/glusterfs/8751621b-213f-4619-8200-10f2a4ec6abb-pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8\") pod \"8751621b-213f-4619-8200-10f2a4ec6abb\" (UID: \"8751621b-213f-4619-8200-10f2a4ec6abb\") "
Jul 25 16:12:02 worker2.kcp5.iefcu.cn hyperkube[2997]: W0725 16:12:02.900200    2997 mount_helper_common.go:133] Warning: "/var/lib/kubelet/pods/8751621b-213f-4619-8200-10f2a4ec6abb/volumes/kubernetes.io~glusterfs/pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8" is not a mountpoint, deleting
Jul 25 16:12:02 worker2.kcp5.iefcu.cn hyperkube[2997]: I0725 16:12:02.900357    2997 operation_generator.go:866] UnmountVolume.TearDown succeeded for volume "kubernetes.io/glusterfs/8751621b-213f-4619-8200-10f2a4ec6abb-pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8" (OuterVolumeSpecName: "nextcloud-data") pod "8751621b-213f-4619-8200-10f2a4ec6abb" (UID: "8751621b-213f-4619-8200-10f2a4ec6abb"). InnerVolumeSpecName "pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8". PluginName "kubernetes.io/glusterfs", VolumeGidValue "2008"
```
=> 佐治说127的/var/log/glusterfs这个目录为空, 本来也应该为空,我搞错了

查看journel日志,发现时kubelet挂载存储的
```
Jul 27 07:22:47 master2.kcp2-arm.iefcu.cn systemd[1]: var-lib-kubelet-pods-c4f9b4dc\x2d7f0b\x2d4963\x2d808a\x2d6a0cce4bce56-volumes-kubernetes.io\x7eprojected-kube\x2dapi\x2daccess\x2d7ggnw.mount: Succeeded.
Jul 27 07:22:47 master2.kcp2-arm.iefcu.cn systemd[2788385]: var-lib-kubelet-pods-c4f9b4dc\x2d7f0b\x2d4963\x2d808a\x2d6a0cce4bce56-volumes-kubernetes.io\x7eglusterfs-pvc\x2d62459741\x2d87ad\x2d489c\x2da28d\x2d17ef3ed15882.mount: Succeeded.
Jul 27 07:22:47 master2.kcp2-arm.iefcu.cn systemd[1]: var-lib-kubelet-pods-c4f9b4dc\x2d7f0b\x2d4963\x2d808a\x2d6a0cce4bce56-volumes-kubernetes.io\x7eglusterfs-pvc\x2d62459741\x2d87ad\x2d489c\x2da28d\x2d17ef3ed15882.mount: Succeeded.
Jul 27 07:22:47 master2.kcp2-arm.iefcu.cn hyperkube[1998]: I0727 07:22:47.264124    1998 operation_generator.go:866] UnmountVolume.TearDown succeeded for volume "kubernetes.io/projected/c4f9b4dc-7f0b-4963-808a-6a0cce4bce56-kube-api-access-7ggnw" (OuterVolumeSpecName: "kube-api-access-7ggnw") pod "c4f9b4dc-7f0b-4963-808a-6a0cce4bce56" (UID: "c4f9b4dc-7f0b-4963-808a-6a0cce4bce56"). InnerVolumeSpecName "kube-api-access-7ggnw". PluginName "kubernetes.io/projected", VolumeGidValue ""
Jul 27 07:22:47 master2.kcp2-arm.iefcu.cn hyperkube[1998]: W0727 07:22:47.295471    1998 mount_helper_common.go:133] Warning: "/var/lib/kubelet/pods/c4f9b4dc-7f0b-4963-808a-6a0cce4bce56/volumes/kubernetes.io~glusterfs/pvc-62459741-87ad-489c-a28d-17ef3ed15882" is not a mountpoint, deleting
Jul 27 07:22:47 master2.kcp2-arm.iefcu.cn hyperkube[1998]: I0727 07:22:47.295885    1998 operation_generator.go:866] UnmountVolume.TearDown succeeded for volume "kubernetes.io/glusterfs/c4f9b4dc-7f0b-4963-808a-6a0cce4bce56-pvc-62459741-87ad-489c-a28d-17ef3ed15882" (OuterVolumeSpecName: "redis-data") pod "c4f9b4dc-7f0b-4963-808a-6a0cce4bce56" (UID: "c4f9b4dc-7f0b-4963-808a-6a0cce4bce56"). InnerVolumeSpecName "pvc-62459741-87ad-489c-a28d-17ef3ed15882". PluginName "kubernetes.io/glusterfs", VolumeGidValue "2003"
Jul 27 07:22:48 master2.kcp2-arm.iefcu.cn systemd[1]: Started Kubernetes transient mount for /var/lib/kubelet/pods/431acc92-183f-4efa-8dba-ce51f91e86d8/volumes/kubernetes.io~glusterfs/pvc-62459741-87ad-489c-a28d-17ef3ed15882.
Jul 27 07:22:49 master2.kcp2-arm.iefcu.cn hyperkube[1998]: I0727 07:22:49.060162    1998 glusterfs.go:399] successfully mounted directory /var/lib/kubelet/pods/431acc92-183f-4efa-8dba-ce51f91e86d8/volumes/kubernetes.io~glusterfs/pvc-62459741-87ad-489c-a28d-17ef3ed15882
```

挂载失败的日志
```
Jul 23 09:40:11 worker1.kcp5.iefcu.cn hyperkube[2995]: E0723 09:40:11.439654    2995 mount_linux.go:184] Mount failed: exit status 1
Jul 23 09:40:11 worker1.kcp5.iefcu.cn hyperkube[2995]: Mounting command: systemd-run
Jul 23 09:40:11 worker1.kcp5.iefcu.cn hyperkube[2995]: Mounting arguments: --description=Kubernetes transient mount for /var/lib/kubelet/pods/42058c08-d033-400b-9e89-838f7c7cb9d8/volumes/kubernetes.io~glusterfs/pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8 --scope -- mount -t glusterfs -o auto_unmount,backup-volfile-servers=192.168.1.131:192.168.1.130:192.168.1.129,log-file=/var/lib/kubelet/plugins/kubernetes.io/glusterfs/pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8/nextcloud-8658d9f6ff-bwns9-glusterfs.log,log-level=ERROR 192.168.1.130:vol_4d078ecee37c902bf1d174ca8b81bb67 /var/lib/kubelet/pods/42058c08-d033-400b-9e89-838f7c7cb9d8/volumes/kubernetes.io~glusterfs/pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8
Jul 23 09:40:11 worker1.kcp5.iefcu.cn hyperkube[2995]: Output: Running scope as unit: run-r7e062fe5e1d84d04863fd8cd730607ca.scope
Jul 23 09:40:11 worker1.kcp5.iefcu.cn hyperkube[2995]: [2022-07-23 01:40:03.368032] E [glusterfsd.c:828:gf_remember_backup_volfile_server] 0-glusterfs: failed to set volfile server: File exists
Jul 23 09:40:11 worker1.kcp5.iefcu.cn hyperkube[2995]: Mounting glusterfs on /var/lib/kubelet/pods/42058c08-d033-400b-9e89-838f7c7cb9d8/volumes/kubernetes.io~glusterfs/pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8 failed.
Jul 23 09:40:11 worker1.kcp5.iefcu.cn hyperkube[2995]: I0723 09:40:11.439768    2995 glusterfs_util.go:37] failure, now attempting to read the gluster log for pod nextcloud-8658d9f6ff-bwns9
Jul 23 09:40:11 worker1.kcp5.iefcu.cn hyperkube[2995]: W0723 09:40:11.446549    2995 mount_helper_common.go:133] Warning: "/var/lib/kubelet/pods/42058c08-d033-400b-9e89-838f7c7cb9d8/volumes/kubernetes.io~glusterfs/pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8" is not a mountpoint, deleting
Jul 23 09:40:11 worker1.kcp5.iefcu.cn hyperkube[2995]: E0723 09:40:11.447983    2995 nestedpendingoperations.go:301] Operation for "{volumeName:kubernetes.io/glusterfs/42058c08-d033-400b-9e89-838f7c7cb9d8-pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8 podName:42058c08-d033-400b-9e89-838f7c7cb9d8 nodeName:}" failed. No retries permitted until 2022-07-23 09:40:11.947922717 +0800 CST m=+3120.720192199 (durationBeforeRetry 500ms). Error: MountVolume.SetUp failed for volume "pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8" (UniqueName: "kubernetes.io/glusterfs/42058c08-d033-400b-9e89-838f7c7cb9d8-pvc-2fc465c6-77d6-424d-acb7-d2831fb9eed8") pod "nextcloud-8658d9f6ff-bwns9" (UID: "42058c08-d033-400b-9e89-838f7c7cb9d8") : mount failed: mount failed: exit status 1
```

宿主机特定目录下也确实可以看到容器里面的目录
```
[root@master2 core]# cd /var/lib/kubelet/pods/431acc92-183f-4efa-8dba-ce51f91e86d8/volumes/kubernetes.io~glusterfs/pvc-62459741-87ad-489c-a28d-17ef3ed15882/
[root@master2 pvc-62459741-87ad-489c-a28d-17ef3ed15882]# ls
adam.txt  appendonly.aof  dump.rdb
```

使用crictl查看容器相关信息
```bash
crictl ps | grep redis
crictl inspect 2e0bf0adf3e68

# 可以看到里面的挂载信息
    "mounts": [
      {
        "containerPath": "/data",
        "hostPath": "/var/lib/kubelet/pods/431acc92-183f-4efa-8dba-ce51f91e86d8/volumes/kubernetes.io~glusterfs/pvc-62459741-87ad-489c-a28d-17ef3ed15882",
        "propagation": "PROPAGATION_PRIVATE",
        "readonly": false,
        "selinuxRelabel": false
      },
```

10.90.4.62 => 10.90.4.63
=> 去除--tls参数即可成功
```
virsh migrate 25588abb-3abf-3e52-1fe0-0d28ef6c1896 --p2p --unsafe --tls qemu+tcp://10.90.4.63/system tcp://10.90.4.63

error: 内部错误：qemu unexpectedly closed the monitor: 2022-07-20T08:33:00.363302Z qemu-kvm: Not a migration stream
2022-07-20T08:33:00.363486Z qemu-kvm: load of migration failed: Invalid argument
```

分析原因:
* 1.libvirt没有配置正确
* 2.证书路径不对, 证书不对
* 3.xxx

确认:
1.看目的libvirt的日志
  源日志,目的, libvirt, qemu


同网段pc scp到eip服务器，结果却到了gw router上！！！！

## openshift 备份恢复

关键字《openshift 备份恢复》
OpenShift 4 - 备份和恢复 Etcd 数据库
https://blog.csdn.net/weixin_43902588/article/details/124822319

https://www.joyk.com/dig/detail/1587517265859351
你的 Kubernetes/Openshift 集群备份了吗

什么是 velero
看官网有一个特别简单直接的介绍， 它可以干嘛呢， 三点：

备份你的集群并在出事的时候可以恢复
迁移集群到其他集群
复制你的生产集群到开发或者测试环境

https://blog.csdn.net/weixin_43902588/article/details/122349684
OpenShift 4 - 容器应用备份和恢复
=> 使用的是velero

OpenShift 4 - 备份和恢复 Etcd 数据库
https://blog.csdn.net/weixin_43902588/article/details/124822319
https://www.codeleading.com/article/26876302164/
=> 在4.10上验证过
TODO: 简单，可以验证尝试一下

https://www.jianshu.com/p/dc7b3ec6abd6
Openshift集群全环境备份
=> 复杂
在Openshift平台，我们可以对集群的完整状态备份到外部存储。集群全环境包括：
* 集群数据文件
* etcd数据库
* Openshift对象配置
* 私有镜像仓库存储
* 持久化卷

#### project_exports.sh导出项目yaml配置

=> 也就勉强能用一点点吧, 感觉还不如从原始的方法进行部署。。。

[OpenShift 项目的备份和恢复实验](https://www.cnblogs.com/ericnie/p/10500572.html)
本测试记录从openshift 3.6环境中导出项目，然后在将项目环境恢复到Openshift 3.11中所需要的步骤 从而指导导入导出的升级过程。


关键字《OpenShift 项目的备份和恢复》
=> project_export.sh 不能用! 经过修改, 去除--export参数，就可以导出数据了
https://github.com/openshift/openshift-ansible-contrib/blob/master/reference-architecture/day2ops/scripts/project_export.sh
=> 原理就是oc get -o=json, 导出配置, 不是很好用, 导出了多余的东西, 例如service-ca configmap

需要注意的地方包括:
* 用户不会导出，但在openshift的权限信息会保存。
* 节点的Label不会导出
* 导入导出过程需要rollout。
* 用glusterfs的时候，每个project的gluster-endpoint资源没有保存下来，估计和gluster-service没有关联相关
* 因为pv不是属于项目资源而属于整个集群资源，导入项目前，先建立pv
* 遇到pod无法启动很多时候和mount存储有关系

#### etcd数据备份和恢复

适合当前集群的备份和恢复, 具体的恢复还是不太明白!

登录master1节点, 执行etcd数据库备份操作, 将etcd数据库备份到目标目录中
```
mkdir -p /home/core/assets/backup
/usr/local/bin/cluster-backup.sh /home/core/assets/backup

# 例如备份单master节点的数据
[root@master1 core]# /usr/local/bin/cluster-backup.sh /home/core/assets/backup
found latest kube-apiserver: /etc/kubernetes/static-pod-resources/kube-apiserver-pod-16
found latest kube-controller-manager: /etc/kubernetes/static-pod-resources/kube-controller-manager-pod-6
found latest kube-scheduler: /etc/kubernetes/static-pod-resources/kube-scheduler-pod-7
found latest etcd: /etc/kubernetes/static-pod-resources/etcd-pod-2
d2af784a8998ee7be000c65cc7dc56c2099c5a73b3b6adbd2326a8face4efc25
etcdctl version: 3.4.14
API version: 3.4
{"level":"info","ts":1655434169.0621967,"caller":"snapshot/v3_snapshot.go:119","msg":"created temporary db file","path":"/home/core/assets/backup/snapshot_2022-06-17_024925.db.part"}
{"level":"info","ts":"2022-06-17T02:49:29.062Z","caller":"clientv3/maintenance.go:200","msg":"opened snapshot stream; downloading"}
{"level":"info","ts":1655434169.0624921,"caller":"snapshot/v3_snapshot.go:127","msg":"fetching snapshot","endpoint":"https://192.168.100.1:2379"}
{"level":"info","ts":"2022-06-17T02:49:31.905Z","caller":"clientv3/maintenance.go:208","msg":"completed snapshot read; closing"}
{"level":"info","ts":1655434172.1335819,"caller":"snapshot/v3_snapshot.go:142","msg":"fetched snapshot","endpoint":"https://192.168.100.1:2379","size":"104 MB","took":3.071241643}
{"level":"info","ts":1655434172.1337464,"caller":"snapshot/v3_snapshot.go:152","msg":"saved","path":"/home/core/assets/backup/snapshot_2022-06-17_024925.db"}
Snapshot saved at /home/core/assets/backup/snapshot_2022-06-17_024925.db
{"hash":668661593,"revision":5414790,"totalKey":8232,"totalSize":103858176}
snapshot db and kube resources are successfully saved to /home/core/assets/backup

[root@master1 core]# cd /home/core/assets/backup
[root@master1 backup]# ls
snapshot_2022-06-17_024925.db  static_kuberesources_2022-06-17_024925.tar.gz

# 三个节点的备份, 主要在于etcd的区别吧?
[root@master1 etcd-all-certs]# pwd
/var/home/core/assets/backup/static-pod-resources/etcd-pod-3/secrets/etcd-all-certs
[root@master1 etcd-all-certs]# ls
etcd-peer-master1.kcp2-arm.iefcu.cn.crt  etcd-peer-master3.kcp2-arm.iefcu.cn.crt     etcd-serving-master2.kcp2-arm.iefcu.cn.crt  etcd-serving-metrics-master1.kcp2-arm.iefcu.cn.crt  etcd-serving-metrics-master3.kcp2-arm.iefcu.cn.crt
etcd-peer-master1.kcp2-arm.iefcu.cn.key  etcd-peer-master3.kcp2-arm.iefcu.cn.key     etcd-serving-master2.kcp2-arm.iefcu.cn.key  etcd-serving-metrics-master1.kcp2-arm.iefcu.cn.key  etcd-serving-metrics-master3.kcp2-arm.iefcu.cn.key
etcd-peer-master2.kcp2-arm.iefcu.cn.crt  etcd-serving-master1.kcp2-arm.iefcu.cn.crt  etcd-serving-master3.kcp2-arm.iefcu.cn.crt  etcd-serving-metrics-master2.kcp2-arm.iefcu.cn.crt
etcd-peer-master2.kcp2-arm.iefcu.cn.key  etcd-serving-master1.kcp2-arm.iefcu.cn.key  etcd-serving-master3.kcp2-arm.iefcu.cn.key  etcd-serving-metrics-master2.kcp2-arm.iefcu.cn.key
```

恢复 Etcd 数据库

1. 在 Master-1 和 Master-2 节点上分别执行以下命令，先将现有 Kubernetes API 服务器 pod 文件和 etcd pod 文件从 kubelet 清单目录中移出。然后确认直到已经没有 etcd 和 kube-apiserver 的 pod 运行。
```
sudo mv /etc/kubernetes/manifests/etcd-pod.yaml /tmp
sudo mv /etc/kubernetes/manifests/kube-apiserver-pod.yaml /tmp
sudo crictl ps | grep etcd | grep -v operator
sudo crictl ps | grep kube-apiserver | grep -v operator
```

2. 在 Master-1 和 Master-2 节点上分别执行以下命令，将 etcd 数据目录移走。
```
sudo mv /var/lib/etcd/ /tmp
```

3. 在 MASTER-0 节点上执行命令恢复 Etcd 数据库。
```
sudo -E /usr/local/bin/cluster-restore.sh /home/core/backup
```

4. 在所有 Master 节点执行命令，重启 kubelet 服务。在确认服务重新运行后 Etcd 数据库即恢复完。
```
sudo systemctl restart kubelet.service
sudo systemctl status kubelet.service
```

5. 在所有 Master 节点执行命令，确认 etcd pod 正常运行。
```
sudo crictl ps | grep etcd | grep -v operator
oc get pods -n openshift-etcd | grep -v etcd-quorum-guard | grep etcd
```

最后发现服务正常，但是web console白屏无法进去(网络请求有502错误)，查看pod日志显示连接错误：
2022/06/17 06:14:52 http: proxy error: dial tcp 172.30.0.1:443: connect: connection refused
E0617 06:40:47.707707       1 auth.go:231] error contacting auth provider (retrying in 10s): Get "https://kubernetes.default.svc/.well-known/oauth-authorization-server": dial tcp 172.30.0.1:443: connect: connection refused
=> 是不是联系不上apiserver了?

https://access.redhat.com/solutions/5444221
After Using the Recovery API Server, Pods are Unable to Reach 172.30.0.1:443
=> 跟这个问题一模一样, 而且问题也还没有解决！也没权限看

没有查到什么资料，看看所有的pod，是否有异常的! 都是跟172.30.0.1:443有关！！
[core@master1 ~]$ oc -n openshift-apiserver-operator get pods
NAME                                            READY   STATUS             RESTARTS          AGE
openshift-apiserver-operator-6c9d95d44d-h85qw   0/1     CrashLoopBackOff   298 (2m10s ago)   12d

=> 发现只有master1的apiserver运行正常, 丫的发现只有master1有etcd和apiserver的静态pod配置文件！！！
oc命令能够正常使用。。。 oc delete 也能用。。。 => 但是整个系统暂不知道怎么恢复

再次尝试, 遇到错误, etcd还是没起来, etcd operator错误日志如下
```
I0618 08:30:30.640858       1 base_controller.go:110] Starting #1 worker of ConfigObserver controller ...
E0618 08:30:30.727538       1 base_controller.go:272] FSyncController reconciliation failed: client query returned empty vector
I0618 08:30:31.538790       1 request.go:665] Waited for 1.498225057s due to client-side throttling, not priority and fairness, request: GET:https://172.30.0.1:443/api/v1/namespaces/kube-system/configmaps/cluster-config-v1
I0618 08:30:31.558694       1 quorumguardcontroller.go:186] etcd-quorum-guard was modified
I0618 08:30:31.558886       1 event.go:282] Event(v1.ObjectReference{Kind:"Deployment", Namespace:"openshift-etcd-operator", Name:"etcd-operator", UID:"f5d36503-a7f1-4202-a58e-78e25320c0d7", APIVersion:"apps/v1", ResourceVersion:"", FieldPath:""}): type: 'Normal' reason: 'ModifiedQuorumGuardDeployment' etcd-quorum-guard was modified
E0618 08:30:32.019055       1 base_controller.go:272] FSyncController reconciliation failed: client query returned empty vector
I0618 08:30:32.738447       1 request.go:665] Waited for 1.396265937s due to client-side throttling, not priority and fairness, request: GET:https://172.30.0.1:443/api/v1/namespaces/openshift-etcd/pods/etcd-master2.kcp2-arm.iefcu.cn
E0618 08:30:34.589319       1 base_controller.go:272] FSyncController reconciliation failed: client query returned empty vector
E0618 08:30:39.719966       1 base_controller.go:272] FSyncController reconciliation failed: client query returned empty vector
```

=> 单节点恢复了, 但是确实不容易
强制删除etcd pod, 还重启了kubelet
但是居然没有恢复出我的项目？？？但是namespaces中有 => 说明openshift-apiserver的数据还是丢失了呢

## 其他

* docker安装，居然使用二进制安装，起不来，使用rpm安装可以
* 存在dhcp服务器，结果bootstrap有问题！关掉了!
* ip冲突问题有问题, 换私有ip装, 装好再处理

up{namespace="openshift-ingress"}
=> 可以查到数据

名称
container
endpoint
instance
job
namespace
pod
prometheus
service
值
up	router	metrics	10.90.3.33:1936	router-internal-default	openshift-ingress	router-default-66ddd5cfb-6wzt2	openshift-monitoring/k8s	router-internal-default	1


https://blog.51cto.com/u_14065119/3698192
可用性监控
除了监控主机的性能参数外，我们还需要关注实例的可用性情况，比如是否关机、exporter是否正常运行等。在exporter返回的指标，有一个up指标，可用来实现这类监控需求。

up{job="node-exporter"}



## TOOLS
https://www.youtube.com/watch?v=2OHrTQVlRMg&ab_channel=TechCraft
======

* exa - https://github.com/ogham/exa
  better ls
* bat - https://github.com/sharkdp/bat
  better cat
* ripgrep - https://github.com/BurntSushi/ripgrep
  学一下ag的区别: 正则匹配, 搜索指定类型的文件
* fzf - https://github.com/junegunn/fzf
* zoxide - https://github.com/ajeetdsouza/zoxide
  smarter cd command
* entr - https://github.com/eradman/entr
  A utility for running arbitrary commands when files change. 
* mc - https://midnight-commander.org/
  visual file manager

vpc网络虚拟化

* 分析ZStack实现方法
* 搭建最新openstack环境，分析openstack实现

#### 利用标签获取应用cpu监控指标

思路:
* 筛选出不在指定命名规则里面的项目
refer https://prometheus.io/docs/prometheus/latest/querying/basics/
```
sum(container_memory_working_set_bytes{cluster="", namespace!~"openshift.*", container!="", image!=""}) by (namespace)
```
* 根据label筛选
  没有label上报, 无法筛选
* 其他?

通过如下命令可以查询出openshift相关项目下的内存使用量?
```
sum(container_memory_working_set_bytes{cluster="", namespace=~"openshift.*", container!="", image!=""}) by (namespace)
```

然后通过页面查询 container_memory_working_set_bytes 的上报数据字段
* container
* id
* instance
* name
k8s_POD_tomcat-58c777d49f-6n5w5_adam-test_06324d9b-7782-45ea-b93b-4cf1264cc09a_0
* namespace
* node
master1
* pod
tomcat-58c777d49f-6n5w5
* ...等字段

=> 发现没有label字段, 就不可能通过label字段来过滤

可以手动查询一下?(是kubelet上报的监控数据)
curl -k -H "Authorization: Bearer sha256~TZy6BQgoMYssf2OY7Zm2pNcnzS_jbqSNNvUkJrHVENk" https://localhost:10250/metrics/cadvisor
=> 没有权限。。。

#### 自定义告警规则添加上了，但是在promethues里没看到

在内置的promethues里面没有看到
Alerts
Rules

在新prome, thanos pod中可以看到配置生效了!
* /etc/prometheus/rules/prometheus-user-workload-rulefiles-0
* /etc/thanos/rules/thanos-ruler-user-workload-rulefiles-0

refer https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.9/html-single/monitoring/index
```bash
$ oc port-forward -n openshift-user-workload-monitoring pod/prometheus-user-workload-0 9090
```

可以在 Web 浏览器中打开 http://localhost:9090/targets，并在 Prometheus UI 中直接查看项目的目标状态。检查与目标相关的错误消息。
=> 可以看这个promethues的Rules等信息

#### 监控api耗时

* 离线部署traefix-mesh
* 配置dns转发
* 应用调用使用新域名(service)
