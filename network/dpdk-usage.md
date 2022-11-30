# dpdk使用

先从ovs-dpdk使用开始

## ovs dpdk原理

#### ovs dpdk 收发包原理

[基于DPDK的OVS虚拟交换机收发包处理流程](https://www.cnblogs.com/JCpeng/p/15167907.html)

[(好)ovs+dpdk下虚机数据接收流程](https://blog.csdn.net/zgy666/article/details/111175876)
=> 两张收包流程图

[virtio+ovs转发原理和性能分析](https://toutiao.io/posts/t6ker80/preview)

关键字《ovs+dpdk 性能提升》

[《深入浅出DPDK》——OVS中的DPDK性能加速](https://blog.csdn.net/qq_41976997/article/details/121608827)
DPDK加速的OVS性能比较
Intel发布过原始OVS与DPDK加速的OVS的性能比较，主要比较两种场景：一个是物理网口到物理网口，另一个是物理网口到虚拟机再到物理网口。

在这两种场景和256字节数据包的大小下，DPDK加速的OVS比原始OVS的性能分别提高了11.4倍和7.1倍。

如果用两个处理器核做OVS的转发逻辑比用一个处理器核体高了1.81倍，其可扩展性还是不错的。

## ubuntu 20.04使用ovs-dpdk

参考资料:
- [OpenVswitch-DPDK](https://ubuntu.com/server/docs/openvswitch-dpdk)
- [Configure Open vSwitch with Data Plane Development Kit on Ubuntu Server 17.04](https://www.intel.cn/content/www/cn/zh/developer/articles/technical/set-up-open-vswitch-with-dpdk-on-ubuntu-server.html)

#### 准备系统

可以使用一个虚拟机来简单验证:
- cpu: 8核
  小一点也没关系 (直通模式,开启嵌套虚拟化)
- 内存: 8G
  给2G给ovs-dpdk, 测两个虚拟机,每个1G
- 磁盘: 200G
- 网卡: 随便弄, 3,4个, virtio, e1000,等

#### 安装软件

安装ovs, libvirt, qemu
```
sudo apt install -y openvswitch-switch-dpdk \
    qemu-kvm libvirt-daemon-system
```

#### 配置iommu,hugepage等

编辑文件 /etc/default/grub
```
GRUB_CMDLINE_LINUX_DEFAULT="default_hugepagesz=1G hugepagesz=1G hugepages=4 iommu=pt intel_iommu=on"
```

grub更新, 重启生效
```
sudo update-grub
sudo reboot
```

#### 配置ovs+dpdk

配额ovs使用dpdk, 以及大页内存
```
sudo update-alternatives --set ovs-vswitchd /usr/lib/openvswitch-switch-dpdk/ovs-vswitchd-dpdk
sudo ovs-vsctl set Open_vSwitch . "other_config:dpdk-init=true"
# Allocate 2G huge pages (not Numa node aware)
ovs-vsctl set Open_vSwitch . "other_config:dpdk-alloc-mem=2048"
sudo systemctl restart openvswitch-switch
```

#### 配置虚拟机

使用centos镜像定义一个虚拟机, 另外一个虚拟机类似(改一下uuid,镜像,网卡mac,vhost path)
```
<domain type='kvm'>
  <name>centos7</name>
  <uuid>ab953e2f-9d16-4955-bb43-1178230ee625</uuid>
  <memory unit='KiB'>1048576</memory>
  <currentMemory unit='KiB'>1048576</currentMemory>
  <memoryBacking>
    <hugepages/>
  </memoryBacking>
  <vcpu placement='static'>2</vcpu>
  <os>
    <type arch='x86_64' machine='pc'>hvm</type>
  </os>
  <cpu mode='custom'>
    <model fallback='allow'/>
    <numa>
      <cell id='0' cpus='0-1' memory='1048576' unit='KiB' memAccess='shared'/>
    </numa>
  </cpu>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
    <emulator>/usr/bin/kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='/home/vm-images/centos7.img'/>
      <target dev='vda' bus='virtio'/>
    </disk>

    <interface type='vhostuser'>
      <mac address='56:48:4f:53:54:e2'/>
      <source type='unix' path='/tmp/vhost-user1' mode='server'/>
      <model type='virtio'/>
    </interface>

    <serial type='pty'>
      <target port='1'></target>
    </serial>

  </devices>

</domain>
```

#### 直接使用qemu启动虚拟机

使用串口登录使用虚拟机验证: -serial stdio
```
/usr/libexec/qemu-kvm -smp 2 -m 1024 -serial stdio \
  -hda /home/vm-images/centos7.img \
  -net none -monitor pty -nographic \
  -chardev socket,id=char1,path=/tmp/vhost-user1,server \
  -netdev type=vhost-user,id=mynet1,chardev=char1,vhostforce \
  -device virtio-net-pci,mac=fa:16:3e:4d:58:6f,netdev=mynet1 \
  -object memory-backend-file,id=mem,size=1024M,mem-path=/mnt/huge,share=on \
  -numa node,memdev=mem -mem-prealloc
```

#### 创建br-dpdk桥

创建br-dpdk
```
ovs-vsctl add-br br-dpdk -- set bridge br-dpdk datapath_type=netdev
```

启动虚拟机之前,先创建vhostuserclient接口
```
ovs-vsctl add-port br-dpdk vhost-user-client1 -- set Interface vhost-user-client1 type=dpdkvhostuserclient options:vhost-server-path=/tmp/vhost-user1
ovs-vsctl add-port br-dpdk vhost-user-client2 -- set Interface vhost-user-client2 type=dpdkvhostuserclient options:vhost-server-path=/tmp/vhost-user2
```

#### 加入dpdk物理网卡

解绑物理网卡驱动驱动
```
modprobe vfio-pci
dpdk-devbind.py --status
# 绑定之后,内核就看不到旧网卡了
dpdk-devbind.py --bind=vfio-pci 00:09.0
dpdk-devbind.py --bind=vfio-pci enp1s0f1
```

加入到br-dpdk桥
```
ovs-vsctl add-port br-dpdk dpdk0 -- set Interface dpdk0 type=dpdk options:dpdk-devargs=00:09.0
```

## centos7.9 编译安装ovs+dpdk

参考资料

- [使用 DPDK 优化 VirtIO 和 OVS 网络](https://my.oschina.net/LastRitter/blog/1807032)
  版本环境旧了,用下面新版本dpdk和ovs,否则有编译问题

- [centos 7.9 编译 ovs+ dpdk](https://zhuanlan.zhihu.com/p/455967651)

### 编译ovs+dpdk

#### 编译dpdk

安装开发依赖包
```
yum install -y gcc numactl numactl-libs numactl-devel kernel kernel-debug kernel-debug-devel kernel-devel kernel-doc kernel-headers libpcap-devel
# 或者用如下命令(有些环境已经有kernel-devel包了)
yum install -y numactl-devel libpcap-devel
```

获取源码
```
mkdir -p /opt/ovs && cd /opt/ovs
git clone https://github.com/DPDK/dpdk.git
cd dpdk &&  git checkout v19.11

# 或者使用发行版
wget https://fast.dpdk.org/rel/dpdk-19.11.10.tar.xz
tar -xJf dpdk-*.tar.xz
ln -sf dpdk-stable-19.11.10 dpdk
```

设置环境变量
```
export OVS_ROOT=/opt/ovs
export DPDK_DIR=$OVS_ROOT/dpdk
export DPDK_BUILD=$DPDK_DIR/build
export DPDK_INSTALL=$DPDK_DIR/install

export DPDK_TARGET=x86_64-native-linuxapp-gcc
```

配置和编译：
```
make config T=$DPDK_TARGET
make -j8 && make install DESTDIR=$DPDK_INSTALL
# 可选, dpdk示例
# make -j8 -C examples RTE_SDK=$DPDK_DIR RTE_TARGET=build O=$DPDK_INSTALL/examples
```

#### 编译ovs

安装开发依赖包
```
yum -y install gcc autoconf automake libtool kernel kernel-devel
# 或者用如下命令(有些环境已经有kernel-devel包了)
yum -y install gcc autoconf automake libtool
```

获取源码
```
mkdir -p /opt/ovs && cd /opt/ovs
git clone https://github.com/openvswitch/ovs.git && cd ovs
git checkout v2.13.6

# 或者使用发行版
wget https://www.openvswitch.org/releases/openvswitch-2.13.6.tar.gz
tar -xzf openvswitch-2.13.6.tar.gz
ln -sf openvswitch-2.13.6 ovs
```

设置环境变量
```
export OVS_ROOT=/opt/ovs

export DPDK_DIR=$OVS_ROOT/dpdk
export DPDK_BUILD=$DPDK_DIR/build
export DPDK_INSTALL=$DPDK_DIR/install
export DPDK_TARGET=x86_64-native-linuxapp-gcc

export OVS_DIR=$OVS_ROOT/target-dpdk
export PATH=$OVS_DIR/bin/:$OVS_DIR/share/openvswitch/scripts:$PATH
```

开始编译(支持dpdk), 可能还需要安装python3
```
cd /opt/ovs/ovs
./boot.sh
mkdir -pv $OVS_ROOT/build-dpdk $OVS_ROOT/target-dpdk && cd $OVS_ROOT/build-dpdk

../ovs/configure --with-dpdk=$DPDK_BUILD --with-linux=/lib/modules/$(uname -r)/build --prefix=$OVS_ROOT/target-dpdk CFLAGS="-g -Ofast"

make -j8 'CFLAGS=-g -Ofast -march=native' && make install
mkdir -pv $OVS_ROOT/target-dpdk/modules && cp -vf $OVS_ROOT/build-dpdk/datapath/linux/*ko $OVS_ROOT/target-dpdk/modules/
```

#### 编译ovs FAQ

编译报错, 原因是内核-devel包跟内核不匹配, reboot换一下内核即可
```
make: *** /lib/modules/3.10.0-1160.el7.x86_64/build: No such file or directory.  Stop.
```

编译报错, 原因是centos7.9的接口名称有改动, 代码改为ndo_change_mtu_rh74即可
=> 后续用了更新的dpdk库, 没有这个问题了
```
/opt/ovs/dpdk/build/build/lib/librte_eal/linuxapp/kni/kni_net.c:714:2: error: unknown field ‘ndo_change_mtu’ specified in initializer
  .ndo_change_mtu = kni_net_change_mtu,
```

### 配置并启动ovs

#### 配置hugepage+iommu

使用grubby给内核参数加上iommu和hugepage, 重启生效
```
grubby --update-kernel=/boot/vmlinuz-`uname -r` --args="intel_iommu=on iommu=pt iommu=pt"
grubby --update-kernel=/boot/vmlinuz-`uname -r` --args="hugepagesz=1G default_hugepagesz=1G"
```

#### 启动停止OVS

首次处理比较复杂, 待简化
```
export OVS_DIR=$OVS_ROOT/target-dpdk && cd $OVS_DIR
mkdir -pv $OVS_DIR/var/run/openvswitch $OVS_DIR/etc/openvswitch

# 创建ovsdb-server数据库：
$OVS_DIR/bin/ovsdb-tool create $OVS_DIR/etc/openvswitch/conf.db $OVS_DIR/share/openvswitch/vswitch.ovsschema

# 启动ovsdb-server数据库服务：
$OVS_DIR/sbin/ovsdb-server --remote=punix:$OVS_DIR/var/run/openvswitch/db.sock --remote=db:Open_vSwitch,Open_vSwitch,manager_options --pidfile --detach

# 初始化数据库（只在第一次运行时需要执行）：
$OVS_DIR/bin/ovs-vsctl --no-wait init

# 查看依赖的内核模块：
cat /usr/lib/modules/`uname -r`/modules.dep | awk '$1~"^extra/openvswitch"{for(i=2;i<=NF;i++) {print $i}}' | xargs echo
cat /usr/lib/modules/`uname -r`/modules.dep | awk '$1~"openvswitch"{for(i=2;i<=NF;i++) {print $i}}' | xargs echo
kernel/net/ipv6/netfilter/nf_nat_ipv6.ko.xz kernel/net/ipv4/netfilter/nf_nat_ipv4.ko.xz kernel/net/ipv6/netfilter/nf_defrag_ipv6.ko.xz kernel/net/netfilter/nf_nat.ko.xz kernel/net/netfilter/nf_conntrack.ko.xz kernel/net/ipv4/udp_tunnel.ko.xz kernel/lib/libcrc32c.ko.xz

# 加载openvswitch.ko依赖的内核模块：
cat /usr/lib/modules/`uname -r`/modules.dep | awk '$1~"^extra/openvswitch"{for(i=2;i<=NF;i++) {mod=gensub(/\.ko\.xz/,"",1,gensub(/.*\//,"",1,$i));cmd="modprobe " mod;system(cmd)}}'
cat /usr/lib/modules/`uname -r`/modules.dep | awk '$1~"openvswitch"{for(i=2;i<=NF;i++) {mod=gensub(/\.ko\.xz/,"",1,gensub(/.*\//,"",1,$i));cmd="modprobe " mod;system(cmd)}}'
modprobe geneve; modprobe gre; modprobe ip6_udp_tunnel; modprobe ip_gre; modprobe ip_tunnel; modprobe libcrc32c; modprobe nf_conntrack; modprobe nf_defrag_ipv6; modprobe nf_nat; modprobe nf_nat_ipv4; modprobe nf_nat_ipv6; modprobe udp_tunnel; modprobe vxlan; modprobe tunnel6;

[root@localhost ~]#  modinfo $OVS_DIR/modules/openvswitch.ko |grep depends
depends:        nf_conntrack,tunnel6,nf_nat,nf_defrag_ipv6,libcrc32c,nf_nat_ipv6,nf_nat_ipv4

# 加载openvswitch.ko内核模块：
insmod $OVS_DIR/modules/openvswitch.ko
# => 上面没有加载依赖内核模块, 这里就频繁报错的: modprobe nf_nat
# openvswitch: Unknown symbol nf_conntrack_find_get (err 0)

# 启动ovs-vswitchd守护进程：
$OVS_DIR/sbin/ovs-vswitchd --pidfile --detach --log-file

# 为ovs-vswitchd增加dpdk支持：
ovs-vsctl --no-wait set Open_vSwitch . other_config:dpdk-init=true
```

使用命令手动停止
```
pkill -9 ovs
rm -rfv $OVS_DIR/var/run/openvswitch $OVS_DIR/etc/openvswitch/ $OVS_DIR/etc/openvswitch/conf.db
```

## ovs dpdk参数配置

#### 绑定内存

例如绑定2048MB内存
```
ovs-vsctl set Open_vSwitch . "other_config:dpdk-alloc-mem=2048"
```

#### 绑定cpu

例如绑定cpu核心1,2,3=>0xE
```
ovs-vsctl set Open_vSwitch . "other_config:pmd-cpu-mask=e"
```

## FAQ

#### 获取当前ovs配置

```
ovs-vsctl clear Open_vSwitch . "other_config
ovs-vsctl get Open_vSwitch . "other_config"
{dpdk-extra="-w 0000:00:00.0", dpdk-init="true", dpdk-socket-mem="2048", pmd-cpu-mask=e}
```

#### 虚拟机之间网络不通

之前没有配置shared memory, 两个虚拟机起来数据不同, 配置之后就可以了
```xml
  <cpu mode='custom'>
    <numa>
      <cell id='0' cpus='0-1' memory='1048576' unit='KiB' memAccess='shared'/>
    </numa>
  </cpu>
```

#### connection has been destroyed

ovs疯狂报错
```
netdev_dpdk|INFO|vHost Device '/tmp/vhost-user2' connection has been destroyed
```

加了内存配置就没有了?之前只配置了dpdk-init=true
```
ovs-vsctl set Open_vSwitch . "other_config:dpdk-alloc-mem=2048"
```

#### 虚拟机e1000网卡绑定vfio-pci失败

暂无解决方法, 再查查有方法没?

而且没有 /sys/kernel/iommu_groups/ 数据, 虚拟机不支持iommu?

```
dpdk-devbind.py --bind=vfio-pci 0000:00:05.0
Error: unbind failed for 0000:00:05.0 - Cannot open /sys/bus/pci/drivers/e1000/unbind

dmesage查看错误
[ 1953.950321] vfio-pci: probe of 0000:00:04.0 failed with error -22
[ 1953.950362] vfio-pci: probe of 0000:00:04.0 failed with error -22
```

#### 虚拟机关机qemu一直不退出?

原来是我的libvirt虚拟机配置没有加电源管理, 加上即可
```
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>

acpi
ACPI is useful for power management, for example, with KVM or HVF guests it is required for graceful shutdown to work.
```

虚拟机内部日志, 关机变为挂起了
```
systemd-shutdown[1]: Syncing filesystems and block devices.
systemd-shutdown[1]: Powering off.
System halted.
```

关机成功的虚拟机内部日志
```
systemd-shutdown[1]: Syncing filesystems and block devices.
systemd-shutdown[1]: Powering off.
ACPI: Preparing to enter system sleep state S5
Power down.
```

#### ovs启动失败: unsupported cpu type

虚拟机cpu兼容模式，改为直通模式即可
```
ovs-ctl[1736]: ERROR: This system does not support "SSSE3".
ovs-ctl[1736]: Please check that RTE_MACHINE is set correctly.
ovs-ctl[1736]: EAL: FATAL: unsupported cpu type.
ovs-ctl[1736]: 2022-11-29T14:01:23Z|00014|dpdk|EMER|Unable to initialize DPDK: Operation not supported
ovs-ctl[1736]: ovs-vswitchd: Cannot init EAL (Operation not supported)
ovs-vswitchd[1736]: ovs|00013|dpdk|ERR|EAL: unsupported cpu type.
ovs-vswitchd[1736]: ovs|00014|dpdk|EMER|Unable to initialize DPDK: Operation not supported
ovs-vswitchd[1735]: ovs|00002|daemon_unix|ERR|fork child died before signaling startup (killed (Aborted), core dumped)
ovs-vswitchd[1735]: ovs|00003|daemon_unix|EMER|could not detach from foreground session
```

#### ovs启动失败: Unable to initialize DPDK: Permission denied

没有配置hugepage, 配置内核开启即可
```
systemd[1]: ovs-vswitchd.service: Control process exited, code=exited, status=1/FAILURE
systemd[1]: ovs-vswitchd.service: Failed with result 'exit-code'.
systemd[1]: Failed to start Open vSwitch Forwarding Unit.
systemd[1]: ovs-vswitchd.service: Scheduled restart job, restart counter is at 4.
systemd[1]: Stopped Open vSwitch Forwarding Unit.
systemd[1]: Starting Open vSwitch Forwarding Unit...
ovs-ctl[1343]: EAL: FATAL: Cannot get hugepage information.
ovs-ctl[1343]: 2022-11-29T14:05:34Z|00021|dpdk|EMER|Unable to initialize DPDK: Permission denied
ovs-ctl[1343]: ovs-vswitchd: Cannot init EAL (Permission denied)
ovs-vswitchd[1343]: ovs|00020|dpdk|ERR|EAL: Cannot get hugepage information.
ovs-vswitchd[1343]: ovs|00021|dpdk|EMER|Unable to initialize DPDK: Permission denied
ovs-vswitchd[1342]: ovs|00002|daemon_unix|ERR|fork child died before signaling startup (killed (Aborted), core dumped)
ovs-ctl[1342]: ovs-vswitchd: could not detach from foreground session
ovs-vswitchd[1342]: ovs|00003|daemon_unix|EMER|could not detach from foreground session
ovs-ctl[1297]:  * Starting ovs-vswitchd
```

#### ovs添加物理网卡报错

需要将一个iommu group的网卡都改为vfio驱动

ovs日志报错
```
00093|dpdk|ERR|EAL: 0000:01:00.1 VFIO group is not viable! Not all devices in IOMMU group bound to VFIO or unbound
00094|dpdk|ERR|EAL: Driver cannot attach the device (0000:01:00.1)
00095|dpdk|ERR|EAL: Failed to attach device on primary process
00096|netdev_dpdk|WARN|Error attaching device '0000:01:00.1' to DPDK
00097|netdev|WARN|dpdk0: could not set configuration (Invalid argument)
00098|dpdk|ERR|Invalid port_id=32
```

#### 其他xxx

暂不知道是不是问题

查看libvirt虚拟机日志
```
kvm: -chardev socket,id=charnet0,path=/tmp/vhost-user1,server: info: QEMU waiting for connection on: disconnected:unix:/tmp/vhost-user1,server
ev/pts/2 (label charserial0)
kvm: warning: host doesn't support requested feature: CPUID.80000001H:ECX.svm [bit 2]
kvm: warning: host doesn't support requested feature: CPUID.80000001H:ECX.svm [bit 2]
kvm: Failed to read from slave.
kvm: Failed to set msg fds.
kvm: vhost VQ 0 ring restore failed: -1: No such file or directory (2)
kvm: Failed to set msg fds.
kvm: vhost VQ 1 ring restore failed: -1: No such file or directory (2)
```

另外一个虚拟机
```
kvm: -chardev socket,id=charnet0,path=/tmp/vhost-user2,server: info: QEMU waiting for connection on: disconnected:unix:/tmp/vhost-user2,server
ev/pts/3 (label charserial0)
kvm: warning: host doesn't support requested feature: CPUID.80000001H:ECX.svm [bit 2]
kvm: warning: host doesn't support requested feature: CPUID.80000001H:ECX.svm [bit 2]
kvm: Failed to read from slave.
kvm: Failed to set msg fds.
kvm: vhost VQ 0 ring restore failed: -1: Input/output error (5)
kvm: Failed to set msg fds.
kvm: vhost VQ 1 ring restore failed: -1: Input/output error (5)
```
