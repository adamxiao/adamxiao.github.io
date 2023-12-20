# kubevirt调研

关键字《kubevirt是什么》

KubeVirt是个Kubernetes的一个插件，使其在原本调度容器之余能够并行调度传统虚拟机。 它通过运用自定义资源定义（以下简称CRD）及其他Kubernetes相关功能来无缝扩展现有的集群，提供一系列可用于管理虚拟机的虚拟化API。

[KubeVirt（Kubernetes接管虚拟化）](https://juejin.cn/post/7128038442277011493)
KubeVirt是Red-Hat开源的，以容器方式运行的虚拟机项目。是基于Kubernetes运行的，具体的来说是基于Kubernetes的CRD（自定义资源）增加虚拟机的运行和管理相关的资源。特别是VM，VMI资源类型。也是说我们通过CRD进行增加关于虚拟机的资源类型，然后通过写YAML的形式来创建虚拟机等一系列的操作。


https://zhuanlan.zhihu.com/p/113568026
KubeVirt 架构
从kubevirt架构看如何创建虚拟机，Kubevirt架构如图所示，由4部分组件组成。从架构图看出kubevirt创建虚拟机的核心就是 创建了一个特殊的pod virt-launcher 其中的子进程包括libvirt和qemu。做过openstack nova项目的朋友应该比较 习惯于一台宿主机中运行一个libvirtd后台进程，kubevirt中采用每个pod中一个libvirt进程是去中心化的模式避免因为 libvirtd 服务异常导致所有的虚拟机无法管理。

https://segmentfault.com/a/1190000041741403
多图
在了解了 Kubevirt 是什么，它的主要架构以及比较关键的资源对象后，我们来看看如何使用 Kubevirt 进行虚拟机管理。这里主要分为**虚拟机创建、存储和网络三个部分**。

https://moelove.info/2023/09/03/KubeVirt-探秘一些核心问题解答/#kubevirt-有哪些用例
OKD用了KubeVirt?

kubevirt在360的探索之路（k8s接管虚拟化）
https://www.cnblogs.com/qinlulu/p/14671435.html
技术选型
有了以上想法以后，就开始调研，发现业界在从openstack转型k8s的过程中涌现了这么一部分比较好的项目，例如，kubevirt，virtlet，rancher/vm等，但是社区活跃度最高，设计最好的还是kubevirt。

## 问题

- 需要在宿主机上安装libvirt,qemu等, 容器里没有libvirt, 跟kolla不一样! 这样都行...
  => 容器里面有libvirt和qemu!
  记得之前容器pod可以把宿主机root根文件系统挂载到容器中!

- 模板镜像哪里来?
  yaml文件定义了镜像模板, 但是里面是文件系统呀?
```
        - name: containerdisk
          containerDisk:
            image: quay.io/kubevirt/cirros-container-disk-demo      #使用此镜像创建个虚拟机。
```
原来是镜像里面压缩了一个qcow2镜像...
```
$qemu-img info disk/downloaded
image: disk/downloaded
file format: qcow2
virtual size: 44M (46137344 bytes)
disk size: 12M
cluster_size: 65536
Format specific information:
    compat: 1.1
    lazy refcounts: false
```
- 磁盘文件哪里来?
  https://kubevirt.io/user-guide/virtual_machines/disks_and_volumes/
  - lun: A lun disk will expose the volume as a LUN device to the VM. This allows the VM to execute arbitrary iSCSI command passthrough.
  - disk: A disk disk will expose the volume as an ordinary disk to the VM.
  - cdrom: A cdrom disk will expose the volume as a cdrom drive to the VM. It is read-only by default.
  - fileystems: virtiofs?
  上面的lun，disk可以使用pvc提供，有filesystem或者block的pvc, 文件系统使用disk.img
- VMI是什么概念?
  就是virtual machine instance吧
- 如何vnc连接虚拟机?
  使用virtctl工具连接，应该就是网络的配置，相关配置信息的获取等等
  => 配置$HOME/.kube/config配置文件，远程也能访问到
- 是否支持裸金属管理?

看官方用户手册，了解功能:
https://kubevirt.io/user-guide/operations/snapshot_restore_api/

- cpu超分比率, 没有内存超分
- pci直通
- usb重定向
  客户端的重定向?
- 热插拔卷，网卡
- 热迁移
  开发支持
- 快照
  Snapshotting a virtualMachine is supported for online and offline vms.
  应该参考openstack的快照，不带内存的
- 克隆，模板等支持
- NUMA, Huge Page等支持
- arm64架构支持
- cpu热插拔


## kubevirt资料

https://mrlch.cn/archives/1572
- virt-api
  kubevirt 是 CRD 形式管理 vm pod，virt-api 就是去所有虚拟化操作 的入口，包括常规的 CRD 更新验证以及vm start、stop
- virt-controlller
  Virt-controller会根据vmi CRD，生成virt-lancher pod，并维护CRD的状态
- virt-handler
  virt-handler会以 Daemonset 的状态部署在每个节点上，负责监控上每个虚拟机实例的状态变化，一旦检测到变化，会进行响应并确保相应的操作能够达到要求的（）状态。
  virt-handler保持集群级之间的同步规范与 libvirt 的同步报告 Libvirt 和集群的规范；调用以节点为中心的变化域 VMI 规范定义的网络状态和管理要求。
- virt-launcher
  virt-lanuncher pod一个 VMI，kubelet 只是负责运行状态，不会去管virt-lanuncher podVMI 创建情况。
  virt-handler会根据 CRD 参数配置去通知 virt-lanuncher 去使用本地 libvirtd 实例来启动 VMI，virt-lanuncher 会通过 pid 去管理 VMI，如果 pod 生命周期结束，virt-lanuncher 也会去通知 VMI 去终止。
  然后再去一个libvirtd，去virt-lanuncher pod，通过libvirtd去管理VM的生命周期，到t-中心，不再是以前的机器那套，libvirtd去管理多个VM。

https://k8s.huweihuang.com/project/kvm/kubevirt/kubevirt-introduction
virt-launcher与libvirt逻辑：

### 什么时候使用kubvirt虚拟机

https://kubevirt.io/user-guide/architecture/#when-to-use-a-virtualmachine
When to use a VirtualMachine¶

- When API stability is required between restarts¶
- When config updates should be picked up on the next restart¶
- When you want to let the cluster manage your individual VirtualMachineInstance¶
  => 估计这个比较关键吧

[(好)kubevirt在360的探索之路（k8s接管虚拟化） 转载](https://blog.51cto.com/u_15293891/3084492)

## kubevirt其他版本验证

### v0.59.2 => 1.0之前的最新版本

### v1.0.1 => 1之后的较新版本

## 其他高级功能验证

#### 导出虚拟机 => 需要高版本kubevirt支持

创建一个secret
```
apiVersion: v1
kind: Secret
metadata:
  name: example-token
stringData:
  token: 1234567890ab
```

然后导出虚拟机卷
```
apiVersion: export.kubevirt.io/v1alpha1
kind: VirtualMachineExport
metadata:
  name: example-export
spec:
  tokenSecretRef: example-token
  source:
    apiGroup: "kubevirt.io"
    kind: VirtualMachine
    name: testvm
```

报错:
```
error: unable to recognize "export-vm.yml": no matches for kind "VirtualMachineExport" in version "export.kubevirt.io/v1alpha1"
```

还有其他导出...

还有virtctl导出虚拟机，更方便使用
```
virtctl vmexport create name [flags]
```
=> 额，安装的版本不支持这个命令。。。

#### 热添加网卡 => 需要安装额外网络组件Multus

https://kubevirt.io/user-guide/operations/hotplug_interfaces/
=> 支持热添加桥模式，或者SRIOV网卡, 仅支持热卸载桥模式网卡
- SRIOV
- 桥接网络?

前提
- 安装Multus

```
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: new-fancy-net
spec:
    config: '{
      "cniVersion": "0.3.1",
      "type": "bridge",
      "mtu": 1300,
      "name":"new-fancy-net"
    }'
```

最后编辑虚拟机spec模板添加网卡 => 验证没有生效添加网卡???
```
kubectl edit vm testvm
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: vm-fedora
template:
  spec:
    domain:
      devices:
        interfaces:
        - name: defaultnetwork
          masquerade: {}
          # new interface
        - name: dyniface1
          bridge: {}
    networks:
    - name: defaultnetwork
      pod: {}
      # new network
    - name: dyniface1
      multus:
        networkName: new-fancy-net
```

#### 热添加磁盘卷 => 验证ok

https://kubevirt.io/user-guide/operations/hotplug_volumes/

前提: 开启`HotplugVolumes`特性

首先声明一个数据卷
```
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: example-volume-hotplug
spec:
  source:
    blank: {}
  pvc:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 5Gi
```

然后热添加卷给虚拟机
```
virtctl addvolume vmi-fedora --volume-name=example-volume-hotplug
```

需要镜像支持
- quay.io/kubevirt/cdi-importer:v1.58.0
- quay.io/kubevirt/cdi-apiserver:v1.58.0

#### 网络配置使用

重点: TODO:
- SRIOV
- 桥接网络?

#### 虚拟机模板

#### 虚拟机克隆

依赖快照

#### 虚拟机快照

前提:
安装 volumesnapshotclass => 还略微有点复杂，挂起

关键字《k8s install volumesnapshotclass》

https://docs.trilio.io/kubernetes/appendix/csi-drivers/installing-volumesnapshot-crds
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-5.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-5.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-5.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml
```

https://github.com/kubernetes-csi/external-snapshotter/blob/master/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml

https://medium.com/linux-shots/point-in-time-snapshot-of-persistent-volume-data-with-kubernetes-volume-snapshots-abfafc210802
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-6.1/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-6.1/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-6.1/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml
```

https://ibrahimhkoyuncu.medium.com/kubernetes-complete-guide-to-kubernetes-volumesnapshot-pvc-backup-and-restore-and-automated-2aade2a3a90a

#### 热迁移虚拟机 => 验证ok

前提: 打开特性`LiveMigration`
写一个patch命令?
https://kubevirt.io/user-guide/operations/activating_feature_gates/#how-to-activate-a-feature-gate
```
cat << END > enable-feature-gate.yaml
---
apiVersion: kubevirt.io/v1
kind: KubeVirt
metadata:
  name: kubevirt
  namespace: kubevirt
spec:
  configuration:
    developerConfiguration: 
      featureGates:
        - LiveMigration
END

kubectl apply -f enable-feature-gate.yaml

kubectl edit kubevirt kubevirt -n kubevirt
```

开始迁移 => 验证成功
```
virtctl migrate testvm
```

## 部署KubeVirt

### 准备工作

```
yum install -y qemu-kvm libvirt virt-install bridge-utils
```

### 安装KubeVirt

https://github.com/kubevirt/kubevirt/releases/tag/v1.1.0
下载所有的yaml文件
- conformance.yaml
- demo-content.yaml
- disks-images-provider.yaml
- kubevirt-cr.yaml
- kubevirtoperator.v1.1.0.clusterserviceversion.yaml
- kubevirt-operator.yaml
- rbac-for-testing.yaml
- uploadproxy-nodeport.yaml

然后部署yaml
```
kubectl apply -f kubevirt-operator.yaml
kubectl apply -f kubevirt-cr.yaml
```

私有环境下部署，没有网络的话，先同步镜像
- quay.io/kubevirt/virt-operator:v1.1.0
  - quay.io/kubevirt/virt-api:v1.1.0
  - quay.io/kubevirt/virt-controller:v1.1.0
  - quay.io/kubevirt/virt-launcher:v1.1.0
  - quay.io/kubevirt/virt-handler:v1.1.0

- quay.io/kubevirt/disks-images-provider:v1.1.0
- quay.io/kubevirt/conformance:v1.1.0

- quay.io/kubevirt/cirros-container-disk-demo:latest

检查结果
```
kubectl get pods -n kubevirt
```

### 部署CDI（v1.47.1）

Containerized Data Importer（CDI）项目提供了用于使 PVC 作为 KubeVirt VM 磁盘的功能。建议同时部署 CDI：


### 安装virtctl客户端工具

https://github.com/kubevirt/kubevirt/releases/download/v1.1.0/virtctl-v1.1.0-linux-amd64

### 下载官方的vm.yaml文件（来生成官方的虚拟机）

```
wget https://kubevirt.io/labs/manifests/vm.yaml --no-check-certificate
```

文件内容如下：
```
apiVersion: kubevirt.io/v1
kind: VirtualMachine           #vm资源
metadata:
  name: testvm
spec:
  running: false            #当此字段为"Running",开始创建vmi资源
  template:
    metadata:
      labels:
        kubevirt.io/size: small
        kubevirt.io/domain: testvm
    spec:
      domain:
        devices:            #代表可以添加设备，比如：磁盘，网络...
          disks:            #硬盘设置。表示创建那种硬盘，这里表示有两块硬盘
            - name: containerdisk
              disk:              #将卷作为磁盘连接到vmi（虚拟机实例）
                bus: virtio      #表示要模拟的磁盘设备的类型，比如有：sata,scsi,virtio
            - name: cloudinitdisk
              disk:
                bus: virtio
          interfaces:            #选择定义的网络，下面的networks字段，就定义了一个"default"网络，这里就表示选择那个"default"网络
          - name: default
            masquerade: {}       #开启masquerade，这个表示使用网络地址转换（NAT）来通过Linux网桥将虚拟机连接至Pod网络后端。
        resources:
          requests:
            memory: 64M
      networks:          #网络的配置
      - name: default              #定义一个网络叫做"default"，这里表示使用Kubernetes默认的CNI，也就是使用默认的网络
        pod: {}
      volumes:
        - name: containerdisk
          containerDisk:
            image: quay.io/kubevirt/cirros-container-disk-demo      #使用此镜像创建个虚拟机。
        - name: cloudinitdisk
          cloudInitNoCloud:
            userDataBase64: SGkuXG4=
```

使用此模板文件创建虚拟机：
```
kubectl apply -f vm.yaml
virtualmachine.kubevirt.io/testvm created
kubectl get vm
NAME     AGE   STATUS    READY
testvm   9s    Stopped   False
```

查看vm的状态，在上面的概念中也将到了，vm中的"running"字段默认是"false"的，我们需要用virtctl命令行去启动此vm，然后virt-controller就会把vm中的"running"字段由"false"改为"true",之后在创建vmi资源，创建虚拟机等操作。

```
virtctl start testvm
VM testvm was scheduled to start
kubectl get pods
virt-launcher-testvm-nlrhp      0/3     PodInitializing   0              11s
kubectl get vmi # 等虚拟机pod运行正常后可以查看?
```

4、进入虚拟机控制台
```
virtctl console testvm
```

硬盘形式xml如下:
```
    <disk type='file' device='disk' model='virtio-non-transitional'>
      <driver name='qemu' type='qcow2' cache='none' error_policy='stop' discard='unmap'/>
      <source file='/var/run/kubevirt-ephemeral-disks/disk-data/containerdisk/disk.qcow2' index='2'/>
      <backingStore type='file' index='3'>
        <format type='qcow2'/>
        <source file='/var/run/kubevirt/container-disks/disk_0.img'/>
      </backingStore>
      <target dev='vda' bus='virtio'/>
      <alias name='ua-containerdisk'/>
      <address type='pci' domain='0x0000' bus='0x04' slot='0x00' function='0x0'/>
    </disk>
    <disk type='file' device='disk' model='virtio-non-transitional'>
      <driver name='qemu' type='raw' cache='none' error_policy='stop' discard='unmap'/>
      <source file='/var/run/kubevirt-ephemeral-disks/cloud-init-data/default/testvm/noCloud.iso' index='1'/>
      <backingStore/>
      <target dev='vdb' bus='virtio'/>
      <alias name='ua-cloudinitdisk'/>
      <address type='pci' domain='0x0000' bus='0x05' slot='0x00' function='0x0'/>
    </disk>
```

### 部署CDI（v1.47.1）

Containerized Data Importer（CDI）项目提供了用于使 PVC 作为 KubeVirt VM 磁盘的功能。建议同时部署 CDI：

FIXME: => 这个版本没有了，换一个吧!
```
#export VERSION=v1.47.1  => 这个版本没有了，换一个吧!
export VERSION=v1.58.0
kubectl create -f https://github.com/kubevirt/containerized-data-importer/releases/download/$VERSION/cdi-operator.yaml
kubectl create -f https://github.com/kubevirt/containerized-data-importer/releases/download/$VERSION/cdi-cr.yaml
```

查看pods
```
kubectl get pods -n cdi
NAME                               READY   STATUS    RESTARTS   AGE
cdi-apiserver-67944db5c9-6bmpz     1/1     Running   0          2m53s
cdi-deployment-6fcc76f596-pfjqq    1/1     Running   0          2m45s
cdi-operator-5f57676b77-vq6rj      1/1     Running   0          5m39s
cdi-uploadproxy-66bd867c6f-5fl2r   1/1     Running   0          2m41s
```

## 部署multus-cni

```
git clone https://github.com/k8snetworkplumbingwg/multus-cni -b v3.9.3
```

```
# 部署文件保存在项目的deployments目录下，具体链接如下：
# http://192.168.120.13/zoutengxiao/multus-cni/-/tree/3.9.3/deployments

# 精简版，没有控制器，由kubelet直接调用multus的二进制文件实现multus的功能
kubectl apply -f multus-daemonset.yml

# 完整版，采用C/S模式，二选一部署即可
kubectl apply -f multus-daemonset-thick-plugin.yml
```

## FAQ

#### The request is invalid: spec.template.spec.volumes[1]: HostDisk feature gate is not enabled

https://kubevirt.io/user-guide/operations/activating_feature_gates/
```
kubectl edit kubevirt kubevirt -n kubevirt
添加"HostDisk"
```

#### 启动虚拟机失败

=> 思路：使用网上成功的版本验证?
=> 使用版本v0.48.1验证可以...

关键字《virt-serial0-log-sigTerm: no such file or directory》
https://github.com/kubevirt/kubevirt/issues/10605 => 未解决

关键字《kubevirt could not create up serial console term file》
https://github.com/kubevirt/kubevirt/issues/10703 => 未解决

会尝试启动三次

pod日志: virt-launcher-testvm-w6w5g
```
{"component":"virt-launcher-monitor","level":"error","msg":"could not create up serial console term file: /var/run/kubevirt-private/7b9d1aec-3ffb-441c-848f-a7622d0fba10/virt-serial0-log-sigTerm","pos":"virt-launcher-monitor.go:72","reason":"open /var/run/kubevirt-private/7b9d1aec-3ffb-441c-848f-a7622d0fba10/virt-serial0-log-sigTerm: no such file or directory","timestamp":"2023-12-14T06:51:25.266542Z"}
```

## 参考文档

- [KubeVirt user guide - Accessing Virtual Machines](https://kubevirt.io/user-guide/virtual_machines/accessing_virtual_machines/)

https://documentation.suse.com/sles/15-SP4/html/SLES-all/article-kubevirt.html

[openshift的virt虚拟机](https://docs.openshift.com/container-platform/4.8/virt/virtual_machines/virt-accessing-vm-consoles.html)

https://medium.com/@tejasmane485/how-to-get-started-with-kubevirt-easy-explained-e916ca1b621

[Labs - KubeVirt quickstart with Minikube](https://kubevirt.io//quickstart_minikube/)
=> 用minikube测试?

[redhat openshift 虚拟化支持](https://access.redhat.com/documentation/zh-cn/openshift_container_platform/4.14/html/virtualization/index
