# 临时计划

cloud-init userdata
```
#cloud-config
timezone: Asia/Shanghai
password: ksvd2020
ssh_pwauth: True
```

#### nfs客户端卡住

关键字《nfs挂载点检测》

[linux 脚本判断挂载,Linux Shell脚本：如何检测NFS挂载点(或服务器)已经死了？](https://blog.csdn.net/weixin_40000999/article/details/116680094)

#### ubuntu配置网口vlan

发现物理pc机器收到h3c交换机的vlan918的arp包, 所以物理pc机器需要配置vlan

关键字《ubuntu命令行设置网卡vlan》

```
sudo apt-get install vlan
```

配置netplan配置文件
```
# Let NetworkManager manage all devices on this system
network:
  version: 2
  renderer: NetworkManager
  ethernets:
      enp2s0f0:
          dhcp4: no
  vlans:
      vlan3:
          id: 3
          link: enp2s0f0
          addresses: [ "172.31.3.103/24" ]
      vlan30:
          id: 30
          link: enp2s0f0
          addresses: [ "172.31.30.103/24" ]
```


#### ubuntu livecd win7密码找回

使用chnptpwd修改windows密码
```
sudo apt install chntpw 
cd WINDOWS/system32/config
sudo chntpw SAM
要修改非管理员密码，在命令行模式键入以下命令：sudo chntpw -u [用户名] SAM。
```

https://docs.openstack.org/openstack-helm-images/latest/vbmc.html
=> 有libvirt 镜像编译?

```
ubuntu@ubuntu:/mnt$ sudo qemu-img convert -f qcow2 -t none -O raw GUEST.IMG /dev/nvme0n1
qemu-img: error while writing sector 0: No space left on device
```
=> 然后/dev/nvme0n1这个设备都不见了???

```
enable_ironic: "yes"
ronic_dnsmasq_interface: "eth1"
ironic_cleaning_network: "enp4s3"
ironic_dnsmasq_dhcp_ranges:
  - range: "192.168.83.100,192.168.83.110"
    routers: "192.168.83.192"
ironic_dnsmasq_boot_file: pxelinux.0
ironic_inspector_kernel_cmdline_extras: ['ipa-lldp-timeout=90.0', 'ipa-collect-lldp=1']
ironic_http_port: "8089"
```

[虚拟机支持BMC IPMi](http://www.chenshake.com/the-virtual-machine-supports-bmc-ipmi-with-the-support-of-the/)
最近打算搞裸机测试，如果用虚拟机来做裸机测试，最大的一个难点就是如何模拟IPMI。
OpenStack经常都是项目开发过程中，解决了很多现实的问题，专门开发了一个IPMI模拟工具。
```
yum -y install python3-pip python3-devel gcc libvirt-devel ipmitool
pip3 install --upgrade pip
pip3 install virtualbmc
```

网络虚拟化不支持tftp协议
丢弃源mac地址为xxx的包, 阻止该死的外部dhcp服务器
```
ovs-ofctl add-flow mdvs2 "priority=100,dl_src=30:85:a9:a3:b7:37 actions=drop"
ovs-ofctl add-flow mdvs2 "table=5,priority=100,dl_src=30:85:a9:a3:b7:37 actions=drop"
ovs-ofctl add-flow mdvs2 "table=5,priority=100,dl_src=6c:b3:11:33:da:df actions=drop"
ovs-ofctl add-flow mdvs2 "table=5,priority=100,dl_src=00:91:10:00:28:c5 actions=drop"
ovs-ofctl add-flow mdvs2 "table=5,priority=100,dl_src=52:54:64:00:00:08 actions=drop"
ovs-ofctl add-flow mdvs2 "table=5,priority=100,dl_src=90:e2:fc:b1:3c:9b actions=drop"
ovs-ofctl add-flow mdvs2 "table=5,priority=99,udp,src_port=67 actions=drop" => TODO: test
ovs-ofctl add-flow mdvs2 "priority=100,dl_src=8c:2a:8e:84:64:35 actions=drop"
```

Cobbler 介绍
Cobbler 是一个 Linux 服务器安装的服务，可以通过网络启动 (PXE) 的方式来快速安装、重装物理服务器和虚拟机，同时还可以管理 DHCP，DNS 等。

Cobbler 可以使用命令行方式管理，也提供了基于 Web 的界面管理工具 (cobbler-web)，还提供了 API 接口，可以方便二次开发使用。

Cobbler 是较早前的 kickstart 的升级版，优点是比较容易配置，还自带 web 界面比较易于管理。

Cobbler 内置了一个轻量级配置管理系统，但它也支持和其它配置管理系统集成，如 Puppet，暂时不支持 SaltStack。

关键字《etcd使用grpc协议》

[学习etcd的消息协议gRPC一点随想](https://yemilice.com/2021/04/06/etcd%E7%9A%84%E6%B6%88%E6%81%AF%E5%8D%8F%E8%AE%AE-grpc%E5%AD%A6%E4%B9%A0%E9%9A%8F%E6%83%B3/)

etcd之间使用了grpc协议(基于http/2)

[从 HTTP 到 gRPC：APISIX 中 etcd 操作的迁移之路](https://www.apiseven.com/blog/migrate-etcd-operation-from-http-to-grpc-in-apisix)

[将你的grpc服务注册到etcd中](https://zhuanlan.zhihu.com/p/450777806)

关键字《ip over ip tunnel》
[揭秘 IPIP 隧道](https://morven.life/posts/networking-3-ipip/)

[一文读懂 HTTP/2 及 HTTP/3 特性](https://blog.fundebug.com/2019/03/07/understand-http2-and-http3/)

[探索 OpenStack 之（9）：深入块存储服务Cinder （功能篇）](https://developer.aliyun.com/article/378435)

[How to increase instance memory in OpenStack](https://urclouds.com/2020/01/01/how-to-increase-instance-memory-in-openstack/)

https://www.expreview.com/61416.html
Percentage Used: 设备使用寿命百分比的估算
```
smartctl -a /dev/disk0
Percentage Used:                    1%
```

#### 创建libvirtd容器，里面运行libvirtd

```
FROM ubuntu:20.04

MAINTAINER  Adam Xiao "iefcuxy@gmail.com"

ENV DEBIAN_FRONTEND noninteractive

# 安装libvirtd和其他必要的软件包
RUN apt-get update && apt-get install -y \
        libvirt-clients \
        libvirt-daemon-system \
        openvswitch-switch \
        qemu-block-extra \
        qemu-system \
        qemu-utils

# 将libvirt配置文件复制到容器中
#COPY libvirtd.conf /etc/libvirt/libvirtd.conf

RUN sed -i -e 's/^#listen_tls.*/listen_tls = 0/' /etc/libvirt/libvirtd.conf

# 暴露libvirt服务端口
EXPOSE 16509

# 启动libvirtd守护进程
#CMD ["/usr/sbin/libvirtd", "-d", "-l"]
CMD ["/usr/sbin/libvirtd", "-l"]
```

在上面的Dockerfile中，我们使用最新版本的Ubuntu作为基础镜像，然后安装了libvirt-daemon-system和libvirt-clients软件包。我们还将libvirtd.conf文件复制到容器中，并通过EXPOSE指令暴露了libvirt服务端口。最后，我们使用CMD指令启动了libvirtd守护进程。

```
docker build -t libvirtd-container .
docker run -d --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro -p 16509:16509 libvirtd-container
--device /dev/kvm
```
在上面的docker run命令中，我们使用--privileged选项允许容器访问主机系统的所有设备，这是必要的，因为libvirtd需要访问主机系统的/dev和/sys目录。我们还将/sys/fs/cgroup目录挂载到容器中，以便容器可以使用cgroup来管理资源。最后，我们使用-p选项将容器内的16509端口映射到主机系统的16509端口上，这样就可以通过主机系统上的libvirt客户端访问容器中的libvirtd守护进程。

现在，您已经成功地创建了一个libvirtd容器，并在其中运行了libvirtd守护进程。您可以使用主机系统上的libvirt客户端连接到容器中的libvirtd守护进程，并管理虚拟化资源。如果您需要在容器中运行其他虚拟机，您可以使用主机系统上的libvirt客户端来创建和管理它们，就像在普通的物理主机上一样。

FAQ
- Cannot read CA certificate '/etc/pki/CA/cacert.pem': No such file or directory
  监听tcp端口，要么需要证书，要么取消tls认证

#### terminal Gogh 配色

gnome terminal 的配置方案, 类似desert

#### 同步手机照片

关键字《Syncthing ubuntu使用》
https://linux.cn/article-11793-1.html

[(二十三)小众但好用: Syncthing 把手机变成同步网盘](https://zhuanlan.zhihu.com/p/121544814)

[Syncthing 文件同步工具部署和 iOS 替代方案](https://wasteland.touko.moe/blog/2020/03/syncthing-all-platform/)
=> ubuntu 下使用apt安装syncthing

[Syncthing vs Resilio Sync vs Nextcloud 文件同步服务对比](https://www.ucloud.cn/yun/63568.html)

https://www.appinn.com/les-pas-for-nextcloud/

Les Pas 是一款开源的专门针对 Nextcloud 私有云的第三方相册应用，可以用来在 Android 设备与 Nextcloud 之间双向同步照片，还能整合 Snapseed 软件联动修图。@Appinn

【村雨组NAS】Nextcloud私有云盘 使用教程
https://www.bilibili.com/read/cv9722094

我的IPhone照片备份方案
https://post.smzdm.com/p/a6lxpoln/

https://zhuanlan.zhihu.com/p/461563481
私家NAS自动备份手机照片文件

两年前我把服务器从A某云搬到了家里，并搭建了NAS服务，用来存储存档型的资料文档。NAS服务千千万，看了眼seafile、nextcloud、ownCloud的界面、对比简介，然后选了Nextcloud。


#### chatgpt使用

https://juejin.cn/post/7198097078005841980

需要使用国外手机号注册使用，中国区不可用
使用[接码平台](sms-activate.org/)

OpenAI's services are not available in your country.

https://www.51cto.com/article/745970.html
在淘宝上买一个现成的账号就行，共享的 3 块一个，独享的 7 块一个。我觉得买一个现成的比较快捷，自己注册需要准备邮箱和接受国外验证码的手机号，比较麻烦。

https://www.xnbeast.com/create-openai-chatgpt-account/
TODO: 尝试注册账号

#### find使用

find 30天内修改的文件
https://www.cnblogs.com/klb561/p/10924399.html

```
#查找 30天内修改的文件
find -mtime -30 -name "*.md"
#查找 30天前修改的文件
find -mtime +30 -name "*.md"
#查找 30~60天内修改的文件
find -mtime +30 -mtime -60 -name "*.md"
# 查找最近180分钟修改的当前目录下的.php文件
find . -name '*.php' -mmin -180
```

#### shell 并行运行工具

关键字《shell 并行运行工具》

[如何在 shell 中实现并行执行](https://youwu.today/blog/parallel-in-shell/)

方案4-使用 xargs 命令的控制参数
```
> seq 20 | xargs -I % -P4 sh -c 'echo %; sleep 1s'
```
方案5-使用 parallel 命令行工具
```
> seq 20 | parallel -j 4 "echo {}; sleep 1"
```

#### ES学习应用

如何入手ES?

ES的应用?


#### 如何写好一篇技术简历?

https://www.xiaoz.me/archives/14072

#### 程序员画图工具

https://zhuanlan.zhihu.com/p/353333743
推荐这个软件draw.io

https://www.51cto.com/article/721130.html
有不少软件推荐

https://codeantenna.com/a/GBE0ahio6i
plantuml, graphviz等特殊工具推荐

https://www.sohu.com/a/452197561_100093134
不止VS Code：程序员高效工作的画图工具一览 

https://github.com/phodal/articles/issues/18

#### pdf图片文字识别

pandoc转换成word?

#### 日志组件

ksvd-netd日志输出，没有截断功能...

日志轮转, logrotate

https://www.jianshu.com/p/cb21d35b686f
```
自定义日志轮转
在 目录下编辑一个文件
/var/log/shark1.log {
        monthly              >== 每月一次轮转
        size=10M             >== 文件大小大于 10M 时， 也开始轮转
        rotate 2             >== 日志文件保留 2 个
        compress             >== 对旧的日志文件进行压缩
        sharedscripts        >== 轮转之前需要先被执行命令
        prerotate
                /usr/bin/chattr -a /var/log/shark1.log      >==去掉特殊属性
        endscript
        sharedscripts      >== 轮转之后需要被执行的命令
        postrotate
            /bin/kill -HUP `cat /var/run/syslogd.pid 2> /dev/null` 2> /dev/null || true
            /usr/bin/chattr +a /var/log/shark1.log     >== 特殊属性，文件内容只能增加不能删除或者修改
        endscript
}
```

logrotate 负责对系统日志的轮转。

通过定时任务每天都会执行一次。
```
cat /etc/cron.daily/logrotate
```

#### tipc

https://blog.csdn.net/fzubbsc/article/details/46439997
一个client和server的示例代码

https://www.cnblogs.com/yipianchuyun/p/15772512.html
这个文章讲的比较详细

https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/8/html/configuring_and_managing_networking/getting-started-with-tipc_configuring-and-managing-networking
redhat的tipc文档

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

[(好)Using tcpdump on the command line](https://docs.netgate.com/pfsense/en/latest/diagnostics/packetcapture/tcpdump.html)
https://danielmiessler.com/study/tcpdump/

```
https://clouddocs.f5.com/training/community/adc/html/class4/module1/lab02.html
Host Filters
tcpdump host 192.168.2.5 This will filter the packet capture to only gather packets going to or coming from the host 192.168.2.5.
tcpdump src host 192.168.2.5 This will filter the packet capture to only gather packets coming from 192.168.2.5.
tcpdump dst host 192.168.2.5 This will filter the packet capture to only gather packets going to 192.168.2.5.
Port Filters
tcpdump port 443 This will filter the packet capture to only gather packets with a source or destination of port 443.
tcpdump src port 1055 This will capture traffic being sourced from port 1055.
tcpdump dst port 443 This will capture traffic destined for port 443.
```

https://www.xmodulo.com/filter-split-merge-pcap-linux.html
```
editcap -A '2023-04-19 12:02:35' -B '2023-04-19 12:02:45' adam.pcap new.pcap
editcap -A '2023-04-19 16:01:50' -B '2023-04-19 16:02:00' new-adam.pcap new-new.pcap
```

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

#### gitbook再优化

https://blog.51cto.com/lovebetterworld/5050024
整理全网文档管理系统，持续更新

http://www.teemlink.com/solutions_kms/
KM知识管理系统

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
