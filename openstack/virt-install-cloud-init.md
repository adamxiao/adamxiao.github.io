# 使用virt-install安装cloud-init虚拟机

关键字《virt-install ubuntu server cloud-init》

[Create Virtual Machines Using Virt-Install(Libvert) With Cloud-Init](https://technekey.com/create-virtual-machines-using-virt-installlibvert-with-cloud-init/)

[Provision a VM with Cloud Image and Cloud-init](https://zhimin-wen.medium.com/provision-a-vm-with-cloud-image-and-cloud-init-36f356a33b90)

## cloud-init概念

主要是一下几个服务
- cloud-init-local.service
- cloud-init.service
- cloud-config.service
- cloud-final.service

## 安装使用

#### step-0: Create your cloud-init configuration file; here is my sample cloud-init file.

```
#cloud-config
system_info:
  default_user:
    name: adam
    home: /home/adam
    sudo: ALL=(ALL) NOPASSWD:ALL
password: adamxiao
chpasswd: { expire: False }
hostname: adam-pc
ssh_authorized_keys:
- ssh-ed25519 AAAsfdfNzasdfsdZDIgfsdgsdTE5FAKEFAKEFAKEFAKE-FAKE-FAKEWsXhHL0ah2QUUbt1f ps@controller


# if you want to allow SSH with password, set this to true
ssh_pwauth: True

# list of packages to install after the VM comes up
package_upgrade: true
packages:
- nfs-common

#run the commands after the first install, the last command is saving VM ip into /tmp/my-ip file
runcmd:
- sudo systemctl enable iscsid
- sudo systemctl start iscsid
- sudo systemctl start apache2
- ip addr show $(ip route get 1.1.1.1  |grep -oP 'dev\s+\K[^ ]+')  |grep -oP '^\s+inet\s+\K[^/]+' |tee /tmp/my-ip
```

创建配置文件: userdata.yaml
```
#cloud-config
hostname: cl-ubuntu
fqdn: cl-ubuntu
manage_etc_hosts: false
ssh_pwauth: true
disable_root: false
users:
  - default
  - name: ubuntu
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: false
    ssh-authorized-keys:
      - "content of ssh public key..."
chpasswd:
  list: |
    root:password
    ubuntu:password
  expire: false
runcmd:
  - [ sh, -c, echo 192.168.100.10 cl-ubuntu | tee -a /etc/hosts]
```

创建网络配置: network.yaml
```
version: 2
ethernets:
  ens3:
    dhcp4: false
    addresses: [ 192.168.100.10/24 ]
    gateway4: 192.168.100.1
    nameservers:
      addresses: [ 192.168.100.1 ]
```

#### 获取虚拟机云镜像

```
wget https://cloud.debian.org/images/cloud/buster/latest/debian-10-generic-amd64.qcow2
curl -LO http://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64-disk-kvm.img
```

#### 创建新的qcow2镜像

扩容大小为100G
```
qemu-img convert  -f qcow2 -O qcow2 debian-10-generic-amd64.qcow2 debian.qcow2
qemu-img resize debian.qcow2 100G
```

#### 创建cloud-init配置iso

ubuntu 20.04安装cloud-localds工具
```
sudo apt install cloud-image-utils
```

生成iso
```
cloud-localds  debian_cloud_init.iso userdata.yaml
```

#### 安装发布虚拟机

```
virt-install 
 --name={{ .vmName }} \
 --ram={{ .mem }} \
 --vcpus={{ .cpu }} \
 --disk path={{ .path }}/{{ .vmName }}.qcow2,bus=virtio,cache=none \
 --disk path={{ .vmName }}-seed.qcow2,device=cdrom \
 --noautoconsole \
 --graphics=vnc \
 --network network={{ .network }},model=virtio \
 --boot hd
```

创建镜像
```
virt-install --name debian \
  --disk debian.qcow2,device=disk,bus=virtio   \
  --disk debian_cloud_init.iso,device=cdrom \
  --os-variant="debian10" \
  --virt-type kvm \
  --graphics none \
  --vcpus "2" \
  --memory "2048" \
  --network network=default,model=virtio \
  --console pty,target_type=serial \
  --import
```

创建镜像
```
virt-install --name debian \
  --disk rhcos.qcow2,device=disk,bus=virtio   \
  --disk debian_cloud_init.iso,device=cdrom \
  --os-variant="debian10" \
  --virt-type kvm \
  --graphics none \
  --vcpus "2" \
  --memory "2048" \
  --network network=default,model=virtio \
  --console pty,target_type=serial \
  --import
```

## 其他资料

#### openstack iso vm create

关键字《openstack iso vm create》

[How to manually create an OpenStack image](https://www.mirantis.com/blog/how-to-manually-create-an-openstack-image)

手动创建openstack qcow2镜像

[Launch an instance using ISO image](https://docs.openstack.org/nova/rocky/user/launch-instance-using-ISO-image.html)


### diskimage-builder构建镜像

关键字《diskimage-builder 用法》

https://davycloud.com/post/using-diskimage-builder-to-build-image/

安装diskimage-builder
```
pip install diskimage-builder
# 大部分的镜像格式需要用到 qemu-img 工具，得额外安装一下：
yum install qemu-img
apt install qemu-utils
```

快速使用
```
一个虚机镜像至少需要指定 2 个 elements，例如：
disk-image-create  centos7 vm
```

https://xionchen.github.io/2016/10/01/dib-introduction/
dib的安装方式有两种:pip安装和源码安装. 如果不需要对代码进行改变和定制的话可以直接进行源码安装,否则的话推荐使用源码安装

#### 使用私有镜像仓库源

https://docs.openstack.org/diskimage-builder/latest/elements/apt-sources/README.html

```
DIB_APT_SOURCES=/etc/apt/sources.list
```

#### 构建debian镜像

https://docs.openstack.org/ironic-python-agent-builder/latest/admin/dib.html
构建IPA镜像, 基于debian
```
export DIB_APT_SOURCES=/etc/apt/sources.list
export DIB_RELEASE=bullseye
# 配置用户名密码
export DIB_DEV_USER_USERNAME=ipa
export DIB_DEV_USER_PWDLESS_SUDO=yes
export DIB_DEV_USER_PASSWORD='123'

disk-image-create -o ironic-python-agent \
    ironic-python-agent-ramdisk debian devuser
```

#### 禁用cloudinit

https://www.jianshu.com/p/2fcfee762877

非云环境，可以选择关闭它，或者彻底删除，方法如下：

方法 1: 通过创建文件禁用 cloud-init
这是最简单最安全的方法，在 /etc/cloud 目录下创建 cloud-init.disabled 文件重启后生效。删除该文件就可以恢复
```
sudo touch /etc/cloud/cloud-init.disabled
```
重启

方法 2: 移除 cloud-init 软件包及文件夹
该方法彻底移除 cloud-init
```
sudo apt purge cloud-init -y
sudo rm -rf /etc/cloud && sudo rm -rf /var/lib/cloud/
```
重启

#### 其他资料

- [HowTo Create OpenStack Cloud Image with NVIDIA GPU and Network Drivers](https://docs.nvidia.com/networking/display/public/SOL/HowTo+Create+OpenStack+Cloud+Image+with+NVIDIA+GPU+and+Network+Drivers)

- [(好)制作openstack镜像](https://hlyani.github.io/notes/openstack/make_openstack_image.html)
  => 有windows, ubuntu, centos等镜像制作方法，还有qemu-img制作镜像的方法

3、安装cloud-utils-growpart来允许分区来调整大小
```
yum install -y cloud-utils-growpart
```

- [Diskimage-builder简介](https://xionchen.github.io/2016/10/01/dib-introduction/)
  3.4 DIB运行的阶段
  dib通过element和阶段来组织脚本,一个element可能在不同的阶段做不同的事情.
  所有的阶段如下:
  - root.d
  - extra-data.d
  - pre-install.d
  - install.d
  - post-install.d
  - block-device.d
  - finalise.d
  - cleanup.d

  DIB这个工具目前而言,制作镜像的能力主要覆盖社区的基础设施.如果需要定制自己的镜像也可以按照这个框架来.但是进行复杂的定制需要对DIB本身,shell和操作系统三个方面比较都比较了解.所以在之后会细致的解读DIB的源码.

- [(好)用 Diskimage-Builder 制作镜像](https://davycloud.com/post/using-diskimage-builder-to-build-image/)
  OpenStack 上的虚机最常用的镜像格式是 qcow2。早期的时候，要制作这样的镜像需要从 iso 镜像手动创建虚机，然后安装完系统后把磁盘保存为镜像。整个过程非常繁琐。
  现在常用的 Linux 系统如 Ubuntu、CentOS 都提供了现成的 qcow2 格式的最小安装镜像文件，可以直接下载使用。现在的难题变成了如何制作一个安装了自定义软件的定制镜像。
  快速开始
  一个虚机镜像至少需要指定 2 个 elements，例如：
```
disk-image-create  centos7 vm
其中 centos7 是指定操作系统发行版，这个是必需的。其它还有哪些操作系统支持，可以在文档里查询。
vm 就是指镜像是供虚拟机用的。如果要制作可供 Ironic 使用的裸金属镜像，则需要指定 baremetal。
```
