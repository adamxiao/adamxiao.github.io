# ubuntu cloud镜像使用

## ubuntu cloud镜像

问题:
- 不能自动扩容文件系统?
  => 必须配合cloudinit使用...
- 没有qga，不能在线修改密码
  => 必须配合cloudinit使用...
- 没有生成netplan默认dhcp网络配置
  => 必须配合cloudinit使用...

### 下载镜像

参考openstack中的获取ubuntu镜像
https://docs.openstack.org/image-guide/obtain-images.html

关键字《ubuntu-20.04-server-cloudimg-amd64-disk-kvm.img 不能用》

镜像列表
- ubuntu-20.04-server-cloudimg-amd64-disk-kvm.img
  名字中带有disk-kvm是什么作用?
  grub启动失败: `GRUB_FORCE_PARTUUID set, attempting initrdless boot.`
- ubuntu-20.04-server-cloudimg-amd64.img
  => 可以用
- focal-server-cloudimg-arm64.img
  有cloudinit?
  => pty控制台能使用，vnc没有shell? => 可能因为是daily build，不是release版本? => 或者是cloudinit配置不启用shell? => console=ttyS0 内核参数?
  => 果然发现ubuntu 22.04内核参数有 `console=ttyS0 console=tty1`
  => 加了`console=ttyS0`之后，guest disabled display...
  => 发现amd64的镜像, 就是有console参数的, 但是不是写在/etc/default/grub中
  => 猜测, 没有串口驱动?
- ubuntu-20.04-server-cloudimg-arm64.img (release-20230506)
  => 同上, vnc没有shell!

- ubuntu-22.04-server-cloudimg-arm64.img (release-20230518)
  => 有cloudinit可以设置密码, vnc也能用

- ubuntu-18.04-server-cloudimg-amd64.img (release-20230525) => ok

参考google cloud， 看使用ubuntu 22.04 server arm64版本怎么样?
https://cloud.google.com/compute/docs/images/os-details?hl=zh-cn#general-info

### 使用

同样可以参考[./virt-install-cloud-init.md](./virt-install-cloud-init.md)
=> 原来ubuntu cloud镜像一定要配合cloud-init才行...

关键字《ubuntu cloud image使用》

