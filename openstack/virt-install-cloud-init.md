# 使用virt-install安装cloud-init虚拟机

关键字《virt-install ubuntu server cloud-init》

[Create Virtual Machines Using Virt-Install(Libvert) With Cloud-Init](https://technekey.com/create-virtual-machines-using-virt-installlibvert-with-cloud-init/)

[Provision a VM with Cloud Image and Cloud-init](https://zhimin-wen.medium.com/provision-a-vm-with-cloud-image-and-cloud-init-36f356a33b90)

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
