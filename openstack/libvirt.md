# libvirt用法

## libvirt 定义一个虚拟机

[15 使用 virsh 配置虚拟机](https://documentation.suse.com/zh-cn/sles/15-SP2/html/SLES-all/cha-libvirt-config-virsh.html)

```
<domain type='kvm'>
  <name>centos7</name>
  <uuid>ab953e2f-9d16-4955-bb43-1178230ee625</uuid>
  <memory unit='KiB'>1048576</memory>
  <currentMemory unit='KiB'>1048576</currentMemory>
  <vcpu placement='static'>2</vcpu>
  <os>
    <type arch='x86_64' machine='pc'>hvm</type>
  </os>
  <cpu mode='custom'>
    <model fallback='allow'/>
  </cpu>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='/home/vm-images/centos7.qcow2'/>
      <target dev='vda' bus='virtio'/>
    </disk>
  </devices>
</domain>
```

## 其他

关键字`virsh web console`
Managing KVM Virtual Machines with Cockpit Web Console in Linux
https://www.tecmint.com/manage-kvm-virtual-machines-using-cockpit-web-console/

## nvram文件权限问题

使用libvirt hook解决
=> 新增hook脚本, 需要重启libvirt
```
cat /etc/libvirt/hooks/qemu
#!/bin/bash

# 在虚拟机启动时设置NVRAM权限
if [ "$2" = "prepare" ] || [ "$2" = "start" ]; then
    VM_NAME="$1"
    NVRAM_FILE="/var/lib/libvirt/qemu/nvram/${VM_NAME}_VARS.fd"

    if [ -f "$NVRAM_FILE" ]; then
        chown kylin-ksvd:kvm "$NVRAM_FILE"
        chmod 660 "$NVRAM_FILE"
    fi
fi
```

rc.ksvd启动脚本处理
```
mkdir -p /etc/libvirt/hooks && install -m 755 /usr/lib/ksvd/bin/qemu-chmod-nvram-hook.sh /etc/libvirt/hooks/qemu && systemctl restart libvirtd
```

## console安装虚拟机

https://gist.github.com/srramasw/a44b71c1573071a2136a
待验证

```
qemu-img create -f qcow2 /var/lib/libvirt/images/csr_3_13_03_disk.qcow2 8G
virt-install               \
      --connect=qemu:///system  \
      --name=csr_3_13_03          \
      --description "CSR 3.13 VM #3"   \
      --os-type=linux           \
      --os-variant=rhel4        \
      --arch=x86_64             \
      --cpu host                \
      --vcpus=1,sockets=2,cores=1,threads=1   \
      --hvm                     \
      --ram=4096                \
      --cdrom=/home/srramasw/csr_images/csr1000v-universalk9.03.13.00.S.154-3.S-ext.iso \
      --disk path=/var/lib/libvirt/images/csr_03_13_03_disk.qcow2,bus=virtio,size=8,sparse=false,cache=none,format=qcow2   \
      --console pty,target_type=virtio  \
      --video=vga                       \
      --graphics vnc            \
      --serial tcp,host=:4577,mode=bind,protocol=telnet   \
      --network bridge=virbr0,model=virtio                \
      --noreboot
```

## 大页内存

```
  <memoryBacking>
    <hugepages/>
  </memoryBacking>
```

```
libvirt: QEMU Driver error : 内部错误：process exited while connecting to monitor: 2022-11-24 21:41:17.731+0000: Domain id=23 is tainted: host-cpu
2022-11-24T21:41:22.309038Z qemu-kvm: unable to map backing store for guest RAM: Cannot allocate memory
Nov-25 05:41:22:5473 E ^[[37;41mcreate vm failed: code: hugepage enable 1, msg: 内部错误：process exited while connecting to monitor: 2022-11-24 21:41:17.731+0000: Domain id=23 is tainted: host-cpu^[[m
```

https://www.cnblogs.com/weiweifeng/p/8194356.html

这个问题的原因可能是：

- 1.host 没有设置足够多的 hugepage

- 2.guest 设置的内存大小超出了 host 的 hugepage

解决办法：

- 1.检查 host hugepage 设置

```
cat /proc/meminfo |grep -i huge
Hugepagesize * HugePages_Free 就是 guest 可以分配的内存。
```

## cpu直通

```
<cpu mode='host-passthrough'>
 <model fallback='allow'/>
 ...
</cpu>
```

## 在线修改磁盘iops限制

gpt关键字《virsh 查询 block_set_io_throttle结果》

最后发现是group_name这个参数起的作用 => 这个能复现两个磁盘iops一样
```
virsh qemu-monitor-command e82dec4f-6d82-3956-3c8e-6cbe0c31da2e '{"execute":"query-block"}' # 查询iops信息
virsh blkdeviotune $DOMAIN vda --write-iops-sec 600 --group-name '1' --live
```

## 在线添加内存

virsh attach-device ${DOMAIN} mem.xml --live
```
<memory model='dimm'>
  <target>
    <size unit='KiB'>1048576</size>
    <node>0</node>
  </target>
  <alias name='dimm0'/>
  <address type='dimm' slot='0' base='0x100000000'/>
</memory>
```

原来不能乱指定地址, 去除即可
```
error: 内部错误：无法执行 QEMU 命令 'device_add'：can't add memory device [0x100000000:0x40000000], usable range for memory devices [0x240000000:0x80200000000]
```

## 在线添加磁盘

virsh attach-device ${DOMAIN} disk.xml --live
```
<disk type='file' device='disk'>
  <driver name='qemu' type='qcow2' cache='none'/>
  <source file='/home/test.img'/>
  <target dev='vdc' bus='virtio'/>
  <address type='pci' bus='0x02' slot='0x02' function='0x0'/>
</disk>
```

添加一个带wwn的scsci磁盘
```
<disk type='file' device='disk'>
  <driver name='qemu' type='qcow2' cache='none'/>
  <source file='/home/test.img'/>
  <target dev='sda' bus='scsi'/>
  <wwn>6001405127fe9894</wwn>
</disk>
```

添加裸设备磁盘
```
<disk type='block' device='disk'>
  <driver name='qemu' type='raw' cache='none'/>
  <source dev='/dev/nvme0n1'/>
  <target dev='sda' bus='scsi'/>
</disk>
```

可能遇到的错误
* error: XML 错误：磁盘经销商超过 8 个字符
* error: 不支持的配置：只有 ide 和 scsi 磁盘支持 wwn
* error: 内部错误：无法执行 QEMU 命令 '__com.redhat_drive_add'：Device 'drive-scsi0-0-0-1' could not be initialized
  无法在线添加吧


## 在线添加网卡

virsh attach-device  e973ac81-6199-3177-6a19-21dece2693e6 if.xml --live
Device attached successfully

```xml
<interface type='bridge'>
  <mac address='52:54:84:01:03:04'/>
  <source bridge='mdvs2'/>
  <virtualport type='openvswitch' />
  <model type='virtio'/>
  <driver name='vhost'/>
</interface>
```

配置ovs桥
```
<interface type='bridge'>
<source bridge='mdvs2'/>
<virtualport type='openvswitch' />
```

测试qemu-ga是否可用
```
# ${DOMAIN}表示虚拟机名字或UUID
virsh qemu-agent-command ${DOMAIN} '{"execute":"guest-ping"}'

#如果返回以下内容则表示qemu-ga可用
{"return":{}}
```

查询qemu-ga支持的命令
```bash
virsh qemu-agent-command ${DOMAIN} '{"execute":"guest-info"}'
```

qemu-ga写文件
```bash
virsh qemu-agent-command
```

应该会看到支持很多命令，由于接下来做的实验需要用到如下命令，因此请先确认是否均支持

* guest-exec：执行命令（异步操作）
* guest-exec-status：查看执行命令的结果
* guest-file-open：打开文件，获得句柄
* guest-file-write：写文件（传递base64）
* guest-file-close：关闭文件


qemu-ga执行命令


```
virsh qemu-agent-command centos8 --cmd '{"execute":"guest-exec","arguments":{"path":"mkdir","arg":["-p","/root/.ssh"]}}'
{"return":{"pid":9468}}

virsh qemu-agent-command centos8 '{"execute":"guest-exec-status","arguments":{"pid":9905}}'
{"return":{"exitcode":0,"exited":true}}

virsh qemu-agent-command $domain --cmd '{"execute":"guest-exec","arguments":{"path":"touch","arg":["/root/.ssh/adam-test"],"capture-output":true}}'

# 打开文件（以读写方式打开），获得句柄 virsh qemu-agent-command centos8 --cmd '{"execute":"guest-file-open", "arguments":{"path":"/root/.ssh/authorized_keys","mode":"w+"}}'
{"return":1001}
# 写文件，假设上一步返回{"return":1000}，1000就是句柄
virsh qemu-agent-command centos8 --cmd '{"execute":"guest-file-write", "arguments":{"handle":1001,"buf-b64":"xxx"}}'

```

TODO: 句柄泄漏的问题?
写配置文件
```
virsh qemu-agent-command $domain --cmd '{"execute":"guest-file-open", "arguments":{"path":"/usr/local/bin/kylin-vr.yaml","mode":"w"}}'
{"return":1000}
# 写文件，假设上一步返回{"return":1000}，1000就是句柄
virsh qemu-agent-command $domain --cmd '{"execute":"guest-file-write", "arguments":{"handle":1000,"buf-b64":"aGVsbG86IHRydWUK"}}'
{"return":{"count":12,"eof":false}}
# 关闭文件
virsh qemu-agent-command $domain '{"execute":"guest-file-close", "arguments":{"handle":1000}}'
```

测试编写配置文件
```
virsh qemu-agent-command $domain --cmd '{"execute":"guest-file-open", "arguments":{"path":"/etc/kylin-vr/kylin-vr.yaml","mode":"w"}}'
{"return":1000}
# 写文件，假设上一步返回{"return":1000}，1000就是句柄
virsh qemu-agent-command $domain --cmd '{"execute":"guest-file-write", "arguments":{"handle":1000,"buf-b64":"IyAxMC45MC4yLjE4OS0xOTMsIHp5YiAxOTQtMTk2CiMgMTAuOTAuMi4yNTAtMjU0CiMgMTAuOTAuMy4yMC0zNiwgMzctMznlt7LnlKgKaWZfbGlzdDoKICAgLSBpcGFkZHI6IDEwLjkwLjMuMzcKICAgICBwcmVmaXg6IDI0CiAgICAgbWFjOiA1Mjo1NDo4NDowMDowODo0NgogICAgIGdhdGV3YXk6IDEwLjkwLjMuMQogICAtIGlwYWRkcjogMTkyLjE2OC4xMDAuMjU0CiAgICAgcHJlZml4OiAyNAogICAgIG1hYzogNTI6NTQ6ODQ6MTE6MDA6MDQKZWlwX2xpc3Q6CiAgLSBlaXA6IDEwLjkwLjIuMTg5CiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMjAzCiAgLSBlaXA6IDEwLjkwLjIuMjUwCiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMTkwCiAgLSBlaXA6IDEwLjkwLjIuMjUxCiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMTkxCiAgLSBlaXA6IDEwLjkwLjIuMjUyCiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMjAwCiAgLSBlaXA6IDEwLjkwLjIuMjUzCiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMTMKICAtIGVpcDogMTAuOTAuMy4yMQogICAgdm0taXA6IDE5Mi4xNjguMTAwLjMxCiAgLSBlaXA6IDEwLjkwLjMuMjIKICAgIHZtLWlwOiAxOTIuMTY4LjEwMC4zMgogIC0gZWlwOiAxMC45MC4zLjIzCiAgICB2bS1pcDogMTkyLjE2OC4xMDAuMzMKcG9ydF9mb3J3YXJkX2xpc3Q6CiAgLSBlaXA6IDEwLjkwLjIuMjU0CiAgICBwcm90b2NhbDogdGNwCiAgICBwb3J0OiA4MAogICAgZW5kX3BvcnQ6IDgyCiAgICB2bS1wb3J0OiA4MAogICAgdm0taXA6IDE5Mi4xNjguMTAwLjE5MAo="}}'
{"return":{"count":12,"eof":false}}
# 关闭文件
virsh qemu-agent-command $domain '{"execute":"guest-file-close", "arguments":{"handle":1000}}'
```





执行kylin-vr脚本
```
domain=468e4a0e-e647-38b0-6f37-ac7d2cb59585
virsh qemu-agent-command $domain --cmd '{"execute":"guest-exec","arguments":{"path":"python3","arg":["/usr/local/bin/kylin-vr.py", "/usr/local/bin/adam.yaml"]}}'
{"return":{"pid":23453}}

virsh qemu-agent-command $domain '{"execute":"guest-exec-status","arguments":{"pid":23478}}'
```


使用firewalld配置iptables规则?
```
# /etc/firewalld/firewalld.conf
# DefaultZone=trusted

/etc/firewalld/direct.xml
<?xml version="1.0" encoding="utf-8"?>
<direct>
  <rule priority="0" table="filter" ipv="ipv4" chain="INPUT">-i docker0 -j ACCEPT</rule>
</direct>
```

禁用ipv6 《network-scripts disable ipv6》
```
# XXX: 禁用ipv6 <network-scripts disable ipv6>
# https://www.looklinux.com/how-to-disable-ipv6-in-centos-and-redhat/
# /etc/sysctl.conf
```

## 常用设备

#### cdrom

```
<disk type='file' device='cdrom'>
  <driver name='qemu' type='raw'/>
  <source file='xxx.iso'/>
  <target dev='hda' bus='ide'/>
  <readonly/>
</disk>
```

#### vnc连接

```
<graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0' />
<graphics type='vnc' port='-1' autoport='yes' passwd='password' listen='0.0.0.0' keymap='en-us'/>
```

## 其他

#### virt-manager连接ssh密码问题

关键字《openssh askpass virt manager》
https://askubuntu.com/questions/1045395/kvm-connection-to-a-remote-server-ubuntu-18-04
```
sudo apt install ssh-askpass-gnome
```

或者配置共享ssh通道, 配置文件 ~/.ssh/config, 然后用ssh联机一次服务端
```
ControlMaster auto
ControlPath /tmp/ssh_mux_%h_%p_%r
```

或者注入ssh密钥，通过密钥免密访问

#### libvirt开启调试日志

关键字《libvirt开启调试日志》

/etc/libvirt/libvirtd.conf
```
log_level=1
log_outputs="1:file:/var/log/libvirt/libvirtd.log"
```

#### arm64设备pci顺序固定

arm64下需要占用pci插槽的设备列表

* usb
* sata controller
* scsi controller
* video
* memballoon

比较常见的列表类型设备
* interface
* disk
* crdom

示例
```
<video>
  <model type='virtio' vram='16384' heads='1' primary='yes' />
  <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
</video>

<memballoon model='virtio'>
  <stats period='10'/>
  <address type='pci' domain='0x0000' bus='0x00' slot='0x0c' function='0x0'/>
</memballoon>

<controller type='usb' index='1' model='qemu-xhci' ports='15'>
  <address type='pci' domain='0x0000' bus='0x00' slot='0x1c' function='0x0'/>
</controller>

<controller type='sata' index='0'>
  <address type='pci' bus='0x00' slot='0x01' function='0x1'/>
</controller>

<controller type='scsi' index='0' model='virtio-scsi'>
  <address type='pci' bus='0x00' slot='0x01' function='0x2'/>
</controller>

<controller type='virtio-serial' index='0'>
  <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
</controller>
```

## systemctl启动卡住

发现在等待
```
systemctl list-jobs | grep libvirt
  250 libvirtd.service                                             start waiting
```

ai查到依赖服务等待, remote-fs.target
```
systemctl list-jobs | grep remote
  241 remote-fs.target                                             start waiting
  176 remote-fs-pre.target                                         start waiting
```

发现启动过，然后又停止了?
```
systemctl status remote-fs.target
● remote-fs.target - Remote File Systems
   Loaded: loaded (/usr/lib/systemd/system/remote-fs.target; enabled; vendor preset: enabled)
   Active: inactive (dead)
     Docs: man:systemd.special(7)

Jan 23 11:36:28 localhost.localdomain systemd[1]: Reached target Remote File Systems.
Jan 23 11:36:30 localhost.localdomain systemd[1]: Stopped target Remote File Systems.
```

ai给libvirt增加了配置，还是启动waiting
=> 我给注释了remote-fs的依赖，可以启动了!
```
# /etc/systemd/system/libvirtd.service.d/override.conf
[Unit]
# 移除可能导致阻塞的依赖
After=network.target dbus.service local-fs.target virtlogd.socket virtlockd.socket
Wants=virtlogd.socket virtlockd.socket

[Service]
# 改为 simple 类型，避免 notify 导致的阻塞
Type=simple
# 设置启动超时
TimeoutStartSec=30
```

后续分析?
```
[ssh_10.30.11.126] root@node1: ~$systemctl list-jobs | grep remote-fs
  241 remote-fs.target                     start waiting
  176 remote-fs-pre.target                 start waiting

[ssh_10.30.11.126] root@node1: ~$systemctl status remote-fs
Unit remote-fs.service could not be found.

[ssh_10.30.11.126] root@node1: ~$systemctl status remote-fs.target
● remote-fs.target - Remote File Systems
   Loaded: loaded (/usr/lib/systemd/system/remote-fs.target; enabled; vendor preset: enabled)
   Active: inactive (dead)
     Docs: man:systemd.special(7)

Jan 23 11:36:28 localhost.localdomain systemd[1]: Reached target Remote File Systems.
Jan 23 11:36:30 localhost.localdomain systemd[1]: Stopped target Remote File Systems.

[ssh_10.30.11.126] root@node1: ~$systemctl status remote-fs-pre.target
● remote-fs-pre.target - Remote File Systems (Pre)
   Loaded: loaded (/usr/lib/systemd/system/remote-fs-pre.target; static; vendor preset: disabled)
   Active: inactive (dead)
     Docs: man:systemd.special(7)

Jan 23 11:36:28 localhost.localdomain systemd[1]: Reached target Remote File Systems (Pre).
Jan 23 11:36:30 localhost.localdomain systemd[1]: Stopped target Remote File Systems (Pre).

[ssh_10.30.11.126] root@node1: ~$date
Fri Jan 23 11:14:08 CST 2026
```

## FAQ

#### Machine 'qemu-3-d4b7a760-68a9-3384-a032-c340d07b8538' already exists

```
# 查看系统中有哪些虚拟机
sudo machinectl list

# 强制删除已存在的虚拟机
sudo machinectl terminate qemu-3-d4b7a760-68a9-3384-a032-c340d07b8538

# 或使用systemctl
sudo systemctl stop machine-qemu\\x2d3\\x2dd4b7a760\\x2d68a9\\x2d3384\\x2da032\\x2dc340d07b8538.scope
sudo systemctl reset-failed machine-qemu\\x2d3\\x2dd4b7a760\\x2d68a9\\x2d3384\\x2da032\\x2dc340d07b8538.scope
```

#### 开启qemu的coredump文件

```
ulimit -c unlimited
sysctl -w kernel.core_pattern=/var/crash/core-%e.%p
# 修改/etc/libvirtd/qemu.conf
max_core = "unlimited"
systemctl restart libvirtd
```

可以实时查看qemu进程的limit配置
```
cat /proc/`pidof qemu-kvm`/limits
```

手动kill进程，验证生成coredump文件
```
killall -11 qemu-kvm
```
=> 验证发现手动kill runtime-server可以产生, qemu-kvm只有日志文件有堆栈信息, 可能捕获了这个信号(魔改版qemu的逻辑。。。)

#### mac地址错误, 添加网卡失败

libvirt: Domain Config error : XML 错误：意外单播 mac 地址，找到多播 '11:11:22:22:33:00'

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


## 其他资料

[Installation of a libvirt VM over a serial console](https://p5r.uk/blog/2020/libvirt-vm-installation-over-serial-console.html)