[在kvm中使用ubuntu cloud image](https://www.jianshu.com/p/aad72f1ab267)

首先创建cloud-init配置文件
```
cat >ubuntu2004-init.conf <<EOF
#cloud-config
apt:
  primary:
    - arches: [default]
      uri: http://docker.iefcu.cn:5565/repository/ubuntu-cn-proxy
timezone: Asia/Shanghai
password: ubuntu
ssh_pwauth: False
runcmd:
  - [ apt, -y, remove, cloud-init ]
EOF
```
=> 最后帐号是ubuntu, 密码是上述配置, 首次进入系统会强制改密码

生成nocloud iso
```
cloud-localds ubuntu2004-init.img ubuntu2004-init.conf
```

其他
```
# 导入基础镜像，制作出模板镜像
virt-install --os-variant ubuntu20.04 \
--name ubuntu2004 \
--memory 4096 \
--vcpus 2 \
--network bridge=br0 \
--disk ubuntu2004.img,device=disk,bus=virtio \
--disk ubuntu2004-init.img,device=cdrom \
--graphics none \
--import

# 关机
virsh shutdown ubuntu2004
# 拔出 Cloud Init 光盘镜像
virsh change-media ubuntu2004 sda --eject --config
```

使用模板镜像生成虚拟机
```
# 使用 clone 的方式从模板镜像直接生成虚拟机
virt-clone -o ubuntu2004 -n ubuntu2004-clone -f ubuntu2004-clone.img
# 通过直接修改镜像中的配置文件配置静态ip地址
virt-customize -a ubuntu2004-clone.img --run-command 'echo "network:\n  version: 2\n  ethernets:\n    enp1s0:\n      dhcp4: false\n      addresses: [192.168.2.2/24]\n      gateway4: 192.168.2.1\n      nameservers:\n        addresses: [192.168.2.250]" >/etc/netplan/50-cloud-init.yaml'

# 修改密码
virt-customize -a ubuntu2004-clone.img --password ubuntu:password:ubuntu
# 修改 root 密码
virt-customize -a ubuntu2004-clone.img --root-password password:root
```

直接修改镜像里面的cloud-init配置? => 相当于cloud-init本地数据源?

[如何制作自己的云镜像](https://bleatingsheep.org/2022/03/14/%E7%94%A8-Ubuntu-Cloud-Images-%E5%88%B6%E4%BD%9C%E8%87%AA%E5%B7%B1%E7%9A%84%E4%BA%91%E9%95%9C%E5%83%8F%EF%BC%88%E9%85%8D%E7%BD%AE-cloud-init-%E7%9A%84-NoCloud-%E6%95%B0%E6%8D%AE%E6%BA%90%EF%BC%89/)

修改 cloud-init 配置
用 cd /mnt/etc/cloud/cloud.cfg.d 切换到 cloud.cfg.d 目录，sudo nano 99-fake_cloud.cfg 创建文件 99-fake_cloud.cfg，内容如下：
```
# configure cloud-init for NoCloud
hostname: myhost # 修改为你的主机名

users:
  - name: foobar # 修改为你的用户名
    gecos: Foo B. Bar # 修改为你的全名
    groups: [adm, audio, cdrom, dialout, dip, floppy, lxd, netdev, plugdev, sudo, video]
    ssh_authorized_keys:
      - '<paste your public key here>' # 修改为你的 SSH 公钥
    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
    shell: /bin/bash

chpasswd:
  expire: true
  list:
    - foobar:foobar # 修改为你的用户名和密码
datasource_list: [ NoCloud, None ]
```


### 用户密码配置

focal-server-cloudimg-xxx 这些镜像是为云环境创建的, 会配合一个init脚本(或者iso)启动并创建普通用户, 默认root不能登录也没有密码, 而单机运行还是需要root的, 所以在安装前, 要设置一下root口令:
```
virt-customize -a some.qcow2c --root-password password:[your password]
```

### 镜像扩容

ubuntu的cloud镜像没有自动扩容的功能, 需要自己手动扩容?

## debian cloud镜像使用

优点:
- 文件系统会自动扩容
- 镜像模板非常小

问题:
- 没有安装qga, 无法在线修改密码功能?
- debian的网络配置，我不熟悉, 不是nmcli, 也不是netowrk, 也不是netplan
- 关键是还没有开启ssh服务? (debian 11?)
  => 原来是no hostkeys available => ssh-keygen -A
  还一定要密钥登录。。。

debian 10镜像都可以的样子?

- debian-10-generic-amd64.qcow2
- debian-10-openstack-amd64.qcow2
- debian-10-openstack-arm64.qcow2

debian 11
- debian-11-generic-amd64-20230124-1270.qcow2
  => 可以用, 但是no hostkeys available?
- debian-11-generic-amd64-20230501-1367.qcow2
  => 可以用
- debian-11-generic-arm64-20230124-1270.qcow2
  => 不行, 一直黑屏? 去除memory balloon也不行(银河麒麟需要去除)
  => 0501版本也不行

关键字《debian 11 arm64 guest disabled display》

#### 上传到openstack中使用

```
openstack image create \
    --container-format bare \
    --disk-format qcow2 \
    --property hw_disk_bus=scsi \
    --property hw_scsi_model=virtio-scsi \
    --property os_type=linux \
    --property os_distro=debian \
    --property os_admin_user=debian \
    --property os_version='10.9.1' \
    --public \
    --file debian-10-generic-arm64-20210329-591.qcow2 \
    debian-10-generic-arm64-20210329-591.qcow2
```

#### 设置静态ip地址

参考: [如何在 Debian 11 系统上设置静态IP地址](https://segmentfault.com/a/1190000043209392)

最小化安装，没有nmcli, 创建文件 /etc/network/interfaces.d/enp4s1
```
# The primary network interface
auto enp4s1
iface enp4s1 inet static
 address 10.90.2.193
 netmask 255.255.255.0
 gateway 10.90.2.1
 dns-nameservers 8.8.8.8
```

重启networking服务生效

#### 镜像格式

debian 11 x86
```
Disk /dev/nbd0: 2147 MB, 2147483648 bytes, 4194304 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: gpt
Disk identifier: 0AC3B12E-66F0-2D42-83EF-E6E4C0179E1A


#         Start          End    Size  Type            Name
 1       262144      4194270    1.9G  Linux filesyste
14         2048         8191      3M  BIOS boot
15         8192       262143    124M  EFI System
```

debian 11 arm
```
Disk /dev/nbd0: 2147 MB, 2147483648 bytes, 4194304 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: gpt
Disk identifier: 3B1412AE-1A6E-4143-973E-981CDF9F832C


#         Start          End    Size  Type            Name
 1       262144      4194270    1.9G  Linux filesyste
15         2048       262143    127M  EFI System
```

## centos cloud镜像使用

- centos7 x86镜像
  用的最多的，不错!
- centos7 arm
  每次都卡在cloudinit中..., 不是很好用

## windows cloud镜像使用

- win2022en-standard-minimal.vmdk
  大小11G, 网上下载到的, 不支持uefi启动!
  => 首次启动, 需要花费比较长的时间, 可以页面设置密码
  => 感觉应该比较好用!

记得之前下载过一个win2012-server的，忘了在哪里了，使用了sysgrep吧!

## coreos

之前有一种方法，将点火文件ign打到iso中去

关键字《coreos qcow2使用》《coreos qcow2使用点火文件》

https://www.osgeo.cn/coreos/fedora-coreos/provisioning-qemu/
=> 未验证
```
qemu-img create -f qcow2 -b fedora-coreos-qemu.qcow2 my-fcos-vm.qcow2
qemu-kvm -m 2048 -cpu host -nographic \
-drive if=virtio,file=my-fcos-vm.qcow2 \
-fw_cfg name=opt/com.coreos/config,file=path/to/example.ign \
-nic user,model=virtio,hostfwd=tcp::2222-:22
```

https://linux.cn/article-12912-1.html

创建点火文件 config.yaml
以下配置创建了一个 core 用户，并在 authorized_keys 文件中添加了一个 SSH 密钥。它还创建了一个 systemd 服务，使用 podman 来运行一个简单的 “hello world” 容器：
```
version: "1.0.0"
variant: fcos
passwd:
  users:
    - name: core
      ssh_authorized_keys:
        - ssh-ed25519 my_public_ssh_key_hash fcos_key
systemd:
  units:
    -
      contents: |
          [Unit]
          Description=Run a hello world web service
          After=network-online.target
          Wants=network-online.target
          [Service]
          ExecStart=/bin/podman run --pull=always   --name=hello --net=host -p 8080:8080 quay.io/cverna/hello
          ExecStop=/bin/podman rm -f hello
          [Install]
          WantedBy=multi-user.target
      enabled: true
      name: hello.service
```

转为json格式
```
$ sudo dnf install fcct
$ fcct -output config.ign config.yaml
```

运行虚拟机
```
$ chcon --verbose unconfined_u:object_r:svirt_home_t:s0 config.ign
$ virt-install --name=fcos \
--vcpus=2 \
--ram=2048 \
--import \
--network=bridge=virbr0 \
--graphics=none \
--qemu-commandline="-fw_cfg name=opt/com.coreos/config,file=${PWD}/config.ign" \
--disk=size=20,backing_store=${PWD}/fedora-coreos-32.20200907.3.0-qemu.x86_64.qcow2
```

https://blog.gmem.cc/coreos-faq
libvirt/Ignition-config
当前推荐的配置CoreOS的方式是Ignition，但是目前libvirt没有对Ignition的直接支持，需要引入QEMU特有的配置片断。

还能这样?
```
<filesystem type='mount' accessmode='squash'>
    <source dir='/home/alex/Vmware/KVM/coreos-20/cloud-config/'/>
    <target dir='config-2'/>
</filesystem>
```

使用libvirt配置
```
<domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
    ...
    <qemu:commandline>
        <qemu:arg value="-fw_cfg"/>
        <qemu:arg value="name=opt/com.coreos/config,file=/home/alex/Vmware/libvirt/mount/coreos-base/provision.ign"/>
  </qemu:commandline>
</domain>
```

[在 Podman 中运行一个 Linux 虚拟机](https://www.51cto.com/article/675547.html)
=> 后续尝试

[从 CoreOS 迁移到 Fedora CoreOS 之 用 fcct 初始化 fcos](https://blog.epurs.com/post/fcos-fcct/)

[使用 Fedora CoreOS 36 创建 Kubernetes 集群](https://devpress.csdn.net/cicd/62ed23277e668234661808c4.html)
估计是通过virt-manager部署k8s集群

[OpenShift Assisted Installer – 让安装更加简单](https://www.talkwithtrend.com/Article/257115)

## nocloud iso镜像制作

创建配置文件
```
#cloud-config
password: ksvd2020
chpasswd: { expire: False }
ssh_pwauth: True
timezone: Asia/Shanghai
```

其实就是这些文件
- user-data
- meta-data
- network-config => 可选

制作引导iso镜像, 使用cloud-localds工具(cloud-init包提供)
```
cloud-localds xxx.iso xxx.conf
```

## FAQ

#### image cloud-init初始化后，放到另外一个虚拟机硬件中跑，密码居然不正确了，cloud-init重新初始化了?

xxx

## 参考资料

- [cloud-init文档](https://cloudinit.readthedocs.io/en/latest/reference/modules.html)

- [使用 KVM 为 Ubuntu 云映像在本地测试 cloud-init](https://blog.csdn.net/allway2/article/details/122170998)
  禁用 cloud-init 系统, `touch /etc/cloud/cloud-init.disabled`
  创建网络配置, xxx
