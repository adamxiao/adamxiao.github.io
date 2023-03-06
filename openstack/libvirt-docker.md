# libvirt在docker容器中运行

问题:
- libvirt进程不能是1号进程，否则不会回收qemu-kvm子进程

临时测试方法:
```
docker run -d --privileged --name libvirt \
  -p 16509:16509 \
  -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
  -v /data/vm-images/:/vm-images \
  libvirtd-container
```

#### 使用xml定义一个虚拟机

参考: [15 使用 virsh 配置虚拟机](https://documentation.suse.com/zh-cn/sles/15-SP2/html/SLES-all/cha-libvirt-config-virsh.html)

使用virsh命令创建
```
virsh -c qemu+tcp://10.20.1.99/system
> define centos7.xml
```

其中centos7.xml内容如下:
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
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='/vm-images/centos7.img'/>
      <target dev='vda' bus='virtio'/>
    </disk>
  </devices>
</domain>
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

## 其他资料

配置文件 /etc/libvirt/qemu.conf
```
user = "kylin-ksvd"
dynamic_ownership = 0
group = "disk"

migrate_tls_x509_cert_dir = "/etc/pki/libvirt-migrate"
migrate_tls_x509_verify = 0

stdio_handler="file"
```

## FAQ

#### Cannot read CA certificate '/etc/pki/CA/cacert.pem': No such file or directory

监听tcp端口，要么需要证书，要么取消tls认证

配置libvirt配置文件为
```
#unix_sock_group = "kylin-ksvd"
unix_sock_rw_perms = "0770"
unix_sock_admin_perms = "0770"
auth_unix_ro = "none"
auth_unix_rw = "none"
listen_tcp = 1
listen_tls = 0
auth_tcp = "none"
log_level = 3
log_outputs = "3:file:/var/log/libvirt/libvirtd.log"
```

#### 启动虚拟机失败: error: can't connect to virtlogd: Failed to connect socket to '/run/libvirt/virtlogd-sock': No such file or directory

https://github.com/crc-org/crc/issues/629

Add `stdio_handler="file"` to  `/etc/libvirt/qemu.conf`

#### 启动虚拟机失败: failed to initialize KVM: Permission denied

运行容器增加`--device /dev/kvm`参数?
=> 最终还有chmod 666 /dev/kvm暂时解决!

```
error: Failed to start domain centos7
error: internal error: qemu unexpectedly closed the monitor: Could not access KVM kernel module: Permission denied
2023-03-01T05:47:14.825945Z qemu-system-x86_64: failed to initialize KVM: Permission denied
```

libvirt的错误日志
```
2023-03-01 06:12:28.280+0000: 1: error : qemuMonitorIORead:509 : Unable to read from monitor: Connection reset by peer
2023-03-01 06:12:28.280+0000: 1: error : qemuProcessReportLogError:2065 : internal error: qemu unexpectedly closed the monitor: Could not access KVM kernel module: Permission denied
2023-03-01T06:12:28.278974Z qemu-system-x86_64: failed to initialize KVM: Permission denied
```
